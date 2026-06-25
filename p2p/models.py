from django.db import models
from accounts.models import User
from wallet.models import Coin

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    logo = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    value_in_usdt = models.DecimalField(max_digits=20, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SellOffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    number = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    exchange_amount = models.DecimalField(max_digits=20, decimal_places=6)
    min_money = models.DecimalField(max_digits=20, decimal_places=6)
    max_money = models.DecimalField(max_digits=20, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)


class BuyOffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    exchange_amount = models.DecimalField(max_digits=20, decimal_places=6)
    min_money = models.DecimalField(max_digits=20, decimal_places=6)
    max_money = models.DecimalField(max_digits=20, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)