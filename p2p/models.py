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


class MyPaymentMethod(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="my_payment_methods"
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name="user_payment_methods"
    )
    number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "payment_method", "number")

    def __str__(self):
        return f"{self.user} - {self.payment_method.name}"


class SellOffer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sell_offers"
    )

    payment_methods = models.ManyToManyField(
        MyPaymentMethod,
        related_name="sell_offers"
    )

    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="sell_offers"
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="sell_offers"
    )

    exchange_amount = models.DecimalField(max_digits=20, decimal_places=6)
    min_money = models.DecimalField(max_digits=20, decimal_places=6)
    max_money = models.DecimalField(max_digits=20, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sell {self.coin} by {self.user}"


class BuyOffer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="buy_offers"
    )

    payment_methods = models.ManyToManyField(
        MyPaymentMethod,
        related_name="buy_offers"
    )

    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="buy_offers"
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="buy_offers"
    )

    exchange_amount = models.DecimalField(max_digits=20, decimal_places=6)
    min_money = models.DecimalField(max_digits=20, decimal_places=6)
    max_money = models.DecimalField(max_digits=20, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Buy {self.coin} by {self.user}"


class SellOrder(models.Model):
    sell_offer = models.ForeignKey(
        SellOffer,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sell_orders_as_seller"
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sell_orders_as_client"
    )

    client_payment_method = models.ForeignKey(
        MyPaymentMethod,
        on_delete=models.PROTECT,
        related_name="sell_orders"
    )

    amount = models.DecimalField(max_digits=20, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sell Order #{self.id}"


class BuyOrder(models.Model):
    buy_offer = models.ForeignKey(
        BuyOffer,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="buy_orders_as_buyer"
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="buy_orders_as_client"
    )

    client_payment_method = models.ForeignKey(
        MyPaymentMethod,
        on_delete=models.PROTECT,
        related_name="buy_orders"
    )

    amount = models.DecimalField(max_digits=20, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Buy Order #{self.id}"