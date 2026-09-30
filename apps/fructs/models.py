from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone
# for authentifications.
from django.contrib.auth.models import User


class LocalUser(User):
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)

    def __str__(self):
        return self.first_name

class SubscribedUsers(models.Model):
    email = models.CharField(unique=True, max_length=50)

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    conf_num = models.CharField(max_length=15)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.email + " (" + ("not " if not self.confirmed else "") + "confirmed)"

class Featured(models.Model):
    title = models.CharField(max_length=50)
    paragraph = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title

class SubscribeModel(models.Model):
    sys_id = models.AutoField(primary_key=True, null=False, blank=True)
    email = models.EmailField(null=False, blank=True, max_length=200, unique=True)
    status = models.CharField(max_length=64, null=False, blank=True)
    created_date = models.DateTimeField(null=False, blank=True)
    updated_date = models.DateTimeField(null=False, blank=True)

    class Meta:
        app_label = "appname"
        db_table = "appname_subscribe"

    def __str__(self):
        return self.email


class Categorie(models.Model):
    label = models.CharField(max_length=100, unique=True, default='')

    def __str__(self):
        return self.label


class Unitie(models.Model):
    unite = models.CharField(max_length=100, unique=True, default='')

    def __str__(self):
        return self.unite


class Product(models.Model):
    """Catalog metadata; order processing and stock tracking are separate concerns."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=50)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    image = models.ImageField(null=True, blank=True,
        upload_to='product_images')
    label = models.ForeignKey(Categorie, on_delete=models.CASCADE, default='')
    unite = models.ForeignKey(Unitie, on_delete=models.DO_NOTHING, default='')
    sante = models.TextField(default='')
    author = models.ForeignKey(LocalUser, on_delete=models.CASCADE, null=True, blank=True)
    isDemo = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Breadcumb(models.Model):
    slug = models.SlugField()
    subtitle = models.CharField(max_length=20)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.slug

class Mail(models.Model):
    email = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message = models.CharField(max_length=150)

    def __str__(self):
        return self.email


class Testimonial(models.Model):
    photo = models.ImageField(null=True, blank=True, upload_to='tester_images')
    name = models.CharField(max_length=50, null=True, blank=True)
    work = models.CharField(max_length=20, null=True, blank=True)
    declaration = models.TextField()
    note = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return self.name or "Unnamed testimonial"

class Title(models.Model):    
    label = models.CharField(max_length=50)
    link = models.CharField(max_length=50, null=True, blank=True)
    note = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.label

class Location(models.Model):
    adresse = models.CharField(max_length=50)
    street = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    town = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=False, blank=True, max_length=200, unique=True)
    innner = models.CharField(max_length=50, null=True, blank=True)
    outter = models.CharField(max_length=50, null=True, blank=True)
    