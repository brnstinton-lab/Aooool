from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from django.utils.formats import date_format
from apps.notifications.models import Announcement
from apps.trips.models import Trip
from apps.ads.models import Ad
from .services import FeedAggregator, get_relative_time_str


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


def profile_view(request):
    """Страница профиля пользователя"""
    return render(request, 'profile.html')


def services_view(request):
    """Страница всех сервисов села"""
    return render(request, 'services.html')

