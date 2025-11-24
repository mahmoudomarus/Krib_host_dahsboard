"""
Test script for messaging system and notifications
Run: python test_messaging.py
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app.core.supabase_client import supabase_client
from app.services.messaging_service import (
    get_conversations,
    get_messages,
    send_message,
    generate_ai_response
)
from app.services.email_service import send_email

async def create_test_conversation(host_id: str, property_id: str):
    """Create a test conversation"""
    print("\n1. Creating test conversation...")
    
    conversation_data = {
        "host_id": host_id,
        "property_id": property_id,
        "guest_name": "Test Guest",
        "guest_email": "test.guest@example.com",
        "status": "active",
        "last_message": "Hi, I have a question about check-in",
        "last_message_at": datetime.utcnow().isoformat(),
        "unread_count_host": 1,
        "unread_count_guest": 0
    }
    
    result = supabase_client.table("conversations").insert(conversation_data).execute()
    
    if result.data:
        conversation = result.data[0]
        print(f"✓ Created conversation: {conversation['id']}")
        return conversation['id']
    else:
        print(f"✗ Failed to create conversation")
        return None

async def create_test_message(conversation_id: str, content: str, is_from_host: bool = False):
    """Create a test message"""
    print(f"\n2. Creating test message...")
    
    message_data = {
        "conversation_id": conversation_id,
        "content": content,
        "is_from_host": is_from_host,
        "read": False
    }
    
    result = supabase_client.table("messages").insert(message_data).execute()
    
    if result.data:
        message = result.data[0]
        print(f"✓ Created message: {message['id']}")
        return message['id']
    else:
        print(f"✗ Failed to create message")
        return None

async def test_ai_response(conversation_id: str, guest_message: str):
    """Test AI response generation"""
    print(f"\n3. Testing AI response generation...")
    
    try:
        response = await generate_ai_response(conversation_id, guest_message)
        print(f"✓ AI Response generated:")
        print(f"  {response}")
        return response
    except Exception as e:
        print(f"✗ AI response failed: {e}")
        return None

async def test_email_notification(host_email: str, guest_name: str, message: str):
    """Test email notification"""
    print(f"\n4. Testing email notification...")
    
    try:
        html_content = f"""
        <h2>New Message from {guest_name}</h2>
        <p>You have a new message:</p>
        <blockquote style="border-left: 3px solid #84CC16; padding-left: 15px; margin: 20px 0;">
            {message}
        </blockquote>
        <p>
            <a href="https://host.krib.ae/dashboard/messages" 
               style="background-color: #84CC16; color: black; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                View and Reply
            </a>
        </p>
        """
        
        await send_email(
            to_email=host_email,
            subject=f"New message from {guest_name}",
            html_content=html_content
        )
        print(f"✓ Email notification sent to {host_email}")
        return True
    except Exception as e:
        print(f"✗ Email notification failed: {e}")
        return False

async def list_conversations(host_id: str):
    """List all conversations for host"""
    print(f"\n5. Listing conversations...")
    
    try:
        conversations = await get_conversations(host_id)
        print(f"✓ Found {len(conversations)} conversations:")
        for conv in conversations:
            print(f"  - {conv['guest_name']}: {conv['last_message']}")
        return conversations
    except Exception as e:
        print(f"✗ Failed to list conversations: {e}")
        return []

async def list_messages(conversation_id: str):
    """List all messages in conversation"""
    print(f"\n6. Listing messages...")
    
    try:
        messages = await get_messages(conversation_id)
        print(f"✓ Found {len(messages)} messages:")
        for msg in messages:
            sender = "Host" if msg['is_from_host'] else "Guest"
            print(f"  [{sender}]: {msg['content'][:50]}...")
        return messages
    except Exception as e:
        print(f"✗ Failed to list messages: {e}")
        return []

async def main():
    print("=" * 60)
    print("Krib Host Platform - Messaging & Notification Test")
    print("=" * 60)
    
    # Get host info
    host_email = input("\nEnter your host email: ").strip()
    
    # Get host from database
    result = supabase_client.table("users").select("id, name").eq("email", host_email).execute()
    
    if not result.data:
        print(f"✗ Host not found with email: {host_email}")
        return
    
    host = result.data[0]
    host_id = host['id']
    host_name = host['name']
    
    print(f"✓ Found host: {host_name} ({host_id})")
    
    # Get host's properties
    props_result = supabase_client.table("properties").select("id, title").eq("user_id", host_id).execute()
    
    if not props_result.data:
        print(f"✗ No properties found for this host")
        return
    
    print(f"\n✓ Found {len(props_result.data)} properties:")
    for i, prop in enumerate(props_result.data):
        print(f"  {i+1}. {prop['title']}")
    
    property_id = props_result.data[0]['id']
    property_title = props_result.data[0]['title']
    
    print(f"\nUsing property: {property_title}")
    
    # Create test conversation
    conversation_id = await create_test_conversation(host_id, property_id)
    
    if not conversation_id:
        return
    
    # Create initial guest message
    guest_message = "Hi, what time is check-in? Also, is parking available?"
    await create_test_message(conversation_id, guest_message, is_from_host=False)
    
    # Test AI response
    ai_response = await test_ai_response(conversation_id, guest_message)
    
    if ai_response:
        # Create AI response as message
        await create_test_message(conversation_id, ai_response, is_from_host=True)
    
    # Test email notification
    await test_email_notification(host_email, "Test Guest", guest_message)
    
    # List conversations
    await list_conversations(host_id)
    
    # List messages
    await list_messages(conversation_id)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Go to https://host.krib.ae/dashboard/messages")
    print("2. You should see the test conversation")
    print("3. Check your email for notification")
    print("4. Try replying to the message")
    print("5. Test the AI response button")
    print("\nConversation ID:", conversation_id)

if __name__ == "__main__":
    asyncio.run(main())

