/**
 * Web3Cookie Tracker: Advanced Cookie Management with Pointer/Keystroke Tracking
 * Replaces traditional cookies with blockchain-based session management
 * Includes SoundCloud-style tracking capabilities
 */

class Web3CookieTracker {
    constructor(web3Provider, contractAddress, contractABI) {
        this.web3 = new Web3(web3Provider);
        this.contractAddress = contractAddress;
        this.contractABI = contractABI;
        this.contract = null;
        this.currentAccount = null;
        this.sessionId = null;

        // Tracking data
        this.pointerMovements = 0;
        this.keystrokes = 0;
        this.sessionStart = Date.now();
        this.pageInteractions = new Map();
        this.mousePath = [];
        this.keystrokePattern = [];

        // SoundCloud-style preferences
        this.soundcloudPrefs = {
            volume: 0.7,
            quality: 'HIGH',
            autoplay: true,
            repeat: 'NONE',
            shuffle: false,
            likedTracks: new Set(),
            following: new Set(),
            listeningHistory: []
        };

        this.init();
    }

    async init() {
        try {
            this.contract = new this.web3.eth.Contract(this.contractABI, this.contractAddress);

            // Connect to MetaMask or other Web3 wallet
            if (typeof window.ethereum !== 'undefined') {
                await this.connectWallet();
            }

            this.setupEventListeners();
            this.startTracking();

        } catch (error) {
            console.error('Web3Cookie initialization failed:', error);
        }
    }

    async connectWallet() {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            this.currentAccount = accounts[0];
            console.log('Connected to Web3 wallet:', this.currentAccount);
        } catch (error) {
            console.error('Wallet connection failed:', error);
        }
    }

    setupEventListeners() {
        // Mouse movement tracking
        document.addEventListener('mousemove', this.trackMouseMovement.bind(this));

        // Keystroke tracking
        document.addEventListener('keydown', this.trackKeystroke.bind(this));

        // Page interaction tracking
        document.addEventListener('click', this.trackClick.bind(this));
        document.addEventListener('scroll', this.trackScroll.bind(this));

        // SoundCloud-style event tracking
        this.setupSoundCloudTracking();

        // Session management
        window.addEventListener('beforeunload', this.saveSessionData.bind(this));
        window.addEventListener('focus', () => this.trackPageInteraction('focus'));
        window.addEventListener('blur', () => this.trackPageInteraction('blur'));
    }

    // Mouse/Pointer Tracking
    trackMouseMovement(event) {
        this.pointerMovements++;

        // Store mouse path for pattern analysis (limit to last 100 points)
        this.mousePath.push({
            x: event.clientX,
            y: event.clientY,
            timestamp: Date.now()
        });

        if (this.mousePath.length > 100) {
            this.mousePath.shift();
        }

        // Throttle blockchain updates to avoid excessive gas costs
        if (this.pointerMovements % 50 === 0) {
            this.updateTrackingData();
        }
    }

    // Keystroke Tracking
    trackKeystroke(event) {
        this.keystrokes++;

        // Store keystroke pattern (without actual key content for privacy)
        this.keystrokePattern.push({
            timestamp: Date.now(),
            keyType: event.key.length === 1 ? 'character' : 'special',
            ctrlKey: event.ctrlKey,
            shiftKey: event.shiftKey,
            altKey: event.altKey
        });

        // Limit pattern history
        if (this.keystrokePattern.length > 200) {
            this.keystrokePattern.shift();
        }
    }

    // Click Tracking
    trackClick(event) {
        const element = event.target;
        const interaction = {
            type: 'click',
            element: element.tagName.toLowerCase(),
            class: element.className,
            id: element.id,
            timestamp: Date.now(),
            x: event.clientX,
            y: event.clientY
        };

        this.trackPageInteraction('click', interaction);
    }

    // Scroll Tracking
    trackScroll(event) {
        const scrollY = window.scrollY;
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;

        if (maxScroll > 0) {
            const scrollPercent = (scrollY / maxScroll) * 100;
            this.trackPageInteraction('scroll', { percentage: Math.round(scrollPercent) });
        }
    }

    // SoundCloud-style Tracking Implementation
    setupSoundCloudTracking() {
        // Track audio playback
        document.addEventListener('play', (e) => {
            if (e.target.tagName === 'AUDIO' || e.target.tagName === 'VIDEO') {
                this.trackSoundCloudEvent('play', e.target.currentSrc);
            }
        }, true);

        document.addEventListener('pause', (e) => {
            if (e.target.tagName === 'AUDIO' || e.target.tagName === 'VIDEO') {
                this.trackSoundCloudEvent('pause', e.target.currentSrc);
            }
        }, true);

        document.addEventListener('ended', (e) => {
            if (e.target.tagName === 'AUDIO' || e.target.tagName === 'VIDEO') {
                this.trackSoundCloudEvent('ended', e.target.currentSrc);
            }
        }, true);

        // Track likes/follows (simulate with custom events)
        document.addEventListener('soundcloud-like', (e) => {
            this.soundcloudPrefs.likedTracks.add(e.detail.trackId);
            this.updateSoundCloudCookie();
        });

        document.addEventListener('soundcloud-follow', (e) => {
            this.soundcloudPrefs.following.add(e.detail.userId);
            this.updateSoundCloudCookie();
        });
    }

    trackSoundCloudEvent(eventType, trackUrl) {
        const trackInfo = {
            event: eventType,
            track: trackUrl,
            timestamp: Date.now(),
            volume: this.soundcloudPrefs.volume,
            quality: this.soundcloudPrefs.quality
        };

        this.soundcloudPrefs.listeningHistory.push(trackInfo);

        // Limit history to last 1000 events
        if (this.soundcloudPrefs.listeningHistory.length > 1000) {
            this.soundcloudPrefs.listeningHistory.shift();
        }

        this.updateSoundCloudCookie();
        this.trackPageInteraction('soundcloud_' + eventType, trackInfo);
    }

    // General page interaction tracking
    trackPageInteraction(interactionType, data = null) {
        const key = data ? `${interactionType}_${JSON.stringify(data)}` : interactionType;
        this.pageInteractions.set(key, (this.pageInteractions.get(key) || 0) + 1);
    }

    // Web3 Cookie Management
    async createWeb3Cookie(domain, data, expirationDays = 30) {
        if (!this.contract || !this.currentAccount) return null;

        try {
            const result = await this.contract.methods.createCookie(
                domain,
                data,
                expirationDays
            ).send({ from: this.currentAccount });

            this.sessionId = result.events.CookieCreated.returnValues.sessionId;
            console.log('Web3Cookie created:', this.sessionId);
            return this.sessionId;
        } catch (error) {
            console.error('Failed to create Web3Cookie:', error);
            return null;
        }
    }

    async getWeb3Cookie(sessionId) {
        if (!this.contract || !this.currentAccount) return null;

        try {
            const cookieData = await this.contract.methods.getCookie(sessionId).call({
                from: this.currentAccount
            });
            return cookieData;
        } catch (error) {
            console.error('Failed to get Web3Cookie:', error);
            return null;
        }
    }

    async updateWeb3Cookie(sessionId, newData) {
        if (!this.contract || !this.currentAccount) return false;

        try {
            await this.contract.methods.updateCookie(sessionId, newData).send({
                from: this.currentAccount
            });
            return true;
        } catch (error) {
            console.error('Failed to update Web3Cookie:', error);
            return false;
        }
    }

    async createSoundCloudCookie() {
        if (!this.contract || !this.currentAccount) return null;

        try {
            const result = await this.contract.methods.createSoundCloudStyleCookie(
                JSON.stringify({
                    volume: this.soundcloudPrefs.volume,
                    quality: this.soundcloudPrefs.quality,
                    autoplay: this.soundcloudPrefs.autoplay,
                    repeat: this.soundcloudPrefs.repeat,
                    shuffle: this.soundcloudPrefs.shuffle
                }),
                this.soundcloudPrefs.listeningHistory.slice(-50), // Last 50 tracks
                365 // 1 year expiration
            ).send({ from: this.currentAccount });

            console.log('SoundCloud-style Web3Cookie created');
            return result.events.CookieCreated.returnValues.sessionId;
        } catch (error) {
            console.error('Failed to create SoundCloud cookie:', error);
            return null;
        }
    }

    async updateSoundCloudCookie() {
        if (!this.sessionId) {
            await this.createSoundCloudCookie();
            return;
        }

        const cookieData = JSON.stringify({
            preferences: this.soundcloudPrefs,
            tracking: {
                pointerMovements: this.pointerMovements,
                keystrokes: this.keystrokes,
                sessionDuration: Date.now() - this.sessionStart,
                pageInteractions: Object.fromEntries(this.pageInteractions)
            }
        });

        await this.updateWeb3Cookie(this.sessionId, cookieData);
    }

    // Consent Management
    async giveConsent() {
        if (!this.contract || !this.currentAccount) return false;

        try {
            await this.contract.methods.giveConsent().send({
                from: this.currentAccount
            });
            console.log('User consent given for tracking');
            return true;
        } catch (error) {
            console.error('Failed to give consent:', error);
            return false;
        }
    }

    async revokeConsent() {
        if (!this.contract || !this.currentAccount) return false;

        try {
            await this.contract.methods.revokeConsent().send({
                from: this.currentAccount
            });
            console.log('User consent revoked');
            return true;
        } catch (error) {
            console.error('Failed to revoke consent:', error);
            return false;
        }
    }

    // Update tracking data on blockchain
    async updateTrackingData() {
        if (!this.contract || !this.currentAccount) return;

        try {
            const pageInteractions = Array.from(this.pageInteractions.keys());
            await this.contract.methods.updateTrackingData(
                this.pointerMovements,
                this.keystrokes,
                Math.floor((Date.now() - this.sessionStart) / 1000), // Convert to seconds
                pageInteractions
            ).send({ from: this.currentAccount });
        } catch (error) {
            console.error('Failed to update tracking data:', error);
        }
    }

    // Save session data before page unload
    async saveSessionData() {
        if (this.contract && this.currentAccount) {
            await this.updateTrackingData();
            await this.updateSoundCloudCookie();
        }
    }

    // Start tracking with user consent
    async startTracking() {
        const consent = await this.requestUserConsent();
        if (consent) {
            await this.giveConsent();
            this.createSoundCloudCookie();
            console.log('Web3Cookie tracking started');
        }
    }

    // Request user consent
    async requestUserConsent() {
        return new Promise((resolve) => {
            const consent = confirm(
                'This site uses Web3Cookie tracking to improve your experience. ' +
                'Your mouse movements and keystrokes will be anonymously tracked ' +
                'and stored on the blockchain. Do you consent?'
            );
            resolve(consent);
        });
    }

    // Get tracking statistics
    getTrackingStats() {
        return {
            pointerMovements: this.pointerMovements,
            keystrokes: this.keystrokes,
            sessionDuration: Date.now() - this.sessionStart,
            pageInteractions: Object.fromEntries(this.pageInteractions),
            soundcloudPrefs: this.soundcloudPrefs,
            mousePathLength: this.mousePath.length,
            keystrokePatternLength: this.keystrokePattern.length
        };
    }

    // Export tracking data for analysis
    exportTrackingData() {
        return {
            sessionId: this.sessionId,
            stats: this.getTrackingStats(),
            mousePath: this.mousePath.slice(-50), // Last 50 points
            keystrokePattern: this.keystrokePattern.slice(-50), // Last 50 keystrokes
            timestamp: Date.now()
        };
    }
}

// Initialize Web3Cookie Tracker when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Configuration - replace with your actual contract details
    const config = {
        web3Provider: 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY',
        contractAddress: '0xYourWeb3CookieContractAddress',
        contractABI: [
            // ABI from Web3Cookie.sol
            {
                "inputs": [{"internalType": "string", "name": "domain", "type": "string"}, {"internalType": "string", "name": "data", "type": "string"}, {"internalType": "uint256", "name": "expirationDays", "type": "uint256"}],
                "name": "createCookie",
                "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "giveConsent",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "pointerMovements", "type": "uint256"}, {"internalType": "uint256", "name": "keystrokes", "type": "uint256"}, {"internalType": "uint256", "name": "sessionDuration", "type": "uint256"}, {"internalType": "string[]", "name": "pageInteractions", "type": "string[]"}],
                "name": "updateTrackingData",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "string", "name": "preferences", "type": "string"}, {"internalType": "string[]", "name": "listeningHistory", "type": "string[]"}, {"internalType": "uint256", "name": "expirationDays", "type": "uint256"}],
                "name": "createSoundCloudStyleCookie",
                "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
            // Add other ABI entries as needed
        ]
    };

    // Initialize the tracker
    window.web3CookieTracker = new Web3CookieTracker(
        config.web3Provider,
        config.contractAddress,
        config.contractABI
    );
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Web3CookieTracker;
}
