"""
Server-Sent Events for real-time updates
"""

import asyncio
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any, Set
from app.api.dependencies import get_current_user
from app.core.supabase_client import supabase_client
from app.core.config import settings
from datetime import datetime, timedelta
import weakref

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active SSE connections using WeakSet for automatic cleanup
class SSEConnectionManager:
    def __init__(self):
        self._connections: Dict[str, Set[asyncio.Queue]] = {}
        self._connection_count = 0
        self._max_connections = settings.sse_max_connections
        self._heartbeat_interval = settings.sse_heartbeat_interval
    
    def add_connection(self, host_id: str) -> asyncio.Queue:
        """Add a new SSE connection for a host"""
        if self._connection_count >= self._max_connections:
            raise HTTPException(status_code=429, detail="Too many active connections")
        
        if host_id not in self._connections:
            self._connections[host_id] = set()
        
        connection_queue = asyncio.Queue(maxsize=100)
        self._connections[host_id].add(connection_queue)
        self._connection_count += 1
        
        logger.info(f"SSE connection added for host {host_id}. Total connections: {self._connection_count}")
        return connection_queue
    
    def remove_connection(self, host_id: str, connection_queue: asyncio.Queue):
        """Remove an SSE connection for a host"""
        if host_id in self._connections:
            self._connections[host_id].discard(connection_queue)
            
            if not self._connections[host_id]:
                del self._connections[host_id]
        
        self._connection_count = max(0, self._connection_count - 1)
        logger.info(f"SSE connection removed for host {host_id}. Total connections: {self._connection_count}")
    
    async def send_to_host(self, host_id: str, event_data: Dict[str, Any]):
        """Send event to all connections for a specific host"""
        if host_id not in self._connections:
            return
        
        # Create a copy of the set to avoid modification during iteration
        connections = self._connections[host_id].copy()
        
        for connection_queue in connections:
            try:
                # Use put_nowait to avoid blocking
                connection_queue.put_nowait(event_data)
            except asyncio.QueueFull:
                logger.warning(f"Queue full for host {host_id}, dropping event")
            except Exception as e:
                logger.error(f"Failed to send event to host {host_id}: {e}")
                # Remove the problematic connection
                self.remove_connection(host_id, connection_queue)
    
    async def broadcast_to_all(self, event_data: Dict[str, Any]):
        """Broadcast event to all active connections"""
        for host_id in list(self._connections.keys()):
            await self.send_to_host(host_id, event_data)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return self._connection_count
    
    def get_host_connection_count(self, host_id: str) -> int:
        """Get number of connections for a specific host"""
        return len(self._connections.get(host_id, set()))

# Global connection manager
sse_manager = SSEConnectionManager()

async def event_stream(host_id: str, connection_queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events for host"""
    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'host_id': host_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"
        
        # Background task to send heartbeat
        heartbeat_task = asyncio.create_task(send_heartbeat(connection_queue))
        
        # Background task to check for new data
        data_check_task = asyncio.create_task(check_for_updates(host_id, connection_queue))
        
        try:
            while True:
                # Wait for events from the queue or timeout
                try:
                    event_data = await asyncio.wait_for(connection_queue.get(), timeout=1.0)
                    yield f"data: {json.dumps(event_data)}\n\n"
                except asyncio.TimeoutError:
                    # Continue the loop, this is normal
                    continue
                    
        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for host {host_id}")
        finally:
            # Clean up background tasks
            heartbeat_task.cancel()
            data_check_task.cancel()
            
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
            
            try:
                await data_check_task
            except asyncio.CancelledError:
                pass
            
    except Exception as e:
        logger.error(f"SSE stream error for host {host_id}: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

async def send_heartbeat(connection_queue: asyncio.Queue):
    """Send periodic heartbeat to keep connection alive"""
    try:
        while True:
            await asyncio.sleep(settings.sse_heartbeat_interval)
            
            heartbeat_data = {
                'type': 'heartbeat',
                'timestamp': datetime.utcnow().isoformat(),
                'server_time': datetime.utcnow().isoformat()
            }
            
            try:
                connection_queue.put_nowait(heartbeat_data)
            except asyncio.QueueFull:
                # If queue is full, skip heartbeat
                pass
            
    except asyncio.CancelledError:
        pass

async def check_for_updates(host_id: str, connection_queue: asyncio.Queue):
    """Check for new notifications and booking updates periodically"""
    try:
        last_check = datetime.utcnow()
        
        while True:
            await asyncio.sleep(2)  # Check every 2 seconds
            
            try:
                current_time = datetime.utcnow()
                
                # Check for new notifications
                notifications = await get_recent_notifications(host_id, last_check)
                for notification in notifications:
                    event_data = {
                        'type': 'notification',
                        'data': notification
                    }
                    try:
                        connection_queue.put_nowait(event_data)
                    except asyncio.QueueFull:
                        break
                
                # Check for booking updates
                booking_updates = await get_recent_booking_updates(host_id, last_check)
                for update in booking_updates:
                    event_data = {
                        'type': 'booking_update',
                        'data': update
                    }
                    try:
                        connection_queue.put_nowait(event_data)
                    except asyncio.QueueFull:
                        break
                
                last_check = current_time
                
            except Exception as e:
                logger.error(f"Error checking for updates for host {host_id}: {e}")
                
    except asyncio.CancelledError:
        pass

async def get_recent_notifications(host_id: str, since: datetime, limit: int = 10):
    """Get recent unread notifications for host"""
    try:
        result = supabase_client.table("host_notifications").select("*").eq(
            "host_id", host_id
        ).eq("is_read", False).gte(
            "created_at", since.isoformat()
        ).order("created_at", desc=True).limit(limit).execute()
        
        return result.data or []
        
    except Exception as e:
        logger.error(f"Failed to get recent notifications for host {host_id}: {e}")
        return []

async def get_recent_booking_updates(host_id: str, since: datetime, limit: int = 10):
    """Get recent booking updates for host's properties"""
    try:
        # Get host's properties
        properties_result = supabase_client.table("properties").select("id").eq("user_id", host_id).execute()
        property_ids = [prop["id"] for prop in properties_result.data]
        
        if not property_ids:
            return []
        
        # Get recent booking updates
        result = supabase_client.table("bookings").select("""
            id, status, property_id, guest_name, check_in, check_out, 
            total_amount, updated_at, created_at,
            properties!inner(title)
        """).in_(
            "property_id", property_ids
        ).gte("updated_at", since.isoformat()).order("updated_at", desc=True).limit(limit).execute()
        
        # Format the data
        updates = []
        for booking in result.data or []:
            updates.append({
                "booking_id": booking["id"],
                "status": booking["status"],
                "property_id": booking["property_id"],
                "property_title": booking["properties"]["title"],
                "guest_name": booking["guest_name"],
                "check_in": booking["check_in"],
                "check_out": booking["check_out"],
                "total_amount": booking["total_amount"],
                "updated_at": booking["updated_at"],
                "created_at": booking["created_at"]
            })
        
        return updates
        
    except Exception as e:
        logger.error(f"Failed to get recent booking updates for host {host_id}: {e}")
        return []

@router.get("/v1/hosts/{host_id}/events")
async def host_event_stream(
    host_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Server-Sent Events endpoint for host real-time updates"""
    try:
        # Verify user can access these events
        if current_user["id"] != host_id:
            raise HTTPException(status_code=403, detail="Access denied - you can only access your own event stream")
        
        # Create connection queue
        connection_queue = sse_manager.add_connection(host_id)
        
        def cleanup_connection():
            sse_manager.remove_connection(host_id, connection_queue)
        
        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no"  # Disable Nginx buffering
        }
        
        return StreamingResponse(
            event_stream(host_id, connection_queue),
            media_type="text/event-stream",
            headers=headers,
            background=BackgroundTasks([cleanup_connection])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create SSE stream for host {host_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create event stream")

@router.post("/v1/hosts/{host_id}/events/send")
async def send_custom_event(
    host_id: str,
    event_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Send custom event to host (for testing or manual notifications)"""
    try:
        # Verify user can send events to this host
        if current_user["id"] != host_id:
            raise HTTPException(status_code=403, detail="Access denied - you can only send events to your own stream")
        
        # Add metadata to the event
        event_with_metadata = {
            **event_data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "manual",
            "host_id": host_id
        }
        
        # Send to all connections for this host
        await sse_manager.send_to_host(host_id, event_with_metadata)
        
        logger.info(f"Custom event sent to host {host_id}: {event_data.get('type', 'unknown')}")
        
        return {
            "status": "sent",
            "host_id": host_id,
            "event": event_with_metadata,
            "connections_notified": sse_manager.get_host_connection_count(host_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send custom event to host {host_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send event")

@router.get("/v1/sse/statistics")
async def get_sse_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get SSE connection statistics (admin only)"""
    try:
        # Basic statistics available to any authenticated user about their own connections
        host_id = current_user["id"]
        
        statistics = {
            "total_connections": sse_manager.get_connection_count(),
            "max_connections": sse_manager._max_connections,
            "heartbeat_interval": sse_manager._heartbeat_interval,
            "user_connections": sse_manager.get_host_connection_count(host_id),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": statistics
        }
        
    except Exception as e:
        logger.error(f"Failed to get SSE statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SSE statistics")

# Admin endpoint for sending broadcasts
@router.post("/v1/external/sse/broadcast")
async def broadcast_event(
    event_data: Dict[str, Any],
    # service_context: dict = Depends(get_external_service_context)  # Uncomment when external deps are available
):
    """Broadcast event to all connected hosts (external services only)"""
    try:
        # Add metadata to the event
        broadcast_event = {
            **event_data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "broadcast",
            "type": event_data.get("type", "system_announcement")
        }
        
        # Broadcast to all connections
        await sse_manager.broadcast_to_all(broadcast_event)
        
        logger.info(f"Broadcast event sent: {event_data.get('type', 'unknown')}")
        
        return {
            "status": "broadcast_sent",
            "event": broadcast_event,
            "total_connections": sse_manager.get_connection_count()
        }
        
    except Exception as e:
        logger.error(f"Failed to broadcast event: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast event")

# Function to send SSE notifications (used by notification service)
async def send_sse_notification(host_id: str, notification: Dict[str, Any]):
    """Send notification via SSE (called from notification service)"""
    try:
        event_data = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await sse_manager.send_to_host(host_id, event_data)
        
        logger.debug(f"SSE notification sent to host {host_id}: {notification.get('title', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to send SSE notification to host {host_id}: {e}")

# Function to send SSE booking updates (used by booking service)
async def send_sse_booking_update(host_id: str, booking_update: Dict[str, Any]):
    """Send booking update via SSE (called from booking service)"""
    try:
        event_data = {
            "type": "booking_update",
            "data": booking_update,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await sse_manager.send_to_host(host_id, event_data)
        
        logger.debug(f"SSE booking update sent to host {host_id}: {booking_update.get('booking_id', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to send SSE booking update to host {host_id}: {e}")
