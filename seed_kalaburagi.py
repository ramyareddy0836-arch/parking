import os
import django
import decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from parking.models import ParkingLocation, ParkingSlot

# Kalaburagi Coordinates
locations = [
    {
        'name': 'Kalaburagi Central Square',
        'address': 'Super Market Area, Kalaburagi, Karnataka',
        'lat': 17.3297,
        'lng': 76.8343,
        'total_slots': 100,
        'base_price': decimal.Decimal('30.00'),
        'is_covered': True,
        'has_ev_charging': True
    },
    {
        'name': 'Gulbarga Railway Station Parking',
        'address': 'Station Road, Kalaburagi',
        'lat': 17.3468,
        'lng': 76.8519,
        'total_slots': 250,
        'base_price': decimal.Decimal('20.00'),
        'is_covered': False,
        'has_ev_charging': False
    },
    {
        'name': 'MSK Mill Road Grid',
        'address': 'MSK Mill Road, Kalaburagi',
        'lat': 17.3180,
        'lng': 76.8300,
        'total_slots': 80,
        'base_price': decimal.Decimal('40.00'),
        'is_covered': True,
        'has_ev_charging': True
    }
]

v_types = ['2-wheeler', '3-wheeler', '4-wheeler']

for loc_data in locations:
    loc, created = ParkingLocation.objects.get_or_create(
        name=loc_data['name'],
        defaults={
            'address': loc_data['address'],
            'lat': loc_data['lat'],
            'lng': loc_data['lng'],
            'total_slots': loc_data['total_slots'],
            'base_price': loc_data['base_price'],
            'is_covered': loc_data['is_covered'],
            'has_ev_charging': loc_data['has_ev_charging']
        }
    )
    
    if created or loc.slots.count() == 0:
        for i in range(1, 21):
            ParkingSlot.objects.create(
                location=loc,
                slot_number=f"K-{i:03d}",
                vehicle_type=random.choice(v_types),
                is_available=(random.random() > 0.2)
            )

print("Successfully seeded Kalaburagi parking nodes.")
