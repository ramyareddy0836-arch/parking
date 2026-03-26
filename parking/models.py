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

    def __str__(self):
        return f"{self.location.name} - {self.slot_number}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    duration_hours = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
