# accounts/tasks.py
import logging
import os
import requests
from celery import shared_task
from django.db import transaction
from django.conf import settings

logger = logging.getLogger(__name__)

SIGNING_SERVICE_URL = os.environ.get("SIGNING_SERVICE_URL", "http://signer:8001")


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def retry_wallet_creation(self, user_id: int):
    from django.contrib.auth import get_user_model
    from accounts.signals import _allocate_wallet_index, _create_user_wallets

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        if not user.user_wallets.exists():
            with transaction.atomic():
                index = _allocate_wallet_index()
                _create_user_wallets(user, index)
            logger.info(f"Wallet retry succeeded for user {user_id}")
    except Exception as exc:
        logger.error(f"Wallet retry failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def initiate_sweep(self, wallet_id: str, amount_raw: str, network: str, coin: str = ""):
    from accounts.models import UserWallet, SweepTask, ApprovalRequest

    try:
        wallet = UserWallet.objects.get(id=wallet_id)
        sweep  = SweepTask.objects.create(
            wallet=wallet,
            coin=coin or network,
            amount_raw=amount_raw,
            status="PENDING",
        )
        ApprovalRequest.objects.create(sweep=sweep, level="SERVER", status="APPROVED", signed_by="server-auto")

        # Auto-approve user layer (add TOTP gate here for large amounts)
        ApprovalRequest.objects.create(sweep=sweep, level="USER", status="APPROVED", signed_by="auto-below-threshold")

        execute_sweep.apply_async(args=[str(sweep.id)], countdown=2)
        logger.info(f"Sweep {sweep.id} initiated | {network}/{coin} | {amount_raw}")

    except Exception as exc:
        logger.error(f"initiate_sweep failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_sweep(self, sweep_id: str):
    from accounts.models import SweepTask
    from accounts.signing.signing_service import generate_approval_token

    try:
        sweep    = SweepTask.objects.select_related("wallet").get(id=sweep_id)
        approvals = {a.level: a.status for a in sweep.approvals.all()}

        for layer in ("USER", "SERVER"):
            if approvals.get(layer) != "APPROVED":
                logger.warning(f"Sweep {sweep_id} blocked — {layer} not approved")
                return

        sweep.status = "SIGNING"
        sweep.save(update_fields=["status"])

        approval_token = generate_approval_token(sweep_id)
        network        = sweep.wallet.network
        index          = sweep.wallet.derivation_index

        if network in ("ETH", "BNB", "POL"):
            signed_tx = _sign_evm(sweep, approval_token, index, network)
        elif network == "TRON":
            signed_tx = _sign_tron(sweep, approval_token, index)
        elif network == "BTC":
            signed_tx = _sign_btc(sweep, approval_token, index)
        else:
            raise ValueError(f"Unsupported network: {network}")

        tx_hash = _broadcast(network, signed_tx)

        sweep.tx_hash = tx_hash
        sweep.status  = "BROADCAST"
        sweep.save(update_fields=["tx_hash", "status"])

        confirm_sweep.apply_async(args=[sweep_id, tx_hash, network], countdown=30)
        logger.info(f"Sweep {sweep_id} broadcast | tx={tx_hash}")

    except Exception as exc:
        logger.error(f"execute_sweep {sweep_id} failed: {exc}", exc_info=True)
        from accounts.models import SweepTask
        SweepTask.objects.filter(id=sweep_id).update(status="FAILED", error=str(exc))
        raise self.retry(exc=exc)


def _sign_evm(sweep, approval_token, index, network):
    from web3 import Web3
    rpc_urls  = {"ETH": settings.ETH_RPC_URL, "BNB": settings.BSC_RPC_URL, "POL": settings.POLYGON_RPC_URL}
    chain_ids = {"ETH": 1, "BNB": 56, "POL": 137}
    w3        = Web3(Web3.HTTPProvider(rpc_urls[network]))
    resp = requests.post(f"{SIGNING_SERVICE_URL}/sign/evm", json={
        "sweep_id":         str(sweep.id),
        "approval_token":   approval_token,
        "derivation_index": index,
        "to_address":       settings.CENTRAL_EVM_ADDRESS,
        "amount_wei":       int(sweep.amount_raw),
        "gas_price_wei":    w3.eth.gas_price,
        "gas_limit":        21000,
        "nonce":            w3.eth.get_transaction_count(sweep.wallet.address),
        "chain_id":         chain_ids[network],
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()["signed_tx"]


def _sign_tron(sweep, approval_token, index):
    resp = requests.post(f"{SIGNING_SERVICE_URL}/sign/tron", json={
        "sweep_id":         str(sweep.id),
        "approval_token":   approval_token,
        "derivation_index": index,
        "from_address":     sweep.wallet.address,
        "to_address":       settings.CENTRAL_TRON_ADDRESS,
        "amount_sun":       int(sweep.amount_raw),
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()["signed_tx"]


def _sign_btc(sweep, approval_token, index):
    resp = requests.post(f"{SIGNING_SERVICE_URL}/sign/btc", json={
        "sweep_id":         str(sweep.id),
        "approval_token":   approval_token,
        "derivation_index": index,
        "from_address":     sweep.wallet.address,
        "to_address":       settings.CENTRAL_BTC_ADDRESS,
        "amount_sat":       int(sweep.amount_raw),
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()["signed_tx"]


def _broadcast(network, signed_tx):
    if network in ("ETH", "BNB", "POL"):
        from web3 import Web3
        rpc_urls = {"ETH": settings.ETH_RPC_URL, "BNB": settings.BSC_RPC_URL, "POL": settings.POLYGON_RPC_URL}
        w3 = Web3(Web3.HTTPProvider(rpc_urls[network]))
        return w3.eth.send_raw_transaction(bytes.fromhex(signed_tx.replace("0x", ""))).hex()
    elif network == "TRON":
        resp = requests.post(
            "https://api.trongrid.io/wallet/broadcasttransaction",
            json=signed_tx,
            headers={"TRON-PRO-API-KEY": settings.TRONGRID_API_KEY},
        )
        resp.raise_for_status()
        return resp.json().get("txid", "")
    elif network == "BTC":
        resp = requests.post(
            "https://api.blockcypher.com/v1/btc/main/txs/push",
            json={"tx": signed_tx},
            params={"token": settings.BLOCKCYPHER_API_KEY},
        )
        resp.raise_for_status()
        return resp.json().get("tx", {}).get("hash", "")
    raise ValueError(f"Unknown network: {network}")


@shared_task(bind=True, max_retries=20, default_retry_delay=60)
def confirm_sweep(self, sweep_id, tx_hash, network):
    from accounts.models import SweepTask
    try:
        confirmed = False
        if network in ("ETH", "BNB", "POL"):
            from web3 import Web3
            rpc_urls = {"ETH": settings.ETH_RPC_URL, "BNB": settings.BSC_RPC_URL, "POL": settings.POLYGON_RPC_URL}
            w3      = Web3(Web3.HTTPProvider(rpc_urls[network]))
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            confirmed = receipt is not None and receipt.status == 1

        if confirmed:
            SweepTask.objects.filter(id=sweep_id).update(status="CONFIRMED")
            logger.info(f"Sweep {sweep_id} confirmed | tx={tx_hash}")
        else:
            raise self.retry(countdown=60)
    except SweepTask.DoesNotExist:
        logger.error(f"SweepTask {sweep_id} not found")
