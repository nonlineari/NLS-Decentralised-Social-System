#!/bin/bash

# Decentralized Social System Deployment Script
# Deploys Web3Cookie, SocialUnits, and BitChat systems

set -e  # Exit on any error

echo "🌐 Decentralized Social System Deployment"
echo "=========================================="

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

# Check prerequisites
print_status "Checking prerequisites..."

command -v node >/dev/null 2>&1 || {
    print_error "Node.js is required but not installed."
    exit 1
}

command -v npm >/dev/null 2>&1 || {
    print_error "npm is required but not installed."
    exit 1
}

command -v python3 >/dev/null 2>&1 || {
    print_error "Python 3 is required but not installed."
    exit 1
}

print_success "Prerequisites check passed"

# Check for MetaMask reminder
print_warning "IMPORTANT: Ensure MetaMask or a Web3 wallet is installed in your browser"
print_warning "You'll need to connect your wallet and deploy smart contracts"

# Create necessary directories
print_status "Creating project directories..."
mkdir -p contracts
mkdir -p test
mkdir -p scripts
mkdir -p docs
print_success "Directories created"

# Check for smart contracts
CONTRACTS=("Web3Cookie.sol" "SocialUnits.sol" "BitChat.sol")
for contract in "${CONTRACTS[@]}"; do
    if [ -f "$contract" ]; then
        print_success "Found $contract"
    else
        print_error "Missing $contract"
        exit 1
    fi
done

# Check for JavaScript files
JS_FILES=("web3_cookie_tracker.js" "social_units_tracker.js")
for js_file in "${JS_FILES[@]}"; do
    if [ -f "$js_file" ]; then
        print_success "Found $js_file"
    else
        print_error "Missing $js_file"
        exit 1
    fi
done

# Check for HTML demos
HTML_FILES=("web3_cookie_demo.html" "social_units_demo.html")
for html_file in "${HTML_FILES[@]}"; do
    if [ -f "$html_file" ]; then
        print_success "Found $html_file"
    else
        print_error "Missing $html_file"
        exit 1
    fi
done

# Initialize Hardhat project for smart contracts
if [ ! -f "hardhat.config.js" ]; then
    print_status "Initializing Hardhat project..."
    npm init -y
    npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
    npx hardhat init --yes

    # Configure Hardhat for Sepolia
    cat > hardhat.config.js << 'EOL'
require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.19",
  networks: {
    sepolia: {
      url: `https://sepolia.infura.io/v3/${process.env.INFURA_KEY}`,
      accounts: [process.env.PRIVATE_KEY]
    }
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_KEY
  }
};
EOL
    print_success "Hardhat project initialized"
else
    print_warning "Hardhat project already exists"
fi

# Create deployment script
if [ ! -f "scripts/deploy.js" ]; then
    print_status "Creating deployment script..."
    cat > scripts/deploy.js << 'EOL'
const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying Decentralized Social System contracts...");

  // Deploy Web3Cookie
  console.log("Deploying Web3Cookie...");
  const Web3Cookie = await ethers.getContractFactory("Web3Cookie");
  const web3cookie = await Web3Cookie.deploy();
  await web3cookie.deployed();
  console.log("Web3Cookie deployed to:", web3cookie.address);

  // Deploy SocialUnits
  console.log("Deploying SocialUnits...");
  const SocialUnits = await ethers.getContractFactory("SocialUnits");
  const socialunits = await SocialUnits.deploy();
  await socialunits.deployed();
  console.log("SocialUnits deployed to:", socialunits.address);

  // Deploy BitChat
  console.log("Deploying BitChat...");
  const BitChat = await ethers.getContractFactory("BitChat");
  const bitchat = await BitChat.deploy();
  await bitchat.deployed();
  console.log("BitChat deployed to:", bitchat.address);

  // Save deployment addresses
  const fs = require("fs");
  const deployment = {
    web3cookie: web3cookie.address,
    socialunits: socialunits.address,
    bitchat: bitchat.address,
    network: network.name,
    timestamp: new Date().toISOString()
  };

  fs.writeFileSync("deployment.json", JSON.stringify(deployment, null, 2));
  console.log("Deployment addresses saved to deployment.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
EOL
    print_success "Deployment script created"
fi

# Create environment template
if [ ! -f ".env.example" ]; then
    print_status "Creating environment template..."
    cat > .env.example << 'EOL'
# Web3 Configuration
INFURA_KEY=your_infura_project_key
PRIVATE_KEY=your_private_key_without_0x_prefix
ETHERSCAN_KEY=your_etherscan_api_key

# Contract Addresses (after deployment)
WEB3COOKIE_CONTRACT_ADDRESS=0x...
SOCIALUNITS_CONTRACT_ADDRESS=0x...
BITCHAT_CONTRACT_ADDRESS=0x...

# ICQ/Telegram (optional)
ICQ_TOKEN=your_icq_bot_token
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_PHONE=+1234567890

# NLS/Text Browser (optional)
NLS_BROWSER_API_KEY=your_nls_api_key
TEXT_BROWSER_API_KEY=your_text_browser_api_key
CURSOR_AGENTS_API_KEY=your_cursor_agents_api_key
EOL
    print_success "Environment template created"
fi

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Created .env file from template. Please fill in your values."
fi

# Create test files
if [ ! -f "test/Web3Cookie.test.js" ]; then
    print_status "Creating basic test files..."
    cat > test/Web3Cookie.test.js << 'EOL'
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Web3Cookie", function () {
  let Web3Cookie, web3cookie, owner, addr1;

  beforeEach(async function () {
    Web3Cookie = await ethers.getContractFactory("Web3Cookie");
    [owner, addr1] = await ethers.getSigners();
    web3cookie = await Web3Cookie.deploy();
    await web3cookie.deployed();
  });

  it("Should create a cookie", async function () {
    const tx = await web3cookie.createCookie("example.com", "test data", 30);
    await tx.wait();

    // Check that cookie was created (events would be checked in full implementation)
    expect(await web3cookie.totalCookies()).to.be.above(0);
  });
});
EOL
    print_success "Test files created"
fi

# Final setup instructions
echo ""
echo "🎉 Decentralized Social System Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Fill in your .env file with API keys and private key"
echo "2. Deploy smart contracts: npx hardhat run scripts/deploy.js --network sepolia"
echo "3. Update contract addresses in ableton_vdmx_web3_bridge.py"
echo "4. Run the Python backend: source venv/bin/activate && python ableton_vdmx_web3_bridge.py"
echo "5. Open demos:"
echo "   - Web3Cookie: http://localhost"
echo "   - SocialUnits: http://localhost/social_units_demo.html"
echo "   - BitChat: http://localhost/chat"
echo ""
echo "🔗 System Components:"
echo "- Web3Cookie: Decentralized session management (no HTTP cookies)"
echo "- SocialUnits: NFT-based social behavior tracking"
echo "- BitChat: Decentralized multimedia chat"
echo "- Pointer/Keystroke Tracking: Advanced behavioral analytics"
echo ""
echo "📊 Monitoring:"
echo "- Prometheus metrics: http://localhost:8000"
echo "- API endpoints: http://localhost:5000/api"
echo ""
echo "Happy decentralized social networking! 🌐⚡🔗"
echo ""

# Offer to install additional dependencies
read -p "Install additional npm dependencies for smart contract development? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing additional dependencies..."
    npm install --save-dev @openzeppelin/contracts dotenv
    print_success "Additional dependencies installed"
fi

# Offer to run tests
read -p "Run smart contract tests? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running tests..."
    npx hardhat test
fi
