"""
Test script for notification system
Run: python test_notifications.py
"""
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app.core.supabase_client import supabase_client
from app.services.notification_service import create_notification
from app.services.email_service import send_email

async def create_test_notifications(user_id: str):
    """Create test notifications for all types"""
    print("\nCreating test notifications...\n")
    
    notifications = [
        {
            "type": "new_booking",
            "title": "New Booking Received",
            "message": "You have a new booking for Luxury Marina Apartment",
            "data": {
                "booking_id": "test-booking-123",
                "guest_name": "John Doe",
                "check_in": "2024-12-15",
                "check_out": "2024-12-20"
            }
        },
        {
            "type": "payment_received",
            "title": "Payment Received",
            "message": "Payment of AED 2,500 has been received",
            "data": {
                "amount": 2500,
                "currency": "AED",
                "booking_id": "test-booking-123"
            }
        },
        {
            "type": "new_message",
            "title": "New Message",
            "message": "You have a new message from Jane Smith",
            "data": {
                "conversation_id": "test-conv-123",
                "guest_name": "Jane Smith",
                "message_preview": "What time is check-in?"
            }
        },
        {
            "type": "review_received",
            "title": "New Review",
            "message": "You received a 5-star review from Michael Brown",
            "data": {
                "rating": 5,
                "reviewer": "Michael Brown",
                "property_id": "test-prop-123"
            }
        },
        {
            "type": "payout_processed",
            "title": "Payout Processed",
            "message": "Payout of AED 15,000 has been processed",
            "data": {
                "amount": 15000,
                "currency": "AED",
                "payout_id": "test-payout-123"
            }
        }
    ]
    
    created_count = 0
    
    for notif in notifications:
        try:
            await create_notification(
                user_id=user_id,
                notification_type=notif["type"],
                title=notif["title"],
                message=notif["message"],
                data=notif["data"]
            )
            print(f"✓ Created: {notif['title']}")
            created_count += 1
        except Exception as e:
            print(f"✗ Failed to create {notif['title']}: {e}")
    
    print(f"\n✓ Created {created_count}/{len(notifications)} notifications")
    return created_count

async def test_email_notifications(user_email: str, user_name: str):
    """Test email notifications"""
    print("\nTesting email notifications...\n")
    
    # Test 1: New Booking Email
    print("1. Testing new booking email...")
    try:
        booking_html = f"""
        <h2>New Booking Received! 🎉</h2>
        <p>Hi {user_name},</p>
        <p>Great news! You have a new booking.</p>
        
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>Booking Details</h3>
            <p><strong>Guest:</strong> John Doe</p>
            <p><strong>Property:</strong> Luxury Marina Apartment</p>
            <p><strong>Check-in:</strong> December 15, 2024</p>
            <p><strong>Check-out:</strong> December 20, 2024</p>
            <p><strong>Guests:</strong> 2 adults</p>
            <p><strong>Total Amount:</strong> AED 2,500</p>
        </div>
        
        <p>
            <a href="https://host.krib.ae/dashboard/bookings" 
               style="background-color: #84CC16; color: black; padding: 12px 24px; 
                      text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 600;">
                View Booking Details
            </a>
        </p>
        """
        
        await send_email(
            to_email=user_email,
            subject="🎉 New Booking Received - Luxury Marina Apartment",
            html_content=booking_html
        )
        print("✓ New booking email sent")
    except Exception as e:
        print(f"✗ Booking email failed: {e}")
    
    # Test 2: Payment Received Email
    print("\n2. Testing payment received email...")
    try:
        payment_html = f"""
        <h2>Payment Received 💰</h2>
        <p>Hi {user_name},</p>
        <p>A payment has been successfully processed for your property.</p>
        
        <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #84CC16;">
            <h3>Payment Details</h3>
            <p><strong>Amount:</strong> AED 2,500</p>
            <p><strong>Guest:</strong> John Doe</p>
            <p><strong>Property:</strong> Luxury Marina Apartment</p>
            <p><strong>Platform Fee (15%):</strong> AED 375</p>
            <p><strong>Your Earnings:</strong> AED 2,125</p>
        </div>
        
        <p>The amount will be transferred to your account according to your payout schedule.</p>
        
        <p>
            <a href="https://host.krib.ae/dashboard/financials" 
               style="background-color: #84CC16; color: black; padding: 12px 24px; 
                      text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 600;">
                View Financial Dashboard
            </a>
        </p>
        """
        
        await send_email(
            to_email=user_email,
            subject="💰 Payment Received - AED 2,500",
            html_content=payment_html
        )
        print("✓ Payment email sent")
    except Exception as e:
        print(f"✗ Payment email failed: {e}")
    
    # Test 3: New Message Email
    print("\n3. Testing new message email...")
    try:
        message_html = f"""
        <h2>New Message 💬</h2>
        <p>Hi {user_name},</p>
        <p>You have a new message from a guest.</p>
        
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>From:</strong> Jane Smith</p>
            <p><strong>Property:</strong> Luxury Marina Apartment</p>
            <blockquote style="border-left: 3px solid #84CC16; padding-left: 15px; margin: 15px 0;">
                Hi! I'd like to know if early check-in is available? We're arriving at 11 AM. Thanks!
            </blockquote>
        </div>
        
        <p>
            <a href="https://host.krib.ae/dashboard/messages" 
               style="background-color: #84CC16; color: black; padding: 12px 24px; 
                      text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 600;">
                Reply to Message
            </a>
        </p>
        
        <p style="color: #666; font-size: 14px; margin-top: 30px;">
            💡 Tip: Quick response times improve your host rating!
        </p>
        """
        
        await send_email(
            to_email=user_email,
            subject="💬 New Message from Jane Smith",
            html_content=message_html
        )
        print("✓ Message email sent")
    except Exception as e:
        print(f"✗ Message email failed: {e}")
    
    print("\n✓ All email tests completed")

async def get_notifications(user_id: str):
    """Get all notifications for user"""
    print("\nFetching notifications...\n")
    
    result = supabase_client.table("notifications")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(10)\
        .execute()
    
    if result.data:
        print(f"✓ Found {len(result.data)} notifications:\n")
        for notif in result.data:
            status = "✓ Read" if notif['read'] else "○ Unread"
            print(f"{status} [{notif['type']}] {notif['title']}")
            print(f"   {notif['message']}")
            print(f"   Created: {notif['created_at']}\n")
    else:
        print("✗ No notifications found")

async def main():
    print("=" * 60)
    print("Krib Host Platform - Notification System Test")
    print("=" * 60)
    
    # Get user info
    user_email = input("\nEnter your email: ").strip()
    
    # Get user from database
    result = supabase_client.table("users").select("id, name, email").eq("email", user_email).execute()
    
    if not result.data:
        print(f"✗ User not found with email: {user_email}")
        return
    
    user = result.data[0]
    user_id = user['id']
    user_name = user['name']
    
    print(f"✓ Found user: {user_name} ({user_id})")
    
    # Create test notifications
    await create_test_notifications(user_id)
    
    # Send test emails
    print("\n" + "-" * 60)
    send_emails = input("\nSend test emails? (y/n): ").strip().lower()
    
    if send_emails == 'y':
        await test_email_notifications(user_email, user_name)
    
    # Show notifications
    print("\n" + "-" * 60)
    await get_notifications(user_id)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Go to https://host.krib.ae/dashboard")
    print("2. Check the notification bell icon")
    print("3. Check your email inbox")
    print("4. Click on notifications to mark as read")
    print("5. Navigate to respective sections (Bookings, Messages, Financials)")

if __name__ == "__main__":
    asyncio.run(main())

