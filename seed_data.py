import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from parking.models import ParkingLocation, ParkingSlot, User
import decimal

# Create dummy users
user, _ = User.objects.get_or_create(username='testuser', email='test@example.com')
user.set_password('password123')
user.save()

# Create dummy locations
loc1, _ = ParkingLocation.objects.get_or_create(
    name='City Center Mall',
    address='123 Downtown Ave, NY',
    lat=40.7128,
    lng=-74.0060,
    total_slots=50,
    base_price=decimal.Decimal('5.00'),
    is_covered=True,
    has_ev_charging=False
)

loc2, _ = ParkingLocation.objects.get_or_create(
    name='Central Park West',
    address='45 Park Street, NY',
    lat=40.7829,
    lng=-73.9654,
    total_slots=20,
    base_price=decimal.Decimal('8.50'),
    is_covered=False,
    has_ev_charging=True
)

loc3, _ = ParkingLocation.objects.get_or_create(
    name='Brooklyn Tech Hub',
    address='89 Brooklyn Bridge Blvd, NY',
    lat=40.6971,
    lng=-73.9936,
    total_slots=100,
    base_price=decimal.Decimal('3.00'),
    is_covered=True,
    has_ev_charging=True
)

# Create dummy slots
for loc in [loc1, loc2, loc3]:
    if loc.slots.count() == 0:
        for i in range(1, 16): # create 15 slots for each to test
            ParkingSlot.objects.create(
                location=loc,
                slot_number=f"{loc.name[:2].upper()}-{i:03d}",
                vehicle_type='car',
                is_available=(i % 3 != 0) # Every 3rd slot is occupied
            )
            
print("Database seeded with sample parking locations and slots.")
