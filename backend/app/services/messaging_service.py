"""
Messaging service for guest-host communication with AI support
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.supabase_client import supabase_client
import aiohttp

logger = logging.getLogger(__name__)


class MessagingService:
    """Service for managing conversations and messages between hosts and guests"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")

    async def create_conversation(
        self,
        property_id: str,
        host_id: str,
        guest_name: str,
        guest_email: str,
        booking_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new conversation"""
        try:
            result = (
                supabase_client.table("conversations")
                .insert(
                    {
                        "property_id": property_id,
                        "host_id": host_id,
                        "guest_name": guest_name,
                        "guest_email": guest_email,
                        "booking_id": booking_id,
                        "status": "active",
                    }
                )
                .execute()
            )

            if result.data:
                return result.data[0]
            raise Exception("Failed to create conversation")

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation details"""
        try:
            result = (
                supabase_client.table("conversations")
                .select("*")
                .eq("id", conversation_id)
                .single()
                .execute()
            )
            return result.data if result.data else None
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None

    async def get_host_conversations(
        self, host_id: str, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a host"""
        try:
            query = (
                supabase_client.table("conversations")
                .select("*")
                .eq("host_id", host_id)
                .order("last_message_at", desc=True)
            )

            if status:
                query = query.eq("status", status)

            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting host conversations: {e}")
            return []

    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        sender_type: str,
        content: str,
        is_ai_generated: bool = False,
    ) -> Dict[str, Any]:
        """Send a message in a conversation"""
        try:
            result = (
                supabase_client.table("messages")
                .insert(
                    {
                        "conversation_id": conversation_id,
                        "sender_id": sender_id,
                        "sender_type": sender_type,
                        "content": content,
                        "is_ai_generated": is_ai_generated,
                        "is_read": False,
                    }
                )
                .execute()
            )

            if result.data:
                return result.data[0]
            raise Exception("Failed to send message")

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def get_messages(
        self, conversation_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages for a conversation"""
        try:
            result = (
                supabase_client.table("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []

    async def mark_as_read(self, conversation_id: str, user_type: str):
        """Mark messages as read"""
        try:
            supabase_client.rpc(
                "mark_messages_read",
                {"p_conversation_id": conversation_id, "p_user_type": user_type},
            ).execute()
        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")

    async def generate_ai_response(
        self, conversation_id: str, guest_message: str, property_data: Dict[str, Any]
    ) -> Optional[str]:
        """Generate AI response to guest inquiry"""
        if not self.openai_api_key:
            return None

        try:
            recent_messages = await self.get_messages(conversation_id, limit=10)

            conversation_history = "\n".join(
                [
                    f"{'Guest' if m['sender_type'] == 'guest' else 'Host'}: {m['content']}"
                    for m in recent_messages[-5:]
                ]
            )

            system_prompt = f"""You are an AI assistant helping respond to guest inquiries about a property rental.

Property Details:
- Title: {property_data.get('title', 'N/A')}
- Type: {property_data.get('property_type', 'N/A')}
- Location: {property_data.get('city', 'N/A')}, {property_data.get('area', 'N/A')}
- Bedrooms: {property_data.get('bedrooms', 'N/A')}
- Bathrooms: {property_data.get('bathrooms', 'N/A')}
- Price per night: AED {property_data.get('price_per_night', 'N/A')}
- Amenities: {', '.join(property_data.get('amenities', []))}
- Description: {property_data.get('description', 'N/A')}

Respond professionally and helpfully to guest questions. Be concise but informative. If you don't have specific information, suggest the host will provide more details. Never make up information."""

            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.ai_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": guest_message},
                ],
                "max_tokens": 300,
                "temperature": 0.7,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=15,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data["choices"][0]["message"]["content"]
                        return ai_response
                    else:
                        logger.error(f"OpenAI API error: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None

    async def archive_conversation(self, conversation_id: str):
        """Archive a conversation"""
        try:
            supabase_client.table("conversations").update({"status": "archived"}).eq(
                "id", conversation_id
            ).execute()
        except Exception as e:
            logger.error(f"Error archiving conversation: {e}")


messaging_service = MessagingService()
