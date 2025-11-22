# RAG Tester Usage Guide

## Overview

The RAG (Retrieval-Augmented Generation) Tester in the Developer Playground allows you to query the vector database directly to find similar past analyses. This is useful for:

- Testing how well the RAG system retrieves relevant historical context
- Understanding what information is stored in the knowledge base
- Debugging similarity search functionality
- Exploring past analyses and patterns

## Prerequisites

Before using the RAG Tester, ensure:

1. **Ollama is running** with the `nomic-embed-text` model:
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # If nomic-embed-text is missing, install it:
   ollama pull nomic-embed-text
   ```

2. **Database has analyses with embeddings**:
   - Run some analyses first: `python -m tradingagents.analyze AAPL MSFT`
   - Or generate embeddings for existing analyses: `python scripts/utilities/fix_embeddings.py`

3. **Backend API is running** on `http://localhost:8005`

## How It Works

1. **Query Input**: You enter a natural language query (e.g., "AAPL showing strong momentum")
2. **Embedding Generation**: The query is converted to a 768-dimensional vector using Ollama's `nomic-embed-text` model
3. **Vector Search**: The system searches the `analyses` table for similar embeddings using cosine similarity
4. **Results**: Returns the most similar past analyses with similarity scores

## Query Examples

### Stock-Specific Queries

Search for analyses related to specific stocks:

```
AAPL strong fundamentals
Microsoft technology sector analysis
NVDA high growth potential
```

### Technical Analysis Queries

Find analyses based on technical indicators:

```
RSI oversold conditions
MACD bullish crossover
momentum indicators positive
volume spike detected
```

### Fundamental Analysis Queries

Search for fundamental analysis patterns:

```
undervalued stock with good P/E ratio
strong revenue growth
dividend yield attractive
low debt to equity ratio
```

### Market Condition Queries

Find analyses based on market situations:

```
bearish market conditions
sector rotation technology
market volatility high
recession concerns
```

### Decision-Based Queries

Search for specific investment decisions:

```
strong buy recommendation
high confidence investment
wait for better entry point
sell signal generated
```

### Risk-Focused Queries

Find analyses discussing risks:

```
regulatory risk concerns
competition threat
earnings risk factors
market volatility risk
```

### Sector and Industry Queries

```
technology sector trends
healthcare sector analysis
energy sector opportunities
financial services sector
```

## Understanding Results

Each result includes:

- **Content**: Summary of the analysis (executive summary, decision, confidence)
- **Metadata**:
  - `source`: Always "analysis" for stored analyses
  - `analysis_id`: Unique ID of the analysis
  - `ticker`: Stock symbol (e.g., "AAPL")
  - `ticker_id`: Internal ticker ID
  - `analysis_date`: Date when analysis was performed
  - `final_decision`: BUY, SELL, HOLD, or WAIT
  - `confidence_score`: Confidence level (0-100)
  - `similarity`: Similarity score (0-1, higher is more similar)

### Similarity Scores

- **0.8-1.0**: Very similar - Strong match
- **0.6-0.8**: Similar - Good match
- **0.4-0.6**: Somewhat similar - Moderate match
- **<0.4**: Not very similar - Weak match (may not appear if threshold is set)

## Best Practices

### 1. Use Natural Language

The RAG system works best with natural language queries, not just keywords:

✅ **Good**: "AAPL showing strong momentum with positive technical indicators"
❌ **Less effective**: "AAPL momentum"

### 2. Be Specific

More specific queries yield better results:

✅ **Good**: "Technology stock with high growth potential and low P/E ratio"
❌ **Less specific**: "good stock"

### 3. Use Context

Include relevant context in your queries:

✅ **Good**: "Undervalued healthcare stock with strong fundamentals during market downturn"
❌ **Less context**: "healthcare stock"

### 4. Try Different Phrasings

If you don't get results, try rephrasing:

- "AAPL buy signal" → "AAPL strong buy recommendation"
- "momentum" → "price momentum indicators"
- "risk" → "risk factors and concerns"

## Troubleshooting

### "No results found"

**Possible causes:**

1. **No analyses in database**: Run some analyses first
   ```bash
   python -m tradingagents.analyze AAPL MSFT GOOGL
   ```

2. **No embeddings generated**: Generate embeddings for existing analyses
   ```bash
   python scripts/utilities/fix_embeddings.py
   ```

3. **Similarity threshold too high**: The default threshold is 0.5. Try a lower query or check if analyses exist:
   ```sql
   SELECT COUNT(*) FROM analyses WHERE embedding IS NOT NULL;
   ```

4. **Query too specific**: Try a more general query or different phrasing

### "Embedding service not available"

**Solution:**

1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Start Ollama if needed:
   ```bash
   ollama serve
   ```

3. Verify model is installed:
   ```bash
   ollama list | grep nomic-embed-text
   ```

4. Install model if missing:
   ```bash
   ollama pull nomic-embed-text
   ```

### "Failed to generate embedding"

**Possible causes:**

1. Ollama service is down
2. Network connectivity issues
3. Model not loaded

**Solution:** Restart Ollama and verify the model is available

## Advanced Usage

### Query Parameters

The API endpoint supports additional parameters:

- `limit`: Maximum number of results (default: 5)
- `similarity_threshold`: Minimum similarity score 0-1 (default: 0.5)

You can test these directly via API:

```bash
curl -X POST "http://localhost:8005/debug/rag_search?query=AAPL%20momentum&limit=10&similarity_threshold=0.6" \
  -H "Content-Type: application/json"
```

### Checking Database Status

To see what's available in the database:

```sql
-- Count analyses with embeddings
SELECT COUNT(*) FROM analyses WHERE embedding IS NOT NULL;

-- See recent analyses
SELECT 
    a.analysis_id,
    t.symbol,
    a.analysis_date,
    a.final_decision,
    a.confidence_score
FROM analyses a
JOIN tickers t ON a.ticker_id = t.ticker_id
WHERE a.embedding IS NOT NULL
ORDER BY a.analysis_date DESC
LIMIT 10;
```

## Example Workflows

### Workflow 1: Testing RAG System

1. Run analyses for multiple stocks:
   ```bash
   python -m tradingagents.analyze AAPL MSFT GOOGL NVDA
   ```

2. Test queries in RAG Tester:
   - "AAPL strong buy signal"
   - "Technology sector momentum"
   - "High confidence investment opportunities"

3. Verify results match your expectations

### Workflow 2: Exploring Historical Patterns

1. Query for specific patterns:
   - "oversold bounce pattern"
   - "earnings beat expectations"
   - "sector rotation opportunity"

2. Review similarity scores to understand pattern strength

3. Use insights to inform future analyses

### Workflow 3: Debugging Similarity Search

1. Enter a query you know should match
2. Check if results appear and similarity scores
3. If no results, check:
   - Database has analyses with embeddings
   - Similarity threshold isn't too high
   - Query phrasing matches stored content

## Tips for Better Results

1. **Build up the knowledge base**: The more analyses you have, the better the RAG system works
2. **Use descriptive queries**: Include context, not just keywords
3. **Check similarity scores**: Higher scores indicate better matches
4. **Review metadata**: Ticker, date, and decision info help understand context
5. **Try variations**: If one query doesn't work, try rephrasing

## Related Documentation

- [RAG Quick Start Guide](RAG_QUICK_START.md) - Getting started with RAG
- [Database Status](DATABASE_STATUS.md) - Database configuration and status
- [Phase 3 Completion Report](PHASE_3_COMPLETION_REPORT.md) - RAG system architecture

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify Ollama and database are running
3. Check backend logs for errors
4. Ensure analyses exist with embeddings in the database

---

**Happy searching! 🔍**

