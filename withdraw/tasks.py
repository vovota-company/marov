"""
withdraw/tasks.py

Celery task that signs and broadcasts an external withdrawal.
Called after balance is reserved and TOTP verified in the view.
"""

import logging
from decimal import Decimal

from celery import shared_task
from django.db import transaction

from wallet.models import Wallet
from core.services import sync_platform_wallet
from .models import Withdraw
from .signing import broadcast

logger = logging.getLogger("withdraw.tasks")


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_external_withdrawal(self, withdraw_id: int):
    try:
        withdraw = Withdraw.objects.select_related("sender", "coin").get(id=withdraw_id)
    except Withdraw.DoesNotExist:
        logger.error(f"Withdraw {withdraw_id} not found")
        return

    withdraw.status = Withdraw.STATUS_BROADCASTING
    withdraw.save(update_fields=["status"])

    try:
        tx_hash = broadcast(
            network=withdraw.coin.network,
            to_address=withdraw.address,
            amount=withdraw.amount,
            contract=withdraw.coin.contract,
        )

        # success — deduct balance permanently and record tx_hash
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(
                user=withdraw.sender,
                coin=withdraw.coin,
            )
            # balance was already reserved (deducted) in the view,
            # so nothing to deduct again — just mark completed
            withdraw.status  = Withdraw.STATUS_COMPLETED
            withdraw.tx_hash = tx_hash
            withdraw.save(update_fields=["status", "tx_hash"])

        sync_platform_wallet(withdraw.coin)
        logger.info(f"Withdraw {withdraw_id} completed: {tx_hash}")

    except Exception as e:
        logger.error(f"Withdraw {withdraw_id} failed: {e}")

        # release the reserved balance back to the user
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(
                user=withdraw.sender,
                coin=withdraw.coin,
            )
            wallet.balance += withdraw.amount
            wallet.save(update_fields=["balance"])

            withdraw.status         = Withdraw.STATUS_FAILED
            withdraw.failure_reason = str(e)
            withdraw.save(update_fields=["status", "failure_reason"])

        sync_platform_wallet(withdraw.coin)

        # retry up to 3 times for transient RPC errors
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Withdraw {withdraw_id} permanently failed after retries")