// BitChat Smart Contract for Decentralized Chat
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract BitChat {
    struct Message {
        address sender;
        string content;
        uint256 timestamp;
        uint256 messageId;
        string mediaType; // "text", "audio", "video"
        bytes32 mediaHash;
    }

    struct ChatRoom {
        string name;
        address[] participants;
        uint256 messageCount;
        mapping(uint256 => Message) messages;
        mapping(address => bool) isParticipant;
    }

    mapping(uint256 => ChatRoom) public chatRooms;
    mapping(address => uint256[]) public userChatRooms;
    uint256 public chatRoomCount;

    event MessageSent(uint256 indexed chatRoomId, address indexed sender, uint256 messageId);
    event ChatRoomCreated(uint256 indexed chatRoomId, string name, address creator);
    event ParticipantJoined(uint256 indexed chatRoomId, address participant);

    // Create a new chat room
    function createChatRoom(string memory _name) public returns (uint256) {
        chatRoomCount++;
        ChatRoom storage room = chatRooms[chatRoomCount];
        room.name = _name;
        room.participants.push(msg.sender);
        room.isParticipant[msg.sender] = true;
        userChatRooms[msg.sender].push(chatRoomCount);

        emit ChatRoomCreated(chatRoomCount, _name, msg.sender);
        return chatRoomCount;
    }

    // Join a chat room
    function joinChatRoom(uint256 _chatRoomId) public {
        require(_chatRoomId > 0 && _chatRoomId <= chatRoomCount, "Invalid chat room");
        require(!chatRooms[_chatRoomId].isParticipant[msg.sender], "Already a participant");

        ChatRoom storage room = chatRooms[_chatRoomId];
        room.participants.push(msg.sender);
        room.isParticipant[msg.sender] = true;
        userChatRooms[msg.sender].push(_chatRoomId);

        emit ParticipantJoined(_chatRoomId, msg.sender);
    }

    // Send a message
    function sendMessage(uint256 _chatRoomId, string memory _content, string memory _mediaType, bytes32 _mediaHash) public {
        require(chatRooms[_chatRoomId].isParticipant[msg.sender], "Not a participant");

        ChatRoom storage room = chatRooms[_chatRoomId];
        room.messageCount++;
        uint256 messageId = room.messageCount;

        room.messages[messageId] = Message({
            sender: msg.sender,
            content: _content,
            timestamp: block.timestamp,
            messageId: messageId,
            mediaType: _mediaType,
            mediaHash: _mediaHash
        });

        emit MessageSent(_chatRoomId, msg.sender, messageId);
    }

    // Get message details
    function getMessage(uint256 _chatRoomId, uint256 _messageId) public view returns (
        address sender,
        string memory content,
        uint256 timestamp,
        string memory mediaType,
        bytes32 mediaHash
    ) {
        Message memory message = chatRooms[_chatRoomId].messages[_messageId];
        return (message.sender, message.content, message.timestamp, message.mediaType, message.mediaHash);
    }

    // Get chat room info
    function getChatRoomInfo(uint256 _chatRoomId) public view returns (
        string memory name,
        address[] memory participants,
        uint256 messageCount
    ) {
        ChatRoom storage room = chatRooms[_chatRoomId];
        return (room.name, room.participants, room.messageCount);
    }

    // Get user's chat rooms
    function getUserChatRooms(address _user) public view returns (uint256[] memory) {
        return userChatRooms[_user];
    }

    // Media hash storage for content verification
    function storeMediaHash(bytes32 _hash) public returns (uint256) {
        // Store hash for verification
        // In production, this could link to IPFS or other storage
        return uint256(_hash);
    }
}
