"""Authentication, likes, form validation and mocked image metrics."""
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Image
from .forms import ImageCreateForm


class ImageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='reader', password='secret')
        self.image = Image.objects.create(user=self.user, title='Green Apple', url='https://example.com/apple.jpg')

    def test_slug_and_absolute_url(self):
        self.assertEqual(self.image.slug, 'green-apple')
        self.assertEqual(self.image.get_absolute_url(), reverse('images:detail', args=[self.image.pk, self.image.slug]))

    def test_like_requires_authentication(self):
        self.assertEqual(self.client.post(reverse('images:like'), {'id': self.image.pk, 'action': 'like'}).status_code, 302)

    def test_like_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('images:like')).status_code, 405)

    def test_like_unlike_counts(self):
        self.client.force_login(self.user)
        for action, expected in [('like', 1), ('like', 1), ('unlike', 0)]:
            response = self.client.post(reverse('images:like'), {'id': self.image.pk, 'action': action})
            self.assertEqual(response.json()['status'], 'ok')
            self.image.refresh_from_db()
            self.assertEqual(self.image.total_likes, expected)

    def test_invalid_like_input(self):
        self.client.force_login(self.user)
        for data in [{'id': 'bad', 'action': 'like'}, {'id': 99999, 'action': 'like'}, {'id': self.image.pk, 'action': 'unknown'}, {}]:
            self.assertEqual(self.client.post(reverse('images:like'), data).json()['status'], 'error')

    def test_direct_clear_updates_count(self):
        self.image.users_like.add(self.user)
        self.image.users_like.clear()
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 0)

    def test_reverse_relation_clear_updates_count(self):
        self.user.images_liked.add(self.image)
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 1)
        self.user.images_liked.clear()
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 0)

    def test_image_url_validation(self):
        for url, valid in [('https://example.com/no-extension', False), ('https://example.com/file.txt', False), ('https://example.com/apple.jpg?size=2', True)]:
            form = ImageCreateForm({'title': 'Apple', 'url': url, 'description': ''})
            self.assertEqual(form.is_valid(), valid)

    def test_missing_image_detail_404_before_redis(self):
        self.assertEqual(self.client.get(reverse('images:detail', args=[99999, 'missing'])).status_code, 404)

    def test_list_requires_login(self):
        self.assertEqual(self.client.get(reverse('images:list')).status_code, 302)

    @patch('apps.images.views.render')
    @patch('apps.images.views.r')
    def test_detail_metrics_without_real_redis(self, redis, render):
        from django.http import HttpResponse
        render.return_value = HttpResponse('detail')
        redis.incr.return_value = 4
        self.assertEqual(self.client.get(self.image.get_absolute_url()).status_code, 200)
        redis.incr.assert_called_once_with(f'image:{self.image.pk}:views')
        redis.zincrby.assert_called_once_with('image_ranking', 1, self.image.pk)

    def test_authenticated_list_renders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('images:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Green Apple')

    def test_login_page_renders(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    @patch('apps.images.views.r')
    def test_detail_template_renders_without_image_file(self, redis):
        redis.incr.return_value = 1
        self.assertEqual(self.client.get(self.image.get_absolute_url()).status_code, 200)

    @patch('apps.images.views.r')
    def test_ranking_order_and_deleted_entries(self, redis):
        second = Image.objects.create(user=self.user, title='Second', url='https://example.com/2.jpg')
        redis.zrange.return_value = [str(second.pk).encode(), b'999999', str(self.image.pk).encode()]
        self.client.force_login(self.user)
        response = self.client.get(reverse('images:ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['most_viewed']), [second, self.image])

    @patch('apps.images.forms.requests.get')
    def test_download_save_uses_timeout_and_checks_status(self, get):
        from tempfile import TemporaryDirectory
        from django.test import override_settings
        get.return_value.content = b'example-image-bytes'
        form = ImageCreateForm({'title': 'Downloaded', 'url': 'https://example.com/file.jpg', 'description': ''})
        self.assertTrue(form.is_valid())
        with TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            image = form.save(commit=False)
            self.assertIsNone(image.pk)
            self.assertTrue(image.image.name.endswith('downloaded.jpg'))
        get.assert_called_once_with('https://example.com/file.jpg', timeout=10)
        get.return_value.raise_for_status.assert_called_once()

    @patch('apps.images.forms.requests.get')
    def test_http_error_does_not_save_image(self, get):
        from requests.exceptions import HTTPError
        get.return_value.raise_for_status.side_effect = HTTPError('download failed')
        form = ImageCreateForm({'title': 'Fail', 'url': 'https://example.com/file.jpg', 'description': ''})
        self.assertTrue(form.is_valid())
        with self.assertRaises(HTTPError):
            form.save(commit=False)
        self.assertEqual(Image.objects.count(), 1)

    def test_image_create_page_renders(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('images:create')).status_code, 200)
