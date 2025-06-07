import hashlib
from web3 import Web3
from web3.exceptions import ContractLogicError
from .config import get_contract, get_web3, PRIVATE_KEY
from fastapi import Request
from app.infrastructure.session_manager import get_private_key_from_cookie


class blockchain_connector:
#    def __init__(self):
#        self.contract, self.web3 = get_contract()
#
#        if PRIVATE_KEY:
#            self.account = self.web3.eth.account.from_key(PRIVATE_KEY)
#            print(f"Using account: {self.account.address}")
#        else:
#            self.account = None
#            print("Warning: No private key provided. Only read operations will work.") 
            
    def __init__(self, request: Request):
        self.contract, self.web3 = get_contract()
        self.private_key = get_private_key_from_cookie(request)
        if not self.private_key:
            raise ValueError("You must be logged in to perform this action")
        self.account = self.web3.eth.account.from_key(self.private_key)
        print(f"[AUTH] Acting as {self.account.address}")    

    def _build_txn(self, function):
        if not self.account:
            raise ValueError("Private key not set")

        nonce = self.web3.eth.get_transaction_count(self.account.address)

        txn = function.build_transaction({
            'from': self.account.address,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': self.web3.to_wei('50', 'gwei')
        })

        return txn

    def _sign_and_send_txn(self, txn):
        signed_txn = self.web3.eth.account.sign_transaction(txn, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def generate_data_id(self, original_file, timestamp):
        combined = f"{original_file}_{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def store_encrypted_data(self, data_id, cid_hash, aes_iv, aes_tag, kem_cyphertext):
        try:
            store_fn = self.contract.functions.storeData(
                data_id, cid_hash, aes_iv, aes_tag, kem_cyphertext
            )

            txn = self._build_txn(store_fn)
            return self._sign_and_send_txn(txn)

        except Exception as e:
            print(f"Store error: {e}")
            raise

    def retrieve_encrypted_data(self, data_id):
        try:
            data_id = data_id.strip()
            return self.contract.functions.retrieveData(data_id).call({'from': self.account.address})
        except Exception as e:
            print(f"Retrieve error: {e}")
            raise

    def update_data(self, data_id, cid_hash, aes_iv, aes_tag, kem_cyphertext):
        try:
            update_fn = self.contract.functions.updateData(data_id, cid_hash, aes_iv, aes_tag, kem_cyphertext)
            txn = self._build_txn(update_fn)
            return self._sign_and_send_txn(txn)
        except Exception as e:
            print(f"Update error: {e}")
            raise

    def grant_access(self, data_id, grantee_address):
        try:
            grantee_address = self.web3.to_checksum_address(grantee_address)
            txn = self._build_txn(self.contract.functions.grantAccess(data_id, grantee_address))
            return self._sign_and_send_txn(txn)
        except Exception as e:
            print(f"Grant error: {e}")
            raise

    def revoke_access(self, data_id, revokee_address):
        try:
            revokee_address = self.web3.to_checksum_address(revokee_address)
            txn = self._build_txn(self.contract.functions.revokeAccess(data_id, revokee_address))
            return self._sign_and_send_txn(txn)
        except Exception as e:
            print(f"Revoke error: {e}")
            raise

    def check_access(self, data_id, address):
        try:
            return self.contract.functions.checkAccess(data_id, self.web3.to_checksum_address(address)).call()
        except Exception as e:
            print(f"Access check error: {e}")
            raise

    def get_all_data_ids(self):
        return self.contract.functions.getAllDataIds().call()

    def get_my_data_ids(self):
        return self.contract.functions.getMyDataIds().call({'from': self.account.address})

    def get_owner_of_data(self, data_id):
        try:
            _, _, _, _, _, owner = self.contract.functions.retrieveData(data_id).call({'from': self.account.address})
            print(f"[DEBUG] Stored owner: {owner}")
            print(f"[DEBUG] Your caller address: {self.account.address}")
            return owner
        except Exception as e:
            print(f"[DEBUG] Owner check failed: {e}")
            raise
