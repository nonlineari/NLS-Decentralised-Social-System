import os
import time
import threading
import json
import uuid
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
from web3 import Web3
import prometheus_client
import requests  # For potential data scraping
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import websocket
from telethon import TelegramClient
from telethon.events import NewMessage
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from nls_browser_interface import nls_browser_request
from cursor_agents_interface import cursor_agents_request

# OSC Settings
ABLETON_OSC_PORT = 9000  # Port to receive from Ableton
VDMX_OSC_IP = "127.0.0.1"
VDMX_OSC_PORT = 7000  # From existing VDMX setup

# Chat and BitChat Settings
CHAT_PORT = 5000
BITCHAT_CONTRACT_ADDRESS = '0xYourBitChatContractAddress'  # Deploy BitChat.sol first
BITCHAT_ROOM_ID = 1  # Default chat room for multimedia events

# NLS Browser API Settings
NLS_BROWSER_URL = "https://api.nls.browser/v1"  # Hypothetical NLS browser API
TEXT_BROWSER_URL = "https://text.browser.api/v1"  # Text browser API
CURSOR_AGENTS_URL = "https://cursor.agents.api/v1"  # Cursor Agents IDE API

# BitChat Contract ABI (from BitChat.sol)
BITCHAT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "_name", "type": "string"}],
        "name": "createChatRoom",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_chatRoomId", "type": "uint256"}],
        "name": "joinChatRoom",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_chatRoomId", "type": "uint256"},
            {"internalType": "string", "name": "_content", "type": "string"},
            {"internalType": "string", "name": "_mediaType", "type": "string"},
            {"internalType": "bytes32", "name": "_mediaHash", "type": "bytes32"}
        ],
        "name": "sendMessage",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_chatRoomId", "type": "uint256"}, {"internalType": "uint256", "name": "_messageId", "type": "uint256"}],
        "name": "getMessage",
        "outputs": [
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "string", "name": "content", "type": "string"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "string", "name": "mediaType", "type": "string"},
            {"internalType": "bytes32", "name": "mediaHash", "type": "bytes32"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Web3 Settings
WEB3_PROVIDER = 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY'  # Replace with actual
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Web3Cookie Contract
WEB3COOKIE_CONTRACT_ADDRESS = '0xYourWeb3CookieContractAddress'  # Deploy Web3Cookie.sol first

# SocialUnits Contract
SOCIALUNITS_CONTRACT_ADDRESS = '0xYourSocialUnitsContractAddress'  # Deploy SocialUnits.sol first
SOCIALUNITS_ABI = [
    {
        "inputs": [{"internalType": "uint8", "name": "unitType", "type": "uint8"}, {"internalType": "string", "name": "metadataURI", "type": "string"}, {"internalType": "uint256", "name": "initialValue", "type": "uint256"}],
        "name": "createSocialUnit",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}, {"internalType": "uint256", "name": "newValue", "type": "uint256"}, {"internalType": "string", "name": "attributeKey", "type": "string"}, {"internalType": "uint256", "name": "attributeValue", "type": "uint256"}],
        "name": "updateSocialUnit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "userB", "type": "uint256"}, {"internalType": "uint256", "name": "connectionType", "type": "uint256"}],
        "name": "createSocialConnection",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "userB", "type": "uint256"}, {"internalType": "uint256", "name": "newStrength", "type": "uint256"}],
        "name": "updateConnectionStrength",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "algorithmId", "type": "string"}, {"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint256[]", "name": "candidateUnits", "type": "uint256[]"}],
        "name": "generateRecommendations",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "algorithmId", "type": "string"}, {"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint256", "name": "score", "type": "uint256"}],
        "name": "updateUserAlgorithmScore",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "calculateEngagementScore",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint256", "name": "maxResults", "type": "uint256"}],
        "name": "findSimilarUsers",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}, {"internalType": "uint8", "name": "interestType", "type": "uint8"}],
        "name": "predictUserInterests",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Initialize Web3Cookie contract
web3cookie_contract = None
if w3.is_connected() and WEB3COOKIE_CONTRACT_ADDRESS != '0xYourWeb3CookieContractAddress':
    try:
        web3cookie_contract = w3.eth.contract(address=WEB3COOKIE_CONTRACT_ADDRESS, abi=WEB3COOKIE_ABI)
        print("Web3Cookie contract connected successfully")
    except Exception as e:
        print(f"Web3Cookie contract error: {e}")

# Initialize SocialUnits contract
socialunits_contract = None
if w3.is_connected() and SOCIALUNITS_CONTRACT_ADDRESS != '0xYourSocialUnitsContractAddress':
    try:
        socialunits_contract = w3.eth.contract(address=SOCIALUNITS_CONTRACT_ADDRESS, abi=SOCIALUNITS_ABI)
        print("SocialUnits contract connected successfully")
    except Exception as e:
        print(f"SocialUnits contract error: {e}")

# Legacy contract for backward compatibility
CONTRACT_ADDRESS = '0xYourContractAddress'
CONTRACT_ABI = [...]  # Add ABI here

# Prometheus Metrics
prometheus_client.start_http_server(8000)
events_counter = prometheus_client.Counter('events_processed', 'Number of OSC events processed')
metadata_stored = prometheus_client.Counter('metadata_stored', 'Number of metadata stored on blockchain')
bitchat_messages = prometheus_client.Counter('bitchat_messages', 'Number of BitChat messages sent')
bitchat_rooms = prometheus_client.Counter('bitchat_rooms', 'Number of BitChat rooms created')
web3_cookies_created = prometheus_client.Counter('web3_cookies_created', 'Number of Web3Cookies created')
tracking_data_updates = prometheus_client.Counter('tracking_data_updates', 'Number of tracking data updates')

# Chat Message Mapping (Ableton MIDI notes to VDMX triggers)
CHAT_MIDI_MAPPING = {
    60: "play_video_1",    # C4 -> Play video 1
    62: "play_video_2",    # D4 -> Play video 2
    64: "play_video_3",    # E4 -> Play video 3
    65: "pause_video",     # F4 -> Pause video
    67: "stop_video",      # G4 -> Stop video
    69: "next_video",      # A4 -> Next video
    71: "prev_video",      # B4 -> Previous video
}

# Flask Chat App (Web-based chat interface)
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# BitChat is our primary chat system (blockchain-based)

# Chat Message Storage
chat_history = []

# BitChat Functions
def create_bitchat_room(name):
    """Create a new BitChat room"""
    if not bitchat_contract or not w3.eth.accounts:
        return {"error": "BitChat contract not initialized"}

    try:
        tx = bitchat_contract.functions.createChatRoom(name).transact({'from': w3.eth.accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        bitchat_rooms.inc()
        return {"success": True, "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        return {"error": str(e)}

def send_bitchat_message(content, media_type="text", media_hash="0x0000000000000000000000000000000000000000000000000000000000000000"):
    """Send a message to BitChat"""
    if not bitchat_contract or not w3.eth.accounts:
        return {"error": "BitChat contract not initialized"}

    try:
        tx = bitchat_contract.functions.sendMessage(
            BITCHAT_ROOM_ID, content, media_type, media_hash
        ).transact({'from': w3.eth.accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        bitchat_messages.inc()
        return {"success": True, "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        return {"error": str(e)}

def get_bitchat_message(message_id):
    """Get a message from BitChat"""
    if not bitchat_contract:
        return {"error": "BitChat contract not initialized"}

    try:
        result = bitchat_contract.functions.getMessage(BITCHAT_ROOM_ID, message_id).call()
        return {
            "sender": result[0],
            "content": result[1],
            "timestamp": result[2],
            "mediaType": result[3],
            "mediaHash": result[4]
        }
    except Exception as e:
        return {"error": str(e)}

# Web3Cookie Functions
def create_web3_cookie(domain, data, expiration_days=30):
    """Create a Web3Cookie"""
    if not web3cookie_contract or not w3.eth.accounts:
        return {"error": "Web3Cookie contract not initialized"}

    try:
        tx = web3cookie_contract.functions.createCookie(domain, data, expiration_days).transact({
            'from': w3.eth.accounts[0]
        })
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        web3_cookies_created.inc()

        # Extract session ID from event logs
        logs = web3cookie_contract.events.CookieCreated().process_receipt(receipt)
        session_id = logs[0]['args']['sessionId']

        return {
            "success": True,
            "session_id": session_id.hex(),
            "tx_hash": receipt.transactionHash.hex()
        }
    except Exception as e:
        return {"error": str(e)}

def get_web3_cookie(session_id):
    """Get Web3Cookie data"""
    if not web3cookie_contract or not w3.eth.accounts:
        return {"error": "Web3Cookie contract not initialized"}

    try:
        data = web3cookie_contract.functions.getCookie(session_id).call({
            'from': w3.eth.accounts[0]
        })
        return {"success": True, "data": data}
    except Exception as e:
        return {"error": str(e)}

def update_tracking_data(pointer_movements, keystrokes, session_duration, page_interactions):
    """Update tracking data on blockchain"""
    if not web3cookie_contract or not w3.eth.accounts:
        return {"error": "Web3Cookie contract not initialized"}

    try:
        tx = web3cookie_contract.functions.updateTrackingData(
            pointer_movements, keystrokes, session_duration, page_interactions
        ).transact({'from': w3.eth.accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        tracking_data_updates.inc()
        return {"success": True, "tx_hash": receipt.transactionHash.hex()}
    except Exception as e:
        return {"error": str(e)}

def get_tracking_profile(user_address):
    """Get tracking profile for a user"""
    if not web3cookie_contract:
        return {"error": "Web3Cookie contract not initialized"}

    try:
        result = web3cookie_contract.functions.getTrackingProfile(user_address).call()
        return {
            "pointer_movements": result[0],
            "keystrokes": result[1],
            "session_duration": result[2],
            "consent_given": result[3],
            "consent_timestamp": result[4]
        }
    except Exception as e:
        return {"error": str(e)}

def create_soundcloud_style_cookie(preferences, listening_history):
    """Create a SoundCloud-style cookie"""
    if not web3cookie_contract or not w3.eth.accounts:
        return {"error": "Web3Cookie contract not initialized"}

    try:
        tx = web3cookie_contract.functions.createSoundCloudStyleCookie(
            json.dumps(preferences), listening_history, 365
        ).transact({'from': w3.eth.accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        web3_cookies_created.inc()

        logs = web3cookie_contract.events.CookieCreated().process_receipt(receipt)
        session_id = logs[0]['args']['sessionId']

        return {
            "success": True,
            "session_id": session_id.hex(),
            "tx_hash": receipt.transactionHash.hex()
        }
    except Exception as e:
        return {"error": str(e)}

# SocialUnits Functions
def create_social_unit(unit_type, metadata_uri, initial_value):
    """Create a SocialUnit"""
    if not socialunits_contract or not w3.eth.accounts:
        return {"error": "SocialUnits contract not initialized"}

    try:
        tx = socialunits_contract.functions.createSocialUnit(unit_type, metadata_uri, initial_value).transact({
            'from': w3.eth.accounts[0]
        })
        receipt = w3.eth.wait_for_transaction_receipt(tx)

        logs = socialunits_contract.events.SocialUnitCreated().process_receipt(receipt)
        token_id = logs[0]['args']['tokenId']

        return {
            "success": True,
            "token_id": token_id,
            "tx_hash": receipt.transactionHash.hex()
        }
    except Exception as e:
        return {"error": str(e)}

def update_social_unit(token_id, new_value, attribute_key, attribute_value):
    """Update a SocialUnit"""
    if not socialunits_contract or not w3.eth.accounts:
        return {"error": "SocialUnits contract not initialized"}

    try:
        tx = socialunits_contract.functions.updateSocialUnit(token_id, new_value, attribute_key, attribute_value).transact({
            'from': w3.eth.accounts[0]
        })
        receipt = w3.eth.wait_for_transaction_receipt(tx)

        return {
            "success": True,
            "tx_hash": receipt.transactionHash.hex()
        }
    except Exception as e:
        return {"error": str(e)}

def create_social_connection(user_b, connection_type):
    """Create a social connection"""
    if not socialunits_contract or not w3.eth.accounts:
        return {"error": "SocialUnits contract not initialized"}

    try:
        tx = socialunits_contract.functions.createSocialConnection(user_b, connection_type).transact({
            'from': w3.eth.accounts[0]
        })
        receipt = w3.eth.wait_for_transaction_receipt(tx)

        return {
            "success": True,
            "tx_hash": receipt.transactionHash.hex()
        }
    except Exception as e:
        return {"error": str(e)}

def generate_recommendations(algorithm_id, user_address, candidate_units):
    """Generate recommendations using SocialUnits algorithm"""
    if not socialunits_contract:
        return {"error": "SocialUnits contract not initialized"}

    try:
        result = socialunits_contract.functions.generateRecommendations(
            algorithm_id, user_address, candidate_units
        ).call()

        return {
            "success": True,
            "recommendations": result
        }
    except Exception as e:
        return {"error": str(e)}

def get_engagement_score(user_address):
    """Get engagement score for a user"""
    if not socialunits_contract:
        return {"error": "SocialUnits contract not initialized"}

    try:
        score = socialunits_contract.functions.calculateEngagementScore(user_address).call()
        return {
            "success": True,
            "engagement_score": score
        }
    except Exception as e:
        return {"error": str(e)}

def find_similar_users(user_address, max_results=10):
    """Find similar users based on SocialUnits"""
    if not socialunits_contract:
        return {"error": "SocialUnits contract not initialized"}

    try:
        similar_users = socialunits_contract.functions.findSimilarUsers(user_address, max_results).call()
        return {
            "success": True,
            "similar_users": similar_users
        }
    except Exception as e:
        return {"error": str(e)}

# BitChat Contract
bitchat_contract = None
if w3.is_connected() and BITCHAT_CONTRACT_ADDRESS != '0xYourBitChatContractAddress':
    try:
        bitchat_contract = w3.eth.contract(address=BITCHAT_CONTRACT_ADDRESS, abi=BITCHAT_ABI)
        print("BitChat contract connected successfully")
    except Exception as e:
        print(f"BitChat contract error: {e}")

# SocketIO Chat Events
@socketio.on('connect')
def handle_connect():
    print('Client connected to chat')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from chat')

@socketio.on('chat_message')
def handle_chat_message(data):
    message = data.get('message', '')
    sender = data.get('sender', 'Anonymous')
    timestamp = int(time.time())

    # Store message locally
    chat_entry = {
        'id': str(uuid.uuid4()),
        'message': message,
        'sender': sender,
        'timestamp': timestamp,
        'source': 'web'
    }
    chat_history.append(chat_entry)

    # Store on BitChat blockchain
    result = send_bitchat_message(message)
    if result.get("success"):
        print(f"Message sent to BitChat: {result['tx_hash']}")
    else:
        print(f"BitChat error: {result.get('error')}")

    # Forward to VDMX if it's a command
    if message.startswith('/'):
        handle_chat_command(message)

    # Broadcast to all connected clients
    emit('chat_message', chat_entry, broadcast=True)

# BitChat Integration Functions
def bitchat_monitor():
    """Monitor BitChat for new messages and relay to local chat"""
    message_id = 1  # Start checking from message 1
    while True:
        try:
            result = get_bitchat_message(message_id)
            if not result.get("error") and result.get("content"):
                # Check if we haven't seen this message yet
                existing_ids = [msg.get('bitchat_id') for msg in chat_history if msg.get('bitchat_id')]
                if message_id not in existing_ids:
                    chat_entry = {
                        'id': str(uuid.uuid4()),
                        'bitchat_id': message_id,
                        'message': result['content'],
                        'sender': f"BitChat:{result['sender'][:8]}...",  # Shorten address
                        'timestamp': result['timestamp'],
                        'source': 'bitchat',
                        'media_type': result['mediaType'],
                        'media_hash': result['mediaHash']
                    }
                    chat_history.append(chat_entry)
                    socketio.emit('chat_message', chat_entry)
                message_id += 1
            else:
                time.sleep(5)  # Wait before checking again
        except Exception as e:
            print(f"BitChat monitor error: {e}")
            time.sleep(10)

# NLS Browser API is now handled by nls_browser_interface.py

# Text Browser is now handled by NLS browser interface

# Chat Command Handler
def handle_chat_command(command):
    cmd_parts = command.split()
    cmd = cmd_parts[0].lower()

    if cmd == '/vdmx':
        # Send command to VDMX
        if len(cmd_parts) > 1:
            vdmx_cmd = ' '.join(cmd_parts[1:])
            vdmx_client = udp_client.SimpleUDPClient(VDMX_OSC_IP, VDMX_OSC_PORT)
            vdmx_client.send_message("/command", vdmx_cmd)
            print(f"Sent to VDMX: {vdmx_cmd}")

    elif cmd == '/ableton':
        # Send command to Ableton (would need Ableton OSC setup)
        if len(cmd_parts) > 1:
            ableton_cmd = ' '.join(cmd_parts[1:])
            # Implementation would depend on Ableton's OSC setup
            print(f"Ableton command: {ableton_cmd}")

    elif cmd == '/nls':
        # Query NLS browser
        if len(cmd_parts) > 1:
            nls_cmd = ' '.join(cmd_parts[1:])
            result = nls_browser_request(nls_cmd)
            if result:
                # Format the result for chat display
                if 'content' in result:
                    message = f"NLS Browse: {result['title']}\n{result['content'][:300]}..."
                elif 'results' in result:
                    message = f"NLS Search: {result['query']}\n" + "\n".join([f"{r['title']}: {r['url']}" for r in result['results'][:3]])
                elif 'bookmarks' in result:
                    message = "NLS Bookmarks:\n" + "\n".join([f"{k}: {v}" for k, v in result['bookmarks'].items()])
                elif 'help' in result:
                    message = "NLS Commands:\n" + "\n".join([f"{k}: {v}" for k, v in result['help'].items()])
                else:
                    message = f"NLS Result: {json.dumps(result, indent=2)[:500]}..."

                chat_entry = {
                    'id': str(uuid.uuid4()),
                    'message': message,
                    'sender': 'NLS_Browser',
                    'timestamp': int(time.time()),
                    'source': 'system'
                }
                chat_history.append(chat_entry)
                socketio.emit('chat_message', chat_entry)

# Browse command is now part of /nls browse

    elif cmd == '/cursor':
        # Cursor Agents IDE command
        if len(cmd_parts) > 1:
            cursor_cmd = ' '.join(cmd_parts[1:])
            result = cursor_agents_request(cursor_cmd, "multimedia_chat")
            if result:
                # Format the result for chat display
                if 'response' in result:
                    message = f"Cursor Agent: {result['response']}"
                elif 'action' in result:
                    message = f"Cursor Agent Action: {result['action']} - {result.get('response', '')}"
                elif 'commands' in result:
                    message = f"Cursor Agent Commands: {'; '.join(result['commands'])}"
                else:
                    message = f"Cursor Agent: {json.dumps(result, indent=2)[:500]}..."

                chat_entry = {
                    'id': str(uuid.uuid4()),
                    'message': message,
                    'sender': 'Cursor_Agent',
                    'timestamp': int(time.time()),
                    'source': 'system'
                }
                chat_history.append(chat_entry)
                socketio.emit('chat_message', chat_entry)

    elif cmd == '/bitchat':
        # BitChat commands
        if len(cmd_parts) > 1:
            subcmd = cmd_parts[1].lower()
            if subcmd == 'room' and len(cmd_parts) > 2:
                room_name = ' '.join(cmd_parts[2:])
                result = create_bitchat_room(room_name)
                response = f"BitChat room created: {result}" if result.get('success') else f"Error: {result.get('error')}"
            elif subcmd == 'send' and len(cmd_parts) > 2:
                msg_content = ' '.join(cmd_parts[2:])
                result = send_bitchat_message(msg_content)
                response = "Message sent to BitChat" if result.get('success') else f"Error: {result.get('error')}"
            else:
                response = "Usage: /bitchat room <name> or /bitchat send <message>"
        else:
            response = "BitChat commands: room, send"

        chat_entry = {
            'id': str(uuid.uuid4()),
            'message': response,
            'sender': 'BitChat_System',
            'timestamp': int(time.time()),
            'source': 'system'
        }
        chat_history.append(chat_entry)
        socketio.emit('chat_message', chat_entry)

# Data Scraper (enhanced with chat data)
def scrape_data():
    while True:
        try:
            # Scrape general data
            response = requests.get('https://api.example.com/data')
            # Process data, perhaps store or use in narrative

            # Scrape chat-related data from various sources
            if chat_history:
                # Analyze recent chat messages for patterns
                recent_messages = [msg for msg in chat_history[-10:]]
                # Could use this for dynamic content generation

            time.sleep(60)  # Scrape every minute
        except Exception as e:
            print(f"Scrape error: {e}")

# OSC Dispatcher
def handle_ableton_message(address, *args):
    print(f"Received from Ableton: {address} {args}")
    events_counter.inc()

    # Handle MIDI note messages for chat integration
    if address == "/midi/note" and len(args) >= 2:
        note = int(args[0])
        velocity = int(args[1])

        # Map MIDI notes to chat commands/VDMX triggers
        if note in CHAT_MIDI_MAPPING and velocity > 0:
            command = CHAT_MIDI_MAPPING[note]

            # Create chat message from MIDI
            chat_entry = {
                'id': str(uuid.uuid4()),
                'message': f"MIDI Trigger: {command}",
                'sender': 'Ableton_DAW',
                'timestamp': int(time.time()),
                'source': 'midi'
            }
            chat_history.append(chat_entry)
            socketio.emit('chat_message', chat_entry)

            # Forward appropriate command to VDMX
            vdmx_client = udp_client.SimpleUDPClient(VDMX_OSC_IP, VDMX_OSC_PORT)
            if command.startswith("play_video_"):
                video_num = command.split("_")[-1]
                vdmx_client.send_message("/video/select", int(video_num))
            elif command == "pause_video":
                vdmx_client.send_message("/video/pause", 1)
            elif command == "stop_video":
                vdmx_client.send_message("/video/stop", 1)
            elif command == "next_video":
                vdmx_client.send_message("/video/next", 1)
            elif command == "prev_video":
                vdmx_client.send_message("/video/prev", 1)

    # Forward general messages to VDMX
    vdmx_client = udp_client.SimpleUDPClient(VDMX_OSC_IP, VDMX_OSC_PORT)
    vdmx_client.send_message(address, args[0] if args else 0)

    # Store on Web3
    if CONTRACT_ADDRESS and CONTRACT_ABI:
        try:
            contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
            tx_hash = contract.functions.storeMetadata(str(args)).transact({'from': w3.eth.accounts[0]})
            metadata_stored.inc()
        except Exception as e:
            print(f"Web3 storage error: {e}")

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/ableton/*", handle_ableton_message)  # Map Ableton messages

# OSC Server
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", ABLETON_OSC_PORT), dispatcher)
print("Serving on {}".format(server.server_address))

# Live Coding Thread (inspired by SuperCollider/Processing)
def live_code_loop():
    # Example: Dynamic code evaluation (be careful in production)
    while True:
        # Could load code from file or input for live changes
        time.sleep(10)
        print("Live code update: Checking for changes...")

# Kubernetes consideration: This script can be containerized
# Dockerfile example would be separate

# Flask Routes for Chat API
@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    return jsonify(chat_history[-50:])  # Return last 50 messages

@app.route('/chat/send', methods=['POST'])
def send_chat_message():
    data = request.json
    message = data.get('message', '')
    sender = data.get('sender', 'API_User')

    chat_entry = {
        'id': str(uuid.uuid4()),
        'message': message,
        'sender': sender,
        'timestamp': int(time.time()),
        'source': 'api'
    }
    chat_history.append(chat_entry)
    socketio.emit('chat_message', chat_entry)

    return jsonify({'status': 'sent', 'message_id': chat_entry['id']})

# Serve Web3Cookie Demo Page
@app.route('/')
def serve_demo():
    try:
        with open('web3_cookie_demo.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return '''
        <html>
        <head><title>Web3Cookie Demo</title></head>
        <body>
        <h1>Web3Cookie Demo</h1>
        <p>Demo page not found. Please ensure web3_cookie_demo.html is in the same directory.</p>
        <a href="/chat">Go to Chat</a>
        </body>
        </html>
        '''

@app.route('/chat')
def serve_chat():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BitChat - Decentralized Multimedia Chat</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            #messages { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; }
            .message { margin: 5px 0; padding: 5px; border-radius: 5px; }
            .system { background: #f0f0f0; }
            .user { background: #e3f2fd; }
            #message-form { display: flex; gap: 10px; }
            #message-input { flex: 1; padding: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>🎵 BitChat - Decentralized Multimedia Chat</h1>
        <div id="messages"></div>
        <form id="message-form">
            <input type="text" id="message-input" placeholder="Type your message..." autocomplete="off">
            <button type="submit">Send</button>
        </form>

        <script>
            const socket = io();
            const messages = document.getElementById('messages');
            const form = document.getElementById('message-form');
            const input = document.getElementById('message-input');

            socket.on('chat_message', function(msg) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (msg.source === 'system' ? 'system' : 'user');
                messageDiv.innerHTML = `<strong>${msg.sender}:</strong> ${msg.message}`;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            });

            form.addEventListener('submit', function(e) {
                e.preventDefault();
                if (input.value) {
                    socket.emit('chat_message', { message: input.value, sender: 'Web_User' });
                    input.value = '';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/bitchat/status', methods=['GET'])
def bitchat_status():
    return jsonify({
        'contract_connected': bitchat_contract is not None,
        'web3_connected': w3.is_connected(),
        'room_id': BITCHAT_ROOM_ID
    })

@app.route('/bitchat/create-room', methods=['POST'])
def create_bitchat_room_api():
    data = request.json
    room_name = data.get('name', 'Multimedia_Room')
    result = create_bitchat_room(room_name)
    return jsonify(result)

@app.route('/bitchat/send', methods=['POST'])
def send_bitchat_message_api():
    data = request.json
    content = data.get('content', '')
    media_type = data.get('media_type', 'text')
    media_hash = data.get('media_hash', '0x0000000000000000000000000000000000000000000000000000000000000000')
    result = send_bitchat_message(content, media_type, media_hash)
    return jsonify(result)

# Web3Cookie API Endpoints
@app.route('/web3cookie/create', methods=['POST'])
def create_web3_cookie_api():
    data = request.json
    domain = data.get('domain', 'localhost')
    cookie_data = data.get('data', '{}')
    expiration_days = data.get('expiration_days', 30)
    result = create_web3_cookie(domain, cookie_data, expiration_days)
    return jsonify(result)

@app.route('/web3cookie/get/<session_id>', methods=['GET'])
def get_web3_cookie_api(session_id):
    result = get_web3_cookie(session_id)
    return jsonify(result)

@app.route('/web3cookie/tracking/update', methods=['POST'])
def update_tracking_api():
    data = request.json
    pointer_movements = data.get('pointer_movements', 0)
    keystrokes = data.get('keystrokes', 0)
    session_duration = data.get('session_duration', 0)
    page_interactions = data.get('page_interactions', [])
    result = update_tracking_data(pointer_movements, keystrokes, session_duration, page_interactions)
    return jsonify(result)

@app.route('/web3cookie/tracking/profile/<user_address>', methods=['GET'])
def get_tracking_profile_api(user_address):
    result = get_tracking_profile(user_address)
    return jsonify(result)

@app.route('/web3cookie/soundcloud/create', methods=['POST'])
def create_soundcloud_cookie_api():
    data = request.json
    preferences = data.get('preferences', {})
    listening_history = data.get('listening_history', [])
    result = create_soundcloud_style_cookie(preferences, listening_history)
    return jsonify(result)

@app.route('/web3cookie/soundcloud/profile', methods=['GET'])
def get_soundcloud_profile_api():
    # Get the user's SoundCloud-style profile
    if not w3.eth.accounts:
        return jsonify({"error": "No Web3 account connected"})

    user_address = w3.eth.accounts[0]
    result = get_tracking_profile(user_address)

    # Add SoundCloud-specific data
    result['soundcloud_features'] = {
        'personalized_recommendations': True,
        'advanced_analytics': True,
        'creator_analytics': True,
        'premium_features': True
    }

    return jsonify(result)

# SocialUnits API Endpoints
@app.route('/socialunits/create', methods=['POST'])
def create_social_unit_api():
    data = request.json
    unit_type = data.get('unit_type', 0)  # BEHAVIOR_PATTERN = 0
    metadata_uri = data.get('metadata_uri', '')
    initial_value = data.get('initial_value', 50)
    result = create_social_unit(unit_type, metadata_uri, initial_value)
    return jsonify(result)

@app.route('/socialunits/update/<int:token_id>', methods=['PUT'])
def update_social_unit_api(token_id):
    data = request.json
    new_value = data.get('new_value', 0)
    attribute_key = data.get('attribute_key', '')
    attribute_value = data.get('attribute_value', 0)
    result = update_social_unit(token_id, new_value, attribute_key, attribute_value)
    return jsonify(result)

@app.route('/socialunits/connection/create', methods=['POST'])
def create_social_connection_api():
    data = request.json
    user_b = data.get('user_b', '')
    connection_type = data.get('connection_type', 1)  # FRIEND = 1
    result = create_social_connection(user_b, connection_type)
    return jsonify(result)

@app.route('/socialunits/recommendations', methods=['POST'])
def generate_recommendations_api():
    data = request.json
    algorithm_id = data.get('algorithm_id', 'content_recommendation')
    user_address = data.get('user_address', '')
    candidate_units = data.get('candidate_units', [])
    result = generate_recommendations(algorithm_id, user_address, candidate_units)
    return jsonify(result)

@app.route('/socialunits/engagement/<user_address>', methods=['GET'])
def get_engagement_score_api(user_address):
    result = get_engagement_score(user_address)
    return jsonify(result)

@app.route('/socialunits/similar/<user_address>', methods=['GET'])
def find_similar_users_api(user_address):
    max_results = int(request.args.get('max_results', 10))
    result = find_similar_users(user_address, max_results)
    return jsonify(result)

@app.route('/socialunits/algorithm/content', methods=['POST'])
def get_content_recommendations_api():
    data = request.json
    user_address = data.get('user_address', '')
    content_items = data.get('content_items', [])

    # Use content recommendation algorithm
    result = generate_recommendations('content_recommendation', user_address, content_items)
    return jsonify(result)

@app.route('/socialunits/algorithm/friends', methods=['POST'])
def get_friend_suggestions_api():
    data = request.json
    user_address = data.get('user_address', '')
    user_list = data.get('user_list', [])

    # Use friend suggestion algorithm
    result = generate_recommendations('friend_suggestion', user_address, user_list)
    return jsonify(result)

@app.route('/vdmx/status', methods=['GET'])
def vdmx_status():
    # Simple ping to check VDMX connection
    try:
        vdmx_client = udp_client.SimpleUDPClient(VDMX_OSC_IP, VDMX_OSC_PORT)
        vdmx_client.send_message("/ping", 1)
        return jsonify({'status': 'connected'})
    except:
        return jsonify({'status': 'disconnected'})

# Live Coding Thread (enhanced with chat integration)
def live_code_loop():
    while True:
        # Could load code from file or input for live changes
        # Check for new chat commands that might affect behavior
        if chat_history:
            recent_commands = [msg for msg in chat_history[-5:] if msg['message'].startswith('/')]
            if recent_commands:
                # Process recent commands for live coding
                pass

        time.sleep(10)
        print("Live code update: Checking for changes...")

# Main execution with all services
if __name__ == "__main__":
    # Start scraper in background
    scraper_thread = threading.Thread(target=scrape_data, daemon=True)
    scraper_thread.start()

    # Start live code loop
    live_thread = threading.Thread(target=live_code_loop, daemon=True)
    live_thread.start()

    # Start BitChat monitor in background
    bitchat_thread = threading.Thread(target=bitchat_monitor, daemon=True)
    bitchat_thread.start()

    # Start Flask chat app in separate thread
    def run_flask():
        socketio.run(app, host='0.0.0.0', port=CHAT_PORT, debug=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    print(f"BitChat server running on port {CHAT_PORT}")
    print(f"Prometheus metrics on port 8000")
    print("BitChat Web3 Blockcode System Active")
    print("Form follows function: Modular design for multimedia integration")
    print("NLS Browser API and Cursor Agents IDE integrated")

    # Start OSC server (main thread)
    server.serve_forever()
