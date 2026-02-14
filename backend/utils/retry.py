"""
Retry logic utilities for robust API calls.
Uses tenacity for exponential backoff and retry mechanisms.
"""

from typing import TypeVar, Callable, Any
from dataclasses import dataclass
from functools import wraps
import asyncio
import logging

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    min_wait_seconds: float = 1.0
    max_wait_seconds: float = 10.0
    exponential_base: float = 2.0
    retry_exceptions: tuple = (Exception,)


def create_retry_decorator(config: RetryConfig):
    """Create a tenacity retry decorator with the given config."""
    return retry(
        stop=stop_after_attempt(config.max_attempts),
        wait=wait_exponential(
            multiplier=config.min_wait_seconds,
            min=config.min_wait_seconds,
            max=config.max_wait_seconds,
            exp_base=config.exponential_base,
        ),
        retry=retry_if_exception_type(config.retry_exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for adding retry logic to async functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        exceptions: Tuple of exceptions to retry on
    
    Usage:
        @with_retry(max_attempts=3, exceptions=(APIError,))
        async def call_api():
            ...
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        min_wait_seconds=min_wait,
        max_wait_seconds=max_wait,
        retry_exceptions=exceptions,
    )
    retry_decorator = create_retry_decorator(config)
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            @retry_decorator
            async def inner():
                return await func(*args, **kwargs)
            
            try:
                return await inner()
            except RetryError as e:
                logger.error(f"All retry attempts failed for {func.__name__}: {e}")
                raise e.last_attempt.exception()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            @retry_decorator
            def inner():
                return func(*args, **kwargs)
            
            try:
                return inner()
            except RetryError as e:
                logger.error(f"All retry attempts failed for {func.__name__}: {e}")
                raise e.last_attempt.exception()
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class APICallError(Exception):
    """Custom exception for API call failures."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int | None = None,
        provider: str | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.provider = provider


class RateLimitError(APICallError):
    """Exception for rate limit errors."""
    pass


class AuthenticationError(APICallError):
    """Exception for authentication errors."""
    pass
