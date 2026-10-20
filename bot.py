import os
import sys
import time
import random
from typing import List

from config import (
    RPC_URL,
    CHAIN_ID,
    TX_PER_WALLET,
    MIN_DELAY_BETWEEN_WALLET,
    MAX_DELAY_BETWEEN_WALLET,
    AUTO_LOOP,
    LOOP_INTERVAL_HOURS,
)
from modules.logger import (
    print_banner,
    log_info,
    log_success,
    log_warning,
    log_error,
    log_wallet,
)
from modules.wallet import WalletManager
from modules.tx_farmer import TransactionFarmer
from modules.aura_api import AuraProtocolClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_KEYS_FILE = os.path.join(BASE_DIR, "private_keys.txt")
PROXIES_FILE = os.path.join(BASE_DIR, "proxies.txt")

def load_file_lines(filepath: str) -> List[str]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return lines

def ensure_private_keys() -> List[str]:
    keys = load_file_lines(PRIVATE_KEYS_FILE)
    if not keys:
        env_key = os.getenv("PRIVATE_KEY")
        if env_key:
            keys = [env_key.strip()]
    return keys

def run_wallet_tasks(
    index: int,
    total: int,
    private_key: str,
    proxy: str = None,
    mode: int = 1,
    tx_count: int = TX_PER_WALLET,
):
    wm = WalletManager(private_key=private_key, proxy=proxy)
    log_wallet(index, total, wm.address)

    if not wm.is_connected():
        log_error("Could not connect to GIWA Sepolia network. Skipping wallet.")
        return

    balance = wm.get_balance()
    log_info(f"Current ETH Balance: {balance:.6f} ETH")

    if balance < 0.0001:
        log_warning(
            f"Balance is very low ({balance:.6f} ETH). Please claim GIWA Sepolia testnet ETH from faucet!"
        )
        if balance == 0:
            log_error("Skipping on-chain transactions due to zero balance.")
            return

    farmer = TransactionFarmer(wm)
    aura_client = AuraProtocolClient(wm)

    # 1. Aura Protocol Check-in / Missions
    if mode in (1, 4):
        log_info("--- Step 1: Aura Protocol Incentives ---")
        aura_client.authenticate_wallet()
        aura_client.claim_daily_checkin()
        farmer.random_sleep(3, 7)

    # 2. Smart Contract Deployment & Interaction
    if mode in (1, 3):
        log_info("--- Step 2: Contract Deployment & Interaction ---")
        deploy_ok = farmer.execute_contract_deploy()
        if deploy_ok:
            farmer.random_sleep(5, 12)
            farmer.execute_contract_interaction()
            farmer.random_sleep(5, 12)

    # 3. Daily Transactions Farming (Self & Random Transfers)
    if mode in (1, 2):
        log_info(f"--- Step 3: Generating {tx_count} On-Chain Transactions ---")
        for i in range(1, tx_count + 1):
            log_info(f"Transaction {i}/{tx_count}...")
            # 70% self transfer (safe, no loss), 30% random address transfer
            if random.random() < 0.7:
                farmer.execute_self_transfer()
            else:
                farmer.execute_random_transfer()

            if i < tx_count:
                farmer.random_sleep()

    final_balance = wm.get_balance()
    log_success(f"Finished wallet {wm.address[:8]}... Remaining Balance: {final_balance:.6f} ETH")

def check_all_balances(keys: List[str]):
    print("\n" + "=" * 65)
    print(f"{'No.':<4} | {'Wallet Address':<42} | {'Balance (ETH)':<12}")
    print("=" * 65)
    total_eth = 0.0
    for idx, pk in enumerate(keys, start=1):
        try:
            wm = WalletManager(private_key=pk)
            bal = wm.get_balance()
            total_eth += bal
            print(f"{idx:<4} | {wm.address:<42} | {bal:<12.6f}")
        except Exception as e:
            print(f"{idx:<4} | Error loading key: {e}")
    print("=" * 65)
    print(f"Total Wallets: {len(keys)} | Total ETH: {total_eth:.6f} ETH\n")

def run_round(keys: List[str], proxies: List[str], mode: int, tx_count: int):
    total = len(keys)
    log_info(f"Starting farming round for {total} wallet(s)...")

    for idx, key in enumerate(keys, start=1):
        proxy = proxies[(idx - 1) % len(proxies)] if proxies else None
        run_wallet_tasks(
            index=idx,
            total=total,
            private_key=key,
            proxy=proxy,
            mode=mode,
            tx_count=tx_count,
        )

        if idx < total:
            delay = random.randint(MIN_DELAY_BETWEEN_WALLET, MAX_DELAY_BETWEEN_WALLET)
            log_info(f"Waiting {delay} seconds before switching to the next wallet (Anti-Sybil)...")
            time.sleep(delay)

    log_success("All wallets have completed the current round!")

def main():
    print_banner()

    keys = ensure_private_keys()
    if not keys:
        log_error(f"File 'private_keys.txt' is empty or missing!")
        log_info(f"Silakan buat file '{PRIVATE_KEYS_FILE}' dan masukkan private key Anda (satu per baris).")
        log_info("Atau salin dari 'private_keys.example.txt'.")
        return

    proxies = load_file_lines(PROXIES_FILE)
    log_info(f"Loaded {len(keys)} private key(s).")
    if proxies:
        log_info(f"Loaded {len(proxies)} proxy/proxies.")
    else:
        log_info("No proxies provided (direct connection mode).")

    print("\nPilih Mode Operasi:")
    print("1. [FULL AUTO] Aura Check-in + Deploy Kontrak + Daily Transaksi")
    print("2. [TX ONLY] Farming Transaksi Harian (Self Transfer & Random Transfer)")
    print("3. [DEPLOY ONLY] Deploy Kontrak & Interaksi Kontrak")
    print("4. [CHECK-IN ONLY] Klaim Aura Protocol Daily Incentives Saja")
    print("5. [CHECK BALANCES] Cek Saldo Semua Wallet")
    print("6. [EXIT] Keluar")

    choice = input("\nMasukkan pilihan (1-6) [default: 1]: ").strip()
    if not choice:
        choice = "1"

    if choice == "6":
        log_info("Exiting bot. Sampai jumpa!")
        return

    if choice == "5":
        check_all_balances(keys)
        return

    try:
        mode = int(choice)
        if mode not in (1, 2, 3, 4):
            mode = 1
    except ValueError:
        mode = 1

    tx_count_input = input(f"Jumlah transaksi per wallet per putaran [default: {TX_PER_WALLET}]: ").strip()
    tx_count = int(tx_count_input) if tx_count_input.isdigit() else TX_PER_WALLET

    loop_input = input("Jalankan otomatis secara berulang (24 Jam loop)? (y/n) [default: n]: ").strip().lower()
    is_loop = loop_input in ("y", "yes", "true", "1") or AUTO_LOOP

    if is_loop:
        log_info(f"Auto-loop mode AKTIF. Interval: {LOOP_INTERVAL_HOURS} jam.")
        round_num = 1
        while True:
            log_info(f"=== Memulai Putaran #{round_num} ===")
            run_round(keys, proxies, mode, tx_count)
            sleep_sec = int(LOOP_INTERVAL_HOURS * 3600)
            log_info(f"Putaran #{round_num} selesai. Tidur selama {LOOP_INTERVAL_HOURS} jam ({sleep_sec} detik)...")
            round_num += 1
            time.sleep(sleep_sec)
    else:
        run_round(keys, proxies, mode, tx_count)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Dihentikan oleh pengguna. Keluar...")
        sys.exit(0)
