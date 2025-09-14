PQC Microservice – Python Backend with Hardhat (Ethereum Integration)
======================================================================

This project includes a Python-based backend microservice that integrates post-quantum cryptography (PQC) with blockchain using Hardhat on Ethereum.

Prerequisites
-------------
Ensure the following tools are installed on your system:

- Python 3.9+
- Node.js (v18+ recommended)
- npm or yarn
- Hardhat (npm install --save-dev hardhat)
- Docker (optional)
- IPFS CLI (optional, for local decentralized storage)

Python Dependencies
-------------------
Use a virtual environment:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Expected packages (examples):
- Flask / FastAPI
- pycryptodome (for AES)
- requests
- ipfshttpclient
- web3 (for Ethereum/Smart Contract interaction)

Project Structure
-----------------

```
project-root/
│
├── backend/
│   ├── main.py                 # Python FastAPI or Flask server
│   ├── encryption.py           # AES + Kyber logic
│   ├── ipfs_handler.py         # IPFS upload/download logic
│   └── web3_handler.py         # Smart contract interaction
│
├── hardhat/
│   ├── contracts/
│   │   └── PQCStorage.sol      # Solidity contract for metadata storage
│   ├── scripts/
│   │   └── deploy.js
│   ├── hardhat.config.js
│   └── .env                    # Infura URL, private keys, etc.
│
├── Dockerfile
│                
│
└── requirements.txt
```

How to Run
----------

### 1. Start Python Backend

```
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Deploy Smart Contract

```
cd hardhat
npx hardhat compile
npx hardhat run scripts/deploy.js --network <your-network>
```

Update `.env` with private key and provider (Infura, Alchemy, etc.)

### 3. API Usage

- **POST /encrypt**
  - Encrypts data, stores AES key with Kyber, uploads ciphertext to IPFS
- **POST /decrypt**
  - Retrieves and decrypts data

### 4. Docker (Optional)
Build and run:

```
docker build -t pqc-python-backend .
docker run -p 8000:8000 pqc-python-backend
```

### 5. Easy Installation

- If you dont want to install everything seperatly then navigate to POC Frontend github link and clone the project
- https://github.com/atharvagithub/PQC_Frontend
- First run the frontend by enterring command "npm start"
- Second start the docker file by the command "docker compose up -d"

License
-------
MIT License – For research and educational use only.
