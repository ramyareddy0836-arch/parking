import os
import django
import decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings')
django.setup()

from parking.models import ParkingLocation, ParkingSlot

# Vehicle types matching map.html
v_types = ['2-wheeler', '3-wheeler', '4-wheeler']

def seed_slots_for_all():
    locations = ParkingLocation.objects.all()
    for loc in locations:
        print(f"Seeding slots for {loc.name} (Total capacity: {loc.total_slots})...")
        # Ensure we have at least as many slot objects as total_slots field says
        current_slots = loc.slots.count()
        needed = max(loc.total_slots, 20) # At least 20 slots for visual density
        
        if loc.total_slots < needed:
            loc.total_slots = needed
            loc.save()

        for i in range(current_slots + 1, needed + 1):
            ParkingSlot.objects.create(
                location=loc,
                slot_number=f"{loc.name[:2].upper()}-{i:02d}",
                vehicle_type=random.choice(v_types),
                is_available=(random.random() > 0.1), # 90% chance available
                is_ev_slot=(random.random() > 0.7 if loc.has_ev_charging else False)
            )
    print("Database slots synchronized and expanded.")

if __name__ == "__main__":
    seed_slots_for_all()
