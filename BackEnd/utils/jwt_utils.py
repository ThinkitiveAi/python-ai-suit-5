"""
JWT utility functions for token generation, validation, and management.
"""
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
from core.config import settings
from schemas.token import JWTPayload, AccessTokenPayload, RefreshTokenPayload, TokenType, DecodedToken


class JWTManager:
    """JWT token management utility class."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60  # 1 hour
        self.access_token_remember_expire_hours = 24  # 24 hours for remember_me
        self.refresh_token_expire_days = 7  # 7 days
        self.refresh_token_remember_expire_days = 30  # 30 days for remember_me

    def create_access_token(
        self,
        provider_id: str,
        email: str,
        specialization: str,
        verification_status: str,
        is_active: bool,
        remember_me: bool = False
    ) -> Tuple[str, int]:
        """
        Create JWT access token.
        
        Args:
            provider_id: Provider UUID
            email: Provider email
            specialization: Medical specialization
            verification_status: Account verification status
            is_active: Account active status
            remember_me: Whether to extend token expiry
            
        Returns:
            Tuple of (token_string, expires_in_seconds)
        """
        now = datetime.now(timezone.utc)
        
        if remember_me:
            expire_delta = timedelta(hours=self.access_token_remember_expire_hours)
        else:
            expire_delta = timedelta(minutes=self.access_token_expire_minutes)
        
        expire_time = now + expire_delta
        
        payload = AccessTokenPayload(
            sub=provider_id,
            email=email,
            specialization=specialization,
            verification_status=verification_status,
            is_active=is_active,
            iat=int(now.timestamp()),
            exp=int(expire_time.timestamp())
        )
        
        token = jwt.encode(
            payload.model_dump(),
            self.secret_key,
            algorithm=self.algorithm
        )
        
        expires_in = int(expire_delta.total_seconds())
        return token, expires_in

    def create_refresh_token(
        self,
        provider_id: str,
        email: str,
        specialization: str,
        verification_status: str,
        is_active: bool,
        remember_me: bool = False
    ) -> Tuple[str, str, datetime]:
        """
        Create JWT refresh token.
        
        Args:
            provider_id: Provider UUID
            email: Provider email
            specialization: Medical specialization
            verification_status: Account verification status
            is_active: Account active status
            remember_me: Whether to extend token expiry
            
        Returns:
            Tuple of (token_string, jti, expires_at)
        """
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())
        
        if remember_me:
            expire_delta = timedelta(days=self.refresh_token_remember_expire_days)
        else:
            expire_delta = timedelta(days=self.refresh_token_expire_days)
        
        expire_time = now + expire_delta
        
        payload = RefreshTokenPayload(
            sub=provider_id,
            email=email,
            specialization=specialization,
            verification_status=verification_status,
            is_active=is_active,
            jti=jti,
            iat=int(now.timestamp()),
            exp=int(expire_time.timestamp())
        )
        
        token = jwt.encode(
            payload.model_dump(),
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return token, jti, expire_time

    def decode_token(self, token: str) -> DecodedToken:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            DecodedToken with payload and validation info
        """
        try:
            payload_dict = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Validate token type and create appropriate payload
            token_type = payload_dict.get('token_type')
            if token_type == TokenType.ACCESS:
                payload = AccessTokenPayload(**payload_dict)
            elif token_type == TokenType.REFRESH:
                payload = RefreshTokenPayload(**payload_dict)
            else:
                payload = JWTPayload(**payload_dict)
            
            # Check if token is expired
            now = datetime.now(timezone.utc)
            exp_time = datetime.fromtimestamp(payload.exp, tz=timezone.utc)
            is_expired = now > exp_time
            
            return DecodedToken(
                payload=payload,
                is_valid=not is_expired,
                is_expired=is_expired,
                error=None
            )
            
        except jwt.ExpiredSignatureError:
            return DecodedToken(
                payload=None,
                is_valid=False,
                is_expired=True,
                error="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            return DecodedToken(
                payload=None,
                is_valid=False,
                is_expired=False,
                error=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            return DecodedToken(
                payload=None,
                is_valid=False,
                is_expired=False,
                error=f"Token decode error: {str(e)}"
            )

    def verify_access_token(self, token: str) -> Optional[AccessTokenPayload]:
        """
        Verify access token and return payload if valid.
        
        Args:
            token: JWT access token
            
        Returns:
            AccessTokenPayload if valid, None otherwise
        """
        decoded = self.decode_token(token)
        
        if not decoded.is_valid or decoded.payload is None:
            return None
            
        if decoded.payload.token_type != TokenType.ACCESS:
            return None
            
        return decoded.payload

    def verify_refresh_token(self, token: str) -> Optional[RefreshTokenPayload]:
        """
        Verify refresh token and return payload if valid.
        
        Args:
            token: JWT refresh token
            
        Returns:
            RefreshTokenPayload if valid, None otherwise
        """
        decoded = self.decode_token(token)
        
        if not decoded.is_valid or decoded.payload is None:
            return None
            
        if decoded.payload.token_type != TokenType.REFRESH:
            return None
            
        return decoded.payload

    def extract_token_from_header(self, authorization: str) -> Optional[str]:
        """
        Extract JWT token from Authorization header.
        
        Args:
            authorization: Authorization header value
            
        Returns:
            Token string if valid format, None otherwise
        """
        if not authorization:
            return None
            
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None

    def get_token_expiry_info(self, token: str) -> Dict[str, Any]:
        """
        Get token expiry information.
        
        Args:
            token: JWT token
            
        Returns:
            Dictionary with expiry information
        """
        decoded = self.decode_token(token)
        
        if not decoded.payload:
            return {"error": decoded.error}
            
        exp_time = datetime.fromtimestamp(decoded.payload.exp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        return {
            "expires_at": exp_time.isoformat(),
            "is_expired": decoded.is_expired,
            "time_remaining": int((exp_time - now).total_seconds()) if not decoded.is_expired else 0
        }


# Global JWT manager instance
jwt_manager = JWTManager()
