# withdraw/models.py

import secrets
from django.db import models
from accounts.models import User
from wallet.models import Coin


def generate_reference():
    return secrets.token_urlsafe(16)


class Withdraw(models.Model):

    STATUS_INTERNAL     = "INTERNAL"
    STATUS_PENDING      = "PENDING"
    STATUS_BROADCASTING = "BROADCASTING"
    STATUS_COMPLETED    = "COMPLETED"
    STATUS_FAILED       = "FAILED"

    STATUS_CHOICES = (
        (STATUS_INTERNAL,     "Internal"),
        (STATUS_PENDING,      "Pending"),
        (STATUS_BROADCASTING, "Broadcasting"),
        (STATUS_COMPLETED,    "Completed"),
        (STATUS_FAILED,       "Failed"),
    )

    sender   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawals_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawals_received", null=True, blank=True)
    coin     = models.ForeignKey(Coin, on_delete=models.CASCADE)

    amount  = models.DecimalField(max_digits=36, decimal_places=18)
    address = models.CharField(max_length=255, blank=True, null=True)

    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INTERNAL)
    tx_hash        = models.CharField(max_length=255, blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)

    reference = models.CharField(
        max_length=64,
        unique=True,
        default=generate_reference,  # named function — Django can serialize this
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["sender"]),
        ]

    def __str__(self):
        return f"{self.sender} -> {self.address or self.receiver} | {self.amount} {self.coin.coin} ({self.status})"