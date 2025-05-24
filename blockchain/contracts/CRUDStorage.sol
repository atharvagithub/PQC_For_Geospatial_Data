// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CRUDStorage {
    struct Record {
        uint id;
        string data;
    }

    mapping(uint => Record) private records;

    event RecordCreated(uint id, string data);
    event RecordUpdated(uint id, string data);
    event RecordDeleted(uint id);

    function create(uint id, string memory data) public {
        require(bytes(records[id].data).length == 0, "Already exists");
        records[id] = Record(id, data);
        emit RecordCreated(id, data);
    }

    function read(uint id) public view returns (string memory) {
        require(bytes(records[id].data).length != 0, "Does not exist");
        return records[id].data;
    }

    function update(uint id, string memory data) public {
        require(bytes(records[id].data).length != 0, "Does not exist");
        records[id].data = data;
        emit RecordUpdated(id, data);
    }

    function destroy(uint id) public {
        require(bytes(records[id].data).length != 0, "Does not exist");
        delete records[id];
        emit RecordDeleted(id);
    }
}
