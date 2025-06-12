from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str(self):
        user = User.objects.create_user(username='struser', email='str@example.com', password='pass')
        self.assertEqual(str(user), user.username)

    def test_authenticate_user(self):
        user = User.objects.create_user(username='authuser', email='auth@example.com', password='authpass')
        authenticated = authenticate(username='authuser', password='authpass')
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.pk, user.pk)

class UserViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='viewuser', email='view@example.com', password='viewpass')

    def test_login_view(self):
        response = self.client.post(reverse('login'), {'username': 'viewuser', 'password': 'viewpass'})
        self.assertEqual(response.status_code, 302)  # Redirect on success

    def test_logout_view(self):
        self.client.login(username='viewuser', password='viewpass')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect on logout

    def test_user_permissions(self):
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_user_profile_view_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        self.client.login(username='viewuser', password='viewpass')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

# ...add more tests as needed for registration, password reset, etc.
