"""Session persistence and coupon validity, without external services."""
import json
from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from django.contrib.sessions.backends.db import SessionStore
from django.test import TestCase
from django.utils import timezone
from apps.fructs.models import Product, Categorie, Unitie
from apps.coupons.models import Coupon
from .cart import Cart
from .forms import CartAddProductForm


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Apple', slug='apple', price='2.50',
            label=Categorie.objects.create(label='Fruit'), unite=Unitie.objects.create(unite='kg'))
        self.session = SessionStore()
        self.cart = Cart(SimpleNamespace(session=self.session))

    def coupon(self, **changes):
        now = timezone.now()
        fields = dict(code='SAVE', discount=20, active=True, valid_from=now-timedelta(days=1), valid_to=now+timedelta(days=1))
        fields.update(changes)
        coupon = Coupon.objects.create(**fields)
        self.cart.coupon_id = self.session['coupon_id'] = coupon.pk
        return coupon

    def test_empty_total_is_decimal(self):
        self.assertEqual(self.cart.get_total_price(), Decimal(0))
        self.assertIsInstance(self.cart.get_total_price(), Decimal)

    def test_add_accumulates(self):
        self.cart.add(self.product, 2)
        self.cart.add(self.product)
        self.assertEqual(len(self.cart), 3)
        self.assertEqual(self.cart.get_total_price(), Decimal('7.50'))

    def test_override_quantity(self):
        self.cart.add(self.product, 2)
        self.cart.add(self.product, 4, True)
        self.assertEqual(len(self.cart), 4)

    def test_reject_bad_quantities(self):
        for quantity in [0, -1, True, '2', 1.5]:
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                self.cart.add(self.product, quantity)

    def test_iteration_preserves_serializable_session(self):
        self.cart.add(self.product, 2)
        item = list(self.cart)[0]
        self.assertEqual(item['total_price'], Decimal('5.00'))
        self.assertEqual(item['product'], self.product)
        json.dumps(dict(self.session))
        self.assertNotIn('product', self.cart.cart[str(self.product.pk)])
        self.session.save()
        loaded = Cart(SimpleNamespace(session=SessionStore(self.session.session_key)))
        self.assertEqual(loaded.get_total_price(), Decimal('5.00'))

    def test_removed_product_skipped(self):
        self.cart.add(self.product)
        self.product.delete()
        self.assertEqual(list(self.cart), [])

    def test_remove_idempotent(self):
        self.cart.add(self.product)
        self.cart.remove(self.product)
        self.cart.remove(self.product)
        self.assertEqual(len(self.cart), 0)

    def test_clear_idempotent_resets_coupon(self):
        self.cart.add(self.product)
        self.coupon()
        self.cart.clear()
        self.cart.clear()
        self.assertEqual(len(self.cart), 0)
        self.assertNotIn('coupon_id', self.session)
        self.assertIsNone(self.cart.coupon)
        self.cart.add(self.product)
        self.assertEqual(len(self.cart), 1)

    def test_valid_coupon(self):
        self.cart.add(self.product, 2)
        self.coupon()
        self.assertEqual(self.cart.get_discount(), Decimal('1.00'))
        self.assertEqual(self.cart.get_total_price_after_discount(), Decimal('4.00'))

    def test_expired_coupon(self):
        self.coupon(valid_to=timezone.now()-timedelta(seconds=1))
        self.assertIsNone(self.cart.coupon)

    def test_future_coupon(self):
        self.coupon(valid_from=timezone.now()+timedelta(days=1))
        self.assertIsNone(self.cart.coupon)

    def test_inactive_coupon(self):
        self.coupon(active=False)
        self.assertIsNone(self.cart.coupon)

    def test_deleted_coupon(self):
        self.coupon().delete()
        self.assertEqual(self.cart.get_discount(), Decimal(0))

    def test_form_quantity_bounds(self):
        self.assertTrue(CartAddProductForm({'quantity': 1}).is_valid())
        self.assertFalse(CartAddProductForm({'quantity': 21}).is_valid())
