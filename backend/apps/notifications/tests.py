import io
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.users.models import Role
from apps.notifications.models import Announcement
from apps.notifications.forms import UrgentNotificationForm, OfficialNotificationForm

User = get_user_model()


def generate_test_image():
    """Генерирует валидное тестовое изображение в памяти"""
    file_obj = io.BytesIO()
    image = Image.new("RGBA", size=(100, 100), color=(255, 0, 0))
    image.save(file_obj, "png")
    file_obj.seek(0)
    return SimpleUploadedFile("test_photo.png", file_obj.read(), content_type="image/png")


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="resident1", password="password123", role=Role.RESIDENT)

    def test_create_urgent_announcement(self):
        announcement = Announcement.objects.create(
            user=self.user,
            announcement_type=Announcement.AnnouncementType.URGENT,
            category=Announcement.Category.FIRE,
            title="Задымление в степи",
            description="Виден дым в 2 км от села",
            status=Announcement.Status.ACTIVE,
            is_important=True
        )
        self.assertTrue(announcement.is_urgent)
        self.assertFalse(announcement.is_official)
        self.assertEqual(announcement.status, Announcement.Status.ACTIVE)


class NotificationFormsTests(TestCase):
    def test_missing_child_without_photo_fails_validation(self):
        """Проверка: для 'Пропал ребёнок' фотография ОБЯЗАТЕЛЬНА"""
        form_data = {
            'category': Announcement.Category.MISSING_CHILD,
            'child_name': 'Алихан Бериков',
            'child_age': '7 лет',
            'location': 'Возле школы №1',
            'contact_phone': '+7 701 111 2233',
            'incident_time': 'Сегодня в 13:00',
        }
        form = UrgentNotificationForm(data=form_data, files={})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_missing_child_with_photo_succeeds(self):
        """Проверка: для 'Пропал ребёнок' с фото форма валидна"""
        form_data = {
            'category': Announcement.Category.MISSING_CHILD,
            'child_name': 'Алихан Бериков',
            'child_age': '7 лет',
            'location': 'Возле школы №1',
            'contact_phone': '+7 701 111 2233',
            'incident_time': 'Сегодня в 13:00',
            'clothing': 'Синяя куртка',
        }
        test_image = generate_test_image()
        form = UrgentNotificationForm(data=form_data, files={'image': test_image})
        self.assertTrue(form.is_valid(), form.errors)

    def test_fire_without_photo_succeeds(self):
        """Проверка: для других срочных категорий фото опционально"""
        form_data = {
            'category': Announcement.Category.FIRE,
            'title': 'Задымление на окраине',
            'description': 'Горит сухая трава',
            'location': 'Восточная окраина',
            'contact_phone': '+7 701 222 3344',
        }
        form = UrgentNotificationForm(data=form_data, files={})
        self.assertTrue(form.is_valid(), form.errors)


class NotificationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.resident = User.objects.create_user(username="resident", password="password123", role=Role.RESIDENT)
        self.organization = User.objects.create_user(username="org1", password="password123", role=Role.ORGANIZATION)
        self.admin = User.objects.create_superuser(username="admin", password="password123", email="admin@aul.kz")

    def test_urgent_created_by_resident_is_active_immediately(self):
        """Житель создает срочное происшествие -> СРАЗУ статус ACTIVE (без модерации)"""
        self.client.login(username="resident", password="password123")
        url = reverse('notifications:create_urgent')
        response = self.client.post(url, {
            'category': Announcement.Category.ACCIDENT,
            'title': 'ДТП на повороте',
            'description': 'Две машины столкнулись, нужна скорая',
            'location': 'Поворот на Коктума',
            'contact_phone': '+7 777 000 1122',
        })
        self.assertEqual(response.status_code, 302)
        
        announcement = Announcement.objects.filter(title='ДТП на повороте').first()
        self.assertIsNotNone(announcement)
        self.assertEqual(announcement.status, Announcement.Status.ACTIVE)
        self.assertEqual(announcement.announcement_type, Announcement.AnnouncementType.URGENT)

    def test_official_created_by_organization_is_pending(self):
        """Организация создает официальное объявление -> статус PENDING (на модерации)"""
        self.client.login(username="org1", password="password123")
        url = reverse('notifications:create_official')
        response = self.client.post(url, {
            'category': Announcement.Category.ELECTRICITY,
            'title': 'Плановое отключение электроэнергии',
            'description': 'Замена трансформатора с 10:00 до 16:00',
            'village': 'с. Кабанбай',
        })
        self.assertEqual(response.status_code, 302)

        announcement = Announcement.objects.filter(title='Плановое отключение электроэнергии').first()
        self.assertIsNotNone(announcement)
        self.assertEqual(announcement.status, Announcement.Status.PENDING)
        self.assertEqual(announcement.announcement_type, Announcement.AnnouncementType.OFFICIAL)

    def test_resident_cannot_access_create_official(self):
        """Обычный житель не может создавать официальные объявления"""
        self.client.login(username="resident", password="password123")
        url = reverse('notifications:create_official')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to list with error message

    def test_guest_can_view_active_only(self):
        """Гость видит только опубликованные ACTIVE объявления, PENDING скрыты"""
        Announcement.objects.create(
            user=self.resident,
            announcement_type=Announcement.AnnouncementType.URGENT,
            category=Announcement.Category.FIRE,
            title="Активный пожар",
            description="Описание",
            status=Announcement.Status.ACTIVE
        )
        Announcement.objects.create(
            user=self.organization,
            announcement_type=Announcement.AnnouncementType.OFFICIAL,
            category=Announcement.Category.WATER,
            title="Скрытое объявление на модерации",
            description="Описание",
            status=Announcement.Status.PENDING
        )

        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Активный пожар")
        self.assertNotContains(response, "Скрытое объявление на модерации")
