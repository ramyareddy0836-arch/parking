from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import ParkingLocation, ParkingSlot, Booking, Notification
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import decimal

def index(request):
    return render(request, 'parking/index.html')

def map_view(request):
    return render(request, 'parking/map.html')

from django.utils import timezone
from django.db.models import Sum, Count, Q

@login_required
def dashboard(request):
    is_staff = request.user.is_staff
    context = {
        'is_staff': is_staff,
    }
    if is_staff:
        return redirect('admin_dashboard')
    
    context['user_bookings'] = Booking.objects.filter(user=request.user).order_by('-created_at')
    context['notifications'] = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'parking/dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    today = timezone.now().date()
    daily_bookings = Booking.objects.filter(created_at__date=today)
    
    # Location-wise breakdown for today
    locations_stats = ParkingLocation.objects.annotate(
        today_bookings_count=Count('slots__bookings', filter=Q(slots__bookings__created_at__date=today))
    )
    
    # EV stats for today
    ev_bookings = daily_bookings.filter(slot__is_ev_slot=True)
    ev_parked_count = ev_bookings.count()
    
    # Reviews today
    from .models import Review
    daily_reviews = Review.objects.filter(created_at__date=today)
    
    # EV Reviews (Reviews for EV bookings today)
    ev_reviews = Review.objects.filter(booking__slot__is_ev_slot=True, created_at__date=today)
        
    # All Individual Slots for Master Table
    all_slots = ParkingSlot.objects.select_related('location').all().order_by('location__name', 'slot_number')
        
    context = {
        'is_staff': True,
        'locations': locations_stats,
        'total_bookings_count': Booking.objects.count(),
        'total_users_count': get_user_model().objects.count(),
        'daily_parked_count': daily_bookings.count(),
        'daily_total_hours': daily_bookings.aggregate(Sum('duration_hours'))['duration_hours__sum'] or 0,
        'daily_total_revenue': daily_bookings.aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'ev_parked_count': ev_parked_count,
        'daily_reviews': daily_reviews,
        'ev_reviews': ev_reviews,
        'locations_stats': locations_stats,
        'all_slots': all_slots,
    }
    
    return render(request, 'parking/admin_dashboard.html', context)

def chatbot(request):
    return render(request, 'parking/chatbot.html')


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Add welcome notification
                Notification.objects.create(
                    user=user,
                    message="Welcome to SmartPark! Your account is active and ready for the grid."
                )
                login(request, user)
                return redirect('map_view')
            except IntegrityError:
                form.add_error('username', 'A user with this username already exists.')
        # If form is not valid, it'll fall through to rendering with errors
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = [{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications]
    return JsonResponse(data, safe=False)

@login_required
def get_locations(request):
    locations = ParkingLocation.objects.all()
    data = []
    for loc in locations:
        slots = loc.slots.all()
        data.append({
            'id': loc.id,
            'name': loc.name,
            'address': loc.address,
            'lat': loc.lat,
            'lng': loc.lng,
            'total_slots': loc.total_slots,
            'available_slots_count': slots.filter(is_available=True).count(),
            'base_price': str(loc.base_price),
            'has_ev_charging': loc.has_ev_charging,
            'slots': [{
                'id': s.id,
                'slot_number': s.slot_number,
                'vehicle_type': s.vehicle_type,
                'is_available': s.is_available,
                'is_ev_slot': s.is_ev_slot
            } for s in slots]
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def create_booking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slot_id = data.get('slot_id')
            duration = int(data.get('duration', 1))
            is_ev_selected = data.get('is_ev_selected', False)

            # Handle virtual slots (generated on the frontend for searched cities)
            if str(slot_id).startswith('v-'):
                virtual_slot = data.get('virtual_slot_data', {})
                virtual_loc = data.get('virtual_location_data', {})

                loc, _ = ParkingLocation.objects.get_or_create(
                    name=virtual_loc.get('name', 'Unknown Location'),
                    defaults={
                        'address': virtual_loc.get('address', 'India'),
                        'lat': float(virtual_loc.get('lat', 0)),
                        'lng': float(virtual_loc.get('lng', 0)),
                        'total_slots': int(virtual_loc.get('total_slots', 20)),
                        'base_price': decimal.Decimal(str(virtual_loc.get('base_price', '30.00'))),
                        'is_covered': False,
                        'has_ev_charging': bool(virtual_loc.get('has_ev_charging', False)),
                    }
                )
                slot, _ = ParkingSlot.objects.get_or_create(
                    location=loc,
                    slot_number=virtual_slot.get('slot_number', 'VR-01'),
                    defaults={
                        'vehicle_type': virtual_slot.get('vehicle_type', '4-wheeler'),
                        'is_available': True,
                        'is_ev_slot': bool(virtual_slot.get('is_ev_slot', False)),
                    }
                )
            else:
                slot = ParkingSlot.objects.get(id=slot_id)

            if not slot.is_available:
                return JsonResponse({'status': 'error', 'message': 'Slot not available'}, status=400)
            
            base_price = slot.location.base_price
            ev_charge = decimal.Decimal('50.00') if is_ev_selected else decimal.Decimal('0.00')
            total_price = (base_price * duration) + ev_charge
            
            booking = Booking.objects.create(
                user=request.user,
                slot=slot,
                start_time=timezone.now(),
                duration_hours=duration,
                total_price=total_price,
                booking_status='confirmed',
                payment_status='paid', # Assuming immediate payment for now
                is_ev_selected=is_ev_selected,
                ev_charge_amount=ev_charge
            )
            
            slot.is_available = False
            slot.save()
            
            # Create notifications
            Notification.objects.create(
                user=request.user,
                message=f"Slot {slot.slot_number} booked successfully at {slot.location.name}."
            )
            Notification.objects.create(
                user=request.user,
                message=f"Payment of ₹{total_price} completed successfully."
            )
            
            return JsonResponse({
                'status': 'success',
                'booking_id': booking.id,
                'message': 'Booking confirmed!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

