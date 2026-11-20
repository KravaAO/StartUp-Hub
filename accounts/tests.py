from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your tests here.

User = get_user_model()

class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='12345678'
        )


    #1. Check create users
    def test_user_ctreation(self):
        self.assertEqual(self.user.username, 'testuser')
    #2. Check testuser without login
    def test_profile_redirect(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
    #3. Check testuser with login
    def test_profile_access(self):
        self.client.login(
            username = 'testuser',
            password = '12345678'
        )
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
    #4. check show username users
    def test_profile_username(self):
        self.client.login(
            username = 'testuser',
            password = '12345678'
        )
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'testuser')