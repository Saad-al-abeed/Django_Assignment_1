from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Event

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Activate Your Account'
        message = f'Hi {instance.username}, please click the link to activate your account: http://127.0.0.1:8000/activate/{instance.id}/'
        # In a real app, generate a secure token.
        
        print(f"\n[EMAIL SENT] To: {instance.email}\nSubject: {subject}\nBody: {message}\n")
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@example.com',
            [instance.email],
            fail_silently=False,
        )

@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_confirmation(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            subject = f'RSVP Confirmation for {instance.name}'
            message = f'Hi {user.username},\n\nYou have successfully RSVP\'d for {instance.name} on {instance.date} at {instance.time}.\n\nLocation: {instance.location}'
            
            print(f"\n[EMAIL SENT] To: {user.email}\nSubject: {subject}\nBody: {message}\n")
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
