"""
generate_offline.py  —  malov HD Wallet Master Key Generator
═══════════════════════════════════════════════════════════════
Run OFFLINE on an air-gapped machine. Wipe immediately after.

Produces:
  account_xpubs.PUBLIC.json     → copy to server
  central_wallets.PUBLIC.json   → copy to server (addresses only)
  master_secrets.PRIVATE.json   → cold storage ONLY

Networks: BTC, ETH/EVM (ETH+BNB+POL), TRON
Tokens:   USDT on all above — same addresses, detected at deposit time
Removed:  Solana, Stellar, XRP (not in scope)

Requirements: pip install bip_utils
"""

import json
from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39WordsNum,
    Bip39SeedGenerator,
    Bip39MnemonicValidator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)

# ── Config ─────────────────────────────────────────────────────────────────────
PASSPHRASE    = "vovota_wakanda_dullah4?"
CENTRAL_INDEX = 9_999_999   # reserved for central/hot wallet

# ── 1. Mnemonic + seed ─────────────────────────────────────────────────────────
mnemonic     = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_24)
mnemonic_str = str(mnemonic)

print("=" * 70)
print("MNEMONIC — write on paper/metal NOW, never store digitally:")
print(mnemonic_str)
print("=" * 70)

Bip39MnemonicValidator().Validate(mnemonic)
seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase=PASSPHRASE)
seed_hex   = seed_bytes.hex()
print(f"Seed hex length: {len(seed_hex)} chars (128 expected)")
assert len(seed_hex) == 128, "Bad seed length"

# ── 2. Account-level keys  m/44'/coin'/0'  ─────────────────────────────────────
# FIX: Bip44 has no .Depth() method — removed that assertion.
# We verify correctness by asserting xpubs are distinct instead.

def account_ctx(coin: Bip44Coins):
    return Bip44.FromSeed(seed_bytes, coin).Purpose().Coin().Account(0)

btc_acct  = account_ctx(Bip44Coins.BITCOIN)
eth_acct  = account_ctx(Bip44Coins.ETHEREUM)   # ETH + BNB + POL share this
tron_acct = account_ctx(Bip44Coins.TRON)

btc_xpub  = btc_acct.PublicKey().ToExtended()
btc_xprv  = btc_acct.PrivateKey().ToExtended()

eth_xpub  = eth_acct.PublicKey().ToExtended()
eth_xprv  = eth_acct.PrivateKey().ToExtended()

tron_xpub = tron_acct.PublicKey().ToExtended()
tron_xprv = tron_acct.PrivateKey().ToExtended()

# Verify all xpubs are distinct — catches misconfiguration immediately
assert btc_xpub != eth_xpub,   "BTC and EVM xpubs identical — abort!"
assert btc_xpub != tron_xpub,  "BTC and TRON xpubs identical — abort!"
assert eth_xpub != tron_xpub,  "EVM and TRON xpubs identical — abort!"
print("\n✅  All three xpubs are distinct.")

print(f"\nBTC  xpub: {btc_xpub}")
print(f"EVM  xpub: {eth_xpub}")
print(f"TRON xpub: {tron_xpub}")

# ── 3. Central wallet  m/44'/coin'/0'/0/CENTRAL_INDEX  ─────────────────────────
def central_key(coin: Bip44Coins):
    return (
        Bip44.FromSeed(seed_bytes, coin)
        .Purpose().Coin().Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(CENTRAL_INDEX)
    )

btc_c  = central_key(Bip44Coins.BITCOIN)
eth_c  = central_key(Bip44Coins.ETHEREUM)
tron_c = central_key(Bip44Coins.TRON)

central_wallets = {
    "derivation_index": CENTRAL_INDEX,
    "note": "Addresses receive swept funds. Private keys in master_secrets.PRIVATE.json",
    "BTC": {
        "address":     btc_c.PublicKey().ToAddress(),
        "privkey_wif": btc_c.PrivateKey().ToWif(),
    },
    "EVM": {
        "address":     eth_c.PublicKey().ToAddress(),
        "privkey_hex": "0x" + eth_c.PrivateKey().Raw().ToHex(),
    },
    "TRON": {
        "address":     tron_c.PublicKey().ToAddress(),
        "privkey_hex": tron_c.PrivateKey().Raw().ToHex(),
    },
}

print(f"\nCentral BTC  address : {central_wallets['BTC']['address']}")
print(f"Central EVM  address : {central_wallets['EVM']['address']}")
print(f"Central TRON address : {central_wallets['TRON']['address']}")

# ── 4. Quick smoke-test: derive index 1 from each xpub ─────────────────────────
def _test_derive(xpub, coin):
    return (
        Bip44.FromExtendedKey(xpub, coin)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(1)
        .PublicKey()
        .ToAddress()
    )

print("\nSmoke-test derivation (index 1):")
print(f"  BTC  : {_test_derive(btc_xpub,  Bip44Coins.BITCOIN)}")
print(f"  EVM  : {_test_derive(eth_xpub,  Bip44Coins.ETHEREUM)}")
print(f"  TRON : {_test_derive(tron_xpub, Bip44Coins.TRON)}")

# ── 5. Write files ──────────────────────────────────────────────────────────────

# PUBLIC — safe to copy to server
with open("account_xpubs.PUBLIC.json", "w") as f:
    json.dump({"btc": btc_xpub, "evm": eth_xpub, "tron": tron_xpub}, f, indent=2)

with open("central_wallets.PUBLIC.json", "w") as f:
    json.dump({
        "BTC":  {"address": central_wallets["BTC"]["address"]},
        "EVM":  {"address": central_wallets["EVM"]["address"]},
        "TRON": {"address": central_wallets["TRON"]["address"]},
    }, f, indent=2)

# PRIVATE — cold storage ONLY
with open("master_secrets.PRIVATE.json", "w") as f:
    json.dump({
        "mnemonic":        mnemonic_str,
        "passphrase":      PASSPHRASE,
        "seed_hex":        seed_hex,
        "btc_xprv":        btc_xprv,
        "evm_xprv":        eth_xprv,
        "tron_xprv":       tron_xprv,
        "central_wallets": central_wallets,
    }, f, indent=2)

print("\n" + "=" * 70)
print("Files written:")
print("  account_xpubs.PUBLIC.json    → copy to server")
print("  central_wallets.PUBLIC.json  → copy to server (addresses only)")
print("  master_secrets.PRIVATE.json  → COLD STORAGE ONLY — never online")
print("=" * 70)
