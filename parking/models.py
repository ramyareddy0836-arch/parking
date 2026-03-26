from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class ParkingLocation(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    lat = models.FloatField()
    lng = models.FloatField()
    total_slots = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_covered = models.BooleanField(default=False)
    has_ev_charging = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ParkingSlot(models.Model):
    VEHICLE_CHOICES = (
        ('2-wheeler', '2-Wheeler'),
        ('3-wheeler', '3-Wheeler'),
        ('4-wheeler', '4-Wheeler'),
    )
    location = models.ForeignKey(ParkingLocation, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=15, choices=VEHICLE_CHOICES, default='4-wheeler')
    is_available = models.BooleanField(default=True)
    is_ev_slot = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.location.name} - {self.slot_number}"

class Booking(models.Model):
    BOOKING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    duration_hours = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    is_ev_selected = models.BooleanField(default=False)
    ev_charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Booking {self.booking.id}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
