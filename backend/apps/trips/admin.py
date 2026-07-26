from django.contrib import admin
from .models import Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'from_location',
        'to_location',
        'driver_name',
        'phone',
        'trip_date',
        'departure_time',
        'seats_available',
        'price',
        'status',
        'created_at',
    )
    list_filter = (
        'status',
        'trip_date',
        'from_location',
        'to_location',
    )
    search_fields = (
        'driver_name',
        'phone',
        'from_location',
        'to_location',
        'comment',
    )
    list_editable = (
        'status',
        'seats_available',
        'price',
    )
    ordering = ('-trip_date', '-created_at')
