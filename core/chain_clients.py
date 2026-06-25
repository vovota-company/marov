"""
core/chain_clients.py

One function per chain that returns the REAL on-chain balance for an
address. Used by the platform-wallet balance-sync task AND by the
deposit-detection helpers.

All amounts returned as Python Decimal, in the coin's standard unit
(BTC not satoshis, ETH not wei, TRX not sun, token amounts in token units).
"""

from decimal import Decimal
from django.conf import settings


# ── EVM (ETH / BSC / Polygon) ────────────────────────────────────────────────

def _evm_w3(network: str):
    from web3 import Web3
    rpc = {
        "ETH":     settings.ETH_RPC_URL,      # e.g. https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
        "BNB":     settings.BSC_RPC_URL,      # e.g. https://bsc-dataseed.binance.org/
        "POL":     settings.POLYGON_RPC_URL,  # e.g. https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
    }
    return Web3(Web3.HTTPProvider(rpc[network]))


ERC20_ABI = [
    {
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
]


def get_evm_native_balance(address: str, network: str) -> Decimal:
    w3 = _evm_w3(network)
    wei = w3.eth.get_balance(w3.to_checksum_address(address))
    return Decimal(wei) / Decimal("1e18")


def get_evm_token_balance(address: str, contract: str, network: str) -> Decimal:
    w3 = _evm_w3(network)
    token = w3.eth.contract(
        address=w3.to_checksum_address(contract),
        abi=ERC20_ABI,
    )
    raw      = token.functions.balanceOf(w3.to_checksum_address(address)).call()
    decimals = token.functions.decimals().call()
    return Decimal(raw) / Decimal(10 ** decimals)


# ── TRON (TRX + TRC20) ───────────────────────────────────────────────────────

def _tron_client():
    from tronpy import Tron
    from tronpy.providers import HTTPProvider
    return Tron(HTTPProvider(api_key=settings.TRONGRID_API_KEY))


def get_tron_native_balance(address: str) -> Decimal:
    client = _tron_client()
    sun = client.get_account_balance(address)  # returns Decimal in TRX already
    return Decimal(str(sun))


def get_trc20_balance(address: str, contract: str) -> Decimal:
    client = _tron_client()
    token = client.get_contract(contract)
    raw      = token.functions.balanceOf(address)
    decimals = token.functions.decimals()
    return Decimal(raw) / Decimal(10 ** decimals)


# ── Bitcoin ───────────────────────────────────────────────────────────────────

def get_btc_balance(address: str) -> Decimal:
    import blockcypher
    data = blockcypher.get_address_details(
        address,
        coin_symbol="btc",
        api_key=settings.BLOCKCYPHER_API_KEY,
    )
    # final_balance = confirmed + unconfirmed; balance = confirmed only
    sats = data.get("final_balance", 0)
    return Decimal(sats) / Decimal("1e8")


# ── Router ────────────────────────────────────────────────────────────────────

def get_onchain_balance(network: str, address: str, contract: str = None) -> Decimal:
    """
    Single entry point — call this with a Coin's fields and get back
    the real on-chain balance as a Decimal.

    network:  matches Coin.network  ("ETH", "BNB", "POL", "TRX", "BTC")
    contract: Coin.contract — None for native coins, address string for tokens
    """
    if network == "BTC":
        return get_btc_balance(address)

    if network == "TRX":
        if contract:
            return get_trc20_balance(address, contract)
        return get_tron_native_balance(address)

    if network in ("ETH", "BNB", "POL"):
        if contract:
            return get_evm_token_balance(address, contract, network)
        return get_evm_native_balance(address, network)

    raise ValueError(f"Unknown network: {network}")