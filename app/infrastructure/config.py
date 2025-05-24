import os
import json
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv

# Load .env environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
BLOCKCHAIN_PROVIDER = os.getenv('BLOCKCHAIN_PROVIDER', 'http://127.0.0.1:8545')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

# File paths for ABI and contract address
ABI_PATH = BASE_DIR / 'blockchain' / 'abi.json'
ADDRESS_PATH = BASE_DIR / 'blockchain' / 'address.txt'


def get_web3():
    """Initialize Web3"""
    return Web3(Web3.HTTPProvider(BLOCKCHAIN_PROVIDER))


def load_contract_abi():
    """Load ABI from JSON file"""
    try:
        with open(ABI_PATH) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading ABI: {e}")
        raise


def load_contract_address():
    """Load contract address from file"""
    try:
        with open(ADDRESS_PATH) as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading contract address: {e}")
        raise


def get_contract():
    """Return contract instance and Web3 connection"""
    web3 = get_web3()

    if not web3.is_connected():
        raise ConnectionError("Web3 is not connected to the blockchain")

    abi = load_contract_abi()
    contract_address = Web3.to_checksum_address(load_contract_address())

    contract = web3.eth.contract(address=contract_address, abi=abi)
    return contract, web3
