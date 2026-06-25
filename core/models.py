from django.db import models
from wallet.models import Coin


class PlatformWallet(models.Model):
    """
    Aggregated sum of all user balances per coin.
    Updated in real time whenever a deposit is credited or withdrawal completes.
    NOT an on-chain address — purely a DB-level aggregate for fast reads.
    """
    coin = models.OneToOneField(
        Coin,
        on_delete=models.CASCADE,
        related_name="platform_wallet",
    )
    balance = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        default=0,
    )
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Platform Wallet"
        verbose_name_plural = "Platform Wallets"

    def __str__(self):
        return f"[PLATFORM] {self.coin.label} = {self.balance}"


class DepositAddress(models.Model):
    """
    Maps a derived deposit address back to a user + coin so we know
    who to credit when a deposit arrives on that address.
    """
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="deposit_addresses",
    )
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="deposit_addresses",
    )
    address = models.CharField(max_length=255, unique=True)
    derivation_index = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coin")
        indexes = [
            models.Index(fields=["address"]),
            models.Index(fields=["coin"]),
        ]

    def __str__(self):
        return f"{self.user} | {self.coin.label} | {self.address}"


class Deposit(models.Model):
    STATUS_PENDING   = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CREDITED  = "CREDITED"
    STATUS_FAILED    = "FAILED"

    STATUS_CHOICES = (
        (STATUS_PENDING,   "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CREDITED,  "Credited"),
        (STATUS_FAILED,    "Failed"),
    )

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="core_deposits",
    )
    coin = models.ForeignKey(
        Coin,
        on_delete=models.CASCADE,
        related_name="deposits",
    )
    deposit_address = models.ForeignKey(
        DepositAddress,
        on_delete=models.SET_NULL,
        null=True,
        related_name="deposits",
    )
    tx_hash       = models.CharField(max_length=255)
    amount        = models.DecimalField(max_digits=36, decimal_places=18)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    block_number  = models.PositiveBigIntegerField(blank=True, null=True)
    confirmations = models.PositiveIntegerField(default=0)
    credited_at   = models.DateTimeField(blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("coin", "tx_hash")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user", "coin"]),
        ]

    def __str__(self):
        return f"{self.coin.label} deposit {self.amount} -> {self.user} ({self.status})"