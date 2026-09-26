/**
 * SocialUnits Tracker: Decentralized Social Network Algorithm Units
 * Replaces traditional social media algorithms with blockchain-based recommendation system
 * Integrates with Web3Cookie for comprehensive user behavior tracking
 */

class SocialUnitsTracker {
    constructor(web3Provider, socialUnitsContractAddress, web3CookieTracker) {
        this.web3 = new Web3(web3Provider);
        this.contractAddress = socialUnitsContractAddress;
        this.contract = null;
        this.web3CookieTracker = web3CookieTracker;
        this.currentAccount = null;

        // Social Units state
        this.userUnits = new Map();
        this.socialConnections = new Map();
        this.recommendations = new Map();
        this.algorithmScores = new Map();

        // Behavior tracking for algorithm input
        this.contentInteractions = new Map();
        this.socialInteractions = new Map();
        this.timeBasedPatterns = new Map();

        // Algorithm types
        this.ALGORITHMS = {
            CONTENT_RECOMMENDATION: 'content_recommendation',
            FRIEND_SUGGESTION: 'friend_suggestion',
            TREND_ANALYSIS: 'trend_analysis',
            ENGAGEMENT_OPTIMIZATION: 'engagement_optimization'
        };

        this.init();
    }

    async init() {
        try {
            // Initialize contract
            const contractABI = await this._loadContractABI();
            this.contract = new this.web3.eth.Contract(contractABI, this.contractAddress);

            // Connect wallet
            if (typeof window.ethereum !== 'undefined') {
                await this.connectWallet();
            }

            this.setupEventListeners();
            this.startBehaviorTracking();
            await this.loadUserUnits();

            console.log('SocialUnits Tracker initialized');

        } catch (error) {
            console.error('SocialUnits initialization failed:', error);
        }
    }

    async connectWallet() {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            this.currentAccount = accounts[0];
            console.log('Connected to SocialUnits wallet:', this.currentAccount);
        } catch (error) {
            console.error('Wallet connection failed:', error);
        }
    }

    setupEventListeners() {
        // Content interaction tracking
        document.addEventListener('click', (e) => this.trackContentInteraction(e));
        document.addEventListener('scroll', () => this.trackScrollBehavior());
        document.addEventListener('visibilitychange', () => this.trackVisibilityChange());

        // Social interaction tracking
        document.addEventListener('social-like', (e) => this.trackSocialInteraction('like', e.detail));
        document.addEventListener('social-share', (e) => this.trackSocialInteraction('share', e.detail));
        document.addEventListener('social-comment', (e) => this.trackSocialInteraction('comment', e.detail));
        document.addEventListener('social-follow', (e) => this.trackSocialInteraction('follow', e.detail));

        // Time-based pattern tracking
        setInterval(() => this.updateTimePatterns(), 60000); // Every minute

        // Integration with Web3Cookie
        if (this.web3CookieTracker) {
            document.addEventListener('web3cookie-behavior-update', (e) => {
                this.updateFromWeb3Cookie(e.detail);
            });
        }
    }

    startBehaviorTracking() {
        // Start comprehensive behavior tracking
        this.trackMouseMovement();
        this.trackKeyboardPatterns();
        this.trackContentEngagement();
        this.trackSocialGraph();

        // Update blockchain every 5 minutes
        setInterval(() => this.updateBlockchainState(), 300000);
    }

    // Content Interaction Tracking
    trackContentInteraction(event) {
        const element = event.target;
        const contentId = this._getContentId(element);
        const interactionType = this._classifyInteraction(element);

        if (contentId && interactionType) {
            const interaction = {
                contentId: contentId,
                type: interactionType,
                element: element.tagName.toLowerCase(),
                timestamp: Date.now(),
                position: { x: event.clientX, y: event.clientY },
                context: this._getPageContext()
            };

            this._recordInteraction('content', interaction);

            // Update engagement score
            this.updateEngagementScore(contentId, interactionType, 1);
        }
    }

    trackScrollBehavior() {
        const scrollDepth = this._calculateScrollDepth();
        const timeSpent = this._calculateTimeOnPage();

        this.timeBasedPatterns.set('scrollDepth', scrollDepth);
        this.timeBasedPatterns.set('timeOnPage', timeSpent);

        // Update behavior pattern unit
        this.updateBehaviorPattern('scrolling', { depth: scrollDepth, duration: timeSpent });
    }

    trackVisibilityChange() {
        const isVisible = !document.hidden;
        const timestamp = Date.now();

        this.timeBasedPatterns.set('visibility', { visible: isVisible, timestamp: timestamp });

        if (!isVisible) {
            // Page became hidden - update session time
            this.updateSessionTime();
        }
    }

    // Social Interaction Tracking
    trackSocialInteraction(type, detail) {
        const interaction = {
            type: type,
            targetUser: detail.targetUser,
            contentId: detail.contentId,
            timestamp: Date.now(),
            strength: detail.strength || 1
        };

        this._recordInteraction('social', interaction);
        this.updateSocialConnection(detail.targetUser, type, interaction.strength);
    }

    // Mouse and Keyboard Tracking (complementary to Web3Cookie)
    trackMouseMovement() {
        let lastPosition = { x: 0, y: 0 };
        let movementCount = 0;
        let movementDistance = 0;

        document.addEventListener('mousemove', (e) => {
            const currentPos = { x: e.clientX, y: e.clientY };
            const distance = Math.sqrt(
                Math.pow(currentPos.x - lastPosition.x, 2) +
                Math.pow(currentPos.y - lastPosition.y, 2)
            );

            movementCount++;
            movementDistance += distance;
            lastPosition = currentPos;

            // Update every 100 movements
            if (movementCount % 100 === 0) {
                this.updateMousePattern({
                    movements: movementCount,
                    totalDistance: movementDistance,
                    averageSpeed: movementDistance / movementCount
                });
                movementCount = 0;
                movementDistance = 0;
            }
        });
    }

    trackKeyboardPatterns() {
        let keystrokeCount = 0;
        let lastKeyTime = 0;
        let keyIntervals = [];

        document.addEventListener('keydown', (e) => {
            const currentTime = Date.now();
            keystrokeCount++;

            if (lastKeyTime > 0) {
                keyIntervals.push(currentTime - lastKeyTime);
            }
            lastKeyTime = currentTime;

            // Update every 50 keystrokes
            if (keystrokeCount % 50 === 0) {
                const avgInterval = keyIntervals.reduce((a, b) => a + b, 0) / keyIntervals.length;
                this.updateKeyboardPattern({
                    keystrokes: keystrokeCount,
                    averageInterval: avgInterval,
                    typingSpeed: 60000 / avgInterval // CPM
                });
                keystrokeCount = 0;
                keyIntervals = [];
            }
        });
    }

    // Social Graph Management
    async updateSocialConnection(targetUser, interactionType, strength) {
        if (!this.currentAccount) return;

        const connectionKey = `${this.currentAccount}-${targetUser}`;

        if (!this.socialConnections.has(connectionKey)) {
            // Create new connection
            await this.createSocialConnection(targetUser, this._getConnectionType(interactionType));
        }

        // Update connection strength
        const currentStrength = this.socialConnections.get(connectionKey) || 0;
        const newStrength = Math.min(currentStrength + strength, 1000);

        await this.updateConnectionStrength(targetUser, newStrength);
        this.socialConnections.set(connectionKey, newStrength);
    }

    async createSocialConnection(targetUser, connectionType) {
        if (!this.contract || !this.currentAccount) return;

        try {
            await this.contract.methods.createSocialConnection(targetUser, connectionType)
                .send({ from: this.currentAccount });
            console.log('Social connection created:', targetUser);
        } catch (error) {
            console.error('Failed to create social connection:', error);
        }
    }

    async updateConnectionStrength(targetUser, strength) {
        if (!this.contract || !this.currentAccount) return;

        try {
            await this.contract.methods.updateConnectionStrength(targetUser, strength)
                .send({ from: this.currentAccount });
            console.log('Connection strength updated:', targetUser, strength);
        } catch (error) {
            console.error('Failed to update connection strength:', error);
        }
    }

    // Social Unit Creation and Management
    async createBehaviorPatternUnit(patternType, patternData) {
        const metadata = {
            type: 'behavior_pattern',
            patternType: patternType,
            data: patternData,
            timestamp: Date.now(),
            userAgent: navigator.userAgent
        };

        const value = this._calculatePatternValue(patternData);

        await this.createSocialUnit('BEHAVIOR_PATTERN', metadata, value);
    }

    async createContentPreferenceUnit(category, preferenceScore) {
        const metadata = {
            type: 'content_preference',
            category: category,
            score: preferenceScore,
            timestamp: Date.now()
        };

        await this.createSocialUnit('CONTENT_PREFERENCE', metadata, preferenceScore);
    }

    async createEngagementUnit(contentId, engagementData) {
        const metadata = {
            type: 'engagement_metric',
            contentId: contentId,
            data: engagementData,
            timestamp: Date.now()
        };

        const value = this._calculateEngagementValue(engagementData);

        await this.createSocialUnit('ENGAGEMENT_METRIC', metadata, value);
    }

    async createSocialUnit(unitType, metadata, value) {
        if (!this.contract || !this.currentAccount) return;

        try {
            const metadataURI = await this._uploadToIPFS(metadata);
            const result = await this.contract.methods.createSocialUnit(unitType, metadataURI, value)
                .send({ from: this.currentAccount });

            const tokenId = result.events.SocialUnitCreated.returnValues.tokenId;
            this.userUnits.set(tokenId, { type: unitType, metadata: metadata, value: value });

            console.log('SocialUnit created:', tokenId, unitType);
            return tokenId;

        } catch (error) {
            console.error('Failed to create SocialUnit:', error);
            return null;
        }
    }

    // Recommendation Engine
    async generateRecommendations(algorithmType, candidateItems) {
        if (!this.contract || !this.currentAccount) return [];

        try {
            const candidateIds = candidateItems.map(item => item.id || item);
            const result = await this.contract.methods.generateRecommendations(
                algorithmType, this.currentAccount, candidateIds
            ).call({ from: this.currentAccount });

            const recommendations = result.map(id => candidateItems.find(item => item.id === id || item === id));
            this.recommendations.set(algorithmType, recommendations);

            return recommendations;

        } catch (error) {
            console.error('Failed to generate recommendations:', error);
            return [];
        }
    }

    async getContentRecommendations(contentItems) {
        return await this.generateRecommendations(this.ALGORITHMS.CONTENT_RECOMMENDATION, contentItems);
    }

    async getFriendSuggestions(userList) {
        return await this.generateRecommendations(this.ALGORITHMS.FRIEND_SUGGESTION, userList);
    }

    async getTrendingContent(contentItems) {
        return await this.generateRecommendations(this.ALGORITHMS.TREND_ANALYSIS, contentItems);
    }

    // Update Functions
    updateEngagementScore(contentId, interactionType, score) {
        const key = `engagement_${contentId}`;
        const currentScore = this.contentInteractions.get(key) || 0;

        // Different interaction types have different weights
        const weights = {
            'click': 1,
            'view': 2,
            'like': 3,
            'share': 5,
            'comment': 4
        };

        const weight = weights[interactionType] || 1;
        const newScore = currentScore + (score * weight);

        this.contentInteractions.set(key, newScore);

        // Update engagement unit
        this.updateEngagementUnit(contentId, { score: newScore, lastInteraction: interactionType });
    }

    updateBehaviorPattern(patternType, patternData) {
        const key = `behavior_${patternType}`;
        this.timeBasedPatterns.set(key, { ...patternData, timestamp: Date.now() });

        // Update behavior pattern unit
        this.createBehaviorPatternUnit(patternType, patternData);
    }

    updateMousePattern(mouseData) {
        this.updateBehaviorPattern('mouse_movement', mouseData);
    }

    updateKeyboardPattern(keyboardData) {
        this.updateBehaviorPattern('keyboard_input', keyboardData);
    }

    updateContentEngagement() {
        // Analyze content engagement patterns
        const engagementData = Object.fromEntries(this.contentInteractions);
        this.updateBehaviorPattern('content_engagement', engagementData);
    }

    updateSocialGraph() {
        // Analyze social connection patterns
        const socialData = Object.fromEntries(this.socialInteractions);
        this.updateBehaviorPattern('social_graph', socialData);
    }

    updateSessionTime() {
        const sessionDuration = Date.now() - (this.timeBasedPatterns.get('sessionStart') || Date.now());
        this.timeBasedPatterns.set('sessionDuration', sessionDuration);
    }

    // Integration with Web3Cookie
    updateFromWeb3Cookie(cookieData) {
        // Sync behavior data with Web3Cookie
        if (cookieData.pointerMovements) {
            this.updateMousePattern({ movements: cookieData.pointerMovements });
        }

        if (cookieData.keystrokes) {
            this.updateKeyboardPattern({ keystrokes: cookieData.keystrokes });
        }

        // Update content preferences based on cookie data
        if (cookieData.soundcloudPrefs) {
            this.updateContentPreferences(cookieData.soundcloudPrefs);
        }
    }

    updateContentPreferences(preferences) {
        // Update content preference units based on user preferences
        Object.entries(preferences).forEach(([category, score]) => {
            this.createContentPreferenceUnit(category, score);
        });
    }

    // Load existing user units from blockchain
    async loadUserUnits() {
        if (!this.contract || !this.currentAccount) return;

        try {
            // This would require additional contract functions to efficiently load user units
            // For now, we'll track newly created units
            console.log('User units loaded');
        } catch (error) {
            console.error('Failed to load user units:', error);
        }
    }

    // Periodic blockchain updates
    async updateBlockchainState() {
        if (!this.currentAccount) return;

        console.log('Updating blockchain state...');

        // Update algorithm scores based on user behavior
        await this.updateAlgorithmScores();

        // Create new units based on accumulated data
        await this.createUnitsFromBehaviorData();

        // Update social connections
        await this.updateSocialConnectionsBatch();
    }

    async updateAlgorithmScores() {
        const algorithms = Object.values(this.ALGORITHMS);

        for (const algorithm of algorithms) {
            const score = this._calculateAlgorithmScore(algorithm);
            await this.updateUserAlgorithmScore(algorithm, this.currentAccount, score);
        }
    }

    async createUnitsFromBehaviorData() {
        // Create units from accumulated behavior data
        if (this.contentInteractions.size > 0) {
            await this.createBehaviorPatternUnit('content_interaction',
                Object.fromEntries(this.contentInteractions));
        }

        if (this.timeBasedPatterns.size > 0) {
            await this.createBehaviorPatternUnit('time_patterns',
                Object.fromEntries(this.timeBasedPatterns));
        }
    }

    async updateSocialConnectionsBatch() {
        // Batch update social connection strengths
        for (const [connectionKey, strength] of this.socialConnections) {
            const [userA, userB] = connectionKey.split('-');
            if (userA === this.currentAccount) {
                await this.updateConnectionStrength(userB, strength);
            }
        }
    }

    async updateUserAlgorithmScore(algorithmId, user, score) {
        if (!this.contract) return;

        try {
            await this.contract.methods.updateUserAlgorithmScore(algorithmId, user, score)
                .send({ from: this.currentAccount });
        } catch (error) {
            console.error('Failed to update algorithm score:', error);
        }
    }

    // Utility Functions
    _loadContractABI() {
        // Return the SocialUnits contract ABI
        return fetch('/socialunits-abi.json').then(r => r.json());
    }

    _getContentId(element) {
        // Extract content ID from element or its parents
        return element.getAttribute('data-content-id') ||
               element.closest('[data-content-id]')?.getAttribute('data-content-id') ||
               element.id ||
               element.getAttribute('data-id');
    }

    _classifyInteraction(element) {
        const tagName = element.tagName.toLowerCase();
        const className = element.className.toLowerCase();
        const id = element.id.toLowerCase();

        if (tagName === 'button' || className.includes('button')) return 'click';
        if (tagName === 'a' || className.includes('link')) return 'click';
        if (className.includes('like') || id.includes('like')) return 'like';
        if (className.includes('share') || id.includes('share')) return 'share';
        if (className.includes('comment') || id.includes('comment')) return 'comment';

        return 'interaction';
    }

    _getPageContext() {
        return {
            url: window.location.href,
            title: document.title,
            referrer: document.referrer,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            scrollPosition: {
                x: window.scrollX,
                y: window.scrollY
            }
        };
    }

    _calculateScrollDepth() {
        const documentHeight = Math.max(
            document.body.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.clientHeight,
            document.documentElement.scrollHeight,
            document.documentElement.offsetHeight
        );

        const windowHeight = window.innerHeight;
        const scrollTop = window.scrollY;

        return Math.min((scrollTop + windowHeight) / documentHeight * 100, 100);
    }

    _calculateTimeOnPage() {
        return Date.now() - (this.timeBasedPatterns.get('pageLoadTime') || Date.now());
    }

    _getConnectionType(interactionType) {
        const types = {
            'follow': 2,
            'friend': 1,
            'like': 3,
            'comment': 3,
            'share': 3
        };
        return types[interactionType] || 3;
    }

    _calculatePatternValue(patternData) {
        // Calculate algorithmic value based on pattern characteristics
        let value = 50; // Base value

        if (patternData.movements) value += Math.min(patternData.movements / 10, 20);
        if (patternData.keystrokes) value += Math.min(patternData.keystrokes / 5, 15);
        if (patternData.depth) value += Math.min(patternData.depth, 15);

        return Math.min(value, 100);
    }

    _calculateEngagementValue(engagementData) {
        let value = 0;

        if (engagementData.score) value += engagementData.score;
        if (engagementData.views) value += engagementData.views * 2;
        if (engagementData.likes) value += engagementData.likes * 3;
        if (engagementData.shares) value += engagementData.shares * 5;

        return Math.min(value, 1000);
    }

    _calculateAlgorithmScore(algorithmType) {
        // Calculate how well this algorithm performs for the user
        let score = 500; // Base score

        // Adjust based on user behavior patterns
        const interactions = this.contentInteractions.size;
        const connections = this.socialConnections.size;

        if (algorithmType === this.ALGORITHMS.CONTENT_RECOMMENDATION) {
            score += interactions * 2;
        } else if (algorithmType === this.ALGORITHMS.FRIEND_SUGGESTION) {
            score += connections * 3;
        } else if (algorithmType === this.ALGORITHMS.TREND_ANALYSIS) {
            score += (interactions + connections);
        }

        return Math.min(score, 1000);
    }

    _recordInteraction(type, interaction) {
        const key = `${type}_${interaction.timestamp}`;
        if (type === 'content') {
            this.contentInteractions.set(key, interaction);
        } else if (type === 'social') {
            this.socialInteractions.set(key, interaction);
        }
    }

    async _uploadToIPFS(data) {
        // In production, upload to IPFS/Arweave
        // For demo, return a mock URI
        return `ipfs://mock/${Date.now()}/${JSON.stringify(data).slice(0, 32)}`;
    }

    // Public API
    getUserUnits() {
        return Array.from(this.userUnits.entries());
    }

    getSocialConnections() {
        return Array.from(this.socialConnections.entries());
    }

    getRecommendations(algorithmType) {
        return this.recommendations.get(algorithmType) || [];
    }

    getBehaviorData() {
        return {
            contentInteractions: Object.fromEntries(this.contentInteractions),
            socialInteractions: Object.fromEntries(this.socialInteractions),
            timePatterns: Object.fromEntries(this.timeBasedPatterns),
            algorithmScores: Object.fromEntries(this.algorithmScores)
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SocialUnitsTracker;
}
