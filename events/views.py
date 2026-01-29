from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.utils import timezone
from .models import Category, Event
from .forms import CategoryForm, EventForm, UserSignupForm
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

# Authentication Views
@unauthenticated_user
def sign_up(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate until email confirmation
            user.save()
            
            # Default to 'Participant' group
            group, created = Group.objects.get_or_create(name='Participant')
            user.groups.add(group)
            
            # Signal send_activation_email will handle the email
            messages.success(request, 'Account created! Please check your email to activate your account.')
            return redirect('login')
    else:
        form = UserSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated! You can now login.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('login')

# Dashboard
@login_required
def dashboard(request):
    today = timezone.now().date()
    # Common context
    context = {}
    
    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name
    
    if group == 'Admin':
        context['total_users'] = User.objects.count()
        context['total_events'] = Event.objects.count()
        context['total_categories'] = Category.objects.count()
        context['events'] = Event.objects.all().order_by('date')
        return render(request, 'events/dashboard_admin.html', context)
        
    elif group == 'Organizer':
        context['total_events'] = Event.objects.count()
        context['total_categories'] = Category.objects.count()
        context['events'] = Event.objects.all().order_by('date')
        return render(request, 'events/dashboard_organizer.html', context)
        
    else: # Participant
        # Events user has RSVP'd to
        context['rsvp_events'] = request.user.rsvp_events.all()
        return render(request, 'events/dashboard_participant.html', context)

# RSVP
@login_required
@allowed_users(allowed_roles=['Participant'])
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user in event.participants.all():
        messages.warning(request, "You have already RSVP'd to this event.")
    else:
        event.participants.add(request.user)
        messages.success(request, f"You have successfully RSVP'd to {event.name}!")
    return redirect('event_detail', pk=pk)

# Event Views
class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = Event.objects.select_related('category').prefetch_related('participants')
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(location__icontains=search_query)
            )
        
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset.annotate(participant_count=Count('participants'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    queryset = Event.objects.select_related('category').prefetch_related('participants')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_rsvped'] = self.object.participants.filter(id=self.request.user.id).exists()
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(['Admin', 'Organizer']), name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(['Admin', 'Organizer']), name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(['Admin', 'Organizer']), name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

# Category CRUD - Admin & Organizer only
@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(['Admin', 'Organizer']), name='dispatch')
class CategoryListView(ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'

@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(['Admin', 'Organizer']), name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(['Admin', 'Organizer']), name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(['Admin', 'Organizer']), name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'events/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
