"""
Simple rate limiter to prevent request spam
"""

import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """
    In-memory rate limiter.
    Prevents too many requests from same session in short time.
    """
    
    def __init__(self, max_requests: int = 1, window_seconds: int = 10):
        """
        Args:
            max_requests: Max requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # session_id -> [timestamps]
        self.lock = Lock()
    
    def is_allowed(self, session_id: str) -> tuple[bool, str]:
        """
        Check if request is allowed.
        
        Returns:
            (allowed: bool, reason: str)
        """
        with self.lock:
            now = time.time()
            
            # Clean old timestamps
            if session_id in self.requests:
                self.requests[session_id] = [
                    ts for ts in self.requests[session_id]
                    if now - ts < self.window_seconds
                ]
            
            # Check rate
            request_count = len(self.requests[session_id])
            
            if request_count >= self.max_requests:
                return False, f"Rate limit exceeded: {request_count}/{self.max_requests} requests in {self.window_seconds}s"
            
            # Allow and record
            self.requests[session_id].append(now)
            return True, "OK"
    
    def reset(self, session_id: str):
        """Clear rate limit for session"""
        with self.lock:
            if session_id in self.requests:
                del self.requests[session_id]

