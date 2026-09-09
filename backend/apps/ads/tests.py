from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Ad

User = get_user_model()


class AdExpirationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='+77011112233',
            phone='+77011112233',
            password='testpassword123'
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_create_ad_with_future_expire_date(self):
        """Проверка создания объявления с датой в будущем"""
        future_dt = timezone.now() + timedelta(days=5)
        future_date_str = future_dt.strftime('%Y-%m-%d')
        future_time_str = "18:30"

        response = self.client.post('/ads/create/', {
            'title': 'Продам сено',
            'ad_type': 'SELL',
            'expire_date': future_date_str,
            'expire_time': future_time_str,
            'description': 'Качественное сено в тюках',
            'phone': '+77011112233',
            'price': '5000',
            'comment': '',
        })
        self.assertEqual(response.status_code, 302)

        ad = Ad.objects.filter(title='Продам сено').first()
        self.assertIsNotNone(ad)
        self.assertIsNotNone(ad.expire_date)
        self.assertFalse(ad.is_expired())
        self.assertIn(ad, Ad.objects.active())

    def test_validation_error_for_past_expire_date(self):
        """Проверка валидации: ошибка при указании даты в прошлом"""
        past_dt = timezone.now() - timedelta(days=2)
        past_date_str = past_dt.strftime('%Y-%m-%d')
        past_time_str = "12:00"

        response = self.client.post('/ads/create/', {
            'title': 'Старое объявление',
            'ad_type': 'SELL',
            'expire_date': past_date_str,
            'expire_time': past_time_str,
            'description': 'Описание',
            'phone': '+77011112233',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дата окончания должна быть в будущем.')
        self.assertEqual(Ad.objects.filter(title='Старое объявление').count(), 0)

    def test_active_vs_expired_ad_display(self):
        """Истекшее объявление не показывается в active, но остается в базе данных"""
        future_dt = timezone.now() + timedelta(days=3)
        past_dt = timezone.now() - timedelta(minutes=5)

        active_ad = Ad.objects.create(
            user=self.user,
            title='Активное объявление',
            ad_type='SELL',
            expire_date=future_dt,
            description='Всё ещё актуально',
            phone='+77011112233',
            status=Ad.Status.ACTIVE
        )

        expired_ad = Ad.objects.create(
            user=self.user,
            title='Истекшее объявление',
            ad_type='SELL',
            expire_date=past_dt,
            description='Срок действия истек',
            phone='+77011112233',
            status=Ad.Status.ACTIVE
        )

        active_queryset = Ad.objects.active()
        self.assertIn(active_ad, active_queryset)
        self.assertNotIn(expired_ad, active_queryset)

        # Проверка: запись НЕ удалена из БД
        self.assertTrue(Ad.objects.filter(id=expired_ad.id).exists())
        self.assertTrue(expired_ad.is_expired())

        # Проверка ответа списка объявлений
        response = self.client.get('/ads/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Активное объявление')
        self.assertNotContains(response, 'Истекшее объявление')

    def test_edit_ad_expire_date(self):
        """Проверка редактирования срока действия объявления"""
        future_dt = timezone.now() + timedelta(days=2)
        ad = Ad.objects.create(
            user=self.user,
            title='Объявление для правки',
            ad_type='SELL',
            expire_date=future_dt,
            description='Описание до правки',
            phone='+77011112233',
            status=Ad.Status.ACTIVE
        )

        new_future_dt = timezone.now() + timedelta(days=10)
        new_date_str = new_future_dt.strftime('%Y-%m-%d')
        new_time_str = "20:00"

        response = self.client.post(f'/ads/{ad.id}/edit/', {
            'title': 'Объявление отредактировано',
            'ad_type': 'SELL',
            'expire_date': new_date_str,
            'expire_time': new_time_str,
            'description': 'Новое описание',
            'phone': '+77011112233',
        })
        self.assertEqual(response.status_code, 302)

        ad.refresh_from_db()
        self.assertEqual(ad.title, 'Объявление отредактировано')
        self.assertEqual(ad.expire_date.date(), new_future_dt.date())
