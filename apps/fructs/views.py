"""Catalog pages build fresh context for each request, never at import time."""
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Product, Categorie, Testimonial, Title, Location, Breadcumb


def setContext():
    """Allow a fresh installation with no optional content or location records."""
    products = Product.objects.all()
    return {
        'titles': Title.objects.all(),
        'filtered': products.filter(isDemo=True),
        'products': products.filter(isDemo=False),
        'testimonials': Testimonial.objects.all(),
        'categories': Categorie.objects.all(),
        'demo': products[:3],
        'location': Location.objects.first(),
    }


def index(request):
    context = setContext()
    context['filtered'] = Paginator(context['filtered'], 3).get_page(request.GET.get('page'))
    return render(request, 'fructs/index.html', context)


def _page(request, slug, template=None):
    context = setContext()
    context['breadcumb'] = Breadcumb.objects.filter(slug=slug).first()
    return render(request, template or f'fructs/{slug}.html', context)


def about(request):
    return _page(request, 'about')


def cart(request):
    return _page(request, 'cart')


def slider(request):
    return _page(request, 'slider', 'fructs/index_2.html')


def news(request):
    return _page(request, 'news')


@require_POST
def suscribe(request):
    # Subscription delivery has no configured workflow yet; never imply success.
    return HttpResponse('Subscriptions are not implemented.', status=501)


def shop(request):
    context = setContext()
    context['products'] = Paginator(context['products'], 3).get_page(request.GET.get('page'))
    context['breadcumb'] = Breadcumb.objects.filter(slug='shop').first()
    return render(request, 'fructs/shop.html', context)


def singleproduct(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = setContext()
    context.update(products=Product.objects.filter(label=product.label), pdt=product)
    return render(request, 'fructs/single-product.html', context)


def checkout(request):
    return _page(request, 'checkout')


def contact(request):
    return _page(request, 'contact')


@require_POST
def send_email(request):
    return HttpResponse('Contact delivery is not implemented.', status=501)
