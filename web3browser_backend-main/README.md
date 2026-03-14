# Web3 Browser Backend

Flask API for the Web3 Browser hackathon project.

## Tech Stack
- Python
- Flask
- SQLAlchemy (ORM)
- Neon PostgreSQL

## Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Update `.env` with your Neon `DATABASE_URL`.

4. **Run Locally**:
   ```bash
   python app.py
   ```

## APIs
- `GET /dapps`: List all available dApps.
- `POST /users/register`: Register wallet address.
- `GET /users/<wallet_address>`: Get user details.
- `POST /wallet/connect`: Log wallet connection.
- `POST /rewards/claim`: Record dApp interaction reward.
- `GET /rewards/<wallet_address>`: Get reward history.
