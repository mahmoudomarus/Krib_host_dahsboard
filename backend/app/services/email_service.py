"""
Email notification service using Resend
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for transactional emails"""

    def __init__(self):
        self.resend_api_key = os.getenv("RESEND_API_KEY", "")
        self.from_email = os.getenv("FROM_EMAIL", "notifications@host.krib.ae")
        self.from_name = os.getenv("FROM_NAME", "Krib Host Platform")
        self.api_url = "https://api.resend.com/emails"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email using Resend API"""
        if not self.resend_api_key:
            logger.warning("Resend API key not configured, skipping email send")
            return {"status": "skipped", "reason": "no_api_key"}

        try:
            headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }

            if text_content:
                payload["text"] = text_content

            if reply_to:
                payload["reply_to"] = reply_to

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, headers=headers, json=payload, timeout=10
                ) as response:
                    response_data = await response.json()

                    if response.status == 200:
                        logger.info(f"Email sent successfully to {to_email}")
                        return {"status": "sent", "data": response_data}
                    else:
                        logger.error(
                            f"Failed to send email: {response.status} - {response_data}"
                        )
                        return {
                            "status": "failed",
                            "error": response_data,
                            "status_code": response.status,
                        }

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"status": "error", "error": str(e)}

    async def send_booking_notification(
        self, host_email: str, host_name: str, booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send new booking notification to host"""
        subject = f"New Booking Request - {booking_data['property_title']}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background-color: #000000; padding: 30px; text-align: center;">
                            <h1 style="color: #C6F432; margin: 0; font-size: 24px; font-weight: 700;">New Booking Request</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="font-size: 16px; color: #333333; margin: 0 0 20px;">Hello {host_name},</p>
                            <p style="font-size: 16px; color: #333333; margin: 0 0 30px;">You have received a new booking request for your property.</p>
                            
                            <table width="100%" cellpadding="12" cellspacing="0" style="background-color: #f9f9f9; border-radius: 6px; margin-bottom: 30px;">
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Property:</td>
                                    <td style="color: #333333;">{booking_data['property_title']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Guest:</td>
                                    <td style="color: #333333;">{booking_data['guest_name']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Check-in:</td>
                                    <td style="color: #333333;">{booking_data['check_in']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Check-out:</td>
                                    <td style="color: #333333;">{booking_data['check_out']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Guests:</td>
                                    <td style="color: #333333;">{booking_data['total_guests']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Total Amount:</td>
                                    <td style="color: #333333; font-weight: 700; font-size: 18px;">AED {booking_data['total_amount']}</td>
                                </tr>
                            </table>
                            
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center">
                                        <a href="https://host.krib.ae/dashboard/bookings/{booking_data['booking_id']}" 
                                           style="display: inline-block; background-color: #C6F432; color: #000000; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-weight: 600; font-size: 16px;">
                                            View Booking Details
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f9f9f9; padding: 20px 30px; border-top: 1px solid #e5e5e5;">
                            <p style="font-size: 14px; color: #666666; margin: 0;">Please respond to this booking request within 24 hours.</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #000000; padding: 20px 30px; text-align: center;">
                            <p style="font-size: 12px; color: #999999; margin: 0;">
                                © 2025 Krib Host Platform. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        text_content = f"""
New Booking Request

Hello {host_name},

You have received a new booking request:

Property: {booking_data['property_title']}
Guest: {booking_data['guest_name']}
Check-in: {booking_data['check_in']}
Check-out: {booking_data['check_out']}
Guests: {booking_data['total_guests']}
Total Amount: AED {booking_data['total_amount']}

View booking: https://host.krib.ae/dashboard/bookings/{booking_data['booking_id']}

Please respond within 24 hours.

© 2025 Krib Host Platform
"""

        return await self.send_email(host_email, subject, html_content, text_content)

    async def send_payment_received_notification(
        self, host_email: str, host_name: str, payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send payment received notification to host"""
        subject = f"Payment Received - AED {payment_data['amount']}"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background-color: #10b981; padding: 30px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Payment Received</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="font-size: 16px; color: #333333; margin: 0 0 20px;">Hello {host_name},</p>
                            <p style="font-size: 16px; color: #333333; margin: 0 0 30px;">Great news! A payment has been received for your property.</p>
                            
                            <table width="100%" cellpadding="12" cellspacing="0" style="background-color: #f0fdf4; border-radius: 6px; margin-bottom: 30px;">
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Property:</td>
                                    <td style="color: #333333;">{payment_data['property_title']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Guest:</td>
                                    <td style="color: #333333;">{payment_data['guest_name']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Amount:</td>
                                    <td style="color: #10b981; font-weight: 700; font-size: 20px;">AED {payment_data['amount']}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: 600; color: #555555;">Payment Date:</td>
                                    <td style="color: #333333;">{payment_data['payment_date']}</td>
                                </tr>
                            </table>
                            
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center">
                                        <a href="https://host.krib.ae/dashboard/financials" 
                                           style="display: inline-block; background-color: #000000; color: #C6F432; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-weight: 600; font-size: 16px;">
                                            View Financial Dashboard
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #000000; padding: 20px 30px; text-align: center;">
                            <p style="font-size: 12px; color: #999999; margin: 0;">
                                © 2025 Krib Host Platform. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        return await self.send_email(host_email, subject, html_content)


email_service = EmailService()
