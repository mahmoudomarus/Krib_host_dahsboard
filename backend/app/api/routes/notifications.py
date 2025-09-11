"""
Host notification endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from app.api.dependencies import get_current_user
from app.api.dependencies_external import get_external_service_context
from app.services.notification_service import NotificationService, NotificationRequest, NotificationResponse
from app.models.external_schemas import ExternalAPIResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/v1/hosts/{host_id}/notifications", response_model=ExternalAPIResponse)
async def send_host_notification(
    host_id: str,
    notification: NotificationRequest,
    service_context: dict = Depends(get_external_service_context)
):
    """Send notification to host dashboard"""
    try:
        result = await NotificationService.send_host_notification(host_id, notification)
        
        logger.info(
            f"Notification sent via API",
            extra={
                "host_id": host_id,
                "notification_id": result["notification_id"],
                "type": notification.type,
                "priority": notification.priority,
                "service_name": service_context.get("service_name", "unknown")
            }
        )
        
        return ExternalAPIResponse(
            success=True,
            data=result,
            message="Notification sent successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to send notification to host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )

@router.get("/v1/hosts/{host_id}/notifications", response_model=ExternalAPIResponse)
async def get_host_notifications(
    host_id: str,
    unread_only: bool = Query(False, description="Return only unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    priority: Optional[str] = Query(None, description="Filter by priority (high, medium, low)"),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    current_user: dict = Depends(get_current_user)
):
    """Get notifications for host"""
    try:
        # Verify user can access these notifications
        if current_user["id"] != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you can only access your own notifications"
            )
        
        result = await NotificationService.get_host_notifications(
            host_id=host_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset,
            priority_filter=priority,
            type_filter=type
        )
        
        return ExternalAPIResponse(
            success=True,
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notifications for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.put("/v1/hosts/{host_id}/notifications/{notification_id}/read", response_model=ExternalAPIResponse)
async def mark_notification_read(
    host_id: str,
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        # Verify user can mark this notification
        if current_user["id"] != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you can only modify your own notifications"
            )
        
        success = await NotificationService.mark_notification_read(notification_id, host_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return ExternalAPIResponse(
            success=True,
            data={"notification_id": notification_id, "marked_read": True},
            message="Notification marked as read"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification {notification_id} as read for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.put("/v1/hosts/{host_id}/notifications/read-all", response_model=ExternalAPIResponse)
async def mark_all_notifications_read(
    host_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark all notifications as read for a host"""
    try:
        # Verify user can mark notifications
        if current_user["id"] != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you can only modify your own notifications"
            )
        
        result = await NotificationService.mark_all_notifications_read(host_id)
        
        return ExternalAPIResponse(
            success=True,
            data=result,
            message=f"Marked {result['marked_count']} notifications as read"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark all notifications as read for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )

@router.delete("/v1/hosts/{host_id}/notifications/{notification_id}", response_model=ExternalAPIResponse)
async def delete_notification(
    host_id: str,
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        # Verify user can delete this notification
        if current_user["id"] != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you can only delete your own notifications"
            )
        
        success = await NotificationService.delete_notification(notification_id, host_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return ExternalAPIResponse(
            success=True,
            data={"notification_id": notification_id, "deleted": True},
            message="Notification deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete notification {notification_id} for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )

@router.get("/v1/hosts/{host_id}/notifications/count", response_model=ExternalAPIResponse)
async def get_notification_count(
    host_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get unread notification count for host"""
    try:
        # Verify user can access notification count
        if current_user["id"] != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you can only access your own notification count"
            )
        
        unread_count = await NotificationService.get_unread_count(host_id)
        
        return ExternalAPIResponse(
            success=True,
            data={
                "host_id": host_id,
                "unread_count": unread_count
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification count for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification count: {str(e)}"
        )

@router.get("/v1/hosts/{host_id}/notifications/statistics", response_model=ExternalAPIResponse)
async def get_notification_statistics(
    host_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get notification statistics for host"""
    try:
        # Verify user can access notification statistics
        if current_user["id"] != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied - you can only access your own notification statistics"
            )
        
        statistics = await NotificationService.get_notification_statistics(host_id)
        
        return ExternalAPIResponse(
            success=True,
            data=statistics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification statistics for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification statistics: {str(e)}"
        )

# External service endpoint for creating booking notifications
@router.post("/v1/external/hosts/{host_id}/booking-notifications", response_model=ExternalAPIResponse)
async def create_booking_notification(
    host_id: str,
    booking_id: str = Query(..., description="Booking ID"),
    property_id: str = Query(..., description="Property ID"),
    notification_type: str = Query(..., description="Notification type"),
    guest_name: str = Query(..., description="Guest name"),
    property_title: str = Query(..., description="Property title"),
    service_context: dict = Depends(get_external_service_context)
):
    """Create a standardized booking notification"""
    try:
        # Get booking details for the notification
        from app.core.supabase_client import supabase_client
        
        booking_result = supabase_client.table("bookings").select("*").eq("id", booking_id).execute()
        
        if not booking_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        booking_details = booking_result.data[0]
        
        result = await NotificationService.create_booking_notification(
            host_id=host_id,
            booking_id=booking_id,
            property_id=property_id,
            notification_type=notification_type,
            guest_name=guest_name,
            property_title=property_title,
            booking_details=booking_details
        )
        
        logger.info(
            f"Booking notification created",
            extra={
                "host_id": host_id,
                "booking_id": booking_id,
                "notification_type": notification_type,
                "notification_id": result["notification_id"],
                "service_name": service_context.get("service_name", "unknown")
            }
        )
        
        return ExternalAPIResponse(
            success=True,
            data=result,
            message="Booking notification created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create booking notification for host {host_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking notification: {str(e)}"
        )

# Bulk operations for external services
@router.post("/v1/external/notifications/bulk", response_model=ExternalAPIResponse)
async def send_bulk_notifications(
    notifications: List[Dict[str, Any]],
    service_context: dict = Depends(get_external_service_context)
):
    """Send multiple notifications in bulk"""
    try:
        results = []
        
        for notification_data in notifications:
            try:
                host_id = notification_data.pop("host_id")
                notification = NotificationRequest(**notification_data)
                
                result = await NotificationService.send_host_notification(host_id, notification)
                results.append({
                    "host_id": host_id,
                    "status": "success",
                    "notification_id": result["notification_id"]
                })
                
            except Exception as e:
                results.append({
                    "host_id": notification_data.get("host_id", "unknown"),
                    "status": "failed",
                    "error": str(e)
                })
        
        successful_count = len([r for r in results if r["status"] == "success"])
        failed_count = len(results) - successful_count
        
        logger.info(
            f"Bulk notifications processed: {successful_count} successful, {failed_count} failed",
            extra={
                "successful_count": successful_count,
                "failed_count": failed_count,
                "total_count": len(results),
                "service_name": service_context.get("service_name", "unknown")
            }
        )
        
        return ExternalAPIResponse(
            success=True,
            data={
                "results": results,
                "total_count": len(results),
                "successful_count": successful_count,
                "failed_count": failed_count
            },
            message=f"Bulk notifications processed: {successful_count} successful, {failed_count} failed"
        )
        
    except Exception as e:
        logger.error(f"Failed to process bulk notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process bulk notifications: {str(e)}"
        )

# Admin endpoint for cleanup
@router.post("/v1/external/notifications/cleanup", response_model=ExternalAPIResponse)
async def cleanup_expired_notifications(
    service_context: dict = Depends(get_external_service_context)
):
    """Clean up expired notifications"""
    try:
        result = await NotificationService.cleanup_expired_notifications()
        
        logger.info(
            f"Notification cleanup completed",
            extra={
                "deleted_count": result["deleted_count"],
                "service_name": service_context.get("service_name", "unknown")
            }
        )
        
        return ExternalAPIResponse(
            success=True,
            data=result,
            message=f"Cleaned up {result['deleted_count']} expired notifications"
        )
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup expired notifications: {str(e)}"
        )
