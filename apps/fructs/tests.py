"""Request isolation, empty-data behavior, and catalog pagination."""
from django.test import TestCase
from .models import Product, Categorie, Unitie, Testimonial
from .views import setContext


class CatalogTests(TestCase):
    def make_product(self, slug='apple', demo=False):
        category, _ = Categorie.objects.get_or_create(label='Fruit')
        unit, _ = Unitie.objects.get_or_create(unite='kg')
        return Product.objects.create(name=slug, slug=slug, price='2.50', label=category, unite=unit, isDemo=demo)

    def test_empty_home(self):
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_empty_pages(self):
        for route in ['about', 'cart', 'checkout', 'contact', 'shop', 'news', 'slider']:
            with self.subTest(route=route):
                self.assertEqual(self.client.get('/'+route).status_code, 200)

    def test_missing_product_is_404(self):
        self.assertEqual(self.client.get('/singleproduct/missing').status_code, 404)

    def test_optional_product_image(self):
        self.make_product()
        self.assertEqual(self.client.get('/singleproduct/apple').status_code, 200)
        self.assertEqual(self.client.get('/shop').status_code, 200)

    def test_checkout_template(self):
        self.assertTemplateUsed(self.client.get('/checkout'), 'fructs/checkout.html')

    def test_context_refreshes_between_requests(self):
        self.assertEqual(setContext()['products'].count(), 0)
        self.make_product()
        self.assertEqual(setContext()['products'].count(), 1)
        self.assertIsNot(setContext(), setContext())

    def test_demo_filtering(self):
        self.make_product('demo', True)
        self.make_product('normal')
        context = setContext()
        self.assertEqual(list(context['filtered'].values_list('slug', flat=True)), ['demo'])
        self.assertEqual(list(context['products'].values_list('slug', flat=True)), ['normal'])

    def test_pagination_handles_invalid_pages(self):
        for i in range(4):
            self.make_product(f'fruit-{i}')
        self.assertEqual(len(self.client.get('/shop?page=bad').context['products']), 3)
        self.assertEqual(len(self.client.get('/shop?page=999').context['products']), 1)
        self.assertEqual(len(self.client.get('/shop').context['products']), 3)

    def test_subscription_contract(self):
        self.assertEqual(self.client.get('/suscribe').status_code, 405)
        self.assertEqual(self.client.post('/suscribe').status_code, 501)

    def test_nullable_testimonial_name(self):
        self.assertEqual(str(Testimonial(name=None)), 'Unnamed testimonial')
