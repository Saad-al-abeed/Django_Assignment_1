from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    phone_number = models.CharField(max_length=15, blank=True) # Basic validation can be added in forms

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rsvp_events', blank=True)
    event_image = models.ImageField(upload_to='event_images/', default='event_images/default.jpg')

    def __str__(self):
        return self.name
