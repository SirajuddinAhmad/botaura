import time
from typing import Optional, Tuple
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests

from config import RPC_URL, CHAIN_ID, EXPLORER_URL
from modules.logger import log_info, log_error, log_warning, log_success

class WalletManager:
    def __init__(self, private_key: str, proxy: Optional[str] = None):
        self.raw_key = private_key.strip()
        if not self.raw_key.startswith("0x"):
            self.raw_key = "0x" + self.raw_key
        
        self.account = Account.from_key(self.raw_key)
        self.address = self.account.address
        self.proxy = proxy

        request_kwargs = {}
        if proxy:
            request_kwargs["proxies"] = {
                "http": proxy,
                "https": proxy
            }
        
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs=request_kwargs))
        # Support POA middleware if needed for testnets
        try:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception:
            pass

    def is_connected(self) -> bool:
        try:
            return self.w3.is_connected()
        except Exception as e:
            log_error(f"Failed to connect to GIWA Sepolia RPC: {e}")
            return False

    def get_balance(self) -> float:
        try:
            balance_wei = self.w3.eth.get_balance(self.address)
            return float(self.w3.from_wei(balance_wei, "ether"))
        except Exception as e:
            log_error(f"Error fetching balance for {self.address}: {e}")
            return 0.0

    def get_nonce(self) -> int:
        return self.w3.eth.get_transaction_count(self.address, "pending")

    def build_and_send_tx(self, tx_dict: dict) -> Tuple[bool, Optional[str]]:
        """
        Signs and broadcasts a transaction with automatic gas and nonce resolution.
        """
        try:
            if "nonce" not in tx_dict:
                tx_dict["nonce"] = self.get_nonce()
            if "chainId" not in tx_dict:
                tx_dict["chainId"] = CHAIN_ID

            # Auto gas estimation & pricing
            try:
                base_fee = self.w3.eth.get_block("latest").get("baseFeePerGas")
                if base_fee:
                    # EIP-1559 transaction
                    priority_fee = self.w3.eth.max_priority_fee
                    tx_dict["maxPriorityFeePerGas"] = priority_fee
                    tx_dict["maxFeePerGas"] = int(base_fee * 1.5) + priority_fee
                    tx_dict.pop("gasPrice", None)
                else:
                    tx_dict["gasPrice"] = int(self.w3.eth.gas_price * 1.15)
            except Exception:
                tx_dict["gasPrice"] = self.w3.eth.gas_price

            if "gas" not in tx_dict:
                try:
                    estimated_gas = self.w3.eth.estimate_gas(tx_dict)
                    tx_dict["gas"] = int(estimated_gas * 1.25)
                except Exception:
                    tx_dict["gas"] = 150000

            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_dict, private_key=self.raw_key)

            # Broadcast
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hex = tx_hash.hex()
            if not tx_hex.startswith("0x"):
                tx_hex = "0x" + tx_hex

            log_info(f"Transaction broadcasted: {EXPLORER_URL}/tx/{tx_hex}")

            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if receipt.status == 1:
                log_success(f"Transaction confirmed in block {receipt.blockNumber}!")
                return True, tx_hex
            else:
                log_error(f"Transaction reverted on-chain: {tx_hex}")
                return False, tx_hex

        except Exception as e:
            log_error(f"Transaction error: {e}")
            return False, None

    def sign_message(self, message_text: str) -> str:
        """
        Signs a standard Ethereum personal message (used for dApp/Aura authentication).
        """
        signable_message = encode_defunct(text=message_text)
        signed = self.account.sign_message(signable_message)
        return signed.signature.hex()
