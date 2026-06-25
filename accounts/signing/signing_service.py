# accounts/signing/signing_service.py
"""
Signing Service — malov
Derives private keys from xprvs and signs sweep transactions.

⚠️  xprvs must be in environment variables on the SIGNING SERVER only.
     Never on the internet-facing Django web server.

In production: move this to a separate FastAPI service with no public ingress.
For development: runs inline (xprvs must be set in .env).
"""

import hashlib
import hmac
import logging
import os

from bip_utils import Bip44, Bip44Coins, Bip44Changes

logger = logging.getLogger(__name__)

_HMAC_SECRET = os.environ.get("APPROVAL_HMAC_SECRET", "").encode()


def generate_approval_token(sweep_id: str) -> str:
    return hmac.new(_HMAC_SECRET, sweep_id.encode(), hashlib.sha256).hexdigest()


def validate_approval_token(sweep_id: str, token: str) -> bool:
    expected = hmac.new(_HMAC_SECRET, sweep_id.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)


def get_evm_privkey_hex(index: int) -> str:
    xprv = os.environ["EVM_ACCOUNT_XPRV"]
    ctx  = (
        Bip44.FromExtendedKey(xprv, Bip44Coins.ETHEREUM)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
    )
    return "0x" + ctx.PrivateKey().Raw().ToHex()


def get_btc_privkey_wif(index: int) -> str:
    xprv = os.environ["BTC_ACCOUNT_XPRV"]
    ctx  = (
        Bip44.FromExtendedKey(xprv, Bip44Coins.BITCOIN)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
    )
    return ctx.PrivateKey().ToWif()


def get_tron_privkey_hex(index: int) -> str:
    xprv = os.environ["TRON_ACCOUNT_XPRV"]
    ctx  = (
        Bip44.FromExtendedKey(xprv, Bip44Coins.TRON)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
    )
    return ctx.PrivateKey().Raw().ToHex()


def sign_evm_sweep(*, sweep_id, approval_token, derivation_index,
                   to_address, amount_wei, gas_price_wei, gas_limit, nonce, chain_id):
    if not validate_approval_token(sweep_id, approval_token):
        raise PermissionError(f"Invalid approval token for sweep {sweep_id}")

    from eth_account import Account
    privkey   = get_evm_privkey_hex(derivation_index)
    signed    = Account.sign_transaction({
        "to":       to_address,
        "value":    amount_wei,
        "gas":      gas_limit,
        "gasPrice": gas_price_wei,
        "nonce":    nonce,
        "chainId":  chain_id,
    }, private_key=privkey)
    del privkey
    return signed.rawTransaction.hex()


def sign_tron_sweep(*, sweep_id, approval_token, derivation_index,
                    from_address, to_address, amount_sun, transaction_dict=None):
    if not validate_approval_token(sweep_id, approval_token):
        raise PermissionError(f"Invalid approval token for sweep {sweep_id}")

    from tronpy.keys import PrivateKey
    privkey_hex = get_tron_privkey_hex(derivation_index)
    priv        = PrivateKey(bytes.fromhex(privkey_hex))
    if transaction_dict:
        sig = priv.sign_msg_bytes(bytes.fromhex(transaction_dict["txID"]))
        transaction_dict["signature"] = [sig.hex()]
        del privkey_hex, priv
        return transaction_dict
    del privkey_hex, priv
    return {}
