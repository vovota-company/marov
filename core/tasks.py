# core/tasks.py
import logging
from decimal import Decimal

from django.utils import timezone
from django.db import transaction
from celery import shared_task
from django.conf import settings

from wallet.models import Coin, Wallet
from .models import PlatformWallet, DepositAddress, Deposit
from .services import sync_platform_wallet, sync_all_platform_wallets

logger = logging.getLogger("core")

REQUIRED_CONFIRMATIONS = {
    "BTC":  2,
    "ETH":  12,
    "BNB":  12,
    "POL":  128,
    "TRON": 19,
}

# TRC-20 USDT contract on TRON mainnet
USDT_TRC20_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


# ── Platform wallet sync ──────────────────────────────────────────────────────

@shared_task
def run_sync_all_platform_wallets():
    sync_all_platform_wallets()


# ── Credit a confirmed deposit ────────────────────────────────────────────────

def credit_deposit(deposit: Deposit):
    """Idempotent. Credits user wallet and syncs PlatformWallet."""
    if deposit.status == Deposit.STATUS_CREDITED:
        return

    with transaction.atomic():
        deposit = Deposit.objects.select_for_update().get(pk=deposit.pk)
        if deposit.status == Deposit.STATUS_CREDITED:
            return

        user_wallet, _ = Wallet.objects.select_for_update().get_or_create(
            user=deposit.user,
            coin=deposit.coin,
            defaults={"balance": Decimal("0")},
        )
        user_wallet.balance += deposit.amount
        user_wallet.save(update_fields=["balance"])

        deposit.status     = Deposit.STATUS_CREDITED
        deposit.credited_at = timezone.now()
        deposit.save(update_fields=["status", "credited_at"])

    sync_platform_wallet(deposit.coin)


# ── Main deposit entry point ──────────────────────────────────────────────────

def handle_incoming_deposit(
    network: str,
    tx_hash: str,
    to_address: str,
    amount: Decimal,
    block_number: int,
    confirmations: int,
    coin_symbol: str = None,
    contract: str = None,
):
    """
    Single entry point for all three listeners (Alchemy, BlockCypher, TronGrid).
    Finds the Coin by (network + contract), finds the DepositAddress owner,
    creates/updates Deposit, and credits when confirmations are enough.

    coin_symbol: optional override (e.g. "USDT") — if None, matched by contract.
    """
    # Find the coin
    try:
        if contract:
            coin = Coin.objects.get(network=network, contract__iexact=contract)
        elif coin_symbol:
            coin = Coin.objects.get(network=network, coin=coin_symbol, contract__isnull=True)
        else:
            # native coin — no contract
            coin = Coin.objects.get(network=network, contract__isnull=True)
    except Coin.DoesNotExist:
        logger.warning(f"No coin for network={network} contract={contract} symbol={coin_symbol} — skip {tx_hash}")
        return
    except Coin.MultipleObjectsReturned:
        logger.error(f"Multiple coins matched network={network} contract={contract} — check DB")
        return

    # Find the user by deposit address
    try:
        dep_addr = DepositAddress.objects.select_related("user").get(address__iexact=to_address)
    except DepositAddress.DoesNotExist:
        return  # not one of ours — ignore

    required = REQUIRED_CONFIRMATIONS.get(network, 12)

    deposit, created = Deposit.objects.get_or_create(
        coin=coin,
        tx_hash=tx_hash,
        defaults=dict(
            user=dep_addr.user,
            deposit_address=dep_addr,
            amount=amount,
            block_number=block_number,
            confirmations=confirmations,
            status=Deposit.STATUS_PENDING,
        ),
    )

    if not created:
        deposit.confirmations = max(deposit.confirmations, confirmations)
        deposit.save(update_fields=["confirmations"])

    if deposit.confirmations >= required and deposit.status != Deposit.STATUS_CREDITED:
        deposit.status = Deposit.STATUS_CONFIRMED
        deposit.save(update_fields=["status"])
        credit_deposit(deposit)


# ── TRON polling (TRX native + USDT TRC-20) ──────────────────────────────────

import requests
TRONGRID_BASE = "https://api.trongrid.io"


@shared_task
def poll_tron_deposits():
    tron_addrs = (
        DepositAddress.objects
        .filter(coin__network="TRON")
        .values_list("address", flat=True)
        .distinct()
    )
    for address in tron_addrs:
        try:
            _poll_trx_native(address)
            _poll_trc20_usdt(address)
        except Exception as exc:
            logger.error(f"TRON poll error {address}: {exc}")


def _trongrid_get(path, params):
    resp = requests.get(
        f"{TRONGRID_BASE}{path}",
        headers={"TRON-PRO-API-KEY": settings.TRONGRID_API_KEY},
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def _poll_trx_native(address: str):
    txs = _trongrid_get(
        f"/v1/accounts/{address}/transactions",
        {"only_to": "true", "only_confirmed": "true", "limit": 20},
    )
    for tx in txs:
        contracts = tx.get("raw_data", {}).get("contract", [])
        if not contracts:
            continue
        value = contracts[0].get("parameter", {}).get("value", {})
        if "amount" not in value:
            continue
        handle_incoming_deposit(
            network="TRON",
            tx_hash=tx["txID"],
            to_address=address,
            amount=Decimal(value["amount"]) / Decimal("1000000"),
            block_number=tx.get("blockNumber", 0),
            confirmations=19,
            coin_symbol="TRX",
            contract=None,
        )


def _poll_trc20_usdt(address: str):
    """Poll USDT TRC-20 deposits."""
    txs = _trongrid_get(
        f"/v1/accounts/{address}/transactions/trc20",
        {"only_confirmed": "true", "limit": 20, "contract_address": USDT_TRC20_CONTRACT},
    )
    for tx in txs:
        if tx.get("to") != address:
            continue
        raw = int(tx.get("value", "0"))
        dec = int(tx.get("token_info", {}).get("decimals", 6))
        handle_incoming_deposit(
            network="TRON",
            tx_hash=tx["transaction_id"],
            to_address=address,
            amount=Decimal(raw) / Decimal(10 ** dec),
            block_number=0,
            confirmations=19,
            coin_symbol="USDT",
            contract=USDT_TRC20_CONTRACT,
        )
