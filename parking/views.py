from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import ParkingLocation, ParkingSlot, Booking, Notification
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

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
                return redirect('dashboard')
            except IntegrityError:
                form.add_error('username', 'A user with this username already exists.')
        # If form is not valid, it'll fall through to rendering with errors
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

