# How to Browse ChromaDB

ChromaDB is used by TradingAgents to store financial situation memories and embeddings. This guide shows you how to browse and explore the database.

## Quick Start

### Using the Browser Script

**Option 1: Use the wrapper script (Recommended)**
```bash
./browse_chromadb.sh
```

**Option 2: Activate virtual environment first**
```bash
source venv/bin/activate
python browse_chromadb.py
```

**Option 3: Use the venv Python directly**
```bash
venv/bin/python browse_chromadb.py
```

**Note:** The script requires the `rich` library, which is installed in the virtual environment. Make sure to activate the venv or use one of the methods above.

## Features

The browser script provides:

1. **List Collections** - See all collections in ChromaDB
2. **View Contents** - Browse documents in each collection
3. **Query Collections** - Search for similar documents
4. **Export Data** - Export collection data to JSON
5. **Statistics** - See document counts and metadata

## Collections in TradingAgents

TradingAgents creates these collections:

- **bull_memory** - Bull researcher's financial situation memories
- **bear_memory** - Bear researcher's financial situation memories
- **trader_memory** - Trader agent's financial situation memories
- **invest_judge_memory** - Research manager's financial situation memories
- **risk_manager_memory** - Risk manager's financial situation memories

Each collection stores:
- **Documents**: Financial situation descriptions
- **Metadata**: Recommendations/advice for each situation
- **Embeddings**: Vector representations for semantic search

## Manual Browsing (Python Script)

You can also browse ChromaDB programmatically:

```python
import os
import chromadb
from chromadb.config import Settings

# Set environment variables
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

# Connect to ChromaDB
client = chromadb.Client(Settings(
    allow_reset=True,
    anonymized_telemetry=False,
))

# List all collections
collections = client.list_collections()
print(f"Found {len(collections)} collections:")
for collection in collections:
    print(f"  - {collection.name} ({collection.count()} documents)")

# Get a specific collection
collection = client.get_collection("bull_memory")

# Get all documents
results = collection.get()
print(f"\nDocuments in 'bull_memory':")
for i, doc in enumerate(results["documents"]):
    print(f"  {i+1}. {doc[:100]}...")

# Query the collection
query_results = collection.query(
    query_texts=["High inflation with rising interest rates"],
    n_results=3
)
print(f"\nQuery results:")
for doc in query_results["documents"][0]:
    print(f"  - {doc[:100]}...")
```

## Using ChromaDB Admin UI

ChromaDB doesn't have a built-in web UI, but you can use:

### Option 1: ChromaDB Admin (Third-party)

Install and run ChromaDB Admin:

```bash
pip install chromadb-admin
chromadb-admin
```

### Option 2: ChromaDB Server Mode

Run ChromaDB in server mode and use the REST API:

```python
# Start ChromaDB server (in a separate terminal)
# chromadb run --path ./chroma_db --port 8000

# Then use the HTTP client
import chromadb
client = chromadb.HttpClient(host="localhost", port=8000)
```

## Common Operations

### View All Collections

```python
collections = client.list_collections()
for collection in collections:
    print(f"{collection.name}: {collection.count()} documents")
```

### Get Collection Contents

```python
collection = client.get_collection("bull_memory")
results = collection.get(limit=10)  # Get first 10 documents

for i, doc in enumerate(results["documents"]):
    print(f"Document {i+1}: {doc}")
    print(f"Metadata: {results['metadatas'][i]}")
    print()
```

### Query by Similarity

```python
collection = client.get_collection("bull_memory")

# Query for similar documents
results = collection.query(
    query_texts=["Market volatility with tech sector decline"],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)

for i, doc in enumerate(results["documents"][0]):
    similarity = 1.0 - results["distances"][0][i]
    print(f"Match {i+1} (similarity: {similarity:.2f}):")
    print(f"  {doc}")
    print(f"  Recommendation: {results['metadatas'][0][i].get('recommendation', 'N/A')}")
    print()
```

### Delete a Collection

```python
client.delete_collection("collection_name")
```

### Reset All Collections

```python
client.reset()  # ⚠️ This deletes ALL data!
```

## Data Structure

Each document in a collection has:

- **ID**: Unique identifier (string)
- **Document**: The financial situation text (string)
- **Metadata**: Dictionary with recommendation/advice (dict)
- **Embedding**: Vector representation (array of floats)

Example:

```python
{
    "id": "0",
    "document": "High inflation rate with rising interest rates and declining consumer spending",
    "metadata": {
        "recommendation": "Consider defensive sectors like consumer staples and utilities."
    },
    "embedding": [0.123, -0.456, 0.789, ...]  # 768-dimensional vector
}
```

## Troubleshooting

### "No collections found"

This means ChromaDB is empty or using in-memory mode. Collections are created when TradingAgents runs and stores memories.

### "Collection not found"

The collection name might be different. List all collections first to see available names.

### "Connection error"

Make sure ChromaDB is initialized. The browser script handles both in-memory and persistent clients automatically.

## Exporting Data

Use the browser script's export feature, or export manually:

```python
collection = client.get_collection("bull_memory")
results = collection.get()

import json
export_data = {
    "collection_name": "bull_memory",
    "documents": [
        {
            "id": results["ids"][i],
            "document": results["documents"][i],
            "metadata": results["metadatas"][i]
        }
        for i in range(len(results["ids"]))
    ]
}

with open("bull_memory_export.json", "w") as f:
    json.dump(export_data, f, indent=2)
```

## Notes

- **In-Memory Mode**: By default, ChromaDB uses in-memory storage. Data is lost when the application closes.
- **Persistent Mode**: To persist data, use `PersistentClient` with a path.
- **Embeddings**: Documents are automatically embedded using the configured embedding model (nomic-embed-text for Ollama, text-embedding-3-small for others).

