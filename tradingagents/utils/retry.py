"""
Retry utilities with exponential backoff
"""
import time
import logging
import random
from functools import wraps
from typing import Callable, Type, Tuple, Optional

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    jitter: bool = True
):
    """
    Decorator for retrying with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exceptions to catch and retry
        jitter: Add random jitter to prevent thundering herd
    
    Example:
        @retry_with_backoff(max_retries=3, exceptions=(requests.RequestException,))
        def fetch_data(url):
            return requests.get(url)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}"
                        )
                        raise
                    
                    # Calculate delay with jitter
                    if jitter:
                        jitter_amount = random.uniform(0, delay * 0.1)
                        actual_delay = delay + jitter_amount
                    else:
                        actual_delay = delay
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}, "
                        f"retrying in {actual_delay:.2f}s: {e}"
                    )
                    time.sleep(actual_delay)
                    
                    # Increase delay for next retry
                    delay = min(delay * backoff_factor, max_delay)
            
            # Should never reach here, but just in case
            raise Exception(f"Retry logic error for {func.__name__}")
        
        return wrapper
    return decorator

