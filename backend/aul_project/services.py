from django.db.models import Q
from django.utils import timezone
from django.utils.formats import date_format
from apps.notifications.models import Announcement
from apps.trips.models import Trip
from apps.ads.models import Ad


class FeedItem:
    """Универсальный объект события для Ленты аула"""
    def __init__(self, id, type, type_label, title, badge, badge_style, icon, icon_style, time_str, timestamp, images, details):
        self.id = id
        self.type = type  # 'ad', 'trip', 'notification', 'directory'
        self.type_label = type_label
        self.title = title
        self.badge = badge
        self.badge_style = badge_style
        self.icon = icon
        self.icon_style = icon_style
        self.time_str = time_str
        self.timestamp = timestamp
        self.images = images or []  # List of image URLs
        self.details = details or {}  # Dict with specific detail fields


def get_relative_time_str(dt):
    """Форматирует дату в человеческое относительное время (Только что, N минут назад, Вчера и т.д.)"""
    if not dt:
        return "Только что"
    now = timezone.now()
    if dt > now:
        return "Только что"
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "Только что"
    
    minutes = seconds // 60
    if minutes < 60:
        if minutes % 10 == 1 and minutes % 100 != 11:
            return f"{minutes} минуту назад"
        elif minutes % 10 in (2, 3, 4) and minutes % 100 not in (12, 13, 14):
            return f"{minutes} минуты назад"
        else:
            return f"{minutes} минут назад"
            
    hours = minutes // 60
    if hours < 24:
        if hours % 10 == 1 and hours % 100 != 11:
            return f"{hours} час назад"
        elif hours % 10 in (2, 3, 4) and hours % 100 not in (12, 13, 14):
            return f"{hours} часа назад"
        else:
            return f"{hours} часов назад"
            
    days = hours // 24
    if days == 1:
        return "Вчера"
    elif days < 7:
        if days % 10 in (2, 3, 4) and days % 100 not in (12, 13, 14):
            return f"{days} дня назад"
        else:
            return f"{days} дней назад"
    else:
        return date_format(timezone.localtime(dt), "j E")


class FeedAggregator:
    """
    Сервис агрегации единой Ленты аула.
    Собирает события из всех доступных источников (Объявления, Поездки, Оповещения, Справочник),
    приводит их к единой структуре FeedItem и сортирует в обратном хронологическом порядке.
    """

    @classmethod
    def get_feed(cls):
        items = []

        # 1. Официальные и срочные оповещения
        now = timezone.now()
        db_announcements = Announcement.objects.filter(
            status=Announcement.Status.ACTIVE
        ).filter(
            Q(expire_date__isnull=True) | Q(expire_date__gt=now)
        ).order_by('-is_pinned', '-is_important', '-publish_date')

        if db_announcements.exists():
            for item in db_announcements:
                if item.is_urgent:
                    category_icon = "emergency"
                    if item.category == Announcement.Category.MISSING_CHILD:
                        category_icon = "person_search"
                    elif item.category == Announcement.Category.MISSING_PERSON:
                        category_icon = "person_search"
                    elif item.category == Announcement.Category.FIRE:
                        category_icon = "local_fire_department"
                    elif item.category == Announcement.Category.ACCIDENT:
                        category_icon = "car_crash"
                    elif item.category == Announcement.Category.DANGER:
                        category_icon = "warning"

                    badge_style = "bg-red-600 text-white font-bold shadow-xs"
                    icon_style = "bg-red-100 text-red-600"
                    type_label = "Срочно"
                else:
                    category_icon = "campaign"
                    if item.category == Announcement.Category.ELECTRICITY:
                        category_icon = "bolt"
                    elif item.category == Announcement.Category.WATER:
                        category_icon = "water_drop"
                    elif item.category == Announcement.Category.ROADS:
                        category_icon = "construction"
                    elif item.category == Announcement.Category.EMERGENCY:
                        category_icon = "warning"

                    badge_style = "bg-amber-100 text-amber-900 border border-amber-200 font-bold"
                    icon_style = "bg-amber-100 text-amber-800"
                    type_label = "Оповещение"

                images = []
                if item.image:
                    images.append(item.image.url)

                items.append(FeedItem(
                    id=f"notification-{item.id}",
                    type="notification",
                    type_label=type_label,
                    title=item.title,
                    badge=item.get_category_display(),
                    badge_style=badge_style,
                    icon=category_icon,
                    icon_style=icon_style,
                    time_str=get_relative_time_str(item.publish_date),
                    timestamp=int(item.publish_date.timestamp()) if item.publish_date else 0,
                    images=images,
                    details={
                        "is_urgent": item.is_urgent,
                        "category": item.category,
                        "category_display": item.get_category_display(),
                        "village": item.village,
                        "description": item.description,
                        "publish_date_str": date_format(timezone.localtime(item.publish_date), "j E, H:i") if item.publish_date else "",
                        "is_important": item.is_important,
                        "location": item.location,
                        "incident_time": item.incident_time,
                        "contact_phone": item.contact_phone,
                        "child_name": item.child_name,
                        "child_age": item.child_age,
                        "appearance": item.appearance,
                        "clothing": item.clothing,
                        "extra_info": item.extra_info,
                    }
                ))
        else:
            mock_announcements = [
                {"id": 1, "title": "Плановое отключение электроэнергии", "text": "В связи с ремонтом на подстанции будет отключен свет на улицах Абая, Жамбыла.", "location": "с. Кабанбай", "category": "⚡ Электричество", "date": "30 июля", "timestamp": 1722330000},
                {"id": 2, "title": "Временное отключение питьевой воды", "text": "Замена центрального водопровода. Просим сделать запас воды.", "location": "с. Коктума", "category": "💧 Водоснабжение", "date": "29 июля", "timestamp": 1722243600},
                {"id": 3, "title": "Перекрытие движения на Центральной улице", "text": "Укладка нового асфальта. Объезд через улицу Достык.", "location": "с. Кабанбай", "category": "🚧 Дороги", "date": "28 июля", "timestamp": 1722157200},
            ]
            for item in mock_announcements:
                items.append(FeedItem(
                    id=f"notification-mock-{item['id']}",
                    type="notification",
                    type_label="Оповещение",
                    title=item["title"],
                    badge=item["category"],
                    badge_style="bg-amber-100 text-amber-900 border border-amber-200 font-bold",
                    icon="bolt",
                    icon_style="bg-amber-100 text-amber-800",
                    time_str=item["date"],
                    timestamp=item.get("timestamp", 0),
                    images=[],
                    details={
                        "category_display": item["category"],
                        "village": item["location"],
                        "description": item["text"],
                        "publish_date_str": item["date"],
                        "is_important": False,
                    }
                ))

        # 2. Поездки (Trips)
        db_trips = Trip.objects.upcoming().order_by('-created_at')
        if db_trips.exists():
            for item in db_trips:
                price_str = f"{item.price} ₸" if item.price is not None else "Договорная"
                date_str = date_format(item.trip_date, "j E") if item.trip_date else ""
                time_val_str = item.departure_time.strftime("%H:%M") if item.departure_time else "По договоренности"

                items.append(FeedItem(
                    id=f"trip-{item.id}",
                    type="trip",
                    type_label="Поездка",
                    title=f"{item.from_location} → {item.to_location}",
                    badge="Новая поездка",
                    badge_style="bg-emerald-100 text-emerald-800 border border-emerald-200 font-bold",
                    icon="directions_car",
                    icon_style="bg-emerald-100 text-emerald-800",
                    time_str=get_relative_time_str(item.created_at),
                    timestamp=int(item.created_at.timestamp()) if item.created_at else 0,
                    images=[],
                    details={
                        "from_location": item.from_location,
                        "to_location": item.to_location,
                        "driver_name": item.driver_name,
                        "phone": item.phone,
                        "trip_date_str": date_str,
                        "departure_time_str": time_val_str,
                        "seats_available": item.seats_available,
                        "price_str": price_str,
                        "comment": item.comment,
                    }
                ))
        else:
            mock_trips = [
                {"id": 1, "title": "Кабанбай → Талдыкорган", "from": "Кабанбай", "to": "Талдыкорган", "driver": "Даулет", "text": "Выезд в 16:00, 2 свободных места, багажник свободен.", "price": "2 000 ₸", "phone": "+77001234567", "date": "Сегодня, 16:00", "timestamp": 1722355200},
                {"id": 2, "title": "Коктума → Алматы", "from": "Коктума", "to": "Алматы", "driver": "Арман", "text": "Поездка на легковом авто, выезжаем утром.", "price": "5 000 ₸", "phone": "+77001234568", "date": "Завтра, 08:00", "timestamp": 1722412800},
            ]
            for item in mock_trips:
                items.append(FeedItem(
                    id=f"trip-mock-{item['id']}",
                    type="trip",
                    type_label="Поездка",
                    title=item["title"],
                    badge="Новая поездка",
                    badge_style="bg-emerald-100 text-emerald-800 border border-emerald-200 font-bold",
                    icon="directions_car",
                    icon_style="bg-emerald-100 text-emerald-800",
                    time_str="Только что",
                    timestamp=item.get("timestamp", 0),
                    images=[],
                    details={
                        "from_location": item["from"],
                        "to_location": item["to"],
                        "driver_name": item["driver"],
                        "phone": item["phone"],
                        "trip_date_str": item["date"],
                        "departure_time_str": "16:00",
                        "seats_available": 2,
                        "price_str": item["price"],
                        "comment": item["text"],
                    }
                ))

        # 3. Объявления (Ads)
        db_ads = Ad.objects.active().prefetch_related('images').order_by('-created_at')
        if db_ads.exists():
            for item in db_ads:
                price_str = f"{item.price} ₸" if item.price is not None else "Договорная"

                images = []
                if hasattr(item, 'images') and item.images.exists():
                    images = [img.image.url for img in item.images.all()]
                elif hasattr(item, 'image') and item.image:
                    images = [item.image.url]

                items.append(FeedItem(
                    id=f"ad-{item.id}",
                    type="ad",
                    type_label="Объявление",
                    title=item.title,
                    badge=item.get_ad_type_display(),
                    badge_style="bg-blue-100 text-blue-800 border border-blue-200 font-bold",
                    icon="shopping_bag",
                    icon_style="bg-blue-100 text-blue-800",
                    time_str=get_relative_time_str(item.created_at),
                    timestamp=int(item.created_at.timestamp()) if item.created_at else 0,
                    images=images,
                    details={
                        "ad_type_display": item.get_ad_type_display(),
                        "category_display": item.get_category_display(),
                        "title": item.title,
                        "price_str": price_str,
                        "description": item.description,
                        "comment": item.comment,
                        "phone": item.phone,
                    }
                ))
        else:
            mock_ads = [
                {"id": 1, "title": "Горный велосипед Forward", "type": "Продам", "category": "Транспорт", "text": "В отличном состоянии, новые шины, 21 скорость.", "price": "25 000 ₸", "phone": "+77009998877", "timestamp": 1722340000, "images": ["https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=800&q=80", "https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?auto=format&fit=crop&w=800&q=80"]},
                {"id": 2, "title": "Кухонный стол из массива", "type": "Отдам", "category": "Мебель", "text": "В хорошие руки при самовывозе.", "price": "Бесплатно", "phone": "+77009998878", "timestamp": 1722210000, "images": []},
            ]
            for item in mock_ads:
                items.append(FeedItem(
                    id=f"ad-mock-{item['id']}",
                    type="ad",
                    type_label="Объявление",
                    title=item["title"],
                    badge=item["type"],
                    badge_style="bg-blue-100 text-blue-800 border border-blue-200 font-bold",
                    icon="shopping_bag",
                    icon_style="bg-blue-100 text-blue-800",
                    time_str="Только что",
                    timestamp=item.get("timestamp", 0),
                    images=item.get("images", []),
                    details={
                        "ad_type_display": item["type"],
                        "category_display": item["category"],
                        "title": item["title"],
                        "price_str": item["price"],
                        "description": item["text"],
                        "comment": "",
                        "phone": item["phone"],
                    }
                ))

        # 4. Справочник (Directory)
        mock_directory = [
            {"id": 1, "title": "Сантехник Арман", "category": "Услуги / Мастера", "text": "Ремонт труб, отопления, насосов и сантехники.", "phone": "+77000000002", "timestamp": 1722320000},
            {"id": 2, "title": "Сельский акимат", "category": "Учреждения", "text": "ул. Абая, 12 • Пн-Пт 09:00–18:00", "phone": "+77283221100", "timestamp": 1722000000},
        ]
        for item in mock_directory:
            items.append(FeedItem(
                id=f"directory-mock-{item['id']}",
                type="directory",
                type_label="Справочник",
                title=item["title"],
                badge=item["category"],
                badge_style="bg-purple-100 text-purple-800 border border-purple-200",
                icon="import_contacts",
                icon_style="bg-purple-100 text-purple-800",
                time_str="Актуально",
                timestamp=item.get("timestamp", 0),
                images=[],
                details={
                    "category_display": item["category"],
                    "description": item["text"],
                    "phone": item.get("phone"),
                }
            ))

        # Сортировка по убыванию времени
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items
