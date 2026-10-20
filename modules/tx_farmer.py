import random
import time
from eth_account import Account
from web3 import Web3
from modules.wallet import WalletManager
from modules.logger import log_info, log_success, log_warning, log_error
from config import (
    MIN_TX_AMOUNT_ETH,
    MAX_TX_AMOUNT_ETH,
    MIN_DELAY_BETWEEN_TX,
    MAX_DELAY_BETWEEN_TX,
    MINIMAL_CONTRACT_BYTECODE,
    MINIMAL_CONTRACT_ABI,
)

class TransactionFarmer:
    def __init__(self, wallet_manager: WalletManager):
        self.wm = wallet_manager
        self.w3 = wallet_manager.w3
        self.deployed_contract_address = None

    def random_sleep(self, min_s: int = MIN_DELAY_BETWEEN_TX, max_s: int = MAX_DELAY_BETWEEN_TX):
        sleep_time = random.randint(min_s, max_s)
        log_info(f"Sleeping for {sleep_time} seconds (anti-sybil delay)...")
        time.sleep(sleep_time)

    def get_random_amount_wei(self) -> int:
        amt = random.uniform(MIN_TX_AMOUNT_ETH, MAX_TX_AMOUNT_ETH)
        return self.w3.to_wei(amt, "ether")

    def execute_self_transfer(self) -> bool:
        """
        Sends a tiny amount of ETH back to self. 
        Zero capital loss, creates on-chain activity & streak for testnet airdrop criteria.
        """
        amount_wei = self.get_random_amount_wei()
        amount_eth = self.w3.from_wei(amount_wei, "ether")
        log_info(f"Farming Action: Self-Transfer {amount_eth:.8f} ETH to {self.wm.address}")

        tx = {
            "to": self.wm.address,
            "value": amount_wei,
            "data": b"",
        }
        success, tx_hash = self.wm.build_and_send_tx(tx)
        return success

    def execute_random_transfer(self) -> bool:
        """
        Sends micro-amount of ETH to a randomly generated EVM address to mimic realistic usage.
        """
        random_recipient = Account.create().address
        amount_wei = self.get_random_amount_wei()
        amount_eth = self.w3.from_wei(amount_wei, "ether")
        log_info(f"Farming Action: Random Transfer {amount_eth:.8f} ETH -> {random_recipient}")

        tx = {
            "to": random_recipient,
            "value": amount_wei,
            "data": b"",
        }
        success, tx_hash = self.wm.build_and_send_tx(tx)
        return success

    def execute_contract_deploy(self) -> bool:
        """
        Deploys a minimal smart contract on GIWA Sepolia.
        Helps qualify for 'Contract Deployer' or developer ecosystem rewards.
        """
        log_info("Farming Action: Deploying lightweight Smart Contract on GIWA Sepolia...")
        tx = {
            "to": "",  # Empty 'to' address triggers contract creation
            "value": 0,
            "data": MINIMAL_CONTRACT_BYTECODE,
        }
        success, tx_hash = self.wm.build_and_send_tx(tx)
        if success and tx_hash:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                self.deployed_contract_address = receipt.contractAddress
                log_success(f"Contract deployed at address: {self.deployed_contract_address}")
            except Exception:
                pass
        return success

    def execute_contract_interaction(self, contract_address: str = None) -> bool:
        """
        Interacts with a smart contract by calling increment() on it.
        """
        target = contract_address or self.deployed_contract_address
        if not target:
            log_warning("No deployed contract address found. Skipping interaction.")
            return False

        log_info(f"Farming Action: Interacting with contract at {target}...")
        try:
            checksum_addr = Web3.to_checksum_address(target)
            contract = self.w3.eth.contract(address=checksum_addr, abi=MINIMAL_CONTRACT_ABI)
            
            # increment() method calldata
            data = contract.encodeABI(fn_name="increment", args=[])
            tx = {
                "to": checksum_addr,
                "value": 0,
                "data": data,
            }
            success, tx_hash = self.wm.build_and_send_tx(tx)
            return success
        except Exception as e:
            log_error(f"Failed contract interaction: {e}")
            return False

    def execute_custom_interaction(self, target_address: str, calldata: str = "0x") -> bool:
        """
        Sends a transaction to a specific protocol contract (e.g. Aura Protocol contract).
        """
        log_info(f"Farming Action: Sending custom transaction to {target_address}")
        try:
            tx = {
                "to": Web3.to_checksum_address(target_address),
                "value": 0,
                "data": calldata,
            }
            success, tx_hash = self.wm.build_and_send_tx(tx)
            return success
        except Exception as e:
            log_error(f"Failed custom interaction: {e}")
            return False
