from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Category, Event

User = get_user_model()

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded', 'rows': 3}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category', 'event_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'event_image': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }

class UserSignupForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}), required=False)
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'w-full px-3 py-2 border rounded'}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}), required=False)
    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'w-full px-3 py-2 border rounded'}), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']

