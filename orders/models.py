from django.db import models
from django.conf import settings


class OrderType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('washing', 'Yuvilmoqda'),
        ('bringing', 'Yetkazilmoqda'),
        ('delivered', 'Yetkazildi'),
    ]

    # Mijoz ma'lumotlari
    name    = models.CharField(max_length=200)
    number  = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    date    = models.DateField()
    izox    = models.TextField(blank=True)

    # Yuk turi va o'lcham
    type   = models.ForeignKey(OrderType, on_delete=models.SET_NULL, null=True)
    width  = models.FloatField(null=True, blank=True)   # metr (gilam, parda)
    height = models.FloatField(null=True, blank=True)   # metr
    kg     = models.FloatField(null=True, blank=True)   # kg (ko'rpa)
    price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='washing')

    # Kim qo'shgan
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.name} ({self.type})"
