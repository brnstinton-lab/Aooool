from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Trip


def trip_list(request):
    """Отображение списка актуальных (непросроченных) поездок (доступно всем)"""
    trips = Trip.objects.upcoming()
    return render(request, 'trips/list.html', {
        'trips': trips
    })


@login_required
def trip_create(request):
    """Создание новой поездки (требует авторизации)"""
    errors = {}
    form_data = {}
    today_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        driver_name = request.POST.get('driver_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        from_location = request.POST.get('from_location', '').strip()
        to_location = request.POST.get('to_location', '').strip()
        trip_date_str = request.POST.get('trip_date', '').strip()
        departure_time_str = request.POST.get('departure_time', '').strip()
        seats_available_str = request.POST.get('seats_available', '1').strip()
        price_str = request.POST.get('price', '0').strip()
        comment = request.POST.get('comment', '').strip()

        form_data = {
            'driver_name': driver_name,
            'phone': phone,
            'from_location': from_location,
            'to_location': to_location,
            'trip_date': trip_date_str,
            'departure_time': departure_time_str,
            'seats_available': seats_available_str,
            'price': price_str,
            'comment': comment,
        }

        # Валидация обязательных полей
        if not driver_name:
            errors['driver_name'] = 'Укажите ваше имя'
        if not phone:
            errors['phone'] = 'Укажите номер телефона'
        if not from_location:
            errors['from_location'] = 'Укажите пункт отправления'
        if not to_location:
            errors['to_location'] = 'Укажите пункт назначения'
        if not trip_date_str:
            errors['trip_date'] = 'Укажите дату поездки'
        if not departure_time_str:
            errors['departure_time'] = 'Укажите время отправления'

        # Обработка необязательных полей
        seats_available = None
        if seats_available_str:
            try:
                seats_available = max(1, int(seats_available_str))
            except ValueError:
                errors['seats_available'] = 'Некорректное число мест'

        price = None
        if price_str:
            try:
                price = max(0, int(price_str))
            except ValueError:
                errors['price'] = 'Некорректная сумма'

        departure_time = None
        if departure_time_str:
            try:
                departure_time = timezone.datetime.strptime(departure_time_str, '%H:%M').time()
            except ValueError:
                errors['departure_time'] = 'Некорректное время'

        trip_date = None
        if trip_date_str:
            try:
                trip_date = timezone.datetime.strptime(trip_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors['trip_date'] = 'Некорректный формат даты'

        if not errors and trip_date and departure_time:
            Trip.objects.create(
                user=request.user,
                driver_name=driver_name,
                phone=phone,
                from_location=from_location,
                to_location=to_location,
                trip_date=trip_date,
                departure_time=departure_time,
                seats_available=seats_available,
                price=price,
                comment=comment,
                status=Trip.Status.ACTIVE,
            )
            messages.success(request, 'Поездка успешно опубликована.')
            return redirect('trips:list')

    return render(request, 'trips/create.html', {
        'errors': errors,
        'form_data': form_data,
        'today_str': today_str,
    })


@login_required
def trip_edit(request, trip_id):
    """Редактирование поездки (только автор или администратор)"""
    trip = get_object_or_404(Trip, id=trip_id)
    if trip.user and trip.user != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет прав для редактирования этой поездки.")
        return redirect('trips:list')

    errors = {}
    today_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')

    form_data = {
        'driver_name': trip.driver_name,
        'phone': trip.phone,
        'from_location': trip.from_location,
        'to_location': trip.to_location,
        'trip_date': trip.trip_date.strftime('%Y-%m-%d') if trip.trip_date else '',
        'departure_time': trip.departure_time.strftime('%H:%M') if trip.departure_time else '',
        'seats_available': str(trip.seats_available) if trip.seats_available is not None else '',
        'price': str(trip.price) if trip.price is not None else '',
        'comment': trip.comment or '',
    }

    if request.method == 'POST':
        driver_name = request.POST.get('driver_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        from_location = request.POST.get('from_location', '').strip()
        to_location = request.POST.get('to_location', '').strip()
        trip_date_str = request.POST.get('trip_date', '').strip()
        departure_time_str = request.POST.get('departure_time', '').strip()
        seats_available_str = request.POST.get('seats_available', '').strip()
        price_str = request.POST.get('price', '').strip()
        comment = request.POST.get('comment', '').strip()

        form_data = {
            'driver_name': driver_name,
            'phone': phone,
            'from_location': from_location,
            'to_location': to_location,
            'trip_date': trip_date_str,
            'departure_time': departure_time_str,
            'seats_available': seats_available_str,
            'price': price_str,
            'comment': comment,
        }

        if not driver_name:
            errors['driver_name'] = 'Укажите ваше имя'
        if not phone:
            errors['phone'] = 'Укажите номер телефона'
        if not from_location:
            errors['from_location'] = 'Укажите пункт отправления'
        if not to_location:
            errors['to_location'] = 'Укажите пункт назначения'
        if not trip_date_str:
            errors['trip_date'] = 'Укажите дату поездки'
        if not departure_time_str:
            errors['departure_time'] = 'Укажите время отправления'

        seats_available = None
        if seats_available_str:
            try:
                seats_available = max(1, int(seats_available_str))
            except ValueError:
                errors['seats_available'] = 'Некорректное число мест'

        price = None
        if price_str:
            try:
                price = max(0, int(price_str))
            except ValueError:
                errors['price'] = 'Некорректная сумма'

        departure_time = None
        if departure_time_str:
            try:
                departure_time = timezone.datetime.strptime(departure_time_str, '%H:%M').time()
            except ValueError:
                errors['departure_time'] = 'Некорректное время'

        trip_date = None
        if trip_date_str:
            try:
                trip_date = timezone.datetime.strptime(trip_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors['trip_date'] = 'Некорректный формат даты'

        if not errors:
            trip.driver_name = driver_name
            trip.phone = phone
            trip.from_location = from_location
            trip.to_location = to_location
            if trip_date:
                trip.trip_date = trip_date
            if departure_time:
                trip.departure_time = departure_time
            if seats_available is not None:
                trip.seats_available = seats_available
            if price is not None:
                trip.price = price
            trip.comment = comment
            trip.save()
            messages.success(request, 'Поездка успешно обновлена.')
            return redirect('trips:my_list')

    return render(request, 'trips/create.html', {
        'errors': errors,
        'form_data': form_data,
        'today_str': today_str,
        'is_edit': True,
        'trip': trip,
    })


@login_required
def trip_delete(request, trip_id):
    """Удаление поездки (только автор или администратор)"""
    trip = get_object_or_404(Trip, id=trip_id)
    if trip.user and trip.user != request.user and not request.user.is_staff:
        messages.error(request, "У вас нет прав для удаления этой поездки.")
        return redirect('trips:list')

    if request.method == 'POST':
        trip.delete()
        messages.success(request, "Поездка успешно удалена.")
    return redirect('trips:list')


@login_required
def trip_my_list(request):
    """Отображение поездок текущего пользователя"""
    trips = Trip.objects.filter(user=request.user).order_by('-trip_date', '-departure_time')
    return render(request, 'trips/my_list.html', {'trips': trips})



