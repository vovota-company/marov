# accounts/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email          = models.EmailField(unique=True)
    google_id      = models.CharField(max_length=255, blank=True, null=True)
    avatar         = models.URLField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name        = models.CharField(max_length=255, blank=True)
    avatar           = models.URLField(blank=True)
    given_name       = models.CharField(max_length=100, blank=True)
    family_name      = models.CharField(max_length=100, blank=True)
    totp_secret      = models.CharField(max_length=64, blank=True, null=True)
    totp_url         = models.TextField(blank=True, null=True)
    is_totp_enabled  = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.email


class WalletIndexCounter(models.Model):
    """Singleton. Always access via select_for_update() inside a transaction."""
    next_index = models.PositiveBigIntegerField(default=1)

    class Meta:
        verbose_name = "Wallet Index Counter"

    def __str__(self):
        return f"Next index: {self.next_index}"


class UserWallet(models.Model):
    """
    One row per user per network.
    ETH/BNB/POL share the same EVM address — separate rows for webhook routing.
    USDT on each network uses the same address — detected by contract at deposit time.
    Private keys NEVER stored — re-derived from xprv + index on demand.
    """
    NETWORK_CHOICES = [
        ("BTC",  "Bitcoin"),
        ("ETH",  "Ethereum"),
        ("BNB",  "BNB Smart Chain"),
        ("POL",  "Polygon"),
        ("TRON", "TRON"),
    ]

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_wallets")
    network          = models.CharField(max_length=10, choices=NETWORK_CHOICES)
    address          = models.CharField(max_length=128, db_index=True)
    derivation_index = models.PositiveBigIntegerField()
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "network")]
        indexes = [
            models.Index(fields=["address"]),
            models.Index(fields=["network", "derivation_index"]),
        ]

    def __str__(self):
        return f"{self.user.email} | {self.network} | {self.address[:16]}..."


class SweepTask(models.Model):
    STATUS = [
        ("PENDING",   "Pending"),
        ("SIGNING",   "Signing"),
        ("BROADCAST", "Broadcast"),
        ("CONFIRMED", "Confirmed"),
        ("FAILED",    "Failed"),
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet     = models.ForeignKey(UserWallet, on_delete=models.PROTECT, related_name="sweeps")
    coin       = models.CharField(max_length=10, default="")  # ETH / USDT / BTC / TRX etc.
    amount_raw = models.CharField(max_length=64)              # wei / satoshi / sun
    tx_hash    = models.CharField(max_length=128, blank=True)
    status     = models.CharField(max_length=12, choices=STATUS, default="PENDING")
    error      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sweep {self.id} | {self.wallet.network}/{self.coin} | {self.status}"


class ApprovalRequest(models.Model):
    LEVEL  = [("USER", "User"), ("SERVER", "Server"), ("HSM", "HSM")]
    STATUS = [("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")]

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sweep     = models.ForeignKey(SweepTask, on_delete=models.CASCADE, related_name="approvals")
    level     = models.CharField(max_length=8, choices=LEVEL)
    status    = models.CharField(max_length=10, choices=STATUS, default="PENDING")
    signed_by = models.CharField(max_length=256, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("sweep", "level")]

    def __str__(self):
        return f"{self.level} | {self.status} | sweep={self.sweep_id}"
