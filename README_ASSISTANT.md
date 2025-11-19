# 🤖 Eddie AI - Human-like Trading Assistant

This is the new premium conversational interface for TradingAgents.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (with `pgvector` extension recommended)
- Ollama (running `llama3.3`)

### 2. Backend Setup
The backend is a FastAPI application that orchestrates the agents.

```bash
# Activate virtual environment
source .venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run the API server
python -m tradingagents.api.main
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup
The frontend is a modern Next.js application.

```bash
cd web-app

# Install dependencies (if not already done)
npm install

# Run the development server
npm run dev
```
The web app will be available at `http://localhost:3000`.

## 🧠 Features

- **Human-like Conversation**: Chats naturally and remembers context.
- **Deep Analysis**: Delegates complex requests to the `TradingAgentsGraph`.
- **Learning System**: Remembers your preferences and learns from feedback.
- **Premium UI**: Dark mode, smooth animations, and responsive design.

## 🔧 Configuration

- **Database**: Configure DB credentials in `.env` or use system keyring.
- **LLM**: Defaults to `llama3.3` via Ollama. Change in `tradingagents/default_config.py`.
