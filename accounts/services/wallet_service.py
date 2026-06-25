# accounts/services/wallet_service.py
"""
Address derivation from xpubs — NO private keys.
Supports: BTC, ETH/BNB/POL (EVM), TRON
USDT on all networks: same address as base network, detected at deposit time.
"""

from django.conf import settings
from bip_utils import Bip44, Bip44Coins, Bip44Changes
import logging

logger = logging.getLogger(__name__)

BTC_XPUB  = settings.BTC_ACCOUNT_XPUB
EVM_XPUB  = settings.EVM_ACCOUNT_XPUB
TRON_XPUB = settings.TRON_ACCOUNT_XPUB

assert BTC_XPUB  != EVM_XPUB,   "BTC and EVM xpubs identical — check .env"
assert EVM_XPUB  != TRON_XPUB,  "EVM and TRON xpubs identical — check .env"


def _derive(xpub: str, coin: Bip44Coins, index: int) -> str:
    return (
        Bip44.FromExtendedKey(xpub, coin)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
        .PublicKey()
        .ToAddress()
    )


def derive_btc_address(index: int) -> str:
    return _derive(BTC_XPUB, Bip44Coins.BITCOIN, index)


def derive_evm_address(index: int) -> str:
    """Same address for ETH, BNB, Polygon and USDT on those chains."""
    return _derive(EVM_XPUB, Bip44Coins.ETHEREUM, index)


def derive_tron_address(index: int) -> str:
    """Same address for TRON and USDT-TRC20."""
    return _derive(TRON_XPUB, Bip44Coins.TRON, index)
