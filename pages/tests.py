from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Page

class PageCreateAccessTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='superuser', email='superuser@test.com', password='password'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser', email='staff@test.com', password='password', is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normaluser', email='normal@test.com', password='password'
        )
        self.client = Client()
        self.url = reverse('pages:create')

    def test_superuser_can_access_create_page(self):
        self.client.login(username='superuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_staff_user_cannot_access_create_page(self):
        self.client.login(username='staffuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_normal_user_cannot_access_create_page(self):
        self.client.login(username='normaluser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    
    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_superuser_sees_admin_menu(self):
        self.client.login(username='superuser', password='password')
        response = self.client.get(reverse('pages:pages')) # Assuming pages:pages renders the menu
        self.assertContains(response, 'Administrar')
        self.assertContains(response, 'Crear página')

    def test_staff_user_does_not_see_admin_menu(self):
        self.client.login(username='staffuser', password='password')
        response = self.client.get(reverse('pages:pages'))
        self.assertNotContains(response, 'Administrar')
        self.assertNotContains(response, 'Crear página')

    def test_normal_user_does_not_see_admin_menu(self):
        self.client.login(username='normaluser', password='password')
        response = self.client.get(reverse('pages:pages'))
        self.assertNotContains(response, 'Administrar')
        self.assertNotContains(response, 'Crear página')
