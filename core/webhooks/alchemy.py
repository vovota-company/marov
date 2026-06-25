# core/webhooks/alchemy.py
import hashlib
import hmac
import json
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.tasks import handle_incoming_deposit

ALCHEMY_NETWORK_MAP = {
    "ETH_MAINNET":   "ETH",
    "MATIC_MAINNET": "POL",
    "BNB_MAINNET":   "BNB",
}

# ERC-20 / BEP-20 token contracts → coin symbol
# USDT on each EVM chain
ERC20_CONTRACTS = {
    # Ethereum
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
    # BNB Smart Chain
    "0x55d398326f99059ff775485246999027b3197955": "USDT",
    # Polygon
    "0xc2132d05d31c914a87c6611c10748aeb04b58e8f": "USDT",
}


def _verify_alchemy_signature(request) -> bool:
    sig = request.headers.get("X-Alchemy-Signature", "")
    computed = hmac.new(
        settings.ALCHEMY_SIGNING_KEY.encode(),
        request.body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(sig, computed)


@csrf_exempt
@require_POST
def alchemy_webhook(request):
    if not _verify_alchemy_signature(request):
        return HttpResponseForbidden("bad signature")

    try:
        payload  = json.loads(request.body)
        event    = payload.get("event", {})
        network  = ALCHEMY_NETWORK_MAP.get(event.get("network", ""), "ETH")

        for activity in event.get("activity", []):
            category   = activity.get("category", "")
            to_address = (activity.get("toAddress") or "").lower()
            tx_hash    = activity.get("hash")
            raw_value  = activity.get("rawContract", {}).get("rawValue", "0x0")
            contract   = (activity.get("rawContract", {}).get("address") or "").lower()

            if not to_address or not tx_hash:
                continue

            # Determine coin symbol
            if category == "external":
                coin_symbol = network          # "ETH", "BNB", or "POL"
                contract    = None
            elif category == "token":
                coin_symbol = ERC20_CONTRACTS.get(contract)
                if not coin_symbol:
                    continue   # unknown token — ignore
            else:
                continue

            try:
                amount_wei = int(raw_value, 16) if raw_value.startswith("0x") else int(raw_value)
            except Exception:
                amount_wei = 0

            if amount_wei == 0:
                continue

            # Convert to decimal units for handle_incoming_deposit
            if coin_symbol in ("USDT",):
                # USDT has 6 decimals on all EVM chains
                amount = Decimal(amount_wei) / Decimal(10 ** 6)
            else:
                # Native coin — 18 decimals
                amount = Decimal(amount_wei) / Decimal("1e18")

            handle_incoming_deposit(
                network=network,
                tx_hash=tx_hash,
                to_address=to_address,
                amount=amount,
                block_number=int(activity.get("blockNum", "0x0"), 16)
                             if activity.get("blockNum") else 0,
                confirmations=12,
                coin_symbol=coin_symbol,
                contract=contract,
            )

    except Exception as exc:
        import logging
        logging.getLogger("core.webhooks").error(f"Alchemy webhook error: {exc}", exc_info=True)

    return JsonResponse({"status": "ok"})
