"""Email service for sending notifications and verification emails."""

import boto3
from botocore.exceptions import ClientError
from typing import Optional
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via AWS SES."""

    def __init__(self):
        """Initialize email service with AWS SES client."""
        self.ses_client = boto3.client(
            "ses",
            region_name=settings.SES_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    async def send_verification_email(self, email: str, verification_url: str) -> bool:
        """Send email verification email."""
        subject = "Verify Your Email - Quote of the Day"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4f46e5; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Quote of the Day!</h1>
                </div>
                <div class="content">
                    <p>Thank you for signing up! To complete your registration, please verify your email address by clicking the button below:</p>
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #4f46e5;">{verification_url}</p>
                    <p>This link will expire in 24 hours for security reasons.</p>
                </div>
                <div class="footer">
                    <p>If you didn't create an account, please ignore this email.</p>
                    <p>&copy; 2024 Quote of the Day. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Quote of the Day!
        
        Thank you for signing up! To complete your registration, please verify your email address by visiting this link:
        
        {verification_url}
        
        This link will expire in 24 hours for security reasons.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        Quote of the Day Team
        """

        return await self._send_email(email, subject, html_body, text_body)

    async def send_password_reset_email(self, email: str, reset_url: str) -> bool:
        """Send password reset email."""
        subject = "Reset Your Password - Quote of the Day"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #dc2626; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
                .warning {{ background-color: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 6px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>We received a request to reset your password for your Quote of the Day account.</p>
                    <p>To reset your password, click the button below:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #dc2626;">{reset_url}</p>
                    <div class="warning">
                        <strong>Important:</strong> This link will expire in 1 hour for security reasons. If you didn't request this password reset, please ignore this email and your password will remain unchanged.
                    </div>
                </div>
                <div class="footer">
                    <p>If you didn't request this password reset, please ignore this email.</p>
                    <p>&copy; 2024 Quote of the Day. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Password Reset Request
        
        We received a request to reset your password for your Quote of the Day account.
        
        To reset your password, visit this link:
        
        {reset_url}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, please ignore this email and your password will remain unchanged.
        
        Best regards,
        Quote of the Day Team
        """

        return await self._send_email(email, subject, html_body, text_body)

    async def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email after successful verification."""
        subject = "Welcome to Quote of the Day!"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome!</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #059669; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .feature {{ margin: 15px 0; padding: 15px; background-color: white; border-radius: 6px; border-left: 4px solid #059669; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Quote of the Day!</h1>
                </div>
                <div class="content">
                    <p>Hi {name},</p>
                    <p>Your email has been verified and your account is now active! Welcome to Quote of the Day.</p>
                    
                    <h3>What you can do now:</h3>
                    <div class="feature">
                        <strong>📱 Download our mobile app</strong><br>
                        Get daily inspirational quotes delivered directly to your device.
                    </div>
                    <div class="feature">
                        <strong>⚙️ Customize your preferences</strong><br>
                        Set your preferred delivery time and notification settings.
                    </div>
                    <div class="feature">
                        <strong>💎 Upgrade to Premium</strong><br>
                        Access exclusive quotes, advanced features, and ad-free experience.
                    </div>
                    
                    <p>We're excited to have you on board!</p>
                </div>
                <div class="footer">
                    <p>Thank you for choosing Quote of the Day!</p>
                    <p>&copy; 2024 Quote of the Day. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Quote of the Day!
        
        Hi {name},
        
        Your email has been verified and your account is now active! Welcome to Quote of the Day.
        
        What you can do now:
        - Download our mobile app to get daily inspirational quotes
        - Customize your preferences and notification settings
        - Upgrade to Premium for exclusive features
        
        We're excited to have you on board!
        
        Best regards,
        Quote of the Day Team
        """

        return await self._send_email(email, subject, html_body, text_body)

    async def _send_email(
        self, to_email: str, subject: str, html_body: str, text_body: str
    ) -> bool:
        """Send email via AWS SES."""
        try:
            response = self.ses_client.send_email(
                Source=settings.SES_EMAIL_FROM,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                    },
                },
            )

            logger.info(
                f"Email sent successfully to {to_email}. MessageId: {response['MessageId']}"
            )
            return True

        except ClientError as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False

    async def send_notification_email(
        self, email: str, quote_text: str, author: str
    ) -> bool:
        """Send daily quote notification email."""
        subject = "Your Daily Quote - Quote of the Day"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Daily Quote</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4f46e5; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .quote {{ font-size: 18px; font-style: italic; text-align: center; margin: 30px 0; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .author {{ text-align: right; color: #6b7280; margin-top: 10px; }}
                .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Daily Quote</h1>
                </div>
                <div class="content">
                    <div class="quote">
                        "{quote_text}"
                        <div class="author">— {author}</div>
                    </div>
                    <p>Have a wonderful day!</p>
                </div>
                <div class="footer">
                    <p>Quote of the Day - Inspiring you every day</p>
                    <p>&copy; 2024 Quote of the Day. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Your Daily Quote
        
        "{quote_text}"
        — {author}
        
        Have a wonderful day!
        
        Quote of the Day - Inspiring you every day
        """

        return await self._send_email(email, subject, html_body, text_body)
