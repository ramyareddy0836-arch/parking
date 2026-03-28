from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from parking.models import ParkingLocation, ParkingSlot, Booking

User = get_user_model()

class DashboardLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='test@example.com', password='Password123!')
        self.location = ParkingLocation.objects.create(
            name="Test Hub", address="123 Test St", lat=12.34, lng=56.78, 
            total_slots=10, base_price=30.00
        )
        self.slot = ParkingSlot.objects.create(location=self.location, slot_number="T-01")

    def test_booking_filtering(self):
        # Active booking
        active_booking = Booking.objects.create(
            user=self.user, slot=self.slot, start_time=timezone.now(), 
            duration_hours=2, total_price=60.00, booking_status='confirmed'
        )
        
        # Expired booking (created 5 hours ago, duration 1 hour)
        expired_start = timezone.now() - timezone.timedelta(hours=5)
        expired_booking = Booking.objects.create(
            user=self.user, slot=self.slot, start_time=expired_start, 
            duration_hours=1, total_price=30.00, booking_status='confirmed'
        )
        
        self.client.login(username='tester', password='Password123!')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Verify filtering in context
        self.assertIn(active_booking, response.context['active_bookings'])
        self.assertIn(expired_booking, response.context['past_bookings'])
        
        # Verify expired booking was updated in DB
        expired_booking.refresh_from_db()
        self.assertEqual(expired_booking.booking_status, 'completed')

    def test_update_profile(self):
        self.client.login(username='tester', password='Password123!')
        response = self.client.post('/update-profile/', {'email': 'new@example.com'})
        self.assertRedirects(response, '/dashboard/')
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
