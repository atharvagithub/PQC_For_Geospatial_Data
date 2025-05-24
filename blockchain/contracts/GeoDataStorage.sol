// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title GeoDataStorage
 * @dev Store encrypted geospatial data references on the blockchain
 */
contract GeoDataStorage {
    address private owner;

    struct EncryptedData {
        string cidHash;          // IPFS CID or hash of encrypted data
        string aes_iv;           // AES IV
        string aes_tag;          // AES GCM tag
        string kem_cyphertext;   // Kyber512 KEM ciphertext
        uint256 timestamp;       // Store time
        address owner;           // Who owns it
        bool exists;             // Safe existence check
    }

    mapping(string => EncryptedData) private dataStore;
    string[] private dataIds;
    mapping(address => mapping(string => bool)) private accessControl;

    event DataStored(string dataId, address indexed owner, uint256 timestamp);
    event AccessGranted(string dataId, address indexed grantee, address indexed grantor);
    event AccessRevoked(string dataId, address indexed revokee, address indexed revoker);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not contract owner");
        _;
    }

    modifier hasAccess(string memory dataId) {
        EncryptedData storage entry = dataStore[dataId];
        require(entry.exists, "Data not found");

        if (msg.sender != entry.owner && !accessControl[msg.sender][dataId]) {
            revert("No access to this data");
        }
        _;
    }

    function storeData(
        string memory dataId,
        string memory cidHash,
        string memory aes_iv,
        string memory aes_tag,
        string memory kem_cyphertext
    ) public {
        require(!dataStore[dataId].exists, "Data already exists");

        dataStore[dataId] = EncryptedData({
            cidHash: cidHash,
            aes_iv: aes_iv,
            aes_tag: aes_tag,
            kem_cyphertext: kem_cyphertext,
            timestamp: block.timestamp,
            owner: msg.sender,
            exists: true
        });

        dataIds.push(dataId);

        emit DataStored(dataId, msg.sender, block.timestamp);
    }

    function retrieveData(string memory dataId)
        public
        view
        hasAccess(dataId)
        returns (
            string memory cidHash,
            string memory aes_iv,
            string memory aes_tag,
            string memory kem_cyphertext,
            uint256 timestamp,
            address dataOwner
        )
    {
        require(dataStore[dataId].exists, "Data not found");

        EncryptedData memory data = dataStore[dataId];
        return (
            data.cidHash,
            data.aes_iv,
            data.aes_tag,
            data.kem_cyphertext,
            data.timestamp,
            data.owner
        );
    }

    function updateData(
        string memory dataId,
        string memory newCidHash,
        string memory newAes_iv,
        string memory newAes_tag,
        string memory newKem_cyphertext
    ) public {
        require(dataStore[dataId].exists, "Data not found");
        require(dataStore[dataId].owner == msg.sender, "Only owner can update");

        dataStore[dataId].cidHash = newCidHash;
        dataStore[dataId].aes_iv = newAes_iv;
        dataStore[dataId].aes_tag = newAes_tag;
        dataStore[dataId].kem_cyphertext = newKem_cyphertext;
        dataStore[dataId].timestamp = block.timestamp;

        emit DataStored(dataId, msg.sender, block.timestamp);
    }

    function grantAccess(string memory dataId, address grantee) public {
        require(dataStore[dataId].exists, "Data not found");
        require(dataStore[dataId].owner == msg.sender, "Only owner can grant");

        accessControl[grantee][dataId] = true;
        emit AccessGranted(dataId, grantee, msg.sender);
    }

    function revokeAccess(string memory dataId, address revokee) public {
        require(dataStore[dataId].exists, "Data not found");
        require(dataStore[dataId].owner == msg.sender, "Only owner can revoke");

        accessControl[revokee][dataId] = false;
        emit AccessRevoked(dataId, revokee, msg.sender);
    }

    function checkAccess(string memory dataId, address addr)
        public
        view
        returns (bool)
    {
        require(dataStore[dataId].exists, "Data not found");
        return (dataStore[dataId].owner == addr || accessControl[addr][dataId]);
    }

    function getAllDataIds()
        public
        view
        returns (string[] memory)
    {
        return dataIds;
    }

    function getMyDataIds()
        public
        view
        returns (string[] memory)
    {
        uint256 count = 0;
        for (uint256 i = 0; i < dataIds.length; i++) {
            if (dataStore[dataIds[i]].owner == msg.sender) {
                count++;
            }
        }

        string[] memory myDataIds = new string[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < dataIds.length; i++) {
            if (dataStore[dataIds[i]].owner == msg.sender) {
                myDataIds[index] = dataIds[i];
                index++;
            }
        }

        return myDataIds;
    }
}
