"""
Host notification service
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.supabase_client import supabase_client
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

try:
    from app.services.email_service import EmailService

    email_service = EmailService()
except Exception as e:
    logger.warning(f"Email service not available: {e}")
    email_service = None

NOTIFICATION_EXPIRY_HOURS = {
    "new_booking": int(os.getenv("NOTIFICATION_EXPIRY_NEW_BOOKING", "72")),
    "default": int(os.getenv("NOTIFICATION_EXPIRY_DEFAULT", "168")),
}


class NotificationRequest(BaseModel):
    type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    booking_id: Optional[str] = Field(None, description="Related booking ID")
    property_id: Optional[str] = Field(None, description="Related property ID")
    priority: str = Field("medium", description="Notification priority")
    action_required: bool = Field(False, description="Whether action is required")
    action_url: Optional[str] = Field(None, description="Action URL")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")


class NotificationResponse(BaseModel):
    id: str
    host_id: str
    type: str
    title: str
    message: str
    booking_id: Optional[str]
    property_id: Optional[str]
    priority: str
    action_required: bool
    action_url: Optional[str]
    is_read: bool
    expires_at: Optional[str]
    created_at: str
    updated_at: str


class NotificationService:

    @staticmethod
    async def send_host_notification(
        host_id: str, notification: NotificationRequest
    ) -> Dict[str, Any]:
        """Send notification to host dashboard"""
        try:
            # Validate notification type
            valid_types = [
                "new_booking",
                "payment_received",
                "guest_message",
                "urgent",
                "booking_update",
            ]
            if notification.type not in valid_types:
                raise ValueError(
                    f"Invalid notification type. Must be one of: {valid_types}"
                )

            # Validate priority
            valid_priorities = ["high", "medium", "low"]
            if notification.priority not in valid_priorities:
                raise ValueError(
                    f"Invalid priority. Must be one of: {valid_priorities}"
                )

            notification_data = {
                "host_id": host_id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "booking_id": notification.booking_id,
                "property_id": notification.property_id,
                "priority": notification.priority,
                "action_required": notification.action_required,
                "action_url": notification.action_url,
                "expires_at": notification.expires_at,
                "is_read": False,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            result = (
                supabase_client.table("host_notifications")
                .insert(notification_data)
                .execute()
            )

            if not result.data:
                raise Exception("Failed to create notification in database")

            notification_record = result.data[0]

            # Send real-time update if SSE is implemented
            await NotificationService._send_realtime_update(
                host_id, notification_record
            )

            # Send email notification
            if email_service:
                try:
                    host_result = (
                        supabase_client.table("users")
                        .select("email, first_name")
                        .eq("id", host_id)
                        .single()
                        .execute()
                    )
                    if host_result.data:
                        host_email = host_result.data.get("email")
                        host_name = host_result.data.get("first_name", "Host")
                        if host_email:
                            await NotificationService._send_email_notification(
                                host_email, host_name, notification, notification_record
                            )
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")

            # Log the notification
            logger.info(
                f"Notification sent to host {host_id}",
                extra={
                    "host_id": host_id,
                    "notification_id": notification_record["id"],
                    "type": notification.type,
                    "priority": notification.priority,
                    "title": notification.title,
                },
            )

            return {
                "status": "sent",
                "notification_id": notification_record["id"],
                "host_id": host_id,
                "type": notification.type,
                "created_at": notification_record["created_at"],
            }

        except ValueError as e:
            logger.error(f"Validation error for notification to host {host_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to send notification to host {host_id}: {e}")
            raise

    @staticmethod
    async def get_host_notifications(
        host_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        priority_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get notifications for host with filtering options"""
        try:
            query = (
                supabase_client.table("host_notifications")
                .select("*")
                .eq("host_id", host_id)
            )

            # Apply filters
            if unread_only:
                query = query.eq("is_read", False)

            if priority_filter:
                query = query.eq("priority", priority_filter)

            if type_filter:
                query = query.eq("type", type_filter)

            # Get total count for pagination
            count_query = (
                supabase_client.table("host_notifications")
                .select("id", count="exact")
                .eq("host_id", host_id)
            )

            if unread_only:
                count_query = count_query.eq("is_read", False)
            if priority_filter:
                count_query = count_query.eq("priority", priority_filter)
            if type_filter:
                count_query = count_query.eq("type", type_filter)

            count_result = count_query.execute()
            total_count = count_result.count or 0

            # Apply pagination and ordering
            result = (
                query.order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            notifications = []
            for notification in result.data or []:
                notifications.append(NotificationResponse(**notification).dict())

            # Get unread count
            unread_count = await NotificationService.get_unread_count(host_id)

            return {
                "notifications": notifications,
                "total_count": total_count,
                "unread_count": unread_count,
                "returned_count": len(notifications),
                "has_more": (offset + limit) < total_count,
                "filters_applied": {
                    "unread_only": unread_only,
                    "priority": priority_filter,
                    "type": type_filter,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get notifications for host {host_id}: {e}")
            return {
                "notifications": [],
                "total_count": 0,
                "unread_count": 0,
                "returned_count": 0,
                "has_more": False,
                "error": str(e),
            }

    @staticmethod
    async def mark_notification_read(notification_id: str, host_id: str) -> bool:
        """Mark notification as read"""
        try:
            result = (
                supabase_client.table("host_notifications")
                .update({"is_read": True, "updated_at": datetime.utcnow().isoformat()})
                .eq("id", notification_id)
                .eq("host_id", host_id)
                .execute()
            )

            success = bool(result.data)

            if success:
                logger.info(
                    f"Notification {notification_id} marked as read by host {host_id}"
                )

            return success

        except Exception as e:
            logger.error(
                f"Failed to mark notification {notification_id} as read for host {host_id}: {e}"
            )
            return False

    @staticmethod
    async def mark_all_notifications_read(host_id: str) -> Dict[str, Any]:
        """Mark all notifications as read for a host"""
        try:
            result = (
                supabase_client.table("host_notifications")
                .update({"is_read": True, "updated_at": datetime.utcnow().isoformat()})
                .eq("host_id", host_id)
                .eq("is_read", False)
                .execute()
            )

            marked_count = len(result.data) if result.data else 0

            logger.info(
                f"Marked {marked_count} notifications as read for host {host_id}"
            )

            return {
                "status": "success",
                "marked_count": marked_count,
                "host_id": host_id,
            }

        except Exception as e:
            logger.error(
                f"Failed to mark all notifications as read for host {host_id}: {e}"
            )
            return {"status": "error", "error": str(e), "marked_count": 0}

    @staticmethod
    async def delete_notification(notification_id: str, host_id: str) -> bool:
        """Delete a notification"""
        try:
            result = (
                supabase_client.table("host_notifications")
                .delete()
                .eq("id", notification_id)
                .eq("host_id", host_id)
                .execute()
            )

            success = bool(result.data)

            if success:
                logger.info(f"Notification {notification_id} deleted by host {host_id}")

            return success

        except Exception as e:
            logger.error(
                f"Failed to delete notification {notification_id} for host {host_id}: {e}"
            )
            return False

    @staticmethod
    async def get_unread_count(host_id: str) -> int:
        """Get count of unread notifications for host"""
        try:
            result = supabase_client.rpc(
                "get_unread_notification_count", {"host_user_id": host_id}
            ).execute()
            return result.data or 0

        except Exception as e:
            logger.error(f"Failed to get unread count for host {host_id}: {e}")
            return 0

    @staticmethod
    async def cleanup_expired_notifications() -> Dict[str, Any]:
        """Clean up expired notifications"""
        try:
            result = supabase_client.rpc("cleanup_expired_notifications").execute()
            deleted_count = result.data or 0

            logger.info(f"Cleaned up {deleted_count} expired notifications")

            return {
                "status": "success",
                "deleted_count": deleted_count,
                "cleaned_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to cleanup expired notifications: {e}")
            return {"status": "error", "error": str(e), "deleted_count": 0}

    @staticmethod
    async def get_notification_statistics(host_id: str) -> Dict[str, Any]:
        """Get notification statistics for a host"""
        try:
            # Get counts by type and priority
            all_notifications = (
                supabase_client.table("host_notifications")
                .select("type, priority, is_read, created_at")
                .eq("host_id", host_id)
                .execute()
            )

            notifications = all_notifications.data or []

            # Calculate statistics
            total_count = len(notifications)
            unread_count = len([n for n in notifications if not n["is_read"]])
            read_count = total_count - unread_count

            # Count by type
            type_counts = {}
            for notification in notifications:
                type_name = notification["type"]
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

            # Count by priority
            priority_counts = {}
            for notification in notifications:
                priority = notification["priority"]
                priority_counts[priority] = priority_counts.get(priority, 0) + 1

            # Recent notifications (last 7 days)
            from datetime import timedelta

            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            recent_count = len(
                [n for n in notifications if n["created_at"] >= week_ago]
            )

            return {
                "host_id": host_id,
                "total_notifications": total_count,
                "unread_notifications": unread_count,
                "read_notifications": read_count,
                "recent_notifications_7d": recent_count,
                "notifications_by_type": type_counts,
                "notifications_by_priority": priority_counts,
                "read_percentage": round((read_count / max(total_count, 1)) * 100, 1),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Failed to get notification statistics for host {host_id}: {e}"
            )
            return {
                "host_id": host_id,
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat(),
            }

    @staticmethod
    async def _send_realtime_update(host_id: str, notification: Dict[str, Any]):
        """Send real-time update via SSE"""
        try:
            # Import here to avoid circular imports
            from app.api.routes.sse import send_sse_notification

            # Send notification via SSE
            await send_sse_notification(host_id, notification)

            logger.debug(
                f"Real-time SSE notification sent to host {host_id} for notification {notification['id']}"
            )

        except Exception as e:
            logger.error(f"Failed to send real-time update to host {host_id}: {e}")
            # Don't raise exception as this is non-critical functionality

    @staticmethod
    async def _send_email_notification(
        host_email: str,
        host_name: str,
        notification: NotificationRequest,
        notification_record: Dict[str, Any],
    ):
        """Send email notification to host"""
        if not email_service:
            return

        try:
            subject = notification.title

            email_templates = {
                "new_booking": f"""
                    <h2>New Booking Request</h2>
                    <p>Hi {host_name},</p>
                    <p>{notification.message}</p>
                    <p><a href="https://host.krib.ae{notification.action_url or '/dashboard/bookings'}" 
                       style="display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 6px;">
                       View Booking
                    </a></p>
                    <p>Best regards,<br>Krib Team</p>
                """,
                "payment_received": f"""
                    <h2>Payment Received</h2>
                    <p>Hi {host_name},</p>
                    <p>{notification.message}</p>
                    <p><a href="https://host.krib.ae/dashboard/financials" 
                       style="display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 6px;">
                       View Financials
                    </a></p>
                    <p>Best regards,<br>Krib Team</p>
                """,
                "guest_message": f"""
                    <h2>New Message from Guest</h2>
                    <p>Hi {host_name},</p>
                    <p>{notification.message}</p>
                    <p><a href="https://host.krib.ae/dashboard/messages" 
                       style="display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 6px;">
                       View Message
                    </a></p>
                    <p>Best regards,<br>Krib Team</p>
                """,
                "urgent": f"""
                    <h2>Urgent: Action Required</h2>
                    <p>Hi {host_name},</p>
                    <p><strong>{notification.message}</strong></p>
                    <p><a href="https://host.krib.ae{notification.action_url or '/dashboard'}" 
                       style="display: inline-block; padding: 12px 24px; background-color: #dc2626; color: #fff; text-decoration: none; border-radius: 6px;">
                       Take Action
                    </a></p>
                    <p>Best regards,<br>Krib Team</p>
                """,
                "booking_update": f"""
                    <h2>Booking Update</h2>
                    <p>Hi {host_name},</p>
                    <p>{notification.message}</p>
                    <p><a href="https://host.krib.ae{notification.action_url or '/dashboard/bookings'}" 
                       style="display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 6px;">
                       View Booking
                    </a></p>
                    <p>Best regards,<br>Krib Team</p>
                """,
            }

            html_content = email_templates.get(
                notification.type,
                f"""
                    <h2>{notification.title}</h2>
                    <p>Hi {host_name},</p>
                    <p>{notification.message}</p>
                    <p><a href="https://host.krib.ae/dashboard" 
                       style="display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 6px;">
                       Go to Dashboard
                    </a></p>
                    <p>Best regards,<br>Krib Team</p>
                """,
            )

            await email_service.send_email(
                to_email=host_email, subject=subject, html_content=html_content
            )

            logger.info(
                f"Email notification sent to {host_email} for notification {notification_record['id']}"
            )

        except Exception as e:
            logger.error(f"Failed to send email notification to {host_email}: {e}")

    @staticmethod
    async def create_booking_notification(
        host_id: str,
        booking_id: str,
        property_id: str,
        notification_type: str,
        guest_name: str,
        property_title: str,
        booking_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a booking-related notification with standardized format"""

        notification_templates = {
            "new_booking": {
                "title": f"New Booking Request",
                "message": f"You have a new booking request from {guest_name} for {property_title}",
                "priority": "high",
                "action_required": True,
                "action_url": f"/dashboard/bookings/{booking_id}",
            },
            "booking_confirmed": {
                "title": f"Booking Confirmed",
                "message": f"Booking from {guest_name} for {property_title} has been confirmed",
                "priority": "medium",
                "action_required": False,
                "action_url": f"/dashboard/bookings/{booking_id}",
            },
            "booking_cancelled": {
                "title": f"Booking Cancelled",
                "message": f"Booking from {guest_name} for {property_title} has been cancelled",
                "priority": "medium",
                "action_required": False,
                "action_url": f"/dashboard/bookings/{booking_id}",
            },
            "payment_received": {
                "title": f"Payment Received",
                "message": f"Payment received for booking from {guest_name} at {property_title}",
                "priority": "medium",
                "action_required": False,
                "action_url": f"/dashboard/bookings/{booking_id}",
            },
        }

        template = notification_templates.get(notification_type)
        if not template:
            raise ValueError(f"Unknown notification type: {notification_type}")

        notification = NotificationRequest(
            type=notification_type,
            title=template["title"],
            message=template["message"],
            booking_id=booking_id,
            property_id=property_id,
            priority=template["priority"],
            action_required=template["action_required"],
            action_url=template["action_url"],
            expires_at=(
                (
                    datetime.utcnow()
                    + timedelta(
                        hours=NOTIFICATION_EXPIRY_HOURS.get(
                            notification_type, NOTIFICATION_EXPIRY_HOURS["default"]
                        )
                    )
                ).isoformat()
                if notification_type == "new_booking"
                else None
            ),
        )

        return await NotificationService.send_host_notification(host_id, notification)


# Global notification service instance
notification_service = NotificationService()
