import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from parking.models import ParkingLocation, ParkingSlot, User
import decimal
import random

user, _ = User.objects.get_or_create(username='testuser', email='test@example.com')
user.set_password('password123')
user.save()

loc1, _ = ParkingLocation.objects.get_or_create(
    name='Connaught Place Smart Parking',
    address='Inner Circle, Delhi, India',
    lat=28.6304,
    lng=77.2177,
    total_slots=150,
    base_price=decimal.Decimal('50.00'), 
    is_covered=True,
    has_ev_charging=True
)

loc2, _ = ParkingLocation.objects.get_or_create(
    name='BKC Neo-Park',
    address='Bandra Kurla Complex, Mumbai, India',
    lat=19.0658,
    lng=72.8687,
    total_slots=200,
    base_price=decimal.Decimal('80.00'),
    is_covered=True,
    has_ev_charging=True
)

loc3, _ = ParkingLocation.objects.get_or_create(
    name='Electronic City Grid Node',
    address='Phase 1, Bangalore, India',
    lat=12.8399,
    lng=77.6770,
    total_slots=100,
    base_price=decimal.Decimal('40.00'),
    is_covered=False,
    has_ev_charging=True
)

v_types = ['2-wheeler', '3-wheeler', '4-wheeler']

for loc in [loc1, loc2, loc3]:
    if loc.slots.count() == 0:
        for i in range(1, 41): 
            v_type = random.choice(v_types)
            ParkingSlot.objects.create(
                location=loc,
                slot_number=f"{loc.name[:3].upper()}-{i:03d}",
                vehicle_type=v_type,
                is_available=(random.random() > 0.3) 
            )
            
print("Database seeded with sample Indian parking locations.")
