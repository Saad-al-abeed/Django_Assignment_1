from django import forms
from .models import Category, Event, Participant

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
        fields = ['name', 'description', 'date', 'time', 'location', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'w-full px-3 py-2 border rounded', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'email', 'events']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'events': forms.SelectMultiple(attrs={'class': 'w-full px-3 py-2 border rounded h-32'}),
        }
