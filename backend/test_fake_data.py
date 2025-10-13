#!/usr/bin/env python3
"""
Simple test script to verify fake data generation
Run this after populating fake data to check if everything was created correctly
"""

import os
import sys
import django

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rayan_backend.settings')
django.setup()

from api.models import *

def test_data_counts():
    """Test if all expected data was created"""
    print("=== Testing Fake Data Generation ===\n")
    
    # Count all models
    counts = {
        'Users': User.objects.count(),
        'Apollonyars': Apollonyar.objects.count(),
        'Courses': Course.objects.count(),
        'Terms': Term.objects.count(),
        'Groups': Group.objects.count(),
        'Assignment Definitions': AssignmentDef.objects.count(),
        'Call Definitions': CallDef.objects.count(),
        'Medal Definitions': MedalDef.objects.count(),
        'Profiles': Profile.objects.count(),
        'Assignments': Assignment.objects.count(),
        'Transactions': Transaction.objects.count(),
        'Installments': Installment.objects.count(),
        'Medals': Medal.objects.count(),
        'Discount Codes': DiscountCode.objects.count(),
        'Calls': Call.objects.count(),
        'Notes': Note.objects.count(),
        'Logs': Log.objects.count(),
    }
    
    # Display counts
    for model_name, count in counts.items():
        status = "✓" if count > 0 else "✗"
        print(f"{status} {model_name}: {count}")
    
    # Test relationships
    print("\n=== Testing Relationships ===")
    
    # Test profiles have proper relationships
    profiles_with_courses = Profile.objects.filter(course__isnull=False).count()
    profiles_with_apollonyars = Profile.objects.filter(apollonyar__isnull=False).count()
    profiles_with_groups = Profile.objects.filter(group__isnull=False).count()
    
    print(f"✓ Profiles with courses: {profiles_with_courses}")
    print(f"✓ Profiles with apollonyars: {profiles_with_apollonyars}")
    print(f"✓ Profiles with groups: {profiles_with_groups}")
    
    # Test assignments are properly assigned
    assignments_with_profiles = Assignment.objects.filter(profile__isnull=False).count()
    print(f"✓ Assignments with profiles: {assignments_with_profiles}")
    
    # Test installments have proper amounts
    installments_with_amounts = Installment.objects.filter(due_amount__gt=0).count()
    print(f"✓ Installments with amounts: {installments_with_amounts}")
    
    # Test medals are awarded
    medals_with_profiles = Medal.objects.filter(profile__isnull=False).count()
    print(f"✓ Medals with profiles: {medals_with_profiles}")
    
    print("\n=== Sample Data ===")
    
    # Show sample data
    if User.objects.exists():
        sample_user = User.objects.first()
        print(f"Sample User: {sample_user.first_name} {sample_user.last_name} - {sample_user.phone_number}")
    
    if Apollonyar.objects.exists():
        sample_apollonyar = Apollonyar.objects.first()
        print(f"Sample Apollonyar: {sample_apollonyar.first_name} {sample_apollonyar.last_name} - {sample_apollonyar.phone_number}")
    
    if Course.objects.exists():
        sample_course = Course.objects.first()
        print(f"Sample Course: {sample_course.name}")
    
    if Profile.objects.exists():
        sample_profile = Profile.objects.first()
        print(f"Sample Profile: {sample_profile.user.first_name} {sample_profile.user.last_name} - {sample_profile.course.name} - Hearts: {sample_profile.hearts}, Stars: {sample_profile.stars}")
    
    print("\n=== Test Complete ===")
    total_records = sum(counts.values())
    print(f"Total records created: {total_records}")

if __name__ == "__main__":
    test_data_counts()
