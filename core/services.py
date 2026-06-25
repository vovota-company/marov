from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from wallet.models import Coin, Wallet
from .models import PlatformWallet


def sync_platform_wallet(coin: Coin):
    """
    Recomputes the total user balance for a single coin and updates
    PlatformWallet. Call this after every deposit credit or withdrawal.
    """
    total = (
        Wallet.objects
        .filter(coin=coin)
        .aggregate(total=Sum("balance"))["total"]
        or Decimal("0")
    )

    with transaction.atomic():
        PlatformWallet.objects.update_or_create(
            coin=coin,
            defaults={
                "balance": total,
                "last_synced_at": timezone.now(),
            },
        )


def sync_all_platform_wallets():
    """Recomputes for all 9 coins at once."""
    for coin in Coin.objects.all():
        sync_platform_wallet(coin)