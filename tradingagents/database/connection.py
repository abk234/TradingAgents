"""
Database Connection Management for Investment Intelligence System

Provides database connection, connection pooling, and basic operations.
"""

import os
import psycopg2
from psycopg2 import pool, sql, extras
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
import logging
import time
from threading import Lock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_credentials() -> Dict[str, Any]:
    """
    Get database credentials from secure sources
    
    Priority order:
    1. System keyring (for local development)
    2. Environment variables (for Docker/CI)
    3. System defaults (fallback)
    """
    credentials = {}
    
    # Try keyring first
    try:
        import keyring
        user = keyring.get_password('tradingagents', 'db_user')
        password = keyring.get_password('tradingagents', 'db_password')
        
        if user:
            credentials['user'] = user
        if password:
            credentials['password'] = password
    except ImportError:
        logger.debug("keyring not installed, using environment variables")
    except Exception as e:
        logger.debug(f"Could not load from keyring: {e}")
    
    # Fall back to environment variables
    credentials['dbname'] = os.getenv('DB_NAME', 'investment_intelligence')
    credentials['host'] = os.getenv('DB_HOST', 'localhost')
    credentials['port'] = int(os.getenv('DB_PORT', '5432'))
    
    if 'user' not in credentials:
        credentials['user'] = os.getenv('DB_USER', os.getenv('USER'))
    
    if 'password' not in credentials:
        credentials['password'] = os.getenv('DB_PASSWORD', '')
    
    return credentials


class MonitoredConnectionPool(psycopg2.pool.SimpleConnectionPool):
    """Connection pool with monitoring and statistics"""
    
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
        """Get connection with timing and statistics"""
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
        """Return connection with statistics"""
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
                'active_connections': getattr(self, '_used', 0),
                'available_connections': max(0, getattr(self, '_minconn', 0) - getattr(self, '_used', 0)),
                'max_connections': getattr(self, '_maxconn', 0),
                'utilization_pct': (getattr(self, '_used', 0) / max(1, getattr(self, '_maxconn', 0))) * 100,
                'avg_wait_time_ms': avg_wait * 1000,
            }


class DatabaseConnection:
    """Manages PostgreSQL database connections with connection pooling."""

    def __init__(
        self,
        dbname: str = "investment_intelligence",
        user: str = None,
        password: str = None,
        host: str = "localhost",
        port: int = 5432,
        minconn: int = 1,
        maxconn: int = 10
    ):
        """
        Initialize database connection pool.

        Args:
            dbname: Database name
            user: Database user (defaults to current OS user)
            password: Database password (optional for local connections)
            host: Database host
            port: Database port
            minconn: Minimum number of connections in pool
            maxconn: Maximum number of connections in pool
        """
        # Get secure credentials if not provided
        if not all([user, password, host, port]):
            creds = get_db_credentials()
            self.dbname = dbname or creds.get('dbname', 'investment_intelligence')
            self.user = user or creds.get('user', os.getenv('USER'))
            self.password = password or creds.get('password', '')
            self.host = host or creds.get('host', 'localhost')
            self.port = port or creds.get('port', 5432)
        else:
            self.dbname = dbname
            self.user = user
            self.password = password
            self.host = host
            self.port = port

        # Create monitored connection pool
        try:
            self.connection_pool = MonitoredConnectionPool(
                minconn,
                maxconn,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            logger.info(f"✓ Monitored connection pool created for '{dbname}'")
        except psycopg2.Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool.

        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ...")
        """
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=None):
        """
        Context manager for getting a cursor.

        Args:
            cursor_factory: Optional cursor factory (e.g., RealDictCursor)

        Usage:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT ...")
                results = cursor.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                logger.error(f"Cursor error: {e}")
                raise
            finally:
                cursor.close()

    def execute_query(
        self,
        query: str,
        params: Tuple = None,
        fetch: bool = True,
        fetch_one: bool = False
    ) -> Optional[List]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters tuple
            fetch: Whether to fetch results
            fetch_one: Fetch only one result

        Returns:
            Query results as list of tuples, or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)

            if fetch:
                return cursor.fetchone() if fetch_one else cursor.fetchall()
            return None

    def execute_dict_query(
        self,
        query: str,
        params: Tuple = None,
        fetch_one: bool = False
    ) -> Optional[List[Dict]]:
        """
        Execute a SQL query and return results as dictionaries.

        Args:
            query: SQL query string
            params: Query parameters tuple
            fetch_one: Fetch only one result

        Returns:
            Query results as list of dicts, or None
        """
        with self.get_cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            results = cursor.fetchone() if fetch_one else cursor.fetchall()

            if results:
                if fetch_one:
                    return dict(results)
                return [dict(row) for row in results]
            return None

    def insert(
        self,
        table: str,
        data: Dict[str, Any],
        returning: str = None
    ) -> Optional[Any]:
        """
        Insert a row into a table.

        Args:
            table: Table name
            data: Dictionary of column:value pairs
            returning: Column to return (e.g., 'ticker_id')

        Returns:
            Value of returning column, or None
        """
        columns = list(data.keys())
        values = list(data.values())

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(values))
        )

        if returning:
            query = sql.SQL("{} RETURNING {}").format(
                query,
                sql.Identifier(returning)
            )

        with self.get_cursor() as cursor:
            cursor.execute(query, values)

            if returning:
                result = cursor.fetchone()
                return result[0] if result else None
            return None

    def bulk_insert(
        self,
        table: str,
        data: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk insert multiple rows into a table.

        Args:
            table: Table name
            data: List of dictionaries with column:value pairs

        Returns:
            Number of rows inserted
        """
        if not data:
            return 0

        columns = list(data[0].keys())
        values = [[row.get(col) for col in columns] for row in data]

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )

        with self.get_cursor() as cursor:
            cursor.executemany(query, values)
            return cursor.rowcount

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> int:
        """
        Update rows in a table.

        Args:
            table: Table name
            data: Dictionary of columns to update
            where: Dictionary of WHERE conditions

        Returns:
            Number of rows updated
        """
        set_clause = sql.SQL(', ').join(
            sql.SQL("{} = {}").format(
                sql.Identifier(k),
                sql.Placeholder()
            ) for k in data.keys()
        )

        where_clause = sql.SQL(' AND ').join(
            sql.SQL("{} = {}").format(
                sql.Identifier(k),
                sql.Placeholder()
            ) for k in where.keys()
        )

        query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
            sql.Identifier(table),
            set_clause,
            where_clause
        )

        values = list(data.values()) + list(where.values())

        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount

    def delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> int:
        """
        Delete rows from a table.

        Args:
            table: Table name
            where: Dictionary of WHERE conditions

        Returns:
            Number of rows deleted
        """
        where_clause = sql.SQL(' AND ').join(
            sql.SQL("{} = {}").format(
                sql.Identifier(k),
                sql.Placeholder()
            ) for k in where.keys()
        )

        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(table),
            where_clause
        )

        values = list(where.values())

        with self.get_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            )
        """
        result = self.execute_query(query, (table_name,), fetch_one=True)
        return result[0] if result else False

    def get_table_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        query = sql.SQL("SELECT COUNT(*) FROM {}").format(
            sql.Identifier(table_name)
        )
        result = self.execute_query(query, fetch_one=True)
        return result[0] if result else 0

    def get_pool_stats(self) -> dict:
        """Get connection pool statistics"""
        if hasattr(self.connection_pool, 'get_stats'):
            return self.connection_pool.get_stats()
        return {}
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("All database connections closed")


# Global database connection instance
_db_instance: Optional[DatabaseConnection] = None


def get_db_connection(
    dbname: str = "investment_intelligence",
    **kwargs
) -> DatabaseConnection:
    """
    Get or create a global database connection instance.

    Args:
        dbname: Database name
        **kwargs: Additional connection parameters

    Returns:
        DatabaseConnection instance
    """
    global _db_instance

    if _db_instance is None:
        _db_instance = DatabaseConnection(dbname=dbname, **kwargs)

    return _db_instance


def close_db_connection():
    """Close the global database connection."""
    global _db_instance

    if _db_instance:
        _db_instance.close_all_connections()
        _db_instance = None
