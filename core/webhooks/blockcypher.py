import json
from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..tasks import handle_incoming_deposit
from core.models import DepositAddress


@csrf_exempt
@require_POST
def blockcypher_webhook(request):
    payload      = json.loads(request.body)
    tx_hash      = payload.get("hash")
    confirmations = payload.get("confirmations", 0)
    block_height = payload.get("block_height", 0)

    our_addresses = set(
        DepositAddress.objects.filter(coin__network="BTC")
        .values_list("address", flat=True)
    )

    for output in payload.get("outputs", []):
        for addr in output.get("addresses", []):
            if addr not in our_addresses:
                continue
            sats = output.get("value", 0)
            handle_incoming_deposit(
                network="BTC",
                tx_hash=tx_hash,
                to_address=addr,
                amount=Decimal(sats) / Decimal("1e8"),
                block_number=block_height,
                confirmations=confirmations,
                contract=None,
            )

    return JsonResponse({"status": "ok"})