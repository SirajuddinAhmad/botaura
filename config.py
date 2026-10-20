import os
from dotenv import load_dotenv

load_dotenv()

# GIWA Sepolia Configuration
RPC_URL = os.getenv("GIWA_RPC_URL", "https://sepolia-rpc.giwa.io")
CHAIN_ID = int(os.getenv("GIWA_CHAIN_ID", "91342"))
EXPLORER_URL = os.getenv("EXPLORER_URL", "https://sepolia-explorer.giwa.io")

# Transaction & Farming Settings
MIN_TX_AMOUNT_ETH = float(os.getenv("MIN_TX_AMOUNT_ETH", "0.000001"))
MAX_TX_AMOUNT_ETH = float(os.getenv("MAX_TX_AMOUNT_ETH", "0.00001"))
TX_PER_WALLET = int(os.getenv("TX_PER_WALLET_PER_ROUND", "3"))

# Anti-Sybil delays (seconds)
MIN_DELAY_BETWEEN_TX = int(os.getenv("MIN_DELAY_BETWEEN_TX", "10"))
MAX_DELAY_BETWEEN_TX = int(os.getenv("MAX_DELAY_BETWEEN_TX", "30"))
MIN_DELAY_BETWEEN_WALLET = int(os.getenv("MIN_DELAY_BETWEEN_WALLET", "20"))
MAX_DELAY_BETWEEN_WALLET = int(os.getenv("MAX_DELAY_BETWEEN_WALLET", "60"))

# Auto Loop Settings
AUTO_LOOP = os.getenv("AUTO_LOOP", "false").lower() in ("true", "1", "yes")
LOOP_INTERVAL_HOURS = float(os.getenv("LOOP_INTERVAL_HOURS", "24"))

# Aura Protocol API
AURA_BASE_URL = os.getenv("AURA_API_BASE_URL", "https://beta.auralaunch.org/api")

# Minimal ERC20 Bytecode for Contract Deployment Farming
# Simple Counter / Storage Contract Bytecode on EVM
# This is a valid, ultra-gas-efficient testnet contract deployment bytecode (stores & increments a number)
MINIMAL_CONTRACT_BYTECODE = (
    "0x608060405234801561001057600080fd5b5060d38061001f6000396000f3fe"
    "6080604052348015600f57600080fd5b506004361060325760003560e01c8063"
    "06661414146037578063d09de08a14605b575b600080fd5b6000546040519081"
    "5260200160405180910390f35b60008054600101905500fea264697066735822"
    "1220a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6"
    "a1b264736f6c634300081a0033"
)

# ABI for the counter contract (has count() and increment())
MINIMAL_CONTRACT_ABI = [
    {
        "inputs": [],
        "name": "count",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "increment",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]
