# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Custom Prometheus metrics for the Trading Agents application.
Tracks business-specific metrics for monitoring and alerting.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import psutil
import time


class TradingMetrics:
    """
    Centralized metrics collection for Trading Agents.
    """

    def __init__(self):
        # Chat interaction metrics
        self.chat_requests = Counter(
            'tradingagents_chat_requests_total',
            'Total number of chat requests received',
            ['endpoint']
        )

        self.chat_success = Counter(
            'tradingagents_chat_success_total',
            'Total number of successful chat interactions'
        )

        self.chat_failures = Counter(
            'tradingagents_chat_failures_total',
            'Total number of failed chat interactions',
            ['error_type']
        )

        self.agent_processing_time = Histogram(
            'tradingagents_agent_processing_seconds',
            'Time spent processing agent requests',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )

        # User feedback metrics
        self.user_feedback = Counter(
            'tradingagents_user_feedback_total',
            'Total user feedback received',
            ['rating']
        )

        self.feedback_score = Gauge(
            'tradingagents_feedback_score_average',
            'Average user feedback score'
        )

        # Trading-specific metrics
        self.trading_signals = Counter(
            'tradingagents_trading_signals_total',
            'Total trading signals generated',
            ['signal_type', 'ticker']
        )

        self.analysis_requests = Counter(
            'tradingagents_analysis_requests_total',
            'Total stock analysis requests',
            ['ticker', 'analysis_type']
        )

        self.tickers_analyzed = Gauge(
            'tradingagents_unique_tickers_analyzed',
            'Number of unique tickers analyzed in current session'
        )

        # LLM interaction metrics
        self.llm_calls = Counter(
            'tradingagents_llm_calls_total',
            'Total LLM API calls',
            ['model', 'provider']
        )

        self.llm_tokens = Counter(
            'tradingagents_llm_tokens_total',
            'Total LLM tokens consumed',
            ['model', 'token_type']  # token_type: input, output
        )

        self.llm_cost = Counter(
            'tradingagents_llm_cost_usd_total',
            'Total estimated LLM cost in USD',
            ['model', 'provider']
        )

        self.llm_latency = Histogram(
            'tradingagents_llm_latency_seconds',
            'LLM API call latency',
            ['model', 'provider'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
        )

        # Database metrics
        self.db_queries = Counter(
            'tradingagents_db_queries_total',
            'Total database queries executed',
            ['operation', 'table']
        )

        self.db_query_duration = Histogram(
            'tradingagents_db_query_duration_seconds',
            'Database query execution time',
            ['operation', 'table'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
        )

        # Cache metrics
        self.cache_hits = Counter(
            'tradingagents_cache_hits_total',
            'Total cache hits',
            ['cache_type']
        )

        self.cache_misses = Counter(
            'tradingagents_cache_misses_total',
            'Total cache misses',
            ['cache_type']
        )

        # System resource metrics
        self.active_conversations = Gauge(
            'tradingagents_active_conversations',
            'Number of currently active conversations'
        )

        # Application info
        self.app_info = Info(
            'tradingagents_app',
            'Trading Agents application information'
        )

        # Internal state tracking
        self._feedback_scores = []
        self._analyzed_tickers = set()

    # Chat tracking methods
    def track_chat_request(self, endpoint: str = "chat"):
        """Track a new chat request."""
        self.chat_requests.labels(endpoint=endpoint).inc()

    def track_successful_chat(self):
        """Track a successful chat interaction."""
        self.chat_success.inc()

    def track_failed_chat(self, error_type: str = "unknown"):
        """Track a failed chat interaction."""
        self.chat_failures.labels(error_type=error_type).inc()

    def track_agent_processing_time(self, duration: float):
        """Track agent processing time in seconds."""
        self.agent_processing_time.observe(duration)

    # User feedback methods
    def track_user_feedback(self, rating: int):
        """Track user feedback rating (1-5)."""
        self.user_feedback.labels(rating=str(rating)).inc()

        # Update average score
        self._feedback_scores.append(rating)
        if len(self._feedback_scores) > 1000:  # Keep last 1000 scores
            self._feedback_scores.pop(0)

        avg_score = sum(self._feedback_scores) / len(self._feedback_scores)
        self.feedback_score.set(avg_score)

    # Trading metrics methods
    def track_trading_signal(self, signal_type: str, ticker: str):
        """Track trading signal generation."""
        self.trading_signals.labels(
            signal_type=signal_type,
            ticker=ticker.upper()
        ).inc()

    def track_analysis_request(self, ticker: str, analysis_type: str = "general"):
        """Track stock analysis request."""
        ticker_upper = ticker.upper()
        self.analysis_requests.labels(
            ticker=ticker_upper,
            analysis_type=analysis_type
        ).inc()

        # Track unique tickers
        self._analyzed_tickers.add(ticker_upper)
        self.tickers_analyzed.set(len(self._analyzed_tickers))

    # LLM metrics methods
    def track_llm_call(self, model: str, provider: str,
                       latency: float, input_tokens: int,
                       output_tokens: int, cost: float = 0.0):
        """Track LLM API call with comprehensive metrics."""
        self.llm_calls.labels(model=model, provider=provider).inc()
        self.llm_tokens.labels(model=model, token_type="input").inc(input_tokens)
        self.llm_tokens.labels(model=model, token_type="output").inc(output_tokens)
        self.llm_latency.labels(model=model, provider=provider).observe(latency)

        if cost > 0:
            self.llm_cost.labels(model=model, provider=provider).inc(cost)

    # Database metrics methods
    def track_db_query(self, operation: str, table: str, duration: float):
        """Track database query execution."""
        self.db_queries.labels(operation=operation, table=table).inc()
        self.db_query_duration.labels(operation=operation, table=table).observe(duration)

    # Cache metrics methods
    def track_cache_hit(self, cache_type: str = "redis"):
        """Track cache hit."""
        self.cache_hits.labels(cache_type=cache_type).inc()

    def track_cache_miss(self, cache_type: str = "redis"):
        """Track cache miss."""
        self.cache_misses.labels(cache_type=cache_type).inc()

    # Conversation tracking
    def increment_active_conversations(self):
        """Increment active conversation count."""
        self.active_conversations.inc()

    def decrement_active_conversations(self):
        """Decrement active conversation count."""
        self.active_conversations.dec()

    # Application info
    def set_app_info(self, version: str, environment: str, commit: str = "unknown"):
        """Set application metadata."""
        self.app_info.info({
            'version': version,
            'environment': environment,
            'commit': commit
        })

    # System metrics (called periodically)
    @staticmethod
    def get_system_metrics():
        """Get current system resource usage."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()
        }


# Global metrics instance
_global_metrics = None


def get_metrics() -> TradingMetrics:
    """Get or create global metrics instance."""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = TradingMetrics()
    return _global_metrics
