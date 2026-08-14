from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.utils.formats import date_format
from apps.notifications.models import Announcement
from apps.trips.models import Trip
from apps.ads.models import Ad
from apps.users.models import RoleRequest
from .services import FeedAggregator, get_relative_time_str

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'phone': 'Номер телефона',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
                'placeholder': 'Введите имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
                'placeholder': 'Введите фамилию'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
                'placeholder': 'example@aul.kz'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
                'placeholder': '+7 (7XX) XXX-XX-XX'
            }),
        }


# Демо-данные для поиска и ленты (до полного подключения всех Django-моделей БД)
MOCK_NOTIFICATIONS = [
    {"title": "Плановое отключение электроэнергии", "text": "В связи с ремонтом на подстанции будет отключен свет на улицах Абая, Жамбыла.", "location": "с. Кабанбай", "category": "Электричество", "date": "30 июля", "timestamp": 1722330000},
    {"title": "Временное отключение питьевой воды", "text": "Замена центрального водопровода. Просим сделать запас воды.", "location": "с. Коктума", "category": "Водоснабжение", "date": "29 июля", "timestamp": 1722243600},
    {"title": "Перекрытие движения на Центральной улице", "text": "Укладка нового асфальта. Объезд через улицу Достык.", "location": "с. Кабанбай", "category": "Дороги", "date": "28 июля", "timestamp": 1722157200},
]

MOCK_TRIPS = [
    {"title": "Кабанбай → Талдыкорган", "text": "Выезд в 16:00, 2 свободных места, багажник свободен.", "price": "2 000 ₸", "phone": "+77001234567", "date": "Сегодня, 16:00", "timestamp": 1722355200},
    {"title": "Коктума → Алматы", "text": "Поездка на легковом авто, выезжаем утром.", "price": "5 000 ₸", "phone": "+77001234568", "date": "Завтра, 08:00", "timestamp": 1722412800},
]

MOCK_ADS = [
    {"title": "Горный велосипед Forward", "text": "В отличном состоянии, новые шины, 21 скорость.", "price": "25 000 ₸", "location": "Кабанбай", "phone": "+77009998877", "category": "Транспорт", "timestamp": 1722340000},
    {"title": "Кухонный стол из массива", "text": "Бесплатно в хорошие руки при самовывозе.", "price": "Бесплатно", "location": "Коктума", "phone": "+77009998878", "category": "Мебель", "timestamp": 1722210000},
]

MOCK_DIRECTORY = [
    {"title": "Сантехник Арман", "text": "Ремонт труб, отопления, насосов и сантехники.", "phone": "+77000000002", "category": "Услуги / Мастера", "timestamp": 1722320000},
    {"title": "Сельский акимат", "text": "ул. Абая, 12 • Пн-Пт 09:00–18:00", "phone": "+77283221100", "category": "Учреждения", "timestamp": 1722000000},
    {"title": "Сельская больница", "text": "ул. Жамбыла, 45 • Круглосуточно", "phone": "+77283221105", "category": "Медицина", "timestamp": 1721900000},
]


def get_aggregated_feed():
    """
    Универсальный генератор сквозной ленты событий.
    Использует сервис FeedAggregator для получения событий со всех модулей.
    """
    return FeedAggregator.get_feed()



def home_view(request):
    """Главная страница приложения с последними 3 объявлениями и событиями ленты"""
    all_events = get_aggregated_feed()
    recent_events = all_events[:5]
    
    # Последние 3 активных объявления
    now = timezone.now()
    recent_announcements = Announcement.objects.filter(
        status=Announcement.Status.ACTIVE
    ).filter(
        Q(expire_date__isnull=True) | Q(expire_date__gt=now)
    ).order_by('-is_pinned', '-publish_date')[:3]

    return render(request, 'index.html', {
        'recent_events': recent_events,
        'recent_announcements': recent_announcements,
    })


def feed_view(request):
    """Отдельная страница полной Ленты аула со всеми событиями в хронологическом порядке"""
    all_events = get_aggregated_feed()
    return render(request, 'feed.html', {'events': all_events})


def search_view(request):
    """Сквозной глобальный поиск по всем разделам приложения, включая объявления из БД"""
    query = request.GET.get('q', '').strip()
    
    notifications_results = []
    trips_results = []
    ads_results = []
    directory_results = []
    
    if query:
        q_lower = query.lower()
        
        # Поиск по базе данных объявлений
        now = timezone.now()
        db_announcements = Announcement.objects.filter(
            status=Announcement.Status.ACTIVE
        ).filter(
            Q(expire_date__isnull=True) | Q(expire_date__gt=now)
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        
        for item in db_announcements:
            local_pub_date = timezone.localtime(item.publish_date) if item.publish_date else None
            date_str = date_format(local_pub_date, "j E, H:i") if local_pub_date else "Сегодня"
            notifications_results.append({
                "title": item.title,
                "text": item.description,
                "location": item.village,
                "category": item.get_category_display(),
                "date": date_str,
            })
            
        if not notifications_results:
            notifications_results = [
                item for item in MOCK_NOTIFICATIONS
                if q_lower in item['title'].lower() or q_lower in item['text'].lower() or q_lower in item['category'].lower()
            ]
        
        # Поиск по поездкам
        db_trips_search = Trip.objects.upcoming().filter(
            Q(from_location__icontains=query) |
            Q(to_location__icontains=query) |
            Q(driver_name__icontains=query) |
            Q(comment__icontains=query)
        )
        for item in db_trips_search:
            trips_results.append({
                "title": f"{item.from_location} → {item.to_location}",
                "text": f"Водитель: {item.driver_name} • {item.seats_available} мест",
                "price": f"{item.price} ₸",
                "phone": item.phone,
                "date": get_relative_time_str(item.created_at)
            })
        if not trips_results:
            trips_results = [
                item for item in MOCK_TRIPS
                if q_lower in item['title'].lower() or q_lower in item['text'].lower()
            ]
        
        # Поиск по объявлениям
        db_ads_search = Ad.objects.active().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(comment__icontains=query)
        )
        for item in db_ads_search:
            ads_results.append({
                "title": item.title,
                "text": item.description,
                "price": f"{item.price} ₸" if item.price is not None else "Договорная",
                "phone": item.phone,
                "category": item.get_category_display()
            })
        if not ads_results:
            ads_results = [
                item for item in MOCK_ADS
                if q_lower in item['title'].lower() or q_lower in item['text'].lower() or q_lower in item['category'].lower()
            ]
        
        # Поиск по справочнику
        directory_results = [
            item for item in MOCK_DIRECTORY
            if q_lower in item['title'].lower() or q_lower in item['text'].lower() or q_lower in item['category'].lower()
        ]

    total_count = len(notifications_results) + len(trips_results) + len(ads_results) + len(directory_results)

    context = {
        'query': query,
        'notifications': notifications_results,
        'trips': trips_results,
        'ads': ads_results,
        'directory': directory_results,
        'total_count': total_count,
    }
    return render(request, 'search.html', context)


@login_required
def profile_view(request):
    """Страница профиля пользователя"""
    user = request.user
    role = getattr(user, 'role', 'resident')
    role_display = user.get_role_display() if hasattr(user, 'get_role_display') else 'Житель'
    display_name = user.get_full_name() or user.username or 'Житель аула'
    user_email = user.email or ''
    user_phone = getattr(user, 'phone', '') or request.session.get('user_phone', '')
    user_village = request.session.get('user_village', 'Кабанбай')

    master_request_pending = RoleRequest.objects.filter(
        user=user,
        requested_role=RoleRequest.RequestedRole.MASTER,
        status=RoleRequest.Status.PENDING
    ).first()

    master_request_rejected = None
    if not master_request_pending:
        master_request_rejected = RoleRequest.objects.filter(
            user=user,
            requested_role=RoleRequest.RequestedRole.MASTER,
            status=RoleRequest.Status.REJECTED
        ).order_by('-created_at').first()

    context = {
        'profile_user': user,
        'user_role': role,
        'role_display': role_display,
        'display_name': display_name,
        'user_phone': user_phone,
        'user_email': user_email,
        'user_village': user_village,
        'master_request_pending': master_request_pending,
        'master_request_rejected': master_request_rejected,
    }
    return render(request, 'profile.html', context)


@login_required
def profile_edit_view(request):
    """Страница и обработка редактирования профиля пользователя (стандартный Django ModelForm + POST)"""
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Обновляем сессионные данные
            request.session['user_first_name'] = user.first_name
            request.session['user_last_name'] = user.last_name
            request.session['user_email'] = user.email
            if hasattr(user, 'phone'):
                request.session['user_phone'] = user.phone
            if 'village' in request.POST:
                request.session['user_village'] = request.POST.get('village', '').strip()

            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    user_phone = getattr(user, 'phone', '') or request.session.get('user_phone', '')
    user_village = request.session.get('user_village', 'Кабанбай')

    context = {
        'form': form,
        'profile_user': user,
        'user_phone': user_phone,
        'user_village': user_village,
        'village_options': ['Кабанбай', 'Коктума', 'Аксу', 'Ушарал', 'Достык'],
    }
    return render(request, 'profile_edit.html', context)



def services_view(request):
    """Страница всех сервисов села"""
    return render(request, 'services.html')

