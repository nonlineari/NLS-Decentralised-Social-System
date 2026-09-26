# BitChat: Decentralized Multimedia Chat System

A complete Web3-powered chat program that integrates BitChat blockchain messaging with Ableton DAW, VDMX6+, and live coding environments. Features form-follows-function design with Prometheus monitoring and Kubernetes deployment.

## 🎯 System Overview

**BitChat** is a decentralized multimedia communication platform that bridges traditional DAW software with blockchain technology. The system enables real-time chat between creative tools using Web3 smart contracts, with integrated data scraping, live coding capabilities, and automated agent management.

### Key Components

- **BitChat Smart Contract**: Decentralized messaging on Ethereum
- **OSC Bridge**: Real-time communication between Ableton DAW and VDMX6+
- **Web Chat Interface**: Real-time chat with SocketIO
- **NLS Browser API**: Text-based web browsing within chat
- **Cursor Agents IDE**: Automated multimedia coordination
- **Prometheus Monitoring**: System metrics and health monitoring
- **Kubernetes Deployment**: Containerized, scalable deployment

## 🚀 Quick Start

### Prerequisites

1. **Deploy BitChat Contract**:
   ```bash
   # Deploy BitChat.sol to Ethereum testnet
   # Update BITCHAT_CONTRACT_ADDRESS in ableton_vdmx_web3_bridge.py
   ```

2. **Install Dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   ```bash
   export WEB3_INFURA_KEY="your_infura_key"
   export BITCHAT_CONTRACT_ADDRESS="0xYourContractAddress"
   ```

### Running the System

```bash
# Activate virtual environment
source venv/bin/activate

# Start the complete system
python ableton_vdmx_web3_bridge.py
```

The system will start:
- OSC server on port 9000 (Ableton communication)
- Web chat on port 5000
- Prometheus metrics on port 8000
- BitChat blockchain monitoring

## 🎛️ Chat Commands

### BitChat Commands
```
/bitchat room <name>     # Create new chat room
/bitchat send <message>  # Send message to blockchain
```

### Multimedia Control
```
/vdmx play               # Start VDMX playback
/vdmx pause              # Pause VDMX
/vdmx select <number>    # Select video segment
/ableton play            # Start Ableton playback
```

### NLS Browser
```
/nls browse <url>        # Browse webpage
/nls search <query>      # Web search
/nls bookmark <name> <url> # Add bookmark
/nls history             # Show browsing history
```

### Cursor Agents
```
/cursor sync video audio # Coordinate multimedia
/cursor moderate chat    # Chat moderation
/cursor analyze patterns # Data analysis
```

## 🔧 Architecture

### Form Follows Function Design

The system follows a modular, function-driven architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ableton DAW   │◄──►│   OSC Bridge     │◄──►│   VDMX6+        │
│   MIDI Events   │    │   Web3 Storage   │    │   Video Control  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BitChat       │    │   Web Interface │    │   Cursor Agents  │
│   Blockchain    │    │   Real-time     │    │   Automation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Prometheus    │    │   NLS Browser   │    │   Kubernetes     │
│   Monitoring    │    │   Text Web      │    │   Deployment     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Ableton** → OSC → **Bridge** → Web3 → **BitChat Contract**
2. **VDMX** ← OSC ← **Bridge** ← Web3 ← **BitChat Contract**
3. **Web Chat** ↔ SocketIO ↔ **Bridge** ↔ **BitChat Contract**
4. **Cursor Agents** → Commands → **Bridge** → **Multimedia Systems**

## 📊 Monitoring & Metrics

### Prometheus Metrics

- `events_processed`: OSC events from Ableton
- `bitchat_messages`: Messages sent to blockchain
- `bitchat_rooms`: Chat rooms created
- `chat_messages`: Total chat messages

### Health Checks

- Web3 connection status
- BitChat contract connectivity
- OSC communication health
- Kubernetes pod status

## 🐳 Kubernetes Deployment

### Deploy to Kubernetes

```bash
# Build Docker image
docker build -t bitchat-system .

# Deploy to Kubernetes
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Service Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: bitchat-service
spec:
  selector:
    app: bitchat
  ports:
    - name: osc
      port: 9000
      targetPort: 9000
    - name: web
      port: 5000
      targetPort: 5000
    - name: metrics
      port: 8000
      targetPort: 8000
```

## 🔒 Security Considerations

### Web3 Security
- Use hardware wallets for production
- Implement proper access controls
- Monitor gas costs and transaction fees

### Network Security
- Use HTTPS for web interface
- Implement rate limiting
- Secure OSC communication

### Data Privacy
- Messages stored on public blockchain
- Consider encryption for sensitive data
- Implement user consent mechanisms

## 🎨 Live Coding Integration

### SuperCollider Integration
```supercollider
// OSC communication with BitChat
n = NetAddr("localhost", 9000);
n.sendMsg("/bitchat/send", "Live coded message from SuperCollider");
```

### Processing Integration
```java
// OSC to BitChat from Processing
import oscP5.*;
OscP5 osc;
NetAddress bridgeAddr;

void setup() {
  osc = new OscP5(this, 12000);
  bridgeAddr = new NetAddress("127.0.0.1", 9000);
}

void draw() {
  // Send multimedia events to BitChat
  OscMessage msg = new OscMessage("/bitchat/send");
  msg.add("Processing frame: " + frameCount);
  osc.send(msg, bridgeAddr);
}
```

## 📈 Performance Optimization

### Video Processing
- Use H.264 compression
- Implement frame rate limiting
- Cache frequently used assets

### Blockchain Optimization
- Batch transactions where possible
- Monitor gas prices
- Use Layer 2 solutions for mainnet

### Network Optimization
- Implement connection pooling
- Use WebSocket compression
- Cache DNS resolutions

## 🔧 Configuration

### Environment Variables

```bash
# Web3 Configuration
WEB3_INFURA_KEY=your_infura_key
BITCHAT_CONTRACT_ADDRESS=0xYourContractAddress

# Chat Configuration
CHAT_PORT=5000
OSC_PORT=9000

# Monitoring
PROMETHEUS_PORT=8000
```

### Smart Contract Deployment

```javascript
// Deploy BitChat.sol using Remix or Hardhat
const BitChat = await ethers.getContractFactory("BitChat");
const bitchat = await BitChat.deploy();
await bitchat.deployed();
console.log("BitChat deployed to:", bitchat.address);
```

## 🚨 Troubleshooting

### Common Issues

1. **OSC Connection Failed**
   - Check firewall settings
   - Verify port availability
   - Ensure Ableton OSC is configured

2. **Web3 Connection Error**
   - Verify Infura key
   - Check network connectivity
   - Confirm contract address

3. **BitChat Messages Not Appearing**
   - Check contract deployment
   - Verify transaction confirmations
   - Monitor blockchain explorer

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
python ableton_vdmx_web3_bridge.py
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes with form-follows-function principle
4. Add tests and documentation
5. Submit pull request

### Code Standards

- Follow PEP 8 for Python
- Use Solidity style guide for contracts
- Maintain modular architecture
- Document all public APIs

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by form-follows-function design principles
- Built with Web3, OSC, and real-time communication technologies
- Integrated with creative tools: Ableton, VDMX, SuperCollider, Processing

---

**Form follows function: A modular system where each component serves its purpose efficiently within the greater multimedia ecosystem.**
