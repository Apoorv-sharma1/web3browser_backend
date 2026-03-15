# 🌐 Web3 Browser Platform - Backend Engine

The powerful Python-based backend server powering the Web3 Browser platform. This intelligence layer manages decentralized user identities (neural signatures), orchestrates gamified reward systems, indexes decentralized applications (dApps), and provides a secure search functionality to prevent cross-origin breaches.

## 🚀 The Vision: Promoting Web3 & Social Impact

Our browser ecosystem aims to solve the steep learning curve associated with Web3. We've built an environment that is **not just a tool, but an educational gateway**. The backend supports these goals by maintaining the state of the user's progress.

### Unique Selling Propositions (USPs)
- **Gamified Onboarding**: Users earn points and cryptocurrency (Hela) by interacting with dApps, completing quests (like the "Scholar" or "Explorer"), and engaging with educational content. The backend validates and issues these rewards to prevent exploitation.
- **Inbuilt Wallet Gateway**: Interacts seamlessly with the frontend's wallet connection, storing profiles mapped to Web3 addresses securely.
- **Native Security**: Validates whether decentralized application links can be securely rendered via `check-frame` endpoints, keeping the user in the safe sandbox environment when possible.
- **Ecosystem Registry**: Serves a curated grid of trusted decentralized applications (DeFi, NFTs, Bridges) to prevent beginners from falling victim to phishing sites.
- **Social Impact**: By rewarding users for learning about decentralized technologies and security best practices, we foster a more educated, technically empowered, and financially self-sovereign community.

---

## 📸 Screenshots

<div align="center">
  <img src="screenshots/media__1773548497610.png" width="45%" alt="Browser Interface" />
  <img src="screenshots/media__1773548500528.png" width="45%" alt="DApp View" />
  <img src="screenshots/media__1773548503095.png" width="45%" alt="Wallet Gateway" />
  <img src="screenshots/media__1773548507357.png" width="45%" alt="Identity Matrix" />
</div>

---

## 🏗️ Project Structure
Built with **Flask** and **SQLAlchemy**, designed as a lightweight, robust JSON API.

```
backend/
├── app.py               # Main Flask application initialization and database setup
├── config.py            # Environment configurations (CORS, Database URI)
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel deployment configuration
├── models/              # Database schema definitions (SQLAlchemy)
│   ├── Base.py          # Declarative Base
│   ├── User.py          # User models and profile tracking
│   ├── AppRegistry.py   # dApp directory and search indexing
│   └── ActivityLog.py   # Gamification logging
├── routes/              # API Endpoints
│   ├── users.py         # Registration and session endpoints
│   ├── rewards.py       # Point claiming and token redemption logic
│   └── search.py        # dApp indexing and frame checking
├── services/            # Core business logic
│   └── hela_engine.py   # Smart contract interaction handlers
└── instance/            # SQLite development database (auto-generated)
```

---

## 🔗 Smart Contract Integration

The platform integrates directly with the **Hela Network**. The backend tracks aggregate points locally, and handles the logic when a user opts to sync (redeem) their points for on-chain assets.

### Network Capabilities (Hela Testnet)
- **Network Name**: Hela Testnet
- **Chain ID**: `666888` (Hex: `0xa2d08`)
- **RPC URL**: `https://testnet-rpc.helachain.com`
- **Block Explorer**: `https://testnet-blockexplorer.helachain.com`
- **Native Currency**: HLUSD

### Deployed Contract Details
- **Token / Contract Address**: `0xBE75FDe9DeDe700635E3dDBe7e29b5db1A76C125`

**Proof of Transactions (Tx Hashes):**
1. `0x189b830b54a34d492d1ba594211f9bb7a54f853dda5cae343b89cb7acd9dc987`
2. `0x661e041ea358d82da5d8ea2fdf37f7bea92370fce6a6f7ae880244abee42b7c2`
3. `0xe80ffdf3b88357dd5490f63ac42a457be69b749168ddc742abd3baf96f51ed9e`

---

## ⚙️ How it Works Currently

1. **User Registration**: When a user connects their wallet on the frontend, the backend registers the address, assigning them an internal ID and initiating their points balance.
2. **Activity Tracking**: As the user explores the decentralized web or completes "WTF Quests", the frontend pings the `/rewards/claim` endpoint. The backend processes the activity type and increments the user's score up to predefined daily caps.
3. **Redemption Matrix**: When a user accumulates over 1,000 internal points, they can execute a redemption. The backend deducts the internal points and converts them to equivalent "Hela Tokens" which represent the user's gamified earnings.
4. **Search and Validation**: The backend provides suggestion endpoints and acts as an indexer. It also formerly provided a `check-frame` API point to natively guard the browser against Cross-Origin resource sharing blocks.

---

## 💻 Setup & Installation

To run the backend locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Apoorv-sharma1/web3browser_backend.git
   cd web3browser_backend
   ```

2. **Create a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Environment Variables:**
   Copy `.env.example` to `.env` and fill in necessary configuration fields (e.g., SECRET_KEY).

5. **Start the Development Server:**
   ```bash
   python app.py
   ```
   *The API will be available at http://127.0.0.1:5000/*
