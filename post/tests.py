from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from post.models import Post, LastStatistics, Like


class RegisterUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)


class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        LastStatistics.objects.create(user=self.user)

    def test_obtain_token(self):
        response = self.client.post('/api/auth/token/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)


class CreatePostTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        LastStatistics.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        data = {'post_text': 'Test post text'}
        response = self.client.post('/api/create_post/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.count(), 1)


class LikeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        LastStatistics.objects.create(user=self.user)
        self.post = Post.objects.create(user=self.user, post_text='Test post text')

    def test_like_post(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/like/', {'post': self.post.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Like.objects.count(), 1)

    def test_unlike_post(self):
        self.client.force_authenticate(user=self.user)
        Like.objects.create(user=self.user, post=self.post)
        response = self.client.delete(f'/api/unlike/{self.post.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 0)


class LikeAnalyticsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_1 = User.objects.create_user(username='testuser_1', password='testpassword', is_staff=True)
        LastStatistics.objects.create(user=self.user_1)

        self.user_2 = User.objects.create_user(username='testuser_2', password='testpassword')
        self.user_3 = User.objects.create_user(username='testuser_3', password='testpassword')

        self.post_2 = Post.objects.create(user=self.user_2, post_text='Test post text from testuser_2')
        self.post_3 = Post.objects.create(user=self.user_3, post_text='Test post text from testuser_3')

        Like.objects.create(user=self.user_2, post=self.post_3)
        Like.objects.create(user=self.user_3, post=self.post_2)

        Like.objects.filter(id=1).update(like_creation='2023-10-22 12:00:00+03')
        Like.objects.filter(id=2).update(like_creation='2023-10-23 12:00:00+03')

    def test_like_analytics(self):
        self.client.force_authenticate(user=self.user_1)
        response = self.client.get('/api/analytics/', {'date_from': '2023-10-21', 'date_to': '2023-10-24'})
        data = list(response.data)

        expected_data = [
            {'like_creation__date': '2023-10-22', 'likes_count': 1},
            {'like_creation__date': '2023-10-23', 'likes_count': 1}
        ]
        for item in data:
            item['like_creation__date'] = str(item['like_creation__date'])

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(data, expected_data)


class UserActivityViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_1 = User.objects.create_user(username='testuser_1', password='testpassword', is_staff=True)
        LastStatistics.objects.create(user=self.user_1)
        self.user_2 = User.objects.create_user(username='testuser_2', password='testpassword')
        self.user_activity = LastStatistics.objects.create(user=self.user_2,
                                                           last_login=timezone.now(),
                                                           last_request=timezone.now())

    def test_user_activity_view_as_admin(self):
        self.client.force_authenticate(user=self.user_1)
        response = self.client.get(f'/api/user_activity/{self.user_2.id}/')
        self.assertEqual(response.status_code, 200)

        expected_data = {
            'username': self.user_2.username,
            'last_login': self.user_activity.last_login,
            'last_request': self.user_activity.last_request,
        }
        self.assertDictEqual(response.data, expected_data)
