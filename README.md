# NLS Decentralised Social System

Web3 social stack that replaces HTTP cookies with user-owned sessions, SocialUnits, and BitChat. The working note is [DECENTRALIZED_SOCIAL_SYSTEM.md](DECENTRALIZED_SOCIAL_SYSTEM.md).

## Components

| Piece | Contract | Client | Notes |
|---|---|---|---|
| Web3Cookie | [Web3Cookie.sol](Web3Cookie.sol) | [web3_cookie_tracker.js](web3_cookie_tracker.js), [web3_cookie_demo.html](web3_cookie_demo.html) | [Web3Cookie_README.md](Web3Cookie_README.md) |
| SocialUnits | [SocialUnits.sol](SocialUnits.sol) | [social_units_tracker.js](social_units_tracker.js), [social_units_demo.html](social_units_demo.html) | [SocialUnits_README.md](SocialUnits_README.md) |
| BitChat | [BitChat.sol](BitChat.sol) | [chat_interface.html](chat_interface.html) | [BitChat_README.md](BitChat_README.md), [README_chat.md](README_chat.md) |

The Python bridge is [ableton_vdmx_web3_bridge.py](ableton_vdmx_web3_bridge.py). It imports [nls_browser_interface.py](nls_browser_interface.py) and [cursor_agents_interface.py](cursor_agents_interface.py). Deploy helpers are [deploy_social_system.sh](deploy_social_system.sh) and [deploy_web3cookie.sh](deploy_web3cookie.sh). Container and cluster files are [Dockerfile](Dockerfile) and [deployment.yaml](deployment.yaml). Python dependencies are in [requirements.txt](requirements.txt).

## Run

```bash
pip install -r requirements.txt
python ableton_vdmx_web3_bridge.py
```

Contract addresses and the Infura key stay in environment variables. Copy the placeholders from the deploy scripts into a local `.env`. That file is gitignored.

Demos, once the bridge is up:

- Web3Cookie: `web3_cookie_demo.html`
- SocialUnits: `social_units_demo.html`
- BitChat: `chat_interface.html`

## Related, separate repository

The NLS tracker-device knowledge base is a separate repository: [nonlineari/NLS-Development-Team](https://github.com/nonlineari/NLS-Development-Team). Its Web3 pages are a sensor/IPFS stub and an empty blockchain-integration note. They do not describe Web3Cookie, SocialUnits, or BitChat.

## License

The social-system note releases this project under the MIT License.
