


# ============================================================================
# Error Handling & Utilities
# ============================================================================

from collections import defaultdict
import logging
import time
from functools import wraps
from typing import Optional
from graphql import GraphQLError

from utils.constants import BURST_LIMIT_REQUESTS, BURST_LIMIT_WINDOW, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with burst support.
    
    Prevents abuse by limiting requests per user.
    Supports both sustained rate and burst limits.
    """
    
    def __init__(
        self,
        sustained_requests: int = RATE_LIMIT_REQUESTS,
        sustained_window: int = RATE_LIMIT_WINDOW,
        burst_requests: int = BURST_LIMIT_REQUESTS,
        burst_window: int = BURST_LIMIT_WINDOW
    ):
        """
        Initialize rate limiter.
        
        Args:
            sustained_requests: Max requests allowed per sustained_window
            sustained_window: Time window in seconds for sustained rate
            burst_requests: Max burst requests per burst_window
            burst_window: Time window in seconds for burst rate
        """
        self.sustained_requests = sustained_requests
        self.sustained_window = sustained_window
        self.burst_requests = burst_requests
        self.burst_window = burst_window
        
        # Track request timestamps per user
        self.sustained_requests_log = defaultdict(list)
        self.burst_requests_log = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> tuple[bool, Optional[float]]:
        """
        Check if request is allowed for user.
        
        Returns:
            (is_allowed: bool, retry_after: Optional[float])
            If not allowed, retry_after indicates seconds to wait
        """
        now = time.monotonic()
        
        # Check burst limit (strict)
        burst_log = self.burst_requests_log[user_id]
        burst_log[:] = [
            t for t in burst_log
            if now - t < self.burst_window
        ]
        
        if len(burst_log) >= self.burst_requests:
            # Calculate when next burst window expires
            oldest_request = min(burst_log)
            retry_after = (oldest_request + self.burst_window) - now
            return False, max(0.1, retry_after)  # Minimum 100ms
        
        # Check sustained rate limit (lenient)
        sustained_log = self.sustained_requests_log[user_id]
        sustained_log[:] = [
            t for t in sustained_log
            if now - t < self.sustained_window
        ]
        
        if len(sustained_log) >= self.sustained_requests:
            # Calculate when oldest request expires
            oldest_request = min(sustained_log)
            retry_after = (oldest_request + self.sustained_window) - now
            return False, max(1.0, retry_after)
        
        # Request allowed - record it
        burst_log.append(now)
        sustained_log.append(now)
        
        return True, None
    
    def cleanup(self, max_age: int = 3600):
        """Remove old entries to prevent memory bloat (hourly)."""
        now = time.monotonic()
        for user_id in list(self.sustained_requests_log.keys()):
            self.sustained_requests_log[user_id] = [
                t for t in self.sustained_requests_log[user_id]
                if now - t < max_age
            ]
            if not self.sustained_requests_log[user_id]:
                del self.sustained_requests_log[user_id]
        
        for user_id in list(self.burst_requests_log.keys()):
            self.burst_requests_log[user_id] = [
                t for t in self.burst_requests_log[user_id]
                if now - t < max_age
            ]
            if not self.burst_requests_log[user_id]:
                del self.burst_requests_log[user_id]


# Global rate limiter instance
_rate_limiter = RateLimiter()


def check_rate_limit(user_id: str) -> None:
    """
    Check if user has exceeded rate limit.
    
    Args:
        user_id: User identifier
    
    Raises:
        GraphQLError: If rate limit exceeded
    """
    is_allowed, retry_after = _rate_limiter.is_allowed(user_id)
    
    if not is_allowed:
        logger.warning(
            f"Rate limit exceeded for user {user_id}. "
            f"Retry after {retry_after:.1f}s"
        )
        raise GraphQLError(
            f"Rate limit exceeded. Please retry after {int(retry_after)} seconds",
            extensions={
                "code": "RATE_LIMITED",
                "retryAfter": int(retry_after)
            }
        )


def rate_limit(func):
    """
    Decorator to apply rate limiting to resolver.
    
    Uses user ID from context to track requests.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract info object to get user
        info = kwargs.get('info')
        if info and hasattr(info, 'context') and info.context:
            context = info.context
            if 'user' in context and hasattr(context['user'], 'id'):
                user_id = str(context['user'].id)
                check_rate_limit(user_id)
        
        return await func(*args, **kwargs)
    return wrapper





# ============================================================================
# Type Casting & Validation
# ============================================================================

