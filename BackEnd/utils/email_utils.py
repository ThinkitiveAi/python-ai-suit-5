"""
Utility functions for email formatting and token generation.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from core.config import settings
from core.security import security
import logging

logger = logging.getLogger(__name__)


class EmailManager:
    """Email management utilities."""
    
    @staticmethod
    def generate_verification_token() -> str:
        """
        Generate a secure verification token.
        
        Returns:
            Secure verification token
        """
        return security.generate_verification_token()
    
    @staticmethod
    def create_verification_email_content(
        provider_name: str, 
        verification_token: str
    ) -> tuple[str, str]:
        """
        Create verification email content.
        
        Args:
            provider_name: Name of the provider
            verification_token: Verification token
            
        Returns:
            Tuple of (subject, html_content)
        """
        subject = f"Verify Your {settings.APP_NAME} Account"
        
        # In a real application, this would be a proper verification URL
        verification_url = f"https://yourdomain.com/verify?token={verification_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Account Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #28a745; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {settings.APP_NAME}</h1>
                </div>
                <div class="content">
                    <h2>Hello {provider_name},</h2>
                    <p>Thank you for registering as a healthcare provider with {settings.APP_NAME}.</p>
                    <p>To complete your registration and activate your account, please verify your email address by clicking the button below:</p>
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </div>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p><a href="{verification_url}">{verification_url}</a></p>
                    <p><strong>Important:</strong> This verification link will expire in 24 hours for security reasons.</p>
                    <p>If you didn't create this account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {settings.APP_NAME}. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, html_content
    
    @staticmethod
    async def send_verification_email(
        recipient_email: str, 
        provider_name: str, 
        verification_token: str
    ) -> bool:
        """
        Send verification email to the provider.
        
        Args:
            recipient_email: Provider's email address
            provider_name: Provider's name
            verification_token: Verification token
            
        Returns:
            True if email sent successfully
        """
        try:
            subject, html_content = EmailManager.create_verification_email_content(
                provider_name, verification_token
            )
            
            # For development/testing, just print to console
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print("VERIFICATION EMAIL (Development Mode)")
                print(f"{'='*50}")
                print(f"To: {recipient_email}")
                print(f"Subject: {subject}")
                print(f"Verification Token: {verification_token}")
                print(f"Provider Name: {provider_name}")
                print(f"{'='*50}\n")
                return True
            
            # In production, send actual email
            return await EmailManager._send_smtp_email(
                recipient_email, subject, html_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {recipient_email}: {e}")
            return False
    
    @staticmethod
    async def _send_smtp_email(
        recipient_email: str, 
        subject: str, 
        html_content: str
    ) -> bool:
        """
        Send email via SMTP.
        
        Args:
            recipient_email: Recipient's email
            subject: Email subject
            html_content: HTML email content
            
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.FROM_EMAIL
            msg['To'] = recipient_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                server.send_message(msg)
            
            logger.info(f"Verification email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error sending email to {recipient_email}: {e}")
            return False
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email format is valid
        """
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize email address.
        
        Args:
            email: Email address to normalize
            
        Returns:
            Normalized email address
        """
        return email.lower().strip()
