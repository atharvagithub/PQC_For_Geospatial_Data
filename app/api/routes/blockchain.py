from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import os
import json
import time

from app.infrastructure.blockchain_connector import blockchain_connector


class StoreRequest(BaseModel):
    cid_hash: str
    aes_iv: str
    aes_tag: str
    kem_cyphertext: str
    original_file: Optional[str] = None
    data_id: Optional[str] = None


class AccessRequest(BaseModel):
    data_id: str
    address: str


router = APIRouter(prefix="/api/blockchain", tags=["Blockchain"])


@router.post("/store")
async def store_on_blockchain(request: StoreRequest):
    """Store encrypted data reference on the blockchain"""
    try:
        blockchain_service = blockchain_connector()

        # Generate data ID if not provided
        data_id = request.data_id or blockchain_service.generate_data_id(request.cid_hash, int(time.time()))

        # Store data on blockchain
        receipt = blockchain_service.store_encrypted_data(
            data_id,
            request.cid_hash,
            request.aes_iv,
            request.aes_tag,
            request.kem_cyphertext
        )

        return {
            'message': 'Data reference stored on blockchain',
            'data_id': data_id,
            'transaction_hash': receipt.transactionHash.hex(),
            'block_number': receipt.blockNumber,
            'gas_used': receipt.gasUsed
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing on blockchain: {str(e)}")


@router.get("/retrieve/{data_id}")
async def retrieve_from_blockchain(data_id: str):
    """Retrieve data reference from the blockchain"""
    try:
        blockchain_service = blockchain_connector()

        cid_hash, aes_iv, aes_tag, kem_cyphertext, timestamp, owner = blockchain_service.retrieve_encrypted_data(data_id)

        return {
            'data_id': data_id,
            'cid_hash': cid_hash,
            'aes_iv': aes_iv,
            'aes_tag': aes_tag,
            'kem_cyphertext': kem_cyphertext,
            'timestamp': timestamp,
            'timestamp_readable': time.ctime(timestamp),
            'owner': owner
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving from blockchain: {str(e)}")


@router.post("/access/grant")
async def grant_access(request: AccessRequest):
    try:
        request.data_id = request.data_id.strip()
        request.address = request.address.strip()
        blockchain_service = blockchain_connector()
        receipt = blockchain_service.grant_access(request.data_id, request.address)

        return {
            'message': f'Access granted for {request.address} to data ID {request.data_id}',
            'transaction_hash': receipt.transactionHash.hex(),
            'block_number': receipt.blockNumber
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error granting access: {str(e)}")


@router.post("/access/revoke")
async def revoke_access(request: AccessRequest):
    try:
        request.data_id = request.data_id.strip()
        request.address = request.address.strip()
        blockchain_service = blockchain_connector()
        receipt = blockchain_service.revoke_access(request.data_id, request.address)

        return {
            'message': f'Access revoked for {request.address} to data ID {request.data_id}',
            'transaction_hash': receipt.transactionHash.hex(),
            'block_number': receipt.blockNumber
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error revoking access: {str(e)}")


@router.get("/access/check")
async def check_access(data_id: str, address: str):
    try:
        data_id = data_id.strip()
        address = address.strip()
        blockchain_service = blockchain_connector()
        has_access = blockchain_service.check_access(data_id, address)

        return {
            'data_id': data_id,
            'address': address,
            'has_access': has_access
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking access: {str(e)}")


@router.get("/data")
async def get_data_ids(owned: bool = Query(False, description="Whether to return only data IDs owned by the caller")):
    try:
        blockchain_service = blockchain_connector()
        data_ids = blockchain_service.get_my_data_ids() if owned else blockchain_service.get_all_data_ids()

        return {
            'data_ids': data_ids,
            'count': len(data_ids)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting data IDs: {str(e)}")
