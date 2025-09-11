"""
Webhook management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.api.dependencies_external import get_external_service_context
from app.core.supabase_client import supabase_client
from app.models.external_schemas import ExternalAPIResponse
from app.services.webhook_service import webhook_service
from pydantic import BaseModel, Field, HttpUrl
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class WebhookSubscriptionRequest(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=255, description="AI agent name")
    webhook_url: HttpUrl = Field(..., description="Webhook endpoint URL")
    events: List[str] = Field(..., min_items=1, description="List of events to subscribe to")
    api_key: str = Field(..., min_length=10, max_length=500, description="API key for verification")

class WebhookSubscriptionResponse(BaseModel):
    id: str
    agent_name: str
    webhook_url: str
    events: List[str]
    is_active: bool
    failed_attempts: int
    last_successful_call: Optional[str]
    created_at: str
    updated_at: str

class WebhookTestRequest(BaseModel):
    event_type: str = Field(..., description="Event type to test")
    test_data: Dict[str, Any] = Field(default_factory=dict, description="Test data payload")

@router.post("/v1/external/webhook-subscriptions", response_model=ExternalAPIResponse)
async def register_webhook_subscription(
    subscription_request: WebhookSubscriptionRequest,
    service_context: dict = Depends(get_external_service_context)
):
    """Register webhook subscription for external AI agent"""
    try:
        # Validate events
        valid_events = [
            "booking.created",
            "booking.confirmed", 
            "booking.cancelled",
            "payment.received",
            "host.response_needed",
            "test.webhook"  # For testing purposes
        ]
        
        invalid_events = [event for event in subscription_request.events if event not in valid_events]
        if invalid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid events provided",
                    "invalid_events": invalid_events,
                    "valid_events": valid_events
                }
            )
        
        # Check if webhook URL is already registered
        existing_result = supabase_client.table("webhook_subscriptions").select("id").eq(
            "webhook_url", str(subscription_request.webhook_url)
        ).execute()
        
        if existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Webhook URL is already registered"
            )
        
        # Create subscription
        subscription_data = {
            "agent_name": subscription_request.agent_name,
            "webhook_url": str(subscription_request.webhook_url),
            "events": subscription_request.events,
            "api_key": subscription_request.api_key,
            "is_active": True,
            "failed_attempts": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase_client.table("webhook_subscriptions").insert(subscription_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create webhook subscription"
            )
        
        subscription = result.data[0]
        
        logger.info(
            f"Webhook subscription created",
            extra={
                "subscription_id": subscription["id"],
                "agent_name": subscription["agent_name"],
                "webhook_url": subscription["webhook_url"],
                "events": subscription["events"]
            }
        )
        
        return ExternalAPIResponse(
            success=True,
            data=WebhookSubscriptionResponse(
                id=subscription["id"],
                agent_name=subscription["agent_name"],
                webhook_url=subscription["webhook_url"],
                events=subscription["events"],
                is_active=subscription["is_active"],
                failed_attempts=subscription["failed_attempts"],
                last_successful_call=subscription.get("last_successful_call"),
                created_at=subscription["created_at"],
                updated_at=subscription["updated_at"]
            ).dict(),
            message="Webhook subscription created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register webhook subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register webhook subscription: {str(e)}"
        )

@router.get("/v1/external/webhook-subscriptions", response_model=ExternalAPIResponse)
async def list_webhook_subscriptions(
    service_context: dict = Depends(get_external_service_context),
    active_only: bool = Query(False, description="Return only active subscriptions"),
    agent_name: Optional[str] = Query(None, description="Filter by agent name"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List webhook subscriptions with filtering options"""
    try:
        query = supabase_client.table("webhook_subscriptions").select("*")
        
        # Apply filters
        if active_only:
            query = query.eq("is_active", True)
        
        if agent_name:
            query = query.ilike("agent_name", f"%{agent_name}%")
        
        # Get total count for pagination
        count_query = supabase_client.table("webhook_subscriptions").select("id", count="exact")
        if active_only:
            count_query = count_query.eq("is_active", True)
        if agent_name:
            count_query = count_query.ilike("agent_name", f"%{agent_name}%")
        
        count_result = count_query.execute()
        total_count = count_result.count or 0
        
        # Apply pagination and ordering
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        subscriptions = []
        for sub in result.data or []:
            subscriptions.append(WebhookSubscriptionResponse(
                id=sub["id"],
                agent_name=sub["agent_name"],
                webhook_url=sub["webhook_url"],
                events=sub["events"],
                is_active=sub["is_active"],
                failed_attempts=sub["failed_attempts"],
                last_successful_call=sub.get("last_successful_call"),
                created_at=sub["created_at"],
                updated_at=sub["updated_at"]
            ).dict())
        
        return ExternalAPIResponse(
            success=True,
            data={
                "subscriptions": subscriptions,
                "total_count": total_count,
                "returned_count": len(subscriptions),
                "has_more": (offset + limit) < total_count,
                "filters_applied": {
                    "active_only": active_only,
                    "agent_name": agent_name
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to list webhook subscriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list webhook subscriptions: {str(e)}"
        )

@router.get("/v1/external/webhook-subscriptions/{subscription_id}", response_model=ExternalAPIResponse)
async def get_webhook_subscription(
    subscription_id: str,
    service_context: dict = Depends(get_external_service_context)
):
    """Get specific webhook subscription details"""
    try:
        result = supabase_client.table("webhook_subscriptions").select("*").eq("id", subscription_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook subscription not found"
            )
        
        subscription = result.data[0]
        
        return ExternalAPIResponse(
            success=True,
            data=WebhookSubscriptionResponse(
                id=subscription["id"],
                agent_name=subscription["agent_name"],
                webhook_url=subscription["webhook_url"],
                events=subscription["events"],
                is_active=subscription["is_active"],
                failed_attempts=subscription["failed_attempts"],
                last_successful_call=subscription.get("last_successful_call"),
                created_at=subscription["created_at"],
                updated_at=subscription["updated_at"]
            ).dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get webhook subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get webhook subscription: {str(e)}"
        )

@router.put("/v1/external/webhook-subscriptions/{subscription_id}", response_model=ExternalAPIResponse)
async def update_webhook_subscription(
    subscription_id: str,
    subscription_update: WebhookSubscriptionRequest,
    service_context: dict = Depends(get_external_service_context)
):
    """Update webhook subscription"""
    try:
        # Validate events
        valid_events = [
            "booking.created",
            "booking.confirmed", 
            "booking.cancelled",
            "payment.received",
            "host.response_needed",
            "test.webhook"
        ]
        
        invalid_events = [event for event in subscription_update.events if event not in valid_events]
        if invalid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid events provided",
                    "invalid_events": invalid_events,
                    "valid_events": valid_events
                }
            )
        
        # Check if subscription exists
        existing_result = supabase_client.table("webhook_subscriptions").select("id").eq("id", subscription_id).execute()
        
        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook subscription not found"
            )
        
        # Update subscription
        update_data = {
            "agent_name": subscription_update.agent_name,
            "webhook_url": str(subscription_update.webhook_url),
            "events": subscription_update.events,
            "api_key": subscription_update.api_key,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase_client.table("webhook_subscriptions").update(update_data).eq("id", subscription_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update webhook subscription"
            )
        
        subscription = result.data[0]
        
        logger.info(f"Webhook subscription {subscription_id} updated by {subscription_update.agent_name}")
        
        return ExternalAPIResponse(
            success=True,
            data=WebhookSubscriptionResponse(
                id=subscription["id"],
                agent_name=subscription["agent_name"],
                webhook_url=subscription["webhook_url"],
                events=subscription["events"],
                is_active=subscription["is_active"],
                failed_attempts=subscription["failed_attempts"],
                last_successful_call=subscription.get("last_successful_call"),
                created_at=subscription["created_at"],
                updated_at=subscription["updated_at"]
            ).dict(),
            message="Webhook subscription updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update webhook subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update webhook subscription: {str(e)}"
        )

@router.delete("/v1/external/webhook-subscriptions/{subscription_id}", response_model=ExternalAPIResponse)
async def delete_webhook_subscription(
    subscription_id: str,
    service_context: dict = Depends(get_external_service_context)
):
    """Delete webhook subscription"""
    try:
        result = supabase_client.table("webhook_subscriptions").delete().eq("id", subscription_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook subscription not found"
            )
        
        deleted_subscription = result.data[0]
        
        logger.info(f"Webhook subscription {subscription_id} deleted for agent {deleted_subscription['agent_name']}")
        
        return ExternalAPIResponse(
            success=True,
            data={
                "deleted_subscription_id": subscription_id,
                "agent_name": deleted_subscription["agent_name"]
            },
            message="Webhook subscription deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete webhook subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete webhook subscription: {str(e)}"
        )

@router.post("/v1/external/webhook-subscriptions/{subscription_id}/toggle", response_model=ExternalAPIResponse)
async def toggle_webhook_subscription(
    subscription_id: str,
    service_context: dict = Depends(get_external_service_context)
):
    """Toggle webhook subscription active status"""
    try:
        # Get current status
        current_result = supabase_client.table("webhook_subscriptions").select("is_active, agent_name").eq("id", subscription_id).execute()
        
        if not current_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook subscription not found"
            )
        
        current_status = current_result.data[0]["is_active"]
        agent_name = current_result.data[0]["agent_name"]
        new_status = not current_status
        
        # Update status
        result = supabase_client.table("webhook_subscriptions").update({
            "is_active": new_status,
            "failed_attempts": 0,  # Reset failed attempts when reactivating
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", subscription_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to toggle webhook subscription"
            )
        
        logger.info(f"Webhook subscription {subscription_id} {'activated' if new_status else 'deactivated'} for agent {agent_name}")
        
        return ExternalAPIResponse(
            success=True,
            data={
                "subscription_id": subscription_id,
                "agent_name": agent_name,
                "previous_status": current_status,
                "new_status": new_status
            },
            message=f"Webhook subscription {'activated' if new_status else 'deactivated'} successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle webhook subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle webhook subscription: {str(e)}"
        )

@router.post("/v1/external/webhook-subscriptions/{subscription_id}/test", response_model=ExternalAPIResponse)
async def test_webhook_subscription(
    subscription_id: str,
    test_request: WebhookTestRequest,
    service_context: dict = Depends(get_external_service_context)
):
    """Test webhook subscription delivery"""
    try:
        result = await webhook_service.test_webhook_subscription(subscription_id)
        
        return ExternalAPIResponse(
            success=True,
            data=result,
            message="Test webhook sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to test webhook subscription {subscription_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test webhook subscription: {str(e)}"
        )

@router.post("/v1/external/webhooks/test", response_model=ExternalAPIResponse)
async def test_webhook_manual(
    event_type: str,
    test_data: Dict[str, Any],
    service_context: dict = Depends(get_external_service_context)
):
    """Test webhook delivery manually"""
    try:
        result = await webhook_service.send_webhook(
            event_type=event_type,
            booking_id="test-booking-123",
            property_id="test-property-456",
            host_id="test-host-789",
            data=test_data
        )
        
        return ExternalAPIResponse(
            success=True,
            data=result,
            message="Test webhook sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to send test webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test webhook: {str(e)}"
        )

@router.get("/v1/external/webhooks/statistics", response_model=ExternalAPIResponse)
async def get_webhook_statistics(
    service_context: dict = Depends(get_external_service_context)
):
    """Get webhook delivery statistics"""
    try:
        statistics = await webhook_service.get_webhook_statistics()
        
        return ExternalAPIResponse(
            success=True,
            data=statistics
        )
        
    except Exception as e:
        logger.error(f"Failed to get webhook statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get webhook statistics: {str(e)}"
        )
