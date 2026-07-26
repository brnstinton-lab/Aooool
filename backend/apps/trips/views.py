from django.shortcuts import render
from .models import Trip


def trip_list(request):
    """Отображение списка актуальных (непросроченных) поездок"""
    trips = Trip.objects.upcoming()
    return render(request, 'trips/list.html', {
        'trips': trips
    })


def trip_create(request):
    """Страница-заглушка для добавления поездки"""
    return render(request, 'trips/create.html')

