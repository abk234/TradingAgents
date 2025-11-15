# Set chromadb environment variables before importing to avoid validation errors
import os
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os


class FinancialSituationMemory:
    def __init__(self, name, config):
        self.llm_provider = config.get("llm_provider", "openai")

        # Skip embeddings if using Google provider (no OpenAI key available)
        if self.llm_provider == "google":
            self.use_embeddings = False
            self.client = None
            self.embedding = None
        elif config["backend_url"] == "http://localhost:11434/v1":
            self.use_embeddings = True
            self.embedding = "nomic-embed-text"
            # Ollama's OpenAI-compatible API doesn't require an API key
            self.client = OpenAI(base_url=config["backend_url"], api_key="ollama")
        else:
            self.use_embeddings = True
            self.embedding = "text-embedding-3-small"
            # Check if API key is valid before creating client
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key and "your-openai-api-key-here" not in api_key:
                self.client = OpenAI(base_url=config["backend_url"])
            else:
                self.use_embeddings = False
                self.client = None
        
        # Fix chromadb configuration by setting required environment variables
        # and temporarily removing extra ones that chromadb doesn't expect
        extra_vars = {}
        for var in ["OPENAI_API_KEY", "ALPHA_VANTAGE_API_KEY", "GOOGLE_API_KEY"]:
            if var in os.environ:
                extra_vars[var] = os.environ.pop(var)
        
        # Set default values for chromadb settings
        os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
        os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
        os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
        os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
        os.environ.setdefault("CLICKHOUSE_PORT", "8123")
        
        try:
            # Initialize ChromaDB with telemetry disabled to avoid errors
            self.chroma_client = chromadb.Client(Settings(
                allow_reset=True,
                anonymized_telemetry=False,  # Disable telemetry to avoid errors
            ))
        except Exception as e:
            # If chromadb fails, try with minimal settings
            try:
                self.chroma_client = chromadb.Client(Settings(
                    allow_reset=True,
                    anonymized_telemetry=False,
                ))
            except Exception:
                # Last resort: use persistent client
                self.chroma_client = chromadb.PersistentClient(
                    settings=Settings(anonymized_telemetry=False)
                )
        
        # Restore extra variables
        os.environ.update(extra_vars)
        
        try:
            self.situation_collection = self.chroma_client.create_collection(name=name)
        except Exception:
            # Collection might already exist
            self.situation_collection = self.chroma_client.get_collection(name=name)

    def get_embedding(self, text):
        """Get OpenAI embedding for a text"""
        if not self.use_embeddings or self.client is None:
            # Return a dummy embedding if embeddings are disabled
            return [0.0] * 1536  # Standard OpenAI embedding dimension

        response = self.client.embeddings.create(
            model=self.embedding, input=text
        )
        return response.data[0].embedding

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        # Check if collection has any data
        try:
            count = self.situation_collection.count()
            if count == 0:
                return []
        except Exception:
            # If count fails, assume empty collection
            return []

        query_embedding = self.get_embedding(current_situation)

        try:
            results = self.situation_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_matches,
                include=["metadatas", "documents", "distances"],
            )
        except Exception as e:
            # If query fails (e.g., ChromaDB compatibility issues), return empty results
            print(f"Warning: Failed to query ChromaDB: {e}")
            return []

        matched_results = []
        try:
            for i in range(len(results["documents"][0])):
                matched_results.append(
                    {
                        "matched_situation": results["documents"][0][i],
                        "recommendation": results["metadatas"][0][i]["recommendation"],
                        "similarity_score": 1 - results["distances"][0][i],
                    }
                )
        except (KeyError, IndexError, TypeError) as e:
            # If results parsing fails, return empty
            print(f"Warning: Failed to parse ChromaDB results: {e}")
            return []

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
