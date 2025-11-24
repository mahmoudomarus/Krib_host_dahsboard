"""
Messaging API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from app.services.messaging_service import messaging_service
from app.core.supabase_client import supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConversationCreate(BaseModel):
    property_id: str
    guest_name: str
    guest_email: str
    booking_id: Optional[str] = None


class MessageCreate(BaseModel):
    content: str


class AIResponseRequest(BaseModel):
    message: str


@router.post("/conversations")
async def create_conversation(
    conversation: ConversationCreate, current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    try:
        property_result = (
            supabase_client.table("properties")
            .select("id,user_id")
            .eq("id", conversation.property_id)
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if not property_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
            )

        result = await messaging_service.create_conversation(
            property_id=conversation.property_id,
            host_id=current_user["id"],
            guest_name=conversation.guest_name,
            guest_email=conversation.guest_email,
            booking_id=conversation.booking_id,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}",
        )


@router.get("/conversations")
async def get_conversations(
    status_filter: Optional[str] = None, current_user: dict = Depends(get_current_user)
):
    """Get all conversations for the current host"""
    try:
        conversations = await messaging_service.get_host_conversations(
            host_id=current_user["id"], status=status_filter
        )
        return conversations

    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}",
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str, current_user: dict = Depends(get_current_user)
):
    """Get conversation details"""
    try:
        conversation = await messaging_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        if conversation["host_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation: {str(e)}",
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """Get messages for a conversation"""
    try:
        conversation = await messaging_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        if conversation["host_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        messages = await messaging_service.get_messages(conversation_id, limit)

        await messaging_service.mark_as_read(conversation_id, "host")

        return messages

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}",
        )


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: dict = Depends(get_current_user),
):
    """Send a message in a conversation"""
    try:
        conversation = await messaging_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        if conversation["host_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        result = await messaging_service.send_message(
            conversation_id=conversation_id,
            sender_id=current_user["id"],
            sender_type="host",
            content=message.content,
            is_ai_generated=False,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )


@router.post("/conversations/{conversation_id}/ai-response")
async def generate_ai_response(
    conversation_id: str,
    request: AIResponseRequest,
    current_user: dict = Depends(get_current_user),
):
    """Generate AI response to guest message"""
    try:
        conversation = await messaging_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        if conversation["host_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        property_result = (
            supabase_client.table("properties")
            .select("*")
            .eq("id", conversation["property_id"])
            .single()
            .execute()
        )

        if not property_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
            )

        ai_response = await messaging_service.generate_ai_response(
            conversation_id=conversation_id,
            guest_message=request.message,
            property_data=property_result.data,
        )

        if not ai_response:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service unavailable",
            )

        return {"ai_response": ai_response, "is_ai_generated": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI response: {str(e)}",
        )


@router.post("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str, current_user: dict = Depends(get_current_user)
):
    """Archive a conversation"""
    try:
        conversation = await messaging_service.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        if conversation["host_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation",
            )

        await messaging_service.archive_conversation(conversation_id)

        return {"status": "archived", "conversation_id": conversation_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to archive conversation: {str(e)}",
        )
