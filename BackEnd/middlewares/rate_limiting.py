"""
Rate limiting middleware for API endpoints.
"""
import time
from typing import Dict, Tuple
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging
from core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory rate limiter for API endpoints."""
    
    def __init__(self):
        # In production, this should be replaced with Redis or similar
        self._requests: Dict[str, list] = {}
        self._blocked_ips: Dict[str, float] = {}
    
    def is_allowed(self, ip_address: str, max_requests: int = None, window_seconds: int = None) -> Tuple[bool, int]:
        """
        Check if request from IP is allowed based on rate limits.
        
        Args:
            ip_address: Client IP address
            max_requests: Maximum requests allowed (defaults to config)
            window_seconds: Time window in seconds (defaults to config)
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if max_requests is None:
            max_requests = settings.RATE_LIMIT_REQUESTS
        if window_seconds is None:
            window_seconds = settings.RATE_LIMIT_WINDOW
        
        current_time = time.time()
        
        # Check if IP is temporarily blocked
        if ip_address in self._blocked_ips:
            if current_time < self._blocked_ips[ip_address]:
                return False, 0
            else:
                # Unblock IP
                del self._blocked_ips[ip_address]
        
        # Initialize or clean up request history for this IP
        if ip_address not in self._requests:
            self._requests[ip_address] = []
        
        # Remove old requests outside the time window
        self._requests[ip_address] = [
            req_time for req_time in self._requests[ip_address]
            if current_time - req_time < window_seconds
        ]
        
        # Check if under the limit
        if len(self._requests[ip_address]) < max_requests:
            self._requests[ip_address].append(current_time)
            remaining = max_requests - len(self._requests[ip_address])
            return True, remaining
        
        # Rate limit exceeded
        logger.warning(f"Rate limit exceeded for IP: {ip_address}")
        
        # Block IP for additional time if they keep hitting the limit
        if len(self._requests[ip_address]) >= max_requests:
            # Block for 15 minutes
            self._blocked_ips[ip_address] = current_time + 900
        
        return False, 0
    
    def get_rate_limit_info(self, ip_address: str) -> Dict[str, int]:
        """
        Get rate limit information for an IP.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            Dictionary with rate limit info
        """
        current_time = time.time()
        
        if ip_address not in self._requests:
            return {
                "requests_made": 0,
                "requests_remaining": settings.RATE_LIMIT_REQUESTS,
                "window_seconds": settings.RATE_LIMIT_WINDOW,
                "reset_time": int(current_time + settings.RATE_LIMIT_WINDOW)
            }
        
        # Clean old requests
        self._requests[ip_address] = [
            req_time for req_time in self._requests[ip_address]
            if current_time - req_time < settings.RATE_LIMIT_WINDOW
        ]
        
        requests_made = len(self._requests[ip_address])
        requests_remaining = max(0, settings.RATE_LIMIT_REQUESTS - requests_made)
        
        # Calculate reset time (when the oldest request will expire)
        reset_time = int(current_time + settings.RATE_LIMIT_WINDOW)
        if self._requests[ip_address]:
            oldest_request = min(self._requests[ip_address])
            reset_time = int(oldest_request + settings.RATE_LIMIT_WINDOW)
        
        return {
            "requests_made": requests_made,
            "requests_remaining": requests_remaining,
            "window_seconds": settings.RATE_LIMIT_WINDOW,
            "reset_time": reset_time
        }
    
    def clear_ip_history(self, ip_address: str):
        """Clear rate limit history for an IP (admin function)."""
        if ip_address in self._requests:
            del self._requests[ip_address]
        if ip_address in self._blocked_ips:
            del self._blocked_ips[ip_address]
        logger.info(f"Cleared rate limit history for IP: {ip_address}")


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for forwarded headers (when behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware for FastAPI.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/endpoint in chain
        
    Returns:
        Response or rate limit error
    """
    # Only apply rate limiting to specific endpoints
    if not request.url.path.startswith("/api/v1/provider/register"):
        response = await call_next(request)
        return response
    
    client_ip = get_client_ip(request)
    
    # Check rate limit
    is_allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        rate_info = rate_limiter.get_rate_limit_info(client_ip)
        
        # Return rate limit error
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "message": "Rate limit exceeded. Too many registration attempts.",
                "details": {
                    "max_requests": settings.RATE_LIMIT_REQUESTS,
                    "window_seconds": settings.RATE_LIMIT_WINDOW,
                    "reset_time": rate_info["reset_time"],
                    "retry_after": rate_info["reset_time"] - int(time.time())
                }
            },
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_info["reset_time"]),
                "Retry-After": str(rate_info["reset_time"] - int(time.time()))
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers to response
    rate_info = rate_limiter.get_rate_limit_info(client_ip)
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(rate_info["requests_remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_info["reset_time"])
    
    return response


def rate_limit_dependency(request: Request):
    """
    FastAPI dependency for rate limiting specific endpoints.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    client_ip = get_client_ip(request)
    
    is_allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        rate_info = rate_limiter.get_rate_limit_info(client_ip)
        
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "message": "Rate limit exceeded. Too many registration attempts.",
                "details": {
                    "max_requests": settings.RATE_LIMIT_REQUESTS,
                    "window_seconds": settings.RATE_LIMIT_WINDOW,
                    "reset_time": rate_info["reset_time"],
                    "retry_after": rate_info["reset_time"] - int(time.time())
                }
            },
            headers={
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_info["reset_time"]),
                "Retry-After": str(rate_info["reset_time"] - int(time.time()))
            }
        )
    
    return {"client_ip": client_ip, "remaining_requests": remaining}
