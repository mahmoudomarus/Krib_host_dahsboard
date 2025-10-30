#!/usr/bin/env python3
"""
Test script for External API endpoints
Tests all external API functionality with sample data
"""

import asyncio
import requests
import json
from datetime import datetime, date, timedelta

from backend.app.services.webhook_service import webhook_service

# Configuration  
BASE_URL = "https://krib-host-dahsboard-backend.onrender.com/api/v1"
# BASE_URL = "http://localhost:8000/api/v1"  # For local testing

# Test API key (safe test key, not a real secret)
API_KEY = "krib_ai_test_key_12345"

# Headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    
    try:
        response = requests.get("https://krib-host-dahsboard-backend.onrender.com/api/health", headers=HEADERS)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['data']['status']}")
            print(f"Service: {data['data']['service']}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_property_search():
    """Test property search endpoint"""
    print("\n🔍 Testing Property Search...")
    
    try:
        # Test basic search
        params = {
            "city": "Dubai",
            "limit": 5,
            "sort_by": "price_asc"
        }
        
        response = requests.get(f"{BASE_URL}/properties/search", 
                              headers=HEADERS, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            properties = data['data']['properties']
            total_count = data['data']['total_count']
            
            print(f"✅ Found {len(properties)} properties (total: {total_count})")
            
            if properties:
                prop = properties[0]
                print(f"Sample property: {prop['title']}")
                print(f"Price: AED {prop['base_price_per_night']}/night")
                print(f"Location: {prop['address']['area']}, {prop['address']['emirate']}")
                return prop['id']  # Return first property ID for other tests
            else:
                print("⚠️ No properties found in search")
                return None
        else:
            print(f"❌ Search failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return None

def test_property_details(property_id):
    """Test property details endpoint"""
    print(f"\n📋 Testing Property Details for {property_id}...")
    
    if not property_id:
        print("⚠️ Skipping property details test - no property ID")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/properties/{property_id}", 
                              headers=HEADERS)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            property_data = data['data']['property']
            
            print(f"✅ Property details retrieved")
            print(f"Title: {property_data['title']}")
            print(f"Host: {property_data['host_info']['name']}")
            print(f"Amenities: {len(property_data['amenities'])} items")
            print(f"Images: {len(property_data['images'])} items")
            return True
        else:
            print(f"❌ Property details failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Property details error: {e}")
        return False

def test_availability_check(property_id):
    """Test availability check endpoint"""
    print(f"\n📅 Testing Availability Check for {property_id}...")
    
    if not property_id:
        print("⚠️ Skipping availability test - no property ID")
        return False
    
    try:
        # Check availability for next week
        start_date = (date.today() + timedelta(days=7)).isoformat()
        end_date = (date.today() + timedelta(days=9)).isoformat()
        
        params = {
            "check_in": start_date,
            "check_out": end_date,
            "guests": 2
        }
        
        response = requests.get(f"{BASE_URL}/properties/{property_id}/availability", 
                              headers=HEADERS, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            availability = data['data']
            
            print(f"✅ Availability check completed")
            print(f"Dates: {availability['check_in']} to {availability['check_out']}")
            print(f"Available: {availability['is_available']}")
            if availability['reasons']:
                print(f"Reasons: {', '.join(availability['reasons'])}")
            return True
        else:
            print(f"❌ Availability check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Availability check error: {e}")
        return False

def test_pricing_calculation(property_id):
    """Test pricing calculation endpoint"""
    print(f"\n💰 Testing Pricing Calculation for {property_id}...")
    
    if not property_id:
        print("⚠️ Skipping pricing test - no property ID")
        return False
    
    try:
        # Calculate pricing for next week
        start_date = (date.today() + timedelta(days=7)).isoformat()
        end_date = (date.today() + timedelta(days=9)).isoformat()
        
        payload = {
            "check_in": start_date,
            "check_out": end_date,
            "guests": 2,
            "promo_code": "KRIB10"
        }    
        # Create a asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
            result = loop.run_until_complete(webhook_service.send_webhook(
                event_type="properties.calculate-pricing",
                property_id=property_id,
                check_in=payload['check_in'],
                check_out=payload['check_out'],
                guests=payload['guests'],
                promo_code=payload['promo_code'],
                data=payload
            ))
        finally:
            loop.close()
        return True
        
    except Exception as e:
        print(f"❌ Pricing calculation error: {e}")
        return False

def test_booking_creation(property_id):
    """Test booking creation endpoint"""
    print(f"\n📝 Testing Booking Creation for {property_id}...")
    
    if not property_id:
        print("⚠️ Skipping booking test - no property ID")
        return False
    
    try:
        # Create booking for next week
        start_date = (date.today() + timedelta(days=7)).isoformat()
        end_date = (date.today() + timedelta(days=9)).isoformat()
        
        payload = {
            "property_id": property_id,
            "check_in": start_date,
            "check_out": end_date,
            "guests": 2,
            "guest_info": {
                "first_name": "Test",
                "last_name": "User",
                "email": "test.user@example.com",
                "phone": "501234567",
                "country_code": "+971"
            },
            "special_requests": "This is a test booking from API integration",
            "total_amount": 950.0,
            "payment_method": "pending",
            "source": "krib_ai_agent"
        }
        
        response = requests.post(f"{BASE_URL}/bookings", 
                               headers=HEADERS, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            booking = data['data']
            
            print(f"✅ Booking created successfully")
            print(f"Booking ID: {booking['booking_id']}")
            print(f"Status: {booking['status']}")
            print(f"Guest: {booking['guest_info']['first_name']} {booking['guest_info']['last_name']}")
            print(f"Total: AED {booking['total_amount']}")
            return booking['booking_id']
        else:
            print(f"❌ Booking creation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Booking creation error: {e}")
        return None

def test_authentication_failure():
    """Test authentication with invalid API key"""
    print("\n🔒 Testing Authentication Failure...")
    
    try:
        invalid_headers = {
            "Authorization": "Bearer invalid_key_12345",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/health", headers=invalid_headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Authentication properly rejected invalid key")
            return True
        else:
            print(f"❌ Authentication should have failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Krib AI External API Tests\n")
    print("=" * 50)
    
    # Track test results
    results = {}
    
    # Run tests
    results['health'] = test_health_check()
    results['auth_failure'] = test_authentication_failure()
    
    property_id = test_property_search()
    results['search'] = property_id is not None
    
    results['details'] = test_property_details(property_id)
    results['availability'] = test_availability_check(property_id)
    results['pricing'] = test_pricing_calculation(property_id)
    
    booking_id = test_booking_creation(property_id)
    results['booking'] = booking_id is not None
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.upper():15} {status}")
    
    print("-" * 50)
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! External API is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the API implementation.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
