#!/usr/bin/env python3
"""
Test script for webhook and notification implementation
Tests all critical Phase 1 components
"""

import requests
import json
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
BASE_URL = "https://krib-host-dahsboard-backend.onrender.com/api"
# BASE_URL = "http://localhost:8000/api"  # For local testing

# Test API key (safe test key, not a real secret)
API_KEY = "krib_ai_test_key_12345"

# Headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class WebhookNotificationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = {}
        
    def test_webhook_subscription(self) -> bool:
        """Test webhook subscription creation"""
        print("🔗 Testing Webhook Subscription...")
        
        try:
            subscription_data = {
                "agent_name": "Krib AI Agent Test",
                "webhook_url": "https://webhook.site/test-webhook-endpoint",
                "events": ["booking.created", "booking.confirmed", "booking.cancelled"],
                "api_key": "test_api_key_12345"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/external/webhook-subscriptions",
                headers=self.headers,
                json=subscription_data
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                subscription_id = data["data"]["id"]
                print(f"✅ Webhook subscription created: {subscription_id}")
                print(f"Agent: {data['data']['agent_name']}")
                print(f"Events: {data['data']['events']}")
                return subscription_id
            else:
                print(f"❌ Webhook subscription failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Webhook subscription error: {e}")
            return None
    
    def test_webhook_list(self) -> bool:
        """Test webhook subscription listing"""
        print("\n📋 Testing Webhook Listing...")
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/external/webhook-subscriptions",
                headers=self.headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                subscriptions = data["data"]["subscriptions"]
                total_count = data["data"]["total_count"]
                
                print(f"✅ Found {total_count} webhook subscriptions")
                for sub in subscriptions[:3]:  # Show first 3
                    print(f"  - {sub['agent_name']}: {sub['webhook_url']}")
                return True
            else:
                print(f"❌ Webhook listing failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook listing error: {e}")
            return False
    
    def test_host_notification(self, host_id: str = "test-host-123") -> bool:
        """Test host notification creation"""
        print(f"\n🔔 Testing Host Notification to {host_id}...")
        
        try:
            notification_data = {
                "type": "new_booking",
                "title": "Test Booking Request",
                "message": "You have a test booking request for Marina Villa Test Property",
                "booking_id": "test-booking-456",
                "property_id": "test-property-789",
                "priority": "high",
                "action_required": True,
                "action_url": "https://host-dashboard.com/bookings/test-booking-456"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/hosts/{host_id}/notifications",
                headers=self.headers,
                json=notification_data
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                notification_id = data["data"]["notification_id"]
                print(f"✅ Host notification created: {notification_id}")
                print(f"Type: {notification_data['type']}")
                print(f"Priority: {notification_data['priority']}")
                return notification_id
            else:
                print(f"❌ Host notification failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Host notification error: {e}")
            return None
    
    def test_booking_creation(self) -> bool:
        """Test external booking creation (triggers webhooks)"""
        print("\n📝 Testing External Booking Creation...")
        
        try:
            # First, search for an available property
            search_response = requests.get(
                f"{self.base_url}/v1/properties/search?city=Dubai&limit=1",
                headers=self.headers
            )
            
            if search_response.status_code != 200:
                print(f"❌ Property search failed: {search_response.text}")
                return False
            
            properties = search_response.json()["data"]["properties"]
            if not properties:
                print("❌ No properties found for booking test")
                return False
            
            property_id = properties[0]["id"]
            property_title = properties[0]["title"]
            
            # Create test booking
            booking_data = {
                "property_id": property_id,
                "guest_info": {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test.user@example.com",
                    "phone": "501234567",
                    "country_code": "+971"
                },
                "check_in": (datetime.now() + timedelta(days=7)).date().isoformat(),
                "check_out": (datetime.now() + timedelta(days=9)).date().isoformat(),
                "guests": 2,
                "total_amount": 950.0,
                "payment_method": "pending",
                "special_requests": "This is a test booking from webhook implementation test"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/bookings",
                headers=self.headers,
                json=booking_data
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                booking_id = data["data"]["booking_id"]
                print(f"✅ External booking created: {booking_id}")
                print(f"Property: {property_title}")
                print(f"Guest: {booking_data['guest_info']['first_name']} {booking_data['guest_info']['last_name']}")
                print(f"Amount: AED {booking_data['total_amount']}")
                return booking_id
            else:
                print(f"❌ External booking failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ External booking error: {e}")
            return None
    
    def test_booking_status_update(self, booking_id: str) -> bool:
        """Test booking status update (triggers webhooks)"""
        print(f"\n🔄 Testing Booking Status Update for {booking_id}...")
        
        try:
            status_update = {"status": "confirmed"}
            
            response = requests.put(
                f"{self.base_url}/v1/external/bookings/{booking_id}/status",
                headers=self.headers,
                json=status_update
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Booking status updated")
                print(f"Old status: {data['data']['old_status']}")
                print(f"New status: {data['data']['new_status']}")
                print(f"Host ID: {data['data']['host_id']}")
                return True
            else:
                print(f"❌ Booking status update failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Booking status update error: {e}")
            return False
    
    def test_webhook_statistics(self) -> bool:
        """Test webhook statistics endpoint"""
        print("\n📊 Testing Webhook Statistics...")
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/external/webhooks/statistics",
                headers=self.headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()["data"]
                print(f"✅ Webhook statistics retrieved")
                print(f"Total subscriptions: {data['total_subscriptions']}")
                print(f"Active subscriptions: {data['active_subscriptions']}")
                print(f"Success rate: {data['success_rate']}%")
                return True
            else:
                print(f"❌ Webhook statistics failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook statistics error: {e}")
            return False
    
    def test_manual_webhook(self) -> bool:
        """Test manual webhook sending"""
        print("\n🧪 Testing Manual Webhook...")
        
        try:
            test_data = {
                "test": True,
                "message": "This is a manual test webhook",
                "timestamp": datetime.utcnow().isoformat(),
                "test_id": "manual-test-123"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/external/webhooks/test?event_type=test.webhook",
                headers=self.headers,
                json=test_data
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()["data"]
                print(f"✅ Manual webhook sent")
                print(f"Event type: test.webhook")
                print(f"Results: {data['successful_deliveries']}/{data['total_subscriptions']} delivered")
                return True
            else:
                print(f"❌ Manual webhook failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Manual webhook error: {e}")
            return False
    
    def test_external_api_health(self) -> bool:
        """Test external API health check"""
        print("\n🏥 Testing External API Health...")
        
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ External API is healthy")
                print(f"Service: {data['data']['service']}")
                print(f"Version: {data['data']['version']}")
                print(f"Endpoints: {len(data['data']['endpoints'])} available")
                return True
            else:
                print(f"❌ Health check failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all webhook and notification tests"""
        print("🚀 Starting Webhook & Notification Implementation Tests\n")
        print("=" * 60)
        
        # Track test results
        results = {}
        
        # Test 1: External API Health
        results['health'] = self.test_external_api_health()
        
        # Test 2: Webhook Subscription
        subscription_id = self.test_webhook_subscription()
        results['webhook_subscription'] = subscription_id is not None
        
        # Test 3: Webhook Listing
        results['webhook_listing'] = self.test_webhook_list()
        
        # Test 4: Host Notification
        notification_id = self.test_host_notification()
        results['host_notification'] = notification_id is not None
        
        # Test 5: Booking Creation (triggers webhooks and notifications)
        booking_id = self.test_booking_creation()
        results['booking_creation'] = booking_id is not None
        
        # Test 6: Booking Status Update (triggers webhooks)
        if booking_id:
            time.sleep(2)  # Brief pause for background jobs
            results['booking_update'] = self.test_booking_status_update(booking_id)
        else:
            results['booking_update'] = False
        
        # Test 7: Webhook Statistics
        results['webhook_statistics'] = self.test_webhook_statistics()
        
        # Test 8: Manual Webhook
        results['manual_webhook'] = self.test_manual_webhook()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.upper().replace('_', ' '):20} {status}")
        
        print("-" * 60)
        print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All webhook and notification tests passed!")
            print("\n✅ Phase 1 implementation is working correctly:")
            print("   • Webhook subscriptions and management")
            print("   • Host dashboard notifications")
            print("   • External booking API with webhook triggers")
            print("   • Booking management and status updates")
            print("   • Background job processing")
        else:
            print("⚠️ Some tests failed. Check the implementation.")
            print(f"\n❌ Failed tests:")
            for test_name, passed in results.items():
                if not passed:
                    print(f"   • {test_name.replace('_', ' ').title()}")
        
        return passed_tests == total_tests

def main():
    """Main test runner"""
    print("🤖 Krib AI Webhook & Notification Implementation Tester")
    print("Testing Phase 1 (CRITICAL) components implementation")
    print(f"Testing against: {BASE_URL}")
    print()
    
    tester = WebhookNotificationTester()
    success = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 IMPLEMENTATION STATUS: ✅ READY FOR PRODUCTION")
        print("\nYour webhook and notification system is fully functional!")
        print("AI agents can now:")
        print("• Register for webhook subscriptions")
        print("• Receive real-time booking notifications") 
        print("• Send notifications to host dashboards")
        print("• Manage bookings via external API")
    else:
        print("🎯 IMPLEMENTATION STATUS: ⚠️ NEEDS ATTENTION")
        print("\nSome components need fixing before production deployment.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
