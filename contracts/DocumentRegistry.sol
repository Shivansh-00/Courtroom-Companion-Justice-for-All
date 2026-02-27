// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";

/// @title DocumentRegistry
/// @notice Stores legal document hashes for immutable verification.
contract DocumentRegistry is AccessControl {
    bytes32 public constant NOTARY_ROLE = keccak256("NOTARY_ROLE");

    struct Record {
        bytes32 documentHash;
        address submitter;
        uint256 timestamp;
        string documentId;
        string jurisdiction;
    }

    mapping(bytes32 => Record) private recordsByHash;
    mapping(string => bytes32) private hashByDocumentId;

    event DocumentNotarized(
        bytes32 indexed documentHash,
        string indexed documentId,
        address indexed submitter,
        string jurisdiction,
        uint256 timestamp
    );

    constructor(address admin, address notary) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(NOTARY_ROLE, notary);
    }

    function notarizeDocument(
        bytes32 documentHash,
        string calldata documentId,
        string calldata jurisdiction
    ) external onlyRole(NOTARY_ROLE) {
        require(documentHash != bytes32(0), "Invalid hash");
        require(recordsByHash[documentHash].timestamp == 0, "Hash already exists");
        require(hashByDocumentId[documentId] == bytes32(0), "Document ID already notarized");

        recordsByHash[documentHash] = Record({
            documentHash: documentHash,
            submitter: msg.sender,
            timestamp: block.timestamp,
            documentId: documentId,
            jurisdiction: jurisdiction
        });

        hashByDocumentId[documentId] = documentHash;

        emit DocumentNotarized(documentHash, documentId, msg.sender, jurisdiction, block.timestamp);
    }

    function verifyByHash(bytes32 documentHash) external view returns (bool exists, Record memory record) {
        record = recordsByHash[documentHash];
        exists = (record.timestamp != 0);
    }

    function verifyByDocumentId(string calldata documentId) external view returns (bool exists, Record memory record) {
        bytes32 hash = hashByDocumentId[documentId];
        record = recordsByHash[hash];
        exists = (record.timestamp != 0);
    }
}
