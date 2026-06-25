from django.db import models
from accounts.models import User 

class Coin(models.Model):
    network = models.CharField(max_length=20)
    coin = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    icon = models.FileField(upload_to="coins/")
    contract = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("network", "coin", "contract")

    def __str__(self):
        return self.label


class Wallet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wallets"
    )
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="wallets"
    )
    balance = models.DecimalField(
        max_digits=30,
        decimal_places=8,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coin")

    def __str__(self):
        return f"{self.user} - {self.coin.label}"