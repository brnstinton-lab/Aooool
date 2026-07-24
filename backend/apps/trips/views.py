from django.shortcuts import render

def trip_list(request):
    """Отображение списка поездок"""
    return render(request, 'trips/list.html')

