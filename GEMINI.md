## Project Overview

This project, `TradingAgents`, is a multi-agent financial trading framework built in Python. It leverages large language models (LLMs) and the `LangGraph` library to simulate the decision-making processes of a real-world trading firm. The framework is designed for research purposes and decomposes complex trading tasks into specialized roles handled by different agents.

The core of the system is a graph of agents, each with a specific function:

*   **Analyst Team:**
    *   `Fundamentals Analyst`: Evaluates company financials.
    *   `Sentiment Analyst`: Gauges market mood from social media.
    *   `News Analyst`: Monitors news and macroeconomic indicators.
    *   `Technical Analyst`: Analyzes price patterns and technical indicators.
*   **Researcher Team:**
    *   `Bullish Researcher`: Argues for the positive potential of an asset.
    *   `Bearish Researcher`: Argues for the negative potential of an asset.
*   **Trader Agent:** Makes the final trading decision based on the analysis and research.
*   **Risk Management:** A team of debaters to assess the risk of the trade.

The project uses a variety of data sources, including `yfinance`, `Alpha Vantage`, and `Google News`, and supports different LLM providers like `OpenAI`, `Google`, and `Anthropic`.

## Building and Running

### 1. Installation

To set up the project, you need to have Python 3.10+ installed.

```bash
# 1. Clone the repository
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 2. API Keys

The project requires API keys for an LLM provider (e.g., OpenAI) and a financial data provider (e.g., Alpha Vantage). These should be stored in a `.env` file in the project root.

```bash
# Create a .env file from the example
cp .env.example .env

# Edit the .env file with your API keys
# OPENAI_API_KEY=...
# ALPHA_VANTAGE_API_KEY=...
```

### 3. Running the Application

The main entry point for the application is `main.py`. You can run it directly to see an example of how to use the `TradingAgentsGraph`.

```bash
python main.py
```

The project also includes a command-line interface (CLI) for interactive use.

```bash
python -m cli.main
```

## Development Conventions

*   **Configuration:** The application is configured through the `tradingagents/default_config.py` file. This file allows you to set the LLM provider, model names, data vendors, and other parameters.
*   **Modularity:** The project is highly modular, with different agents, data sources, and functionalities separated into their own modules.
*   **LangGraph:** The core of the application is built around `LangGraph`, which allows for the creation of cyclical graphs of agents.
*   **RAG System:** The framework includes a Retrieval-Augmented Generation (RAG) system to provide historical context to the agents. This system uses a `ChromaDB` vector database to store and retrieve information.
*   **Testing:** While no dedicated test files were found in the initial analysis, the `test.py` file in the root directory suggests that there is a testing setup.

## Key Files

*   `README.md`: Provides a high-level overview of the project, its features, and how to get started.
*   `pyproject.toml` & `requirements.txt`: Define the project's Python dependencies.
*   `main.py`: The main entry point for the application, demonstrating how to use the `TradingAgentsGraph`.
*   `cli/main.py`: The entry point for the interactive command-line interface.
*   `tradingagents/default_config.py`: Contains the default configuration for the application.
*   `tradingagents/graph/trading_graph.py`: The core of the application, defining the `TradingAgentsGraph` class and the structure of the multi-agent system.
*   `tradingagents/agents/`: This directory contains the implementation of the different agents.
*   `tradingagents/dataflows/`: This directory contains the code for fetching data from different sources.
