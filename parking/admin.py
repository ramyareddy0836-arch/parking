from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ParkingLocation, ParkingSlot, Booking, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(ParkingLocation)
class ParkingLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'total_slots', 'base_price', 'is_covered', 'has_ev_charging')
    search_fields = ('name', 'address')

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('location', 'slot_number', 'vehicle_type', 'is_available')
    list_filter = ('is_available', 'vehicle_type', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'slot', 'start_time', 'duration_hours', 'booking_status', 'payment_status', 'is_ev_selected')
    list_filter = ('booking_status', 'payment_status', 'is_ev_selected', 'start_time')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
