// Web3Cookie: Decentralized Cookie Management System
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Web3Cookie is Ownable, ReentrancyGuard {
    struct CookieData {
        bytes32 sessionId;
        address user;
        string domain;
        string data;
        uint256 created;
        uint256 expires;
        uint256 lastAccessed;
        bool isActive;
        string[] trackingData; // Pointer/keystroke data
    }

    struct TrackingProfile {
        address user;
        uint256 pointerMovements;
        uint256 keystrokes;
        uint256 sessionDuration;
        uint256[] timestamps;
        mapping(string => uint256) pageInteractions;
        bool consentGiven;
        uint256 consentTimestamp;
    }

    // Storage
    mapping(bytes32 => CookieData) public cookies;
    mapping(address => mapping(string => bytes32[])) public userDomainCookies;
    mapping(address => TrackingProfile) public userTrackingProfiles;
    mapping(string => bool) public allowedDomains;

    // Events
    event CookieCreated(bytes32 indexed sessionId, address indexed user, string domain);
    event CookieAccessed(bytes32 indexed sessionId, address indexed user);
    event CookieExpired(bytes32 indexed sessionId);
    event TrackingDataUpdated(address indexed user, uint256 pointerMovements, uint256 keystrokes);
    event ConsentUpdated(address indexed user, bool consent);

    // Modifiers
    modifier onlyAllowedDomain(string memory domain) {
        require(allowedDomains[domain], "Domain not allowed");
        _;
    }

    modifier validConsent(address user) {
        require(userTrackingProfiles[user].consentGiven, "User consent required");
        _;
    }

    constructor() {
        // Allow localhost for development
        allowedDomains["localhost"] = true;
        allowedDomains["127.0.0.1"] = true;
    }

    // Cookie Management Functions
    function createCookie(
        string memory domain,
        string memory data,
        uint256 expirationDays
    ) external onlyAllowedDomain(domain) validConsent(msg.sender) returns (bytes32) {
        bytes32 sessionId = keccak256(abi.encodePacked(
            msg.sender,
            domain,
            block.timestamp,
            block.difficulty
        ));

        uint256 expires = block.timestamp + (expirationDays * 1 days);

        cookies[sessionId] = CookieData({
            sessionId: sessionId,
            user: msg.sender,
            domain: domain,
            data: data,
            created: block.timestamp,
            expires: expires,
            lastAccessed: block.timestamp,
            isActive: true,
            trackingData: new string[](0)
        });

        userDomainCookies[msg.sender][domain].push(sessionId);

        emit CookieCreated(sessionId, msg.sender, domain);
        return sessionId;
    }

    function getCookie(bytes32 sessionId) external returns (string memory) {
        require(cookies[sessionId].isActive, "Cookie not active");
        require(cookies[sessionId].expires > block.timestamp, "Cookie expired");
        require(cookies[sessionId].user == msg.sender, "Not cookie owner");

        cookies[sessionId].lastAccessed = block.timestamp;
        emit CookieAccessed(sessionId, msg.sender);

        return cookies[sessionId].data;
    }

    function updateCookie(bytes32 sessionId, string memory newData) external {
        require(cookies[sessionId].isActive, "Cookie not active");
        require(cookies[sessionId].user == msg.sender, "Not cookie owner");

        cookies[sessionId].data = newData;
        cookies[sessionId].lastAccessed = block.timestamp;
    }

    function deleteCookie(bytes32 sessionId) external {
        require(cookies[sessionId].user == msg.sender, "Not cookie owner");

        cookies[sessionId].isActive = false;
        emit CookieExpired(sessionId);
    }

    // Tracking Data Management (Pointer/Keystroke alternative)
    function updateTrackingData(
        uint256 pointerMovements,
        uint256 keystrokes,
        uint256 sessionDuration,
        string[] memory pageInteractions
    ) external validConsent(msg.sender) {
        TrackingProfile storage profile = userTrackingProfiles[msg.sender];

        profile.pointerMovements += pointerMovements;
        profile.keystrokes += keystrokes;
        profile.sessionDuration += sessionDuration;
        profile.timestamps.push(block.timestamp);

        for (uint256 i = 0; i < pageInteractions.length; i++) {
            profile.pageInteractions[pageInteractions[i]]++;
        }

        emit TrackingDataUpdated(msg.sender, profile.pointerMovements, profile.keystrokes);
    }

    function addCookieTrackingData(bytes32 sessionId, string memory trackingEntry) external {
        require(cookies[sessionId].isActive, "Cookie not active");
        require(cookies[sessionId].user == msg.sender, "Not cookie owner");

        cookies[sessionId].trackingData.push(trackingEntry);
    }

    // Consent Management
    function giveConsent() external {
        userTrackingProfiles[msg.sender].consentGiven = true;
        userTrackingProfiles[msg.sender].consentTimestamp = block.timestamp;

        emit ConsentUpdated(msg.sender, true);
    }

    function revokeConsent() external {
        userTrackingProfiles[msg.sender].consentGiven = false;

        // Delete all cookies for this user
        // Note: In production, this would need to be implemented more efficiently
        emit ConsentUpdated(msg.sender, false);
    }

    // SoundCloud-style Cookie Implementation
    function createSoundCloudStyleCookie(
        string memory preferences,
        string[] memory listeningHistory,
        uint256 expirationDays
    ) external returns (bytes32) {
        string memory cookieData = string(abi.encodePacked(
            '{"preferences":"', preferences, '",',
            '"listening_history":', _arrayToJson(listeningHistory), ',',
            '"consent_given":', userTrackingProfiles[msg.sender].consentGiven ? 'true' : 'false', ',',
            '"created":', _uintToString(block.timestamp),
            '}'
        ));

        return createCookie("soundcloud.com", cookieData, expirationDays);
    }

    // Administrative Functions
    function addAllowedDomain(string memory domain) external onlyOwner {
        allowedDomains[domain] = true;
    }

    function removeAllowedDomain(string memory domain) external onlyOwner {
        allowedDomains[domain] = false;
    }

    // View Functions
    function getUserCookies(address user, string memory domain) external view returns (bytes32[] memory) {
        return userDomainCookies[user][domain];
    }

    function getCookieInfo(bytes32 sessionId) external view returns (
        address user,
        string memory domain,
        uint256 created,
        uint256 expires,
        bool isActive
    ) {
        CookieData memory cookie = cookies[sessionId];
        return (cookie.user, cookie.domain, cookie.created, cookie.expires, cookie.isActive);
    }

    function getTrackingProfile(address user) external view returns (
        uint256 pointerMovements,
        uint256 keystrokes,
        uint256 sessionDuration,
        bool consentGiven,
        uint256 consentTimestamp
    ) {
        TrackingProfile storage profile = userTrackingProfiles[user];
        return (
            profile.pointerMovements,
            profile.keystrokes,
            profile.sessionDuration,
            profile.consentGiven,
            profile.consentTimestamp
        );
    }

    function getPageInteraction(address user, string memory page) external view returns (uint256) {
        return userTrackingProfiles[user].pageInteractions[page];
    }

    // Utility Functions
    function _arrayToJson(string[] memory arr) internal pure returns (string memory) {
        if (arr.length == 0) return "[]";

        string memory result = "[";
        for (uint256 i = 0; i < arr.length; i++) {
            result = string(abi.encodePacked(result, '"', arr[i], '"'));
            if (i < arr.length - 1) result = string(abi.encodePacked(result, ","));
        }
        result = string(abi.encodePacked(result, "]"));
        return result;
    }

    function _uintToString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";

        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }

        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }

        return string(buffer);
    }

    // Clean up expired cookies (call periodically)
    function cleanupExpiredCookies() external {
        // In production, this would iterate through all cookies
        // For now, it's a placeholder for maintenance
    }
}
