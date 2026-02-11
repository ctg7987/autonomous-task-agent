from __future__ import annotations

import asyncio
import functools
import random
from typing import Any, Callable, Tuple, Type

from ..logging_config import get_logger

logger = get_logger("resilience.retry")


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator for exponential backoff with jitter. Works with async functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.warning(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    if jitter:
                        delay += random.uniform(0, delay * 0.5)
                    logger.info(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)
            raise last_exception  # unreachable but satisfies type checker

        return wrapper
    return decorator
