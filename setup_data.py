
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def create_groups():
    groups = ['Admin', 'Organizer', 'Participant']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)
    print("Groups created.")

def create_users():
    # Admin
    admin_group = Group.objects.get(name='Admin')
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        admin.groups.add(admin_group)
        print("Superuser 'admin' created.")
    
    # Organizer
    organizer_group = Group.objects.get(name='Organizer')
    if not User.objects.filter(username='org').exists():
        org = User.objects.create_user('org', 'org@example.com', 'orgpass')
        org.groups.add(organizer_group)
        print("Organizer 'org' created.")

    # Participant
    participant_group = Group.objects.get(name='Participant')
    if not User.objects.filter(username='part').exists():
        part = User.objects.create_user('part', 'part@example.com', 'partpass')
        part.groups.add(participant_group)
        print("Participant 'part' created.")

if __name__ == '__main__':
    create_groups()
    create_users()
