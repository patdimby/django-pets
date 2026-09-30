"""Coupon endpoints mounted alongside the optional session cart for integration tests."""
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import include, path, reverse
from django.utils import timezone
from .models import Coupon

urlpatterns = [path('basket/', include('apps.cart.urls')), path('coupons/', include('apps.coupons.urls')), path('', include('backend.urls'))]


@override_settings(ROOT_URLCONF=__name__)
class CouponTests(TestCase):
    def setUp(self):
        now = timezone.now()
        self.coupon = Coupon.objects.create(code='SAVE', discount=25, active=True,
            valid_from=now-timedelta(days=1), valid_to=now+timedelta(days=1))

    def test_discount_bounds(self):
        for discount in [-1, 101]:
            self.coupon.discount = discount
            with self.assertRaises(ValidationError):
                self.coupon.full_clean()

    def test_coupon_apply_requires_post(self):
        self.assertEqual(self.client.get(reverse('coupons:apply')).status_code, 405)

    def test_case_insensitive_code(self):
        response = self.client.post(reverse('coupons:apply'), {'code': 'save'})
        self.assertRedirects(response, reverse('cart:cart_detail'))
        self.assertEqual(self.client.session['coupon_id'], self.coupon.pk)

    def test_invalid_form_clears_previous_coupon(self):
        session = self.client.session
        session['coupon_id'] = self.coupon.pk
        session.save()
        self.client.post(reverse('coupons:apply'), {'code': ''})
        self.assertIsNone(self.client.session['coupon_id'])

    def test_unknown_code_clears_coupon(self):
        self.client.post(reverse('coupons:apply'), {'code': 'MISSING'})
        self.assertIsNone(self.client.session['coupon_id'])

    def test_empty_cart_template(self):
        self.assertEqual(self.client.get(reverse('cart:cart_detail')).status_code, 200)

    def test_cart_add_and_remove_endpoints(self):
        from apps.fructs.models import Product, Categorie, Unitie
        product = Product.objects.create(name='Apple', slug='apple', price='2.50',
            label=Categorie.objects.create(label='Fruit'), unite=Unitie.objects.create(unite='kg'))
        add = reverse('cart:cart_add', args=[product.pk])
        self.assertEqual(self.client.get(add).status_code, 405)
        self.assertRedirects(self.client.post(add, {'quantity': 2}), reverse('cart:cart_detail'))
        self.assertEqual(self.client.session['cart'][str(product.pk)]['quantity'], 2)
        self.assertRedirects(self.client.post(reverse('cart:cart_remove', args=[product.pk])), reverse('cart:cart_detail'))
        self.assertEqual(self.client.session['cart'], {})

    def test_invalid_cart_quantity_does_not_change_session(self):
        from apps.fructs.models import Product, Categorie, Unitie
        product = Product.objects.create(name='Apple', slug='apple', price='2.50',
            label=Categorie.objects.create(label='Fruit'), unite=Unitie.objects.create(unite='kg'))
        self.client.post(reverse('cart:cart_add', args=[product.pk]), {'quantity': 0})
        self.assertEqual(self.client.session['cart'], {})
