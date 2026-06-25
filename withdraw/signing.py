"""
withdraw/signing.py

Signs and broadcasts one withdrawal transaction per network.
Private keys are derived from xprv at index 0 (platform hot wallet).

xprv values must be in settings:
    BTC_ACCOUNT_XPRV
    EVM_ACCOUNT_XPRV
    TRON_ACCOUNT_XPRV

SECURITY: these are private keys. They must never be logged, returned
in responses, or stored anywhere other than environment variables on
a machine with no public internet access to this module.
"""

import logging
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger("withdraw.signing")

# ── Key derivation ────────────────────────────────────────────────────────────

def _derive_private_key(xprv: str, coin_type, index: int = 0) -> bytes:
    from bip_utils import Bip44, Bip44Changes
    ctx = (
        Bip44.FromExtendedKey(xprv, coin_type)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
    )
    return ctx.PrivateKey().Raw().ToBytes()


def _evm_private_key(index: int = 0) -> str:
    from bip_utils import Bip44Coins
    raw = _derive_private_key(settings.EVM_ACCOUNT_XPRV, Bip44Coins.ETHEREUM, index)
    return "0x" + raw.hex()


def _btc_private_key_wif(index: int = 0) -> str:
    from bip_utils import Bip44Coins, Bip44
    from bip_utils import Bip44Changes
    ctx = (
        Bip44.FromExtendedKey(settings.BTC_ACCOUNT_XPRV, Bip44Coins.BITCOIN)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(index)
    )
    return ctx.PrivateKey().ToWif()


def _tron_private_key_hex(index: int = 0) -> str:
    from bip_utils import Bip44Coins
    raw = _derive_private_key(settings.TRON_ACCOUNT_XPRV, Bip44Coins.TRON, index)
    return raw.hex()


# ── EVM (ETH native + ERC20/BEP20 tokens) ────────────────────────────────────

ERC20_TRANSFER_ABI = [
    {
        "name": "transfer",
        "type": "function",
        "inputs": [
            {"name": "_to",    "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
    },
    {
        "name": "decimals",
        "type": "function",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
    },
]

_EVM_RPC = {
    "ETH": lambda: settings.ETH_RPC_URL,
    "BNB": lambda: settings.BSC_RPC_URL,
    "POL": lambda: settings.POLYGON_RPC_URL,
}


def broadcast_evm(network: str, to_address: str, amount: Decimal, contract: str = None) -> str:
    """Returns tx_hash on success, raises on failure."""
    from web3 import Web3

    w3  = Web3(Web3.HTTPProvider(_EVM_RPC[network]()))
    key = _evm_private_key()
    account = w3.eth.account.from_key(key)

    to  = w3.to_checksum_address(to_address)
    gas_price = w3.eth.gas_price
    nonce = w3.eth.get_transaction_count(account.address, "pending")

    if contract:
        # ERC20 / BEP20 token transfer
        token = w3.eth.contract(
            address=w3.to_checksum_address(contract),
            abi=ERC20_TRANSFER_ABI,
        )
        decimals  = token.functions.decimals().call()
        raw_amount = int(amount * Decimal(10 ** decimals))

        tx = token.functions.transfer(to, raw_amount).build_transaction({
            "from":     account.address,
            "nonce":    nonce,
            "gasPrice": gas_price,
            "gas":      100_000,
            "chainId":  w3.eth.chain_id,
        })
    else:
        # native coin (ETH / BNB / POL)
        wei = int(amount * Decimal("1e18"))
        tx  = {
            "from":     account.address,
            "to":       to,
            "value":    wei,
            "nonce":    nonce,
            "gasPrice": gas_price,
            "gas":      21_000,
            "chainId":  w3.eth.chain_id,
        }

    signed = w3.eth.account.sign_transaction(tx, key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()


# ── TRON (TRX native + TRC20) ─────────────────────────────────────────────────

def broadcast_tron(to_address: str, amount: Decimal, contract: str = None) -> str:
    """Returns tx_hash on success, raises on failure."""
    from tronpy import Tron
    from tronpy.keys import PrivateKey
    from tronpy.providers import HTTPProvider

    client  = Tron(HTTPProvider(api_key=settings.TRONGRID_API_KEY))
    priv    = PrivateKey(bytes.fromhex(_tron_private_key_hex()))
    sender  = priv.public_key.to_base58check_address()

    if contract:
        # TRC20 token
        token      = client.get_contract(contract)
        decimals   = token.functions.decimals()
        raw_amount = int(amount * Decimal(10 ** decimals))
        txn = (
            token.functions.transfer(to_address, raw_amount)
            .with_owner(sender)
            .fee_limit(30_000_000)  # 30 TRX max fee
            .build()
            .sign(priv)
        )
    else:
        # native TRX  (1 TRX = 1_000_000 sun)
        sun = int(amount * Decimal("1000000"))
        txn = (
            client.trx.transfer(sender, to_address, sun)
            .build()
            .sign(priv)
        )

    result = txn.broadcast().wait()
    return result["id"]


# ── Bitcoin ───────────────────────────────────────────────────────────────────

def broadcast_btc(to_address: str, amount: Decimal) -> str:
    """
    Returns tx_hash on success, raises on failure.
    Uses blockcypher to build, sign (via WIF key), and broadcast.
    pip install blockcypher
    """
    import blockcypher

    wif        = _btc_private_key_wif()
    satoshis   = int(amount * Decimal("1e8"))

    # derive the from-address from the same WIF so blockcypher knows the UTXO source
    from bip_utils import Bip44, Bip44Coins, Bip44Changes
    from_address = (
        Bip44.FromExtendedKey(settings.BTC_ACCOUNT_XPRV, Bip44Coins.BITCOIN)  # xprv accepted here
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
        .PublicKey()
        .ToAddress()
    )

    tx_hash = blockcypher.simple_spend(
        from_privkey=wif,
        to_address=to_address,
        to_satoshis=satoshis,
        coin_symbol="btc",           # use "btc-testnet" while testing
        api_key=settings.BLOCKCYPHER_API_KEY,
    )
    return tx_hash


# ── Router ────────────────────────────────────────────────────────────────────

def broadcast(network: str, to_address: str, amount: Decimal, contract: str = None) -> str:
    """
    Single entry point. Returns tx_hash on success, raises on any failure.
    network: "ETH" | "BNB" | "POL" | "TRX" | "BTC"
    """
    if network == "BTC":
        return broadcast_btc(to_address, amount)

    if network == "TRX":
        return broadcast_tron(to_address, amount, contract)

    if network in ("ETH", "BNB", "POL"):
        return broadcast_evm(network, to_address, amount, contract)

    raise ValueError(f"Unsupported network for broadcast: {network}")