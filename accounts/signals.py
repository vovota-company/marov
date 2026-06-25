# accounts/signals.py
import logging
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
import pyotp

from accounts.models import Profile, UserWallet, WalletIndexCounter
from wallet.models import Coin, Wallet
from accounts.services.wallet_service import (
    derive_btc_address,
    derive_evm_address,
    derive_tron_address,
)

logger = logging.getLogger(__name__)

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except Exception:
    from django.contrib.auth.models import User


def _allocate_wallet_index() -> int:
    """Atomically claim the next derivation index. Collision-proof under load."""
    counter, _ = WalletIndexCounter.objects.select_for_update().get_or_create(id=1)
    index = counter.next_index
    counter.next_index += 1
    counter.save(update_fields=["next_index"])
    return index


def _create_user_wallets(user, index: int) -> str:
    """
    Derives deposit addresses and saves UserWallet rows.
    Returns the EVM address for Alchemy webhook registration.
    USDT uses the same address as the base network — no extra rows needed.
    """
    evm_address  = derive_evm_address(index)
    btc_address  = derive_btc_address(index)
    tron_address = derive_tron_address(index)

    UserWallet.objects.bulk_create([
        # EVM chains — same address, separate rows for per-network webhook lookup
        UserWallet(user=user, network="ETH",  derivation_index=index, address=evm_address),
        UserWallet(user=user, network="BNB",  derivation_index=index, address=evm_address),
        UserWallet(user=user, network="POL",  derivation_index=index, address=evm_address),
        # Native chains
        UserWallet(user=user, network="BTC",  derivation_index=index, address=btc_address),
        UserWallet(user=user, network="TRON", derivation_index=index, address=tron_address),
    ])

    logger.info(
        f"Wallets created | user={user.id} | index={index} | "
        f"EVM={evm_address[:10]} BTC={btc_address[:10]} TRON={tron_address[:10]}"
    )
    return evm_address


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if not created:
        return

    evm_address = None
    try:
        with transaction.atomic():
            # 1. Profile + TOTP
            secret   = pyotp.random_base32()
            totp_url = pyotp.TOTP(secret).provisioning_uri(
                name=instance.email,
                issuer_name="malov.com",
            )
            Profile.objects.create(
                user=instance,
                totp_secret=secret,
                totp_url=totp_url,
            )

            # 2. Atomic derivation index
            index = _allocate_wallet_index()

            # 3. Deposit wallets
            evm_address = _create_user_wallets(instance, index)

            # 4. Coin balance wallets (platform ledger)
            Wallet.objects.bulk_create([
                Wallet(user=instance, coin=coin)
                for coin in Coin.objects.all()
            ])

    except Exception as exc:
        logger.error(f"Wallet creation failed for user {instance.id}: {exc}", exc_info=True)
        from accounts.tasks import retry_wallet_creation
        retry_wallet_creation.apply_async(args=[instance.id], countdown=30)
        return

    # Register EVM address with Alchemy (outside atomic — network call)
    if evm_address:
        try:
            from deposit.tasks import register_address_alchemy
            register_address_alchemy.apply_async(args=[evm_address], countdown=5)
        except Exception as exc:
            logger.warning(f"Alchemy registration queuing failed: {exc}")
