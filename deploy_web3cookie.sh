#!/bin/bash

# Web3Cookie & BitChat Deployment Script
# This script sets up the complete Web3Cookie system with BitChat integration

set -e  # Exit on any error

echo "🍪 Web3Cookie & BitChat Deployment Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
else
    print_error "Unsupported OS: $OSTYPE"
    exit 1
fi

print_status "Detected OS: $OS"

# Check for required tools
command -v python3 >/dev/null 2>&1 || {
    print_error "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
}

command -v pip3 >/dev/null 2>&1 || {
    print_error "pip3 is required but not installed. Please install pip3 first."
    exit 1
}

print_success "Python 3 and pip3 are available"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip
print_success "pip upgraded"

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Python dependencies installed"

# Check for MetaMask or Web3 wallet recommendation
print_warning "IMPORTANT: Make sure you have a Web3 wallet (like MetaMask) installed in your browser"
print_warning "You will need to connect your wallet when accessing the Web3Cookie demo"

# Check for contract deployment
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating template..."
    cat > .env << EOL
# Web3Cookie Configuration
WEB3_INFURA_KEY=your_infura_key_here
WEB3COOKIE_CONTRACT_ADDRESS=0xYourWeb3CookieContractAddress
BITCHAT_CONTRACT_ADDRESS=0xYourBitChatContractAddress

# ICQ/Telegram Configuration (optional)
ICQ_TOKEN=your_icq_bot_token
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_PHONE=+1234567890

# NLS Browser API (optional)
NLS_BROWSER_API_KEY=your_nls_api_key
TEXT_BROWSER_API_KEY=your_text_browser_api_key
CURSOR_AGENTS_API_KEY=your_cursor_agents_api_key
EOL
    print_warning "Please edit the .env file with your actual configuration values"
    print_warning "You need to deploy the smart contracts and get their addresses"
else
    print_success ".env file already exists"
fi

# Make the script executable (for the main application)
if [ -f "ableton_vdmx_web3_bridge.py" ]; then
    chmod +x ableton_vdmx_web3_bridge.py
    print_success "Main application script is executable"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p video_analysis_output/processed
mkdir -p logs
print_success "Directories created"

# Check for smart contract files
if [ -f "Web3Cookie.sol" ] && [ -f "BitChat.sol" ]; then
    print_success "Smart contract files found"
    print_status "To deploy contracts:"
    echo "  1. Use Remix IDE (remix.ethereum.org)"
    echo "  2. Or use Hardhat/Truffle"
    echo "  3. Update contract addresses in ableton_vdmx_web3_bridge.py"
else
    print_error "Smart contract files not found!"
    exit 1
fi

# Check for demo files
if [ -f "web3_cookie_demo.html" ] && [ -f "web3_cookie_tracker.js" ]; then
    print_success "Demo files found"
else
    print_error "Demo files not found!"
    exit 1
fi

# Docker check (optional)
if command -v docker >/dev/null 2>&1; then
    print_success "Docker is available"
    print_status "To build Docker image: docker build -t web3cookie-system ."
else
    print_warning "Docker not found. Consider installing Docker for containerized deployment"
fi

# Final instructions
echo ""
echo "🎉 Web3Cookie & BitChat System Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Deploy Web3Cookie.sol and BitChat.sol contracts to Ethereum testnet"
echo "2. Update contract addresses in ableton_vdmx_web3_bridge.py"
echo "3. Configure your .env file with API keys"
echo "4. Run the system: source venv/bin/activate && python ableton_vdmx_web3_bridge.py"
echo "5. Open http://localhost in your browser"
echo ""
echo "Ports used:"
echo "- 80: Web interface (nginx)"
echo "- 5000: Flask/SocketIO chat server"
echo "- 9000: OSC communication (Ableton/VDMX)"
echo "- 8000: Prometheus metrics"
echo ""
echo "Happy Web3Cookie tracking! 🍪⚡🔐"
echo ""

# Offer to start the system
read -p "Would you like to start the Web3Cookie system now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting Web3Cookie system..."
    python ableton_vdmx_web3_bridge.py
fi
