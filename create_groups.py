import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group

groups = ['Admin', 'Organizer', 'Participant']
for name in groups:
    group, created = Group.objects.get_or_create(name=name)
    if created:
        print(f'Group "{name}" created')
    else:
        print(f'Group "{name}" already exists')
