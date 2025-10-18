#!/usr/bin/env python3
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rayan_backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from api.models import Course, Term, Profile, User

print("=" * 50)
print("Testing Database Content")
print("=" * 50)

print(f"\nCourses: {Course.objects.count()}")
for course in Course.objects.all()[:5]:
    print(f"  - {course.name}")

print(f"\nTerms: {Term.objects.count()}")
for term in Term.objects.all()[:5]:
    print(f"  - {term.name} ({term.course.name})")

print(f"\nProfiles: {Profile.objects.count()}")
for profile in Profile.objects.all()[:5]:
    user = profile.user
    print(f"  - {user.first_name} {user.last_name} ({user.phone_number})")

print(f"\nUsers: {User.objects.count()}")
print(f"Superusers: {User.objects.filter(is_superuser=True).count()}")

print("\n" + "=" * 50)
print("Testing API Endpoints (authentication required)")
print("=" * 50)

from django.test import Client
from api.models import User

client = Client()

# Get a superuser for authentication
superuser = User.objects.filter(is_superuser=True).first()
if superuser:
    client.force_login(superuser)
    print(f"\nAuthenticated as: {superuser.phone_number}")

    # Test endpoints
    endpoints = [
        ('/api/courses/', 'Courses'),
        ('/api/terms/', 'Terms'),
        ('/api/profiles/', 'Profiles'),
        ('/api/apollonyars/', 'Apollonyars'),
        ('/api/groups/', 'Groups'),
    ]

    for url, name in endpoints:
        response = client.get(url)
        status = '✓' if response.status_code == 200 else '✗'
        print(f"{status} {name}: {response.status_code}")
        if response.status_code == 200:
            import json
            data = json.loads(response.content)
            if isinstance(data, list):
                print(f"   Found {len(data)} items")
            elif isinstance(data, dict) and 'results' in data:
                print(f"   Found {len(data['results'])} items")
else:
    print("No superuser found!")
