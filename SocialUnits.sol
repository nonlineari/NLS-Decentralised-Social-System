// SocialUnits: Decentralized Social Network Algorithm Units
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract SocialUnits is ERC721, ERC721URIStorage, Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;

    // Social Unit Types
    enum UnitType {
        BEHAVIOR_PATTERN,    // User's behavior patterns (likes, views, shares)
        CONTENT_PREFERENCE,  // Content category preferences
        SOCIAL_CONNECTION,   // Friend/follower connections
        ENGAGEMENT_METRIC,   // Engagement scores and patterns
        RECOMMENDATION_UNIT  // AI-generated recommendation data
    }

    // Social Unit Structure
    struct SocialUnit {
        UnitType unitType;
        address owner;
        uint256 creationTime;
        uint256 lastUpdate;
        uint256 value;           // Algorithmic value score
        uint256 rarity;          // 1-100 rarity score
        string metadataURI;      // IPFS or Arweave link
        mapping(string => uint256) attributes; // Dynamic attributes
        bool isActive;
        uint256[] relatedUnits;  // Connected social units
    }

    // Social Graph Structure
    struct SocialConnection {
        address userA;
        address userB;
        uint256 connectionStrength; // 0-1000
        uint256 connectionType;     // 1=friend, 2=follow, 3=block
        uint256 establishedTime;
        uint256 lastInteraction;
        bool isActive;
    }

    // Algorithm Data Structure
    struct RecommendationAlgorithm {
        string algorithmId;
        string algorithmType;    // "content", "friend", "trend"
        uint256 accuracy;        // 0-100 accuracy score
        uint256 usageCount;
        bool isActive;
        mapping(address => uint256) userScores; // User-specific scores
    }

    // Storage
    mapping(uint256 => SocialUnit) public socialUnits;
    mapping(address => uint256[]) public userUnits;
    mapping(bytes32 => SocialConnection) public socialConnections;
    mapping(string => RecommendationAlgorithm) public algorithms;
    mapping(address => mapping(UnitType => uint256[])) public userUnitsByType;

    // Global Statistics
    uint256 public totalUnits;
    uint256 public totalConnections;
    uint256 public totalAlgorithms;

    // Events
    event SocialUnitCreated(uint256 indexed tokenId, address indexed owner, UnitType unitType);
    event SocialUnitUpdated(uint256 indexed tokenId, uint256 newValue);
    event SocialConnectionCreated(bytes32 indexed connectionId, address indexed userA, address indexed userB);
    event SocialConnectionUpdated(bytes32 indexed connectionId, uint256 newStrength);
    event RecommendationGenerated(address indexed user, string algorithmId, uint256[] recommendedUnits);
    event AlgorithmTrained(string algorithmId, uint256 newAccuracy);

    constructor() ERC721("SocialUnits", "SOCIAL") {}

    // Social Unit Creation and Management
    function createSocialUnit(
        UnitType unitType,
        string memory metadataURI,
        uint256 initialValue
    ) external returns (uint256) {
        _tokenIdCounter.increment();
        uint256 tokenId = _tokenIdCounter.current();

        uint256 rarity = _calculateRarity(unitType, initialValue);

        SocialUnit storage unit = socialUnits[tokenId];
        unit.unitType = unitType;
        unit.owner = msg.sender;
        unit.creationTime = block.timestamp;
        unit.lastUpdate = block.timestamp;
        unit.value = initialValue;
        unit.rarity = rarity;
        unit.metadataURI = metadataURI;
        unit.isActive = true;

        userUnits[msg.sender].push(tokenId);
        userUnitsByType[msg.sender][unitType].push(tokenId);
        totalUnits++;

        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, metadataURI);

        emit SocialUnitCreated(tokenId, msg.sender, unitType);
        return tokenId;
    }

    function updateSocialUnit(uint256 tokenId, uint256 newValue, string memory attributeKey, uint256 attributeValue) external {
        require(ownerOf(tokenId) == msg.sender, "Not unit owner");
        require(socialUnits[tokenId].isActive, "Unit not active");

        SocialUnit storage unit = socialUnits[tokenId];
        unit.value = newValue;
        unit.lastUpdate = block.timestamp;
        unit.attributes[attributeKey] = attributeValue;

        emit SocialUnitUpdated(tokenId, newValue);
    }

    function connectSocialUnits(uint256 unitIdA, uint256 unitIdB) external {
        require(ownerOf(unitIdA) == msg.sender || ownerOf(unitIdB) == msg.sender, "Not unit owner");
        require(socialUnits[unitIdA].isActive && socialUnits[unitIdB].isActive, "Units not active");

        socialUnits[unitIdA].relatedUnits.push(unitIdB);
        socialUnits[unitIdB].relatedUnits.push(unitIdA);
    }

    // Social Graph Management
    function createSocialConnection(address userB, uint256 connectionType) external {
        require(userB != msg.sender, "Cannot connect to self");
        require(connectionType >= 1 && connectionType <= 3, "Invalid connection type");

        bytes32 connectionId = keccak256(abi.encodePacked(msg.sender, userB));
        require(!socialConnections[connectionId].isActive, "Connection already exists");

        socialConnections[connectionId] = SocialConnection({
            userA: msg.sender,
            userB: userB,
            connectionStrength: 100, // Initial strength
            connectionType: connectionType,
            establishedTime: block.timestamp,
            lastInteraction: block.timestamp,
            isActive: true
        });

        totalConnections++;
        emit SocialConnectionCreated(connectionId, msg.sender, userB);
    }

    function updateConnectionStrength(address userB, uint256 newStrength) external {
        require(newStrength <= 1000, "Strength max 1000");

        bytes32 connectionId = keccak256(abi.encodePacked(msg.sender, userB));
        require(socialConnections[connectionId].isActive, "Connection not active");
        require(socialConnections[connectionId].userA == msg.sender ||
                socialConnections[connectionId].userB == msg.sender, "Not connection participant");

        socialConnections[connectionId].connectionStrength = newStrength;
        socialConnections[connectionId].lastInteraction = block.timestamp;

        emit SocialConnectionUpdated(connectionId, newStrength);
    }

    function getSocialConnections(address user) external view returns (bytes32[] memory) {
        // This is a simplified version - in production, you'd want pagination
        bytes32[] memory connections = new bytes32[](totalConnections);
        uint256 count = 0;

        // Inefficient but functional for demo - production would use indexed storage
        for (uint256 i = 1; i <= totalConnections; i++) {
            bytes32 testId = keccak256(abi.encodePacked(user, address(uint160(i))));
            if (socialConnections[testId].isActive &&
                (socialConnections[testId].userA == user || socialConnections[testId].userB == user)) {
                connections[count] = testId;
                count++;
            }
        }

        // Trim array to actual size
        bytes32[] memory result = new bytes32[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = connections[i];
        }

        return result;
    }

    // Decentralized Algorithm System
    function registerAlgorithm(string memory algorithmId, string memory algorithmType) external onlyOwner {
        require(bytes(algorithms[algorithmId].algorithmType).length == 0, "Algorithm exists");

        algorithms[algorithmId] = RecommendationAlgorithm({
            algorithmId: algorithmId,
            algorithmType: algorithmType,
            accuracy: 50, // Initial accuracy
            usageCount: 0,
            isActive: true
        });

        totalAlgorithms++;
    }

    function updateUserAlgorithmScore(string memory algorithmId, address user, uint256 score) external {
        require(algorithms[algorithmId].isActive, "Algorithm not active");
        require(score <= 1000, "Score max 1000");

        algorithms[algorithmId].userScores[user] = score;
        algorithms[algorithmId].usageCount++;
    }

    function generateRecommendations(string memory algorithmId, address user, uint256[] memory candidateUnits)
        external returns (uint256[] memory) {

        require(algorithms[algorithmId].isActive, "Algorithm not active");

        // Simple recommendation algorithm based on user behavior patterns
        uint256[] memory scores = new uint256[](candidateUnits.length);
        uint256[] memory recommendations = new uint256[](min(10, candidateUnits.length));

        // Score units based on user's existing units and connections
        for (uint256 i = 0; i < candidateUnits.length; i++) {
            uint256 unitId = candidateUnits[i];
            scores[i] = _calculateRecommendationScore(user, unitId, algorithmId);
        }

        // Sort by score and return top recommendations
        recommendations = _sortByScore(candidateUnits, scores);

        emit RecommendationGenerated(user, algorithmId, recommendations);
        return recommendations;
    }

    // Trading and Marketplace Functions
    function transferSocialUnit(address to, uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not unit owner");

        // Update our internal tracking
        _removeFromUserArray(msg.sender, tokenId);
        userUnits[to].push(tokenId);
        socialUnits[tokenId].owner = to;

        safeTransferFrom(msg.sender, to, tokenId);
    }

    function batchTransferUnits(address to, uint256[] memory tokenIds) external {
        for (uint256 i = 0; i < tokenIds.length; i++) {
            require(ownerOf(tokenIds[i]) == msg.sender, "Not unit owner");
        }

        for (uint256 i = 0; i < tokenIds.length; i++) {
            this.transferSocialUnit(to, tokenIds[i]);
        }
    }

    // Social Network Algorithm Functions
    function calculateEngagementScore(address user) external view returns (uint256) {
        uint256[] memory userUnitIds = userUnits[user];
        uint256 totalEngagement = 0;

        for (uint256 i = 0; i < userUnitIds.length; i++) {
            SocialUnit memory unit = socialUnits[userUnitIds[i]];
            if (unit.unitType == UnitType.ENGAGEMENT_METRIC) {
                totalEngagement += unit.value;
            }
        }

        return totalEngagement;
    }

    function findSimilarUsers(address user, uint256 maxResults) external view returns (address[] memory) {
        address[] memory similarUsers = new address[](maxResults);
        uint256 count = 0;

        // Find users with similar behavior patterns
        // Simplified version - production would use more sophisticated similarity algorithms
        uint256[] memory userUnitIds = userUnits[user];

        for (uint256 i = 0; i < totalUnits && count < maxResults; i++) {
            SocialUnit memory unit = socialUnits[i + 1]; // tokenId starts from 1
            if (unit.owner != user && unit.isActive) {
                if (_calculateUserSimilarity(user, unit.owner, userUnitIds) > 70) {
                    similarUsers[count] = unit.owner;
                    count++;
                }
            }
        }

        return similarUsers;
    }

    function predictUserInterests(address user, UnitType interestType) external view returns (uint256[] memory) {
        uint256[] memory userUnitIds = userUnits[user];
        uint256[] memory interests = new uint256[](userUnitIds.length);
        uint256 count = 0;

        for (uint256 i = 0; i < userUnitIds.length; i++) {
            SocialUnit memory unit = socialUnits[userUnitIds[i]];
            if (unit.unitType == interestType && unit.isActive) {
                interests[count] = unit.value;
                count++;
            }
        }

        // Trim array
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = interests[i];
        }

        return result;
    }

    // Internal Helper Functions
    function _calculateRarity(UnitType unitType, uint256 value) internal pure returns (uint256) {
        // Simple rarity calculation based on type and value
        uint256 baseRarity = 50;

        if (unitType == UnitType.BEHAVIOR_PATTERN) baseRarity += 10;
        if (unitType == UnitType.SOCIAL_CONNECTION) baseRarity += 15;
        if (unitType == UnitType.RECOMMENDATION_UNIT) baseRarity += 20;

        if (value > 500) baseRarity += 20;
        else if (value > 200) baseRarity += 10;

        return min(baseRarity, 100);
    }

    function _calculateRecommendationScore(address user, uint256 unitId, string memory algorithmId)
        internal view returns (uint256) {

        SocialUnit memory unit = socialUnits[unitId];
        uint256 score = unit.value;

        // Boost score based on user's algorithm preferences
        uint256 userAlgoScore = algorithms[algorithmId].userScores[user];
        score = (score * (100 + userAlgoScore)) / 100;

        // Boost score for socially connected users
        bytes32 connectionId = keccak256(abi.encodePacked(user, unit.owner));
        if (socialConnections[connectionId].isActive) {
            score = (score * (100 + socialConnections[connectionId].connectionStrength / 10)) / 100;
        }

        return min(score, 1000);
    }

    function _calculateUserSimilarity(address userA, address userB, uint256[] memory userAUnits)
        internal view returns (uint256) {

        uint256[] memory userBUnits = userUnits[userB];
        uint256 similarity = 0;

        // Calculate similarity based on shared unit types and values
        for (uint256 i = 0; i < userAUnits.length; i++) {
            SocialUnit memory unitA = socialUnits[userAUnits[i]];
            for (uint256 j = 0; j < userBUnits.length; j++) {
                SocialUnit memory unitB = socialUnits[userBUnits[j]];
                if (unitA.unitType == unitB.unitType) {
                    uint256 valueDiff = abs(int256(unitA.value) - int256(unitB.value));
                    if (valueDiff < 50) similarity += 10;
                }
            }
        }

        return min(similarity, 100);
    }

    function _sortByScore(uint256[] memory ids, uint256[] memory scores)
        internal pure returns (uint256[] memory) {

        require(ids.length == scores.length, "Array length mismatch");

        // Simple bubble sort for demo (production would use more efficient sorting)
        for (uint256 i = 0; i < scores.length; i++) {
            for (uint256 j = i + 1; j < scores.length; j++) {
                if (scores[j] > scores[i]) {
                    // Swap scores
                    uint256 tempScore = scores[i];
                    scores[i] = scores[j];
                    scores[j] = tempScore;

                    // Swap corresponding ids
                    uint256 tempId = ids[i];
                    ids[i] = ids[j];
                    ids[j] = tempId;
                }
            }
        }

        return ids;
    }

    function _removeFromUserArray(address user, uint256 tokenId) internal {
        uint256[] storage userUnitList = userUnits[user];
        for (uint256 i = 0; i < userUnitList.length; i++) {
            if (userUnitList[i] == tokenId) {
                userUnitList[i] = userUnitList[userUnitList.length - 1];
                userUnitList.pop();
                break;
            }
        }
    }

    // ERC721 Overrides
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        socialUnits[tokenId].isActive = false;
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return socialUnits[tokenId].metadataURI;
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    // Utility functions
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }

    function abs(int256 x) internal pure returns (uint256) {
        return x >= 0 ? uint256(x) : uint256(-x);
    }
}
