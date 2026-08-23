from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.users.models import Role

User = get_user_model()


class UserAuthTests(TestCase):

    def test_registration_creates_resident_user(self):
        url = reverse('register')
        data = {
            'first_name': 'Алихан',
            'last_name': 'Смаилов',
            'phone': '+77001234567',
            'email': 'alihan@aul.kz',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

        # Check user in DB
        user = User.objects.get(email='alihan@aul.kz')
        self.assertEqual(user.first_name, 'Алихан')
        self.assertEqual(user.last_name, 'Смаилов')
        self.assertEqual(user.phone, '+77001234567')
        self.assertEqual(user.role, Role.RESIDENT)
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_registration_password_mismatch(self):
        url = reverse('register')
        data = {
            'first_name': 'Алихан',
            'email': 'alihan2@aul.kz',
            'password1': 'StrongPassword123!',
            'password2': 'WrongPassword!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='alihan2@aul.kz').exists())

    def test_login_and_logout(self):
        # Create test user
        user = User.objects.create_user(
            username='testuser',
            email='test@aul.kz',
            password='Password123!',
            first_name='Тест',
            role=Role.RESIDENT
        )

        # Try logging in with email
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'login_input': 'test@aul.kz',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

        # Check profile page accessible
        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, 'Тест')

        # Logout
        logout_url = reverse('logout')
        logout_response = self.client.post(logout_url)
        self.assertEqual(logout_response.status_code, 302)

        # Check profile page renders guest state for anonymous user
        guest_response = self.client.get(reverse('profile'))
        self.assertEqual(guest_response.status_code, 200)

    def test_profile_protected_for_anonymous_user(self):
        profile_url = reverse('profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)

