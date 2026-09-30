from decimal import Decimal
from django.conf import settings
from apps.fructs.models import Product
from apps.coupons.models import Coupon


class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # store current applied coupon
        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        # Construct presentation items separately: the session must contain only JSON values.
        products = list(Product.objects.filter(id__in=self.cart.keys()))
        existing = {str(product.pk) for product in products}
        stale = set(self.cart) - existing
        for product_id in stale:
            del self.cart[product_id]
        if stale:
            self.save()
        for product in products:
            item = self.cart[str(product.id)].copy()
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError("Quantity must be a positive integer.")
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        # remove cart from session
        self.cart.clear()
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.pop("coupon_id", None)
        self.coupon_id = None
        self.save()

    def get_total_price(self):
        return sum((Decimal(item['price']) * item['quantity'] for item in self.cart.values()), Decimal(0))

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                from django.utils import timezone
                now = timezone.now()
                return Coupon.objects.get(id=self.coupon_id, active=True, valid_from__lte=now, valid_to__gte=now)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        coupon = self.coupon
        if coupon:
            return (coupon.discount / Decimal(100)) \
                * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
