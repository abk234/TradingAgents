"""
Langfuse Integration for TradingAgents

Provides Langfuse callback handler integration for LangGraph tracing.
"""

import os as _os
from typing import Optional, Dict, Any
import logging

# Load environment variables early
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required, but helpful

logger = logging.getLogger(__name__)

# Try to import Langfuse, but don't fail if not installed
LANGFUSE_AVAILABLE = False
CallbackHandler = None
Langfuse = None

try:
    from langfuse import Langfuse

    # Try different import paths for Langfuse callback handlers
    CallbackHandler = None
    try:
        # Langfuse v3 with langchain - import as CallbackHandler (not LangfuseCallbackHandler)
        from langfuse.langchain import CallbackHandler
        LANGFUSE_AVAILABLE = True
        logger.debug("✓ Langfuse CallbackHandler imported successfully")
    except ImportError as e:
        try:
            # Fallback to older naming
            from langfuse.langchain import LangfuseCallbackHandler as CallbackHandler
            LANGFUSE_AVAILABLE = True
            logger.debug("✓ Langfuse LangfuseCallbackHandler imported successfully")
        except ImportError:
            try:
                # Fallback to callback module (older versions)
                from langfuse.callback import CallbackHandler
                LANGFUSE_AVAILABLE = True
                logger.debug("✓ Langfuse callback.CallbackHandler imported successfully")
            except ImportError:
                LANGFUSE_AVAILABLE = False
                logger.debug(
                    f"Langfuse LangChain integration not available: {e}. "
                    "Install with: pip install langfuse langchain"
                )
except ImportError as e:
    LANGFUSE_AVAILABLE = False
    # Use debug level instead of warning - Langfuse is optional
    logger.debug(
        f"Langfuse not installed (optional): {e}\n"
        "To enable monitoring, install with: pip install langfuse>=3.0.0 langchain"
    )


class LangfuseTracer:
    """
    Langfuse tracer for TradingAgents.
    
    Provides automatic tracing of LangGraph executions with Langfuse.
    """
    
    def __init__(
        self,
        enabled: bool = True,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        release: Optional[str] = None,
    ):
        """
        Initialize Langfuse tracer.
        
        Args:
            enabled: Whether tracing is enabled
            public_key: Langfuse public key (from env LANGFUSE_PUBLIC_KEY)
            secret_key: Langfuse secret key (from env LANGFUSE_SECRET_KEY)
            host: Langfuse host URL (from env LANGFUSE_HOST, default: http://localhost:3000)
            session_id: Optional session ID for grouping traces
            user_id: Optional user ID
            release: Optional release/version identifier
        """
        self.enabled = enabled and LANGFUSE_AVAILABLE
        
        if not self.enabled:
            self.handler = None
            logger.info("Langfuse tracing disabled")
            return
        
        # Get credentials from environment or parameters
        self.public_key = public_key or _os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or _os.getenv("LANGFUSE_SECRET_KEY")
        self.host = host or _os.getenv("LANGFUSE_HOST", "http://localhost:3000")
        
        if not self.public_key or not self.secret_key:
            logger.warning(
                "Langfuse credentials not found. Set LANGFUSE_PUBLIC_KEY and "
                "LANGFUSE_SECRET_KEY environment variables. Tracing disabled."
            )
            self.enabled = False
            self.handler = None
            return
        
        try:
            # Create callback handler using proper Langfuse LangChain integration
            if CallbackHandler:
                # Langfuse v3 CallbackHandler reads credentials from environment variables
                # Set env vars for CallbackHandler to pick up
                _os.environ["LANGFUSE_PUBLIC_KEY"] = self.public_key
                _os.environ["LANGFUSE_SECRET_KEY"] = self.secret_key
                _os.environ["LANGFUSE_HOST"] = self.host

                # Initialize the callback handler (reads from env)
                # Note: session_id, user_id, release are handled via tags/metadata
                self.handler = CallbackHandler()

                # Store metadata for tagging traces
                self.metadata = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "release": release,
                }

                # Initialize Langfuse client (optional, for manual operations)
                self.langfuse_client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                    host=self.host,
                )

                logger.info(
                    f"✓ Langfuse tracing enabled (host: {self.host}, "
                    f"session: {session_id or 'default'})"
                )
            else:
                logger.warning("Langfuse CallbackHandler not available, tracing disabled")
                self.handler = None
                self.langfuse_client = None
                self.enabled = False

        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
            self.enabled = False
            self.handler = None
            self.langfuse_client = None
    
    def get_callback_handler(self):
        """
        Get Langfuse callback handler for LangGraph.
        
        Returns:
            CallbackHandler instance or None if disabled
        """
        return self.handler if self.enabled else None
    
    def get_config(self, additional_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get LangGraph config with Langfuse callbacks.
        
        Args:
            additional_config: Additional config to merge in
        
        Returns:
            Config dictionary with callbacks
        """
        config = additional_config or {}
        
        if self.enabled and self.handler:
            # Add Langfuse callback to config
            if "callbacks" not in config:
                config["callbacks"] = []
            
            if self.handler not in config["callbacks"]:
                config["callbacks"].append(self.handler)
        
        return config
    
    def trace_analysis(
        self,
        ticker: str,
        analysis_date: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Create a trace for a stock analysis.

        Note: With Langfuse v3 + LangChain, traces are created automatically
        via the callback handler. This method is kept for compatibility but
        is a no-op since tracing happens automatically.

        Args:
            ticker: Stock ticker symbol
            analysis_date: Date of analysis
            metadata: Additional metadata to attach

        Returns:
            None (automatic tracing via callback handler)
        """
        if not self.enabled:
            return None

        # In Langfuse v3 with LangChain integration, traces are created
        # automatically via the callback handler. No manual trace creation needed.
        logger.debug(f"Auto-tracing enabled for {ticker} on {analysis_date}")
        return None
    
    def score_trace(
        self,
        trace_id: str,
        score: float,
        comment: Optional[str] = None
    ):
        """
        Score a trace (for quality feedback).

        Args:
            trace_id: Trace ID to score
            score: Score value (0-1)
            comment: Optional comment
        """
        if not self.enabled or not self.langfuse_client:
            return

        try:
            # Use the Langfuse client to create a score
            self.langfuse_client.create_score(
                trace_id=trace_id,
                name="quality",
                value=score,
                comment=comment
            )
        except Exception as e:
            logger.error(f"Failed to score Langfuse trace: {e}")


# Global tracer instance (initialized on import if env vars are set)
_global_tracer: Optional[LangfuseTracer] = None


def get_langfuse_tracer(
    enabled: Optional[bool] = None,
    **kwargs
) -> LangfuseTracer:
    """
    Get or create global Langfuse tracer instance.
    
    Args:
        enabled: Override enabled state (default: from env or True)
        **kwargs: Additional tracer initialization kwargs
    
    Returns:
        LangfuseTracer instance
    """
    global _global_tracer
    
    if _global_tracer is None:
        # Check if enabled from environment (default to False if not explicitly set)
        if enabled is None:
            enabled = _os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"

        _global_tracer = LangfuseTracer(enabled=enabled, **kwargs)
    
    return _global_tracer


def reset_tracer():
    """Reset global tracer (useful for testing)."""
    global _global_tracer
    _global_tracer = None

