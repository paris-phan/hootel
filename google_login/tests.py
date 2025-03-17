from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from google_login.models import UserProfile

class LoginTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            user_type='PATRON'
        )
        
        # Create a librarian user
        self.librarian = User.objects.create_user(
            username='librarian',
            email='librarian@example.com',
            password='password123'
        )
        self.librarian_profile = UserProfile.objects.create(
            user=self.librarian,
            user_type='LIBRARIAN'
        )
        
        self.client = Client()
    
    def test_login_redirect_to_home(self):
        # Test that after login, user is redirected to home
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
    
    def test_patron_sees_correct_home(self):
        # Test that patron user sees patron home
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'google_login/patron_home.html')
        
    def test_librarian_sees_correct_home(self):
        # Test that librarian user sees librarian home
        self.client.login(username='librarian', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'google_login/librarian_home.html')
    
    def test_unauthenticated_user_redirected(self):
        # Test that unauthenticated users are redirected to login
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/login/')

    @patch('google_login.views.UserProfile.profile_picture_url', new_callable=MagicMock)
    def test_profile_picture_url_default(self, mock_url):
        # Test default profile picture URL when none exists
        mock_url.__get__ = MagicMock(return_value='https://example.com/default_profile.png')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile_picture_url', response.context)
        self.assertEqual(response.context['profile_picture_url'], 'https://example.com/default_profile.png')


class ProfilePictureTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            user_type='PATRON'
        )
        self.client = Client()
        self.client.login(username='testuser', password='password123')
    
    @patch('google_login.views.UserProfile.profile_picture.delete')
    @patch('google_login.views.UserProfile.save')
    def test_update_profile_picture(self, mock_save, mock_delete):
        # Test profile picture update endpoint
        with open('test_image.jpg', 'wb') as f:
            f.write(b'dummy image content')
        
        with open('test_image.jpg', 'rb') as image:
            response = self.client.post(
                reverse('update_profile_picture'),
                {'profile_picture': image},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        
        self.assertEqual(response.status_code, 200)
        mock_delete.assert_called_once()
        mock_save.assert_called_once()