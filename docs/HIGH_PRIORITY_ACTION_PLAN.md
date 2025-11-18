# High Priority Fixes - Action Plan

**Target Timeline:** 3-4 weeks (120-160 hours)  
**Focus:** Security, Performance, Reliability  
**Goal:** Production-grade system with critical improvements

---

## 📋 High Priority Items (12 Total)

### Security & Configuration (4 items)
1. ✅ Remove hardcoded paths
2. ✅ Implement API key rotation
3. ✅ Fix database credential management
4. ✅ Remove API keys from documentation

### Performance (3 items)
5. ✅ Implement Redis caching layer
6. ✅ Optimize database queries
7. ✅ Add connection pool monitoring

### Monitoring (3 items)
8. ✅ Add centralized logging
9. ✅ Add application metrics
10. ✅ Add health check endpoints

### Reliability (2 items)
11. ✅ Implement circuit breakers
12. ✅ Add retry with exponential backoff

---

## 🚀 Week-by-Week Implementation Plan

### **Week 1: Security Fixes** (30-40 hours)

#### Day 1-2: Configuration Fixes (8-10 hours)

**Task 1.1: Fix Hardcoded Paths** (1 hour)
```bash
# File: tradingagents/default_config.py
```

```python
import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    
    # FIX: Remove hardcoded user path
    # OLD: "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", 
                         os.path.join(os.path.dirname(__file__), "..", "data")),
    
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # ... rest of config
}
```

**Task 1.2: Create .env.example** (30 minutes)
```bash
# Create new file: .env.example
```

```bash
# TradingAgents Environment Configuration
# Copy this file to .env and fill in your actual values

# === LLM Provider API Keys ===
# Only fill in the key for your chosen provider

# OpenAI (if using OpenAI as llm_provider)
OPENAI_API_KEY=sk-proj-your_key_here

# Google Gemini (if using Google as llm_provider)
GOOGLE_API_KEY=your_key_here

# Anthropic Claude (if using Anthropic as llm_provider)
ANTHROPIC_API_KEY=your_key_here

# === Data Provider API Keys ===
# Alpha Vantage (for news and fundamental data)
ALPHA_VANTAGE_API_KEY=your_key_here

# === Directory Configuration ===
# Where to store results and data
TRADINGAGENTS_RESULTS_DIR=./results
TRADINGAGENTS_DATA_DIR=./data

# === Database Configuration ===
# PostgreSQL connection (optional, defaults shown)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=investment_intelligence
# DB_USER=your_username
# DB_PASSWORD=your_password

# === Ollama Configuration ===
# Only needed if Ollama is running on a different host
# OLLAMA_URL=http://localhost:11434/v1

# === Notification Configuration (Optional) ===
# EMAIL_SMTP_HOST=smtp.gmail.com
# EMAIL_SMTP_PORT=587
# EMAIL_FROM=your-email@gmail.com
# EMAIL_PASSWORD=your_app_password
# EMAIL_TO=recipient@example.com

# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Task 1.3: Clean Documentation of API Keys** (1 hour)
```bash
# Update these files to remove actual API keys:
# - docs/ENV_SETUP_GUIDE.md
# - Any other docs with real keys
```

```bash
# Search for exposed keys
grep -r "LOCR3UMJ91AJ1VBF" docs/
grep -r "AIzaSy" docs/

# Replace with placeholders
# Example: ALPHA_VANTAGE_API_KEY=LOCR3UMJ91AJ1VBF
# Replace: ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

#### Day 3-4: API Key Rotation System (16-20 hours)

**Create: tradingagents/utils/secrets_manager.py**
```python
"""
Secrets management with rotation support
"""
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
import keyring

logger = logging.getLogger(__name__)


@dataclass
class APIKey:
    """API key with metadata"""
    key: str
    service: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    rotation_days: int = 90


class SecretsManager:
    """Manage API keys with rotation support"""
    
    def __init__(self, app_name: str = "tradingagents"):
        self.app_name = app_name
        self.cache_file = Path.home() / ".tradingagents" / "key_metadata.json"
        self.cache_file.parent.mkdir(exist_ok=True)
        self._metadata: Dict[str, dict] = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, dict]:
        """Load key metadata from cache"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load key metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save key metadata to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save key metadata: {e}")
    
    def set_key(
        self,
        service: str,
        key: str,
        rotation_days: int = 90,
        use_keyring: bool = True
    ):
        """
        Store API key securely
        
        Args:
            service: Service name (e.g., 'openai', 'alpha_vantage')
            key: API key value
            rotation_days: Days until key should be rotated
            use_keyring: Use system keyring (more secure) vs env var
        """
        if use_keyring:
            try:
                keyring.set_password(self.app_name, service, key)
                logger.info(f"Stored {service} key in system keyring")
            except Exception as e:
                logger.warning(f"Could not store in keyring: {e}, falling back to env")
                use_keyring = False
        
        # Store metadata
        self._metadata[service] = {
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=rotation_days)).isoformat(),
            'rotation_days': rotation_days,
            'uses_keyring': use_keyring
        }
        self._save_metadata()
    
    def get_key(self, service: str) -> Optional[str]:
        """
        Get API key for service
        
        Args:
            service: Service name (e.g., 'openai', 'alpha_vantage')
        
        Returns:
            API key or None if not found
        """
        # Check if key needs rotation
        if self._should_rotate(service):
            logger.warning(f"⚠️  API key for {service} should be rotated!")
        
        metadata = self._metadata.get(service, {})
        uses_keyring = metadata.get('uses_keyring', False)
        
        # Try keyring first
        if uses_keyring:
            try:
                key = keyring.get_password(self.app_name, service)
                if key:
                    return key
            except Exception as e:
                logger.warning(f"Could not get {service} from keyring: {e}")
        
        # Fall back to environment variable
        env_var = f"{service.upper()}_API_KEY"
        return os.getenv(env_var)
    
    def _should_rotate(self, service: str) -> bool:
        """Check if key should be rotated"""
        metadata = self._metadata.get(service)
        if not metadata or not metadata.get('expires_at'):
            return False
        
        expires_at = datetime.fromisoformat(metadata['expires_at'])
        return datetime.now() >= expires_at
    
    def rotate_key(self, service: str, new_key: str):
        """
        Rotate API key for service
        
        Args:
            service: Service name
            new_key: New API key value
        """
        old_metadata = self._metadata.get(service, {})
        rotation_days = old_metadata.get('rotation_days', 90)
        use_keyring = old_metadata.get('uses_keyring', True)
        
        logger.info(f"Rotating API key for {service}")
        self.set_key(service, new_key, rotation_days, use_keyring)
    
    def list_keys(self) -> Dict[str, dict]:
        """List all managed keys with status"""
        result = {}
        for service, metadata in self._metadata.items():
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            days_until_expiry = (expires_at - datetime.now()).days
            
            result[service] = {
                'service': service,
                'created_at': metadata['created_at'],
                'expires_at': metadata['expires_at'],
                'days_until_expiry': days_until_expiry,
                'needs_rotation': days_until_expiry <= 0,
                'uses_keyring': metadata.get('uses_keyring', False)
            }
        
        return result


# Global instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get or create global secrets manager"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_api_key(service: str) -> Optional[str]:
    """
    Convenience function to get API key
    
    Usage:
        from tradingagents.utils.secrets_manager import get_api_key
        
        openai_key = get_api_key('openai')
        alpha_vantage_key = get_api_key('alpha_vantage')
    """
    return get_secrets_manager().get_key(service)
```

**Update: tradingagents/dataflows/alpha_vantage_common.py**
```python
# Replace this:
# ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

# With this:
from tradingagents.utils.secrets_manager import get_api_key

ALPHA_VANTAGE_API_KEY = get_api_key('alpha_vantage')
```

**Create CLI tool: scripts/manage_keys.py**
```python
#!/usr/bin/env python3
"""
CLI tool for managing API keys
"""
import click
from tradingagents.utils.secrets_manager import get_secrets_manager
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
def cli():
    """Manage TradingAgents API keys"""
    pass


@cli.command()
@click.argument('service')
@click.option('--key', prompt=True, hide_input=True, help='API key value')
@click.option('--rotation-days', default=90, help='Days until rotation needed')
def set(service, key, rotation_days):
    """Store an API key"""
    manager = get_secrets_manager()
    manager.set_key(service, key, rotation_days)
    console.print(f"✅ Stored {service} API key (expires in {rotation_days} days)")


@cli.command()
def list():
    """List all managed API keys"""
    manager = get_secrets_manager()
    keys = manager.list_keys()
    
    if not keys:
        console.print("No API keys configured")
        return
    
    table = Table(title="Managed API Keys")
    table.add_column("Service", style="cyan")
    table.add_column("Created", style="white")
    table.add_column("Expires", style="white")
    table.add_column("Days Left", justify="right")
    table.add_column("Status", style="yellow")
    
    for service, info in keys.items():
        status = "⚠️ ROTATE" if info['needs_rotation'] else "✅ Valid"
        style = "red" if info['needs_rotation'] else "green"
        
        table.add_row(
            service,
            info['created_at'][:10],
            info['expires_at'][:10],
            str(info['days_until_expiry']),
            status,
            style=style
        )
    
    console.print(table)


@cli.command()
@click.argument('service')
@click.option('--new-key', prompt=True, hide_input=True, help='New API key')
def rotate(service, new_key):
    """Rotate an API key"""
    manager = get_secrets_manager()
    manager.rotate_key(service, new_key)
    console.print(f"✅ Rotated {service} API key")


if __name__ == '__main__':
    cli()
```

**Usage:**
```bash
# Install keyring for secure storage
pip install keyring

# Store keys securely
python scripts/manage_keys.py set openai
python scripts/manage_keys.py set alpha_vantage

# List all keys and check expiry
python scripts/manage_keys.py list

# Rotate a key
python scripts/manage_keys.py rotate openai
```

#### Day 5: Database Credential Security (8-10 hours)

**Update: tradingagents/database/connection.py**
```python
"""
Database Connection Management with Secure Credentials
"""
import os
import psycopg2
from psycopg2 import pool, sql, extras
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


def get_db_credentials() -> Dict[str, str]:
    """
    Get database credentials from secure sources
    
    Priority order:
    1. Environment variables (for Docker/CI)
    2. System keyring (for local development)
    3. Prompt user (fallback)
    """
    credentials = {}
    
    # Try environment variables first
    credentials['dbname'] = os.getenv('DB_NAME', 'investment_intelligence')
    credentials['host'] = os.getenv('DB_HOST', 'localhost')
    credentials['port'] = int(os.getenv('DB_PORT', '5432'))
    
    # For user and password, try keyring then env
    try:
        import keyring
        user = keyring.get_password('tradingagents', 'db_user')
        password = keyring.get_password('tradingagents', 'db_password')
        
        if user:
            credentials['user'] = user
        if password:
            credentials['password'] = password
    except Exception as e:
        logger.debug(f"Could not load from keyring: {e}")
    
    # Fall back to environment or system user
    if 'user' not in credentials:
        credentials['user'] = os.getenv('DB_USER', os.getenv('USER'))
    
    if 'password' not in credentials:
        credentials['password'] = os.getenv('DB_PASSWORD', '')
    
    return credentials


class DatabaseConnection:
    """Manages PostgreSQL database connections with connection pooling."""

    def __init__(
        self,
        dbname: str = None,
        user: str = None,
        password: str = None,
        host: str = None,
        port: int = None,
        minconn: int = 1,
        maxconn: int = 10
    ):
        """
        Initialize database connection pool with secure credentials.
        
        Args:
            dbname: Database name (optional, will use secure defaults)
            user: Database user (optional, will use secure defaults)
            password: Database password (optional, will use secure defaults)
            host: Database host (optional, will use secure defaults)
            port: Database port (optional, will use secure defaults)
            minconn: Minimum number of connections in pool
            maxconn: Maximum number of connections in pool
        """
        # Get secure credentials
        creds = get_db_credentials()
        
        # Override with provided values
        self.dbname = dbname or creds['dbname']
        self.user = user or creds['user']
        self.password = password or creds['password']
        self.host = host or creds['host']
        self.port = port or creds['port']

        # Create connection pool
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn,
                maxconn,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.info(f"✓ Database connection pool created for '{self.dbname}'")
        except psycopg2.Error as e:
            logger.error(f"✗ Error creating connection pool: {e}")
            raise

    # ... rest of the class remains the same ...
```

**Create setup script: scripts/setup_db_credentials.py**
```python
#!/usr/bin/env python3
"""
Setup secure database credentials
"""
import click
import keyring
from rich.console import Console

console = Console()


@click.command()
@click.option('--user', prompt='Database user', help='PostgreSQL username')
@click.option('--password', prompt=True, hide_input=True, help='PostgreSQL password')
def setup(user, password):
    """Store database credentials securely in system keyring"""
    try:
        keyring.set_password('tradingagents', 'db_user', user)
        keyring.set_password('tradingagents', 'db_password', password)
        console.print("✅ Database credentials stored securely in system keyring")
        console.print("\n💡 Credentials are now stored in your system's secure keyring")
        console.print("   No need to use environment variables or .env file!")
    except Exception as e:
        console.print(f"❌ Error storing credentials: {e}", style="red")
        console.print("\n💡 Fallback: You can use environment variables instead:")
        console.print("   export DB_USER=your_username")
        console.print("   export DB_PASSWORD=your_password")


if __name__ == '__main__':
    setup()
```

---

### **Week 2: Performance Optimizations** (40-50 hours)

#### Day 1-2: Redis Caching Layer (16-20 hours)

**Install Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis:latest

# Test connection
redis-cli ping  # Should return "PONG"
```

**Create: tradingagents/utils/cache_manager.py**
```python
"""
Caching layer with Redis backend
"""
import redis
import json
import logging
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based caching for expensive operations"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 3600,
        key_prefix: str = "ta:"
    ):
        """
        Initialize cache manager
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
            key_prefix: Prefix for all cache keys
        """
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            self.default_ttl = default_ttl
            self.key_prefix = key_prefix
            logger.info("✓ Redis cache connected")
        except Exception as e:
            logger.warning(f"⚠️  Redis unavailable: {e}. Caching disabled.")
            self.redis = None
    
    def _make_key(self, namespace: str, *args, **kwargs) -> str:
        """Generate cache key from function args"""
        # Create deterministic hash from arguments
        key_data = json.dumps({
            'args': args,
            'kwargs': sorted(kwargs.items())
        }, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{self.key_prefix}{namespace}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        if not self.redis:
            return
        
        try:
            serialized = json.dumps(value)
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis:
            return
        
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
    
    def clear_namespace(self, namespace: str):
        """Clear all keys in a namespace"""
        if not self.redis:
            return
        
        try:
            pattern = f"{self.key_prefix}{namespace}:*"
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
            logger.info(f"Cleared cache namespace: {namespace}")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
    
    def cached(
        self,
        namespace: str,
        ttl: int = None,
        key_func: Optional[Callable] = None
    ):
        """
        Decorator for caching function results
        
        Args:
            namespace: Cache namespace (e.g., 'stock_data', 'analysis')
            ttl: Time-to-live in seconds (None = use default)
            key_func: Custom function to generate cache key from args
        
        Example:
            @cache.cached('stock_data', ttl=3600)
            def get_stock_data(symbol: str, date: str):
                return expensive_api_call(symbol, date)
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._make_key(namespace, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache HIT: {func.__name__}")
                    return cached_result
                
                # Cache miss - execute function
                logger.debug(f"Cache MISS: {func.__name__}")
                result = func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl)
                
                return result
            
            # Add cache management methods to wrapper
            wrapper.cache_clear = lambda: self.clear_namespace(namespace)
            wrapper.cache_info = lambda: {
                'namespace': namespace,
                'ttl': ttl or self.default_ttl
            }
            
            return wrapper
        return decorator
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis:
            return {'status': 'disabled'}
        
        try:
            info = self.redis.info('stats')
            return {
                'status': 'connected',
                'total_keys': self.redis.dbsize(),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': info.get('keyspace_hits', 0) / 
                           max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0))
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
```

**Update: tradingagents/dataflows/y_finance.py**
```python
# Add at top of file:
from tradingagents.utils.cache_manager import get_cache_manager

cache = get_cache_manager()

# Wrap expensive functions:
@cache.cached('stock_data', ttl=3600)  # Cache for 1 hour
def get_stock_data_window(
    symbol: str,
    start_date: str,
    end_date: str,
    look_back_days: int = 365
) -> str:
    """Get stock data with caching"""
    # Existing implementation...
    pass

@cache.cached('indicators', ttl=1800)  # Cache for 30 minutes
def get_stock_stats_indicators_window(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int
) -> str:
    """Get technical indicators with caching"""
    # Existing implementation...
    pass
```

**Update: requirements.txt**
```bash
# Add to requirements.txt
redis>=5.0.0
```

#### Day 3-4: Database Query Optimization (16-20 hours)

**Create: scripts/migrations/010_performance_indexes.sql**
```sql
-- ============================================================================
-- Performance Optimization Indexes
-- Add composite indexes for common query patterns
-- ============================================================================

-- Composite index for recent analyses by ticker and decision
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analyses_ticker_decision_date 
    ON analyses(ticker_id, final_decision, analysis_date DESC)
    WHERE final_decision IS NOT NULL;

-- Composite index for daily scans by date and priority
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_scans_date_priority 
    ON daily_scans(scan_date DESC, priority_score DESC, priority_rank)
    WHERE priority_score IS NOT NULL;

-- Composite index for performance tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_ticker_return 
    ON performance_tracking(ticker_id, actual_return_pct DESC, entry_date DESC)
    WHERE actual_return_pct IS NOT NULL;

-- Partial index for active tickers only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickers_active_high_priority 
    ON tickers(symbol, sector) 
    WHERE active = true AND priority_tier = 1;

-- Index for buy signals with high confidence
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_buy_signals_confident 
    ON buy_signals(ticker_id, signal_date DESC, confidence_score DESC)
    WHERE signal_type IN ('BUY', 'STRONG_BUY') AND confidence_score >= 70;

-- Index for recent portfolio actions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_portfolio_actions_recent 
    ON portfolio_actions(action_date DESC, ticker_id, action_type);

-- Covering index for common ticker queries (includes frequently selected columns)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickers_covering 
    ON tickers(ticker_id, symbol, company_name, sector)
    WHERE active = true;

-- Index for price data range queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_prices_ticker_range 
    ON daily_prices(ticker_id, price_date DESC, close);

-- GIN index for JSONB columns (technical_signals in daily_scans)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_scans_signals_gin 
    ON daily_scans USING gin(technical_signals);

-- GIN index for array columns (triggered_alerts)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_scans_alerts_gin 
    ON daily_scans USING gin(triggered_alerts);

-- ============================================================================
-- Analyze tables to update statistics
-- ============================================================================
ANALYZE tickers;
ANALYZE daily_prices;
ANALYZE daily_scans;
ANALYZE analyses;
ANALYZE buy_signals;
ANALYZE portfolio_actions;
ANALYZE performance_tracking;

-- ============================================================================
-- Completion message
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Performance indexes created successfully!';
    RAISE NOTICE 'Run EXPLAIN ANALYZE on your queries to verify index usage.';
END $$;
```

**Run migration:**
```bash
psql -U $USER -d investment_intelligence -f scripts/migrations/010_performance_indexes.sql
```

**Optimize queries in tradingagents/database/analysis_ops.py:**
```python
class AnalysisOperations:
    """Database operations for analyses with optimized queries"""
    
    def get_recent_buy_recommendations(
        self,
        days: int = 30,
        min_confidence: int = 70,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent BUY recommendations (OPTIMIZED)
        
        Uses: idx_analyses_ticker_decision_date
        """
        query = """
            SELECT 
                a.analysis_id,
                t.symbol,
                t.company_name,
                t.sector,
                a.analysis_date,
                a.confidence_score,
                a.entry_price_target,
                a.stop_loss_price,
                a.position_size_pct,
                a.expected_return_pct
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            WHERE a.final_decision = 'BUY' 
                AND a.analysis_date >= CURRENT_DATE - INTERVAL '%s days'
                AND a.confidence_score >= %s
                AND t.active = true
            ORDER BY a.analysis_date DESC, a.confidence_score DESC
            LIMIT %s
        """
        return self.db.execute_dict_query(query, (days, min_confidence, limit))
    
    def get_ticker_analysis_history(
        self,
        ticker_id: int,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get analysis history for a ticker (OPTIMIZED)
        
        Uses: idx_analyses_ticker_decision_date
        """
        query = """
            SELECT 
                analysis_id,
                analysis_date,
                final_decision,
                confidence_score,
                price_at_analysis,
                entry_price_target,
                key_catalysts,
                risk_factors
            FROM analyses
            WHERE ticker_id = %s
            ORDER BY analysis_date DESC
            LIMIT %s
        """
        return self.db.execute_dict_query(query, (ticker_id, limit))
```

**Create query monitoring: tradingagents/utils/query_monitor.py**
```python
"""
Query performance monitoring
"""
import logging
import time
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


class QueryMonitor:
    """Monitor database query performance"""
    
    def __init__(self, slow_query_threshold_ms: float = 100.0):
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.query_stats = {}
    
    @contextmanager
    def monitor_query(self, query_name: str, query: str):
        """
        Context manager to monitor query execution time
        
        Usage:
            with query_monitor.monitor_query('get_tickers', query_sql):
                cursor.execute(query_sql)
        """
        start_time = time.time()
        
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log slow queries
            if duration_ms > self.slow_query_threshold_ms:
                logger.warning(
                    f"SLOW QUERY ({duration_ms:.2f}ms): {query_name}\n"
                    f"Query: {query[:200]}"
                )
            
            # Track statistics
            if query_name not in self.query_stats:
                self.query_stats[query_name] = {
                    'count': 0,
                    'total_time_ms': 0,
                    'max_time_ms': 0
                }
            
            stats = self.query_stats[query_name]
            stats['count'] += 1
            stats['total_time_ms'] += duration_ms
            stats['max_time_ms'] = max(stats['max_time_ms'], duration_ms)
    
    def get_stats(self) -> dict:
        """Get query performance statistics"""
        result = {}
        for query_name, stats in self.query_stats.items():
            result[query_name] = {
                **stats,
                'avg_time_ms': stats['total_time_ms'] / stats['count']
            }
        return result


# Global instance
_query_monitor: Optional[QueryMonitor] = None


def get_query_monitor() -> QueryMonitor:
    """Get or create global query monitor"""
    global _query_monitor
    if _query_monitor is None:
        _query_monitor = QueryMonitor()
    return _query_monitor
```

#### Day 5: Connection Pool Monitoring (8-10 hours)

**Update: tradingagents/database/connection.py**
```python
from threading import Lock
import time

class MonitoredConnectionPool(psycopg2.pool.SimpleConnectionPool):
    """Connection pool with monitoring"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stats = {
            'connections_borrowed': 0,
            'connections_returned': 0,
            'wait_time_total': 0.0,
            'slow_acquisitions': 0,
        }
        self.stats_lock = Lock()
    
    def getconn(self, key=None):
        """Get connection with timing"""
        start = time.time()
        conn = super().getconn(key)
        wait_time = time.time() - start
        
        with self.stats_lock:
            self.stats['connections_borrowed'] += 1
            self.stats['wait_time_total'] += wait_time
            
            if wait_time > 1.0:
                self.stats['slow_acquisitions'] += 1
                logger.warning(f"⚠️  Slow connection acquisition: {wait_time:.2f}s")
        
        return conn
    
    def putconn(self, conn, key=None, close=False):
        """Return connection"""
        with self.stats_lock:
            self.stats['connections_returned'] += 1
        return super().putconn(conn, key, close)
    
    def get_stats(self) -> dict:
        """Get pool statistics"""
        with self.stats_lock:
            borrowed = self.stats['connections_borrowed']
            avg_wait = self.stats['wait_time_total'] / max(1, borrowed)
            
            return {
                **self.stats,
                'active_connections': self._used,
                'available_connections': self._minconn - self._used,
                'max_connections': self._maxconn,
                'utilization_pct': (self._used / self._maxconn) * 100,
                'avg_wait_time_ms': avg_wait * 1000,
            }


class DatabaseConnection:
    """Updated to use monitored pool"""
    
    def __init__(self, ...):
        # Replace SimpleConnectionPool with MonitoredConnectionPool
        self.connection_pool = MonitoredConnectionPool(
            minconn,
            maxconn,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        logger.info(f"✓ Monitored connection pool created")
    
    def get_pool_stats(self) -> dict:
        """Get connection pool statistics"""
        return self.connection_pool.get_stats()
```

---

### **Week 3: Monitoring & Observability** (30-40 hours)

#### Day 1-2: Centralized Logging (12-16 hours)

**Create: tradingagents/utils/logging_config.py**
```python
"""
Centralized logging configuration
"""
import logging
import sys
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields
        for attr in ['ticker', 'duration_ms', 'vendor', 'cache_hit']:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname:8}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_dir: Path = Path('./logs'),
    level: str = "INFO",
    enable_json: bool = False,
    console_output: bool = True
):
    """
    Configure application-wide logging
    
    Args:
        log_dir: Directory for log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Use JSON format for file logs
        console_output: Enable console output
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler (if enabled)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        root_logger.addHandler(console_handler)
    
    # Main log file (rotating daily)
    main_handler = TimedRotatingFileHandler(
        log_dir / 'tradingagents.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    main_handler.setLevel(level)
    main_handler.setFormatter(
        JSONFormatter() if enable_json else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    )
    root_logger.addHandler(main_handler)
    
    # Error-only file (rotating by size)
    error_handler = RotatingFileHandler(
        log_dir / 'errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        JSONFormatter() if enable_json else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s\n'
        )
    )
    root_logger.addHandler(error_handler)
    
    # Performance log (for slow operations)
    perf_handler = RotatingFileHandler(
        log_dir / 'performance.log',
        maxBytes=10*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    perf_handler.setLevel(logging.WARNING)
    perf_filter = lambda record: hasattr(record, 'duration_ms')
    perf_handler.addFilter(perf_filter)
    perf_handler.setFormatter(JSONFormatter() if enable_json else logging.Formatter(
        '%(asctime)s - %(message)s [%(duration_ms).2fms]'
    ))
    root_logger.addHandler(perf_handler)
    
    # Silence noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    logging.info(f"✓ Logging configured (level={level}, json={enable_json})")
    
    return root_logger
```

**Update application startup:**
```python
# Add to tradingagents/graph/trading_graph.py __init__
from tradingagents.utils.logging_config import setup_logging

# In __init__ method:
setup_logging(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    enable_json=os.getenv('LOG_FORMAT', 'text') == 'json'
)
```

**(Continue in next message due to length...)**

