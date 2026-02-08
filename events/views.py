from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.models import Group
User = get_user_model()
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator, classonlymethod
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View, RedirectView
from django.utils import timezone
from .models import Category, Event
from .forms import CategoryForm, EventForm, UserSignupForm, UserUpdateForm
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

# Authentication Views
class UserSignupView(UserPassesTestMixin, CreateView):
    model = User
    form_class = UserSignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def test_func(self):
        return self.request.user.is_anonymous

    def handle_no_permission(self):
        return redirect('dashboard')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False # Deactivate until email confirmation
        user.save()
        
        # Default to 'Participant' group
        group, created = Group.objects.get_or_create(name='Participant')
        user.groups.add(group)
        
        # Signal send_activation_email will handle the email
        messages.success(self.request, 'Account created! Please check your email to activate your account.')
        return super().form_valid(form)

class ActivateAccountView(RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated! You can now login.')
        else:
            messages.error(request, 'Activation link is invalid!')
        return super().get(request, *args, **kwargs)

# Dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        user = self.request.user
        if user.groups.filter(name='Admin').exists():
            return ['events/dashboard_admin.html']
        elif user.groups.filter(name='Organizer').exists():
            return ['events/dashboard_organizer.html']
        else:
            return ['events/dashboard_participant.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        
        if user.groups.filter(name='Admin').exists():
            context['total_users'] = User.objects.count()
            context['total_events'] = Event.objects.count()
            context['total_categories'] = Category.objects.count()
            context['events'] = Event.objects.all().order_by('date') # Show all events for admin
        elif user.groups.filter(name='Organizer').exists():
            # Assuming organizers can see all events or just theirs? 
            # Existing code: Event.objects.all().order_by('date')
            context['total_events'] = Event.objects.count()
            context['total_categories'] = Category.objects.count()
            context['events'] = Event.objects.all().order_by('date')
        else: # Participant
            context['rsvp_events'] = user.rsvp_events.all()
        return context

# RSVP
class RSVPEventView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.groups.filter(name='Participant').exists()

    def handle_no_permission(self):
         messages.warning(self.request, "Only participants can RSVP.")
         return redirect('event_detail', pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        event = get_object_or_404(Event, pk=pk)
        if request.user in event.participants.all():
            messages.warning(request, "You have already RSVP'd to this event.")
        else:
            event.participants.add(request.user)
            messages.success(request, f"You have successfully RSVP'd to {event.name}!")
        return redirect('event_detail', pk=pk)

# Profile Views
class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'events/profile_detail.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'events/profile_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)

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
