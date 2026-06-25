# deposit/tasks.py
"""
Deposit support tasks:
  register_address_alchemy — adds new user EVM address to all Alchemy webhooks
"""
import logging
import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def register_address_alchemy(self, evm_address: str):
    """
    Registers a new EVM deposit address on all three Alchemy ADDRESS_ACTIVITY webhooks.
    Called automatically from signals.py when a user registers.

    Setup steps:
      1. dashboard.alchemy.com → Webhooks → Create ADDRESS_ACTIVITY webhook
         (one each for ETH, BNB, Polygon mainnet)
      2. Copy webhook IDs + auth token to .env
      3. This task auto-runs — no manual action per user needed
    """
    webhook_ids = [
        settings.ALCHEMY_WEBHOOK_ID_ETH,
        settings.ALCHEMY_WEBHOOK_ID_BNB,
        settings.ALCHEMY_WEBHOOK_ID_POL,
    ]
    headers = {
        "X-Alchemy-Token": settings.ALCHEMY_AUTH_TOKEN,
        "Content-Type":    "application/json",
    }

    for webhook_id in webhook_ids:
        try:
            resp = requests.patch(
                "https://dashboard.alchemy.com/api/update-webhook-addresses",
                headers=headers,
                json={
                    "webhook_id":          webhook_id,
                    "addresses_to_add":    [evm_address],
                    "addresses_to_remove": [],
                },
                timeout=15,
            )
            resp.raise_for_status()
            logger.info(f"Alchemy: registered {evm_address[:10]}... on {webhook_id}")
        except Exception as exc:
            logger.error(f"Alchemy registration failed for {evm_address}: {exc}")
            raise self.retry(exc=exc)
