from __future__ import annotations

import asyncio
import functools
import time
from enum import Enum
from typing import Any, Callable

from ..logging_config import get_logger

logger = get_logger("resilience.circuit_breaker")


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info(f"Circuit '{self.name}' transitioned to HALF_OPEN")
        return self._state

    def record_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            logger.info(f"Circuit '{self.name}' CLOSED (recovered)")
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit '{self.name}' re-OPENED from HALF_OPEN")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                f"Circuit '{self.name}' OPENED after {self._failure_count} failures"
            )


_breakers: dict[str, CircuitBreaker] = {}


def _get_breaker(name: str, **kwargs: Any) -> CircuitBreaker:
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name=name, **kwargs)
    return _breakers[name]


class CircuitOpenError(Exception):
    pass


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
) -> Callable:
    """Decorator that wraps an async function with a circuit breaker."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            breaker = _get_breaker(
                name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )

            if breaker.state == CircuitState.OPEN:
                raise CircuitOpenError(
                    f"Circuit '{name}' is OPEN. Service unavailable."
                )

            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except CircuitOpenError:
                raise
            except Exception as e:
                breaker.record_failure()
                raise

        return wrapper
    return decorator
