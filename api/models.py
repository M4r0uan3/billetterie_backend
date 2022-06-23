from django.db import models
from django.conf import settings
from uuid import uuid4
from django.contrib import admin
from .validatores import validate_file_size


class Theme(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Customer(models.Model):
    phone = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    @admin.display(ordering='user__email')
    def email(self):
        return self.user.email

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    city = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    theme = models.ForeignKey(
        Theme, on_delete=models.PROTECT, related_name='events')

    date = models.DateTimeField()

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['-id']


class EventImage(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event/images',
                              validators=[validate_file_size])


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return str(self.placed_at)

    class Meta:
        ordering = ['placed_at']
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]


class OrderTicket(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartTicket(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart', 'event']]
