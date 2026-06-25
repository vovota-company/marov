# core/address_router.py
from django.conf import settings
from bip_utils import Bip44, Bip44Coins, Bip44Changes

_COIN_TO_BIP44 = {
    "BTC":  Bip44Coins.BITCOIN,
    "ETH":  Bip44Coins.ETHEREUM,
    "BNB":  Bip44Coins.ETHEREUM,
    "POL":  Bip44Coins.ETHEREUM,
    "TRON": Bip44Coins.TRON,
}

_XPUBS = {
    "BTC":  lambda: settings.BTC_ACCOUNT_XPUB,
    "ETH":  lambda: settings.EVM_ACCOUNT_XPUB,
    "BNB":  lambda: settings.EVM_ACCOUNT_XPUB,
    "POL":  lambda: settings.EVM_ACCOUNT_XPUB,
    "TRON": lambda: settings.TRON_ACCOUNT_XPUB,
}


def derive_deposit_address(network: str, index: int) -> str:
    """
    Derives a deposit address for a user at the given index.
    Used by the signal and any manual re-derivation.
    USDT shares the same address as the base network.
    """
    if network not in _XPUBS:
        raise ValueError(f"No xpub configured for network: {network}")
    coin_type = _COIN_TO_BIP44[network]
    xpub      = _XPUBS[network]()
    return (
        Bip44.FromExtendedKey(xpub, coin_type)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
        .PublicKey()
        .ToAddress()
    )
