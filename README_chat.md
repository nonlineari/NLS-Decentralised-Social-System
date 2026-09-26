# ICQ Chat Bridge - Ableton VDMX Web3 Integration

A form-follows-function multimedia chat system that bridges Ableton DAW, VDMX6+, Web3 blockcode, and various browser APIs in a modular, efficient architecture.

## Features

### 🎵 **Ableton DAW Integration**
- OSC communication for real-time MIDI control
- MIDI note-to-chat mapping (C4=E4 triggers video commands)
- Live performance data streaming

### 🎬 **VDMX6+ Integration**
- OSC control for video playback and effects
- Chat command interface (`/vdmx play`, `/vdmx stop`)
- Real-time video triggering from chat/MIDI

### 💬 **ICQ Chat Protocol**
- Telegram-based ICQ messaging (modern ICQ uses Telegram backend)
- Cross-platform chat between DAW and video systems
- Command processing in chat messages

### 🌐 **Web3 Blockcode**
- Chat messages stored on blockchain
- Immutable message history
- Decentralized multimedia metadata

### 🔍 **Data Scraping & Monitoring**
- Prometheus metrics for system monitoring
- Custom data scrapers for content generation
- Kubernetes-ready deployment

### 🌍 **Browser API Integration**
- **NLS Browser API**: Natural language search and queries
- **Text Browser API**: Web content extraction and processing
- **Cursor Agents IDE**: AI-assisted code generation and commands

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ableton DAW   │───▶│  Python Bridge  │───▶│    VDMX6+       │
│   (OSC/MIDI)    │    │  (Flask/Socket) │    │   (OSC/Video)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ICQ/Telegram  │    │   Web3 Block    │    │   Prometheus     │
│   Chat System   │    │   Chain Storage │    │   Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ NLS Browser API │    │ Text Browser    │    │ Cursor Agents   │
│ (NL Search)     │    │ (Web Content)   │    │ IDE (AI Code)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Setup Instructions

### 1. Environment Variables
```bash
export ICQ_TOKEN="your_icq_bot_token"
export TELEGRAM_API_ID="your_telegram_api_id"
export TELEGRAM_API_HASH="your_telegram_api_hash"
export TELEGRAM_PHONE="+1234567890"
export WEB3_INFURA_KEY="your_infura_key"
export CHAT_CONTRACT_ADDRESS="0xYourChatContractAddress"
```

### 2. Install Dependencies
```bash
source venv/bin/activate
pip install python-osc web3 flask flask-socketio telethon requests-html beautifulsoup4 prometheus-client
```

### 3. Run the System
```bash
python ableton_vdmx_web3_bridge.py
```

### 4. Access Interfaces
- **Chat Web Interface**: http://localhost/chat_interface.html
- **Chat API**: http://localhost:5000
- **Prometheus Metrics**: http://localhost:8000
- **ICQ Status**: http://localhost:5000/icq/status

## Chat Commands

### VDMX Control
```
/vdmx play          # Start video playback
/vdmx stop          # Stop video playback
/vdmx pause         # Pause video
/vdmx next          # Next video
/vdmx prev          # Previous video
```

### Ableton Control
```
/ableton play       # Start playback
/ableton stop       # Stop playback
/ableton record     # Start recording
```

### Browser Integration
```
/nls [query]        # Natural language search via NLS API
/browse [url]       # Extract text content from website
/cursor [command]   # Execute AI-assisted IDE commands
```

### MIDI Mapping
- **C4 (60)**: Play Video 1
- **D4 (62)**: Play Video 2
- **E4 (64)**: Play Video 3
- **F4 (65)**: Pause Video
- **G4 (67)**: Stop Video
- **A4 (69)**: Next Video
- **B4 (71)**: Previous Video

## Kubernetes Deployment

```bash
# Build and deploy
docker build -t multimedia-chat-bridge .
kubectl apply -f deployment.yaml
```

## Form Follows Function

This system embodies "form follows function" through:
- **Modular Architecture**: Each component serves a single purpose
- **Efficient Communication**: OSC/WebSocket for real-time data
- **Scalable Design**: Container-ready with monitoring
- **Live Coding**: Dynamic code evaluation for performance
- **Blockchain Integration**: Immutable data storage for multimedia metadata

## Monitoring

Access Prometheus metrics at `http://localhost:8000` to monitor:
- Events processed
- Chat messages sent
- Metadata stored on blockchain
- ICQ message traffic

## License

Form follows function - use responsibly for multimedia art and performance.
