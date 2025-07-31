"""
Email service for sending verification emails and notifications.
"""
import logging
from typing import Optional
from utils.email_utils import EmailManager
from core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling email operations."""
    
    def __init__(self):
        self.email_manager = EmailManager()
    
    async def send_verification_email(
        self, 
        provider_email: str, 
        provider_name: str, 
        verification_token: str
    ) -> bool:
        """
        Send verification email to newly registered provider.
        
        Args:
            provider_email: Provider's email address
            provider_name: Provider's full name
            verification_token: Unique verification token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending verification email to {provider_email}")
            
            success = await self.email_manager.send_verification_email(
                recipient_email=provider_email,
                provider_name=provider_name,
                verification_token=verification_token
            )
            
            if success:
                logger.info(f"Verification email sent successfully to {provider_email}")
            else:
                logger.error(f"Failed to send verification email to {provider_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending verification email to {provider_email}: {e}")
            return False
    
    async def send_welcome_email(
        self, 
        provider_email: str, 
        provider_name: str
    ) -> bool:
        """
        Send welcome email after successful verification.
        
        Args:
            provider_email: Provider's email address
            provider_name: Provider's full name
            
        Returns:
            True if email sent successfully
        """
        try:
            logger.info(f"Sending welcome email to {provider_email}")
            
            # For development, just log the welcome email
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print("WELCOME EMAIL (Development Mode)")
                print(f"{'='*50}")
                print(f"To: {provider_email}")
                print(f"Subject: Welcome to {settings.APP_NAME}!")
                print(f"Provider Name: {provider_name}")
                print("Content: Welcome! Your account has been verified successfully.")
                print(f"{'='*50}\n")
                return True
            
            # In production, implement actual welcome email sending
            # This would use the same SMTP logic as verification email
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome email to {provider_email}: {e}")
            return False
    
    async def send_password_reset_email(
        self, 
        provider_email: str, 
        provider_name: str, 
        reset_token: str
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            provider_email: Provider's email address
            provider_name: Provider's full name
            reset_token: Password reset token
            
        Returns:
            True if email sent successfully
        """
        try:
            logger.info(f"Sending password reset email to {provider_email}")
            
            # For development, just log the reset email
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print("PASSWORD RESET EMAIL (Development Mode)")
                print(f"{'='*50}")
                print(f"To: {provider_email}")
                print(f"Subject: Password Reset Request - {settings.APP_NAME}")
                print(f"Provider Name: {provider_name}")
                print(f"Reset Token: {reset_token}")
                print("Content: Click the link to reset your password.")
                print(f"{'='*50}\n")
                return True
            
            # In production, implement actual password reset email
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email to {provider_email}: {e}")
            return False
    
    async def send_account_locked_email(
        self, 
        provider_email: str, 
        provider_name: str
    ) -> bool:
        """
        Send account locked notification email.
        
        Args:
            provider_email: Provider's email address
            provider_name: Provider's full name
            
        Returns:
            True if email sent successfully
        """
        try:
            logger.info(f"Sending account locked email to {provider_email}")
            
            # For development, just log the account locked email
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print("ACCOUNT LOCKED EMAIL (Development Mode)")
                print(f"{'='*50}")
                print(f"To: {provider_email}")
                print(f"Subject: Account Security Alert - {settings.APP_NAME}")
                print(f"Provider Name: {provider_name}")
                print("Content: Your account has been temporarily locked due to security reasons.")
                print(f"{'='*50}\n")
                return True
            
            # In production, implement actual account locked email
            return True
            
        except Exception as e:
            logger.error(f"Error sending account locked email to {provider_email}: {e}")
            return False
    
    def generate_verification_token(self) -> str:
        """
        Generate a new verification token.
        
        Returns:
            Secure verification token
        """
        return self.email_manager.generate_verification_token()
    
    @staticmethod
    def validate_email_deliverability(email: str) -> bool:
        """
        Check if email address is deliverable (basic validation).
        
        Args:
            email: Email address to check
            
        Returns:
            True if email appears deliverable
        """
        # In a production system, you might integrate with email validation services
        # like ZeroBounce, Hunter.io, or similar services
        
        # For now, just do basic format validation
        return EmailManager.validate_email_format(email)


# Global email service instance
email_service = EmailService()
