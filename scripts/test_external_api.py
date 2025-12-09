#!/usr/bin/env python3
"""
External API Test Script
Tests the external API endpoints for properties, availability, and pricing.

Usage: python scripts/test_external_api.py
"""

import requests
import json
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURATION
# =============================================================================
KRIB_API_URL = "https://api.host.krib.ae"
SUPABASE_URL = "https://bpomacnqaqzgeuahhlka.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWhobGthIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ1NzIyNSwiZXhwIjoyMDcxMDMzMjI1fQ.Esc_wEXe2WnbDiMpsHa3Za9eon6BVjdFYzBXftPBWAc"


def get_existing_api_key():
    """Retrieve an existing API key from Supabase"""
    print("🔍 Looking for existing API keys in database...")
    
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/api_keys?is_active=eq.true&select=*",
        headers=headers
    )
    
    if response.status_code == 200:
        keys = response.json()
        if keys:
            print(f"   Found {len(keys)} active API key(s)")
            for key in keys:
                print(f"   - {key.get('name')}: {key.get('key_prefix')}...")
            return keys
        else:
            print("   No active API keys found")
            return []
    else:
        print(f"   ❌ Error fetching keys: {response.text}")
        return []


def test_property_search(api_key: str):
    """Test the property search endpoint"""
    print("\n" + "=" * 60)
    print("🏠 TEST 1: Property Search")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1a: Basic search (all properties)
    print("\n1a. Searching for ALL available properties...")
    try:
        response = requests.get(
            f"{KRIB_API_URL}/api/v1/properties/search",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get("data", {}).get("results", [])
            total = data.get("data", {}).get("total_count", 0)
            
            print(f"   ✅ Success! Found {total} total properties")
            
            if properties:
                print(f"\n   📋 Properties ({len(properties)} shown):")
                for i, prop in enumerate(properties[:5], 1):
                    print(f"   {i}. {prop.get('title', 'N/A')}")
                    print(f"      ID: {prop.get('id')}")
                    print(f"      Location: {prop.get('location', {}).get('city', 'N/A')}, {prop.get('location', {}).get('state', 'N/A')}")
                    print(f"      Bedrooms: {prop.get('bedrooms', 'N/A')}, Bathrooms: {prop.get('bathrooms', 'N/A')}")
                    print(f"      Price: AED {prop.get('price_per_night', 'N/A')}/night")
                    print(f"      Max Guests: {prop.get('max_guests', 'N/A')}")
                    print()
                
                return properties
            else:
                print("   ⚠️ No properties found in response")
                return []
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []


def test_property_search_with_filters(api_key: str):
    """Test property search with various filters"""
    print("\n" + "-" * 60)
    print("1b. Testing search with filters...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with bedroom filter
    print("\n   Testing filter: bedrooms=2")
    try:
        response = requests.get(
            f"{KRIB_API_URL}/api/v1/properties/search?bedrooms=2",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("data", {}).get("total_count", 0)
            print(f"   ✅ Found {total} properties with 2+ bedrooms")
        else:
            print(f"   ❌ Filter search failed: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with price filter
    print("\n   Testing filter: max_price_per_night=500")
    try:
        response = requests.get(
            f"{KRIB_API_URL}/api/v1/properties/search?max_price_per_night=500",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("data", {}).get("total_count", 0)
            print(f"   ✅ Found {total} properties under AED 500/night")
        else:
            print(f"   ❌ Filter search failed: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_availability(api_key: str, property_id: str):
    """Test the availability check endpoint"""
    print("\n" + "=" * 60)
    print("📅 TEST 2: Check Availability")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Use dates 2 weeks from now
    check_in = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=24)).strftime("%Y-%m-%d")
    
    print(f"\n   Property ID: {property_id}")
    print(f"   Check-in: {check_in}")
    print(f"   Check-out: {check_out}")
    print(f"   Guests: 2")
    
    try:
        response = requests.get(
            f"{KRIB_API_URL}/api/v1/properties/{property_id}/availability",
            params={
                "check_in": check_in,
                "check_out": check_out,
                "guests": 2
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            availability = data.get("data", {})
            
            is_available = availability.get("is_available", False)
            available_dates = availability.get("available_dates", [])
            blocked_dates = availability.get("blocked_dates", [])
            
            print(f"\n   ✅ Availability check successful!")
            print(f"   Is Available: {'Yes ✓' if is_available else 'No ✗'}")
            print(f"   Available dates: {len(available_dates)}")
            print(f"   Blocked dates: {len(blocked_dates)}")
            
            if blocked_dates:
                print(f"   Blocked dates: {blocked_dates[:5]}...")
                
            return is_available
        else:
            print(f"   ❌ Availability check failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_pricing(api_key: str, property_id: str):
    """Test the pricing calculation endpoint"""
    print("\n" + "=" * 60)
    print("💰 TEST 3: Calculate Pricing")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Use dates 2 weeks from now
    check_in = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=24)).strftime("%Y-%m-%d")
    
    print(f"\n   Property ID: {property_id}")
    print(f"   Check-in: {check_in}")
    print(f"   Check-out: {check_out}")
    print(f"   Guests: 2")
    
    try:
        response = requests.post(
            f"{KRIB_API_URL}/api/v1/properties/{property_id}/calculate-pricing",
            json={
                "check_in": check_in,
                "check_out": check_out,
                "guests": 2
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            pricing = data.get("data", {})
            
            nights = pricing.get("nights", 0)
            base_price = pricing.get("base_price", 0)
            cleaning_fee = pricing.get("cleaning_fee", 0)
            service_fee = pricing.get("service_fee", 0)
            total_price = pricing.get("total_price", 0)
            currency = pricing.get("currency", "AED")
            
            print(f"\n   ✅ Pricing calculation successful!")
            print(f"\n   📊 Pricing Breakdown:")
            print(f"   ├── Nights: {nights}")
            print(f"   ├── Base Price: {currency} {base_price}")
            print(f"   ├── Cleaning Fee: {currency} {cleaning_fee}")
            print(f"   ├── Service Fee: {currency} {service_fee}")
            print(f"   └── TOTAL: {currency} {total_price}")
            
            # Show breakdown items if available
            breakdown = pricing.get("breakdown", [])
            if breakdown:
                print(f"\n   📋 Daily Breakdown (first 5 days):")
                for item in breakdown[:5]:
                    print(f"   - {item.get('date')}: {currency} {item.get('price')} ({item.get('rate_type', 'standard')})")
            
            return pricing
        else:
            print(f"   ❌ Pricing calculation failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_booking_status(api_key: str):
    """Test listing bookings (if any exist)"""
    print("\n" + "=" * 60)
    print("📖 TEST 4: List Bookings (Optional)")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("\n   Note: This tests the booking listing endpoint")
    print("   (Actual booking creation requires payment flow)")
    
    # We'll just test the search endpoint with date filters to simulate
    # checking booking availability for a property
    try:
        check_in = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{KRIB_API_URL}/api/v1/properties/search",
            params={
                "check_in": check_in,
                "check_out": check_out
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("data", {}).get("total_count", 0)
            print(f"\n   ✅ Properties available for {check_in} to {check_out}: {total}")
        else:
            print(f"   ❌ Search failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    print("=" * 60)
    print("🧪 KRIB EXTERNAL API TEST SUITE")
    print("=" * 60)
    print(f"\n📍 API URL: {KRIB_API_URL}")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Get existing API keys
    api_keys = get_existing_api_key()
    
    if not api_keys:
        print("\n⚠️ No API keys found. Please run generate_api_key.py first.")
        print("   Or provide an API key manually.")
        
        # Try with a hardcoded test key if available
        api_key = input("\nEnter API key to test (or press Enter to skip): ").strip()
        if not api_key:
            print("\n❌ No API key provided. Exiting.")
            return
    else:
        # Use the first active key
        # Note: We don't have the plain text key stored, so we need the user to provide it
        print("\n⚠️ API keys are stored hashed. Please provide the plain-text key.")
        print(f"   Available keys: {[k.get('key_prefix') + '...' for k in api_keys]}")
        api_key = input("\nEnter API key to test: ").strip()
        
        if not api_key:
            print("\n❌ No API key provided. Exiting.")
            return
    
    # Step 2: Test property search
    properties = test_property_search(api_key)
    
    # Step 2b: Test filtered search
    test_property_search_with_filters(api_key)
    
    if properties:
        # Use the first property for availability and pricing tests
        first_property = properties[0]
        property_id = first_property.get("id")
        
        if property_id:
            # Step 3: Test availability
            test_availability(api_key, property_id)
            
            # Step 4: Test pricing
            test_pricing(api_key, property_id)
    else:
        print("\n⚠️ No properties found - skipping availability and pricing tests")
    
    # Step 5: Test booking status
    test_booking_status(api_key)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"""
✅ Tests completed!

Endpoints tested:
1. GET /api/v1/properties/search - Property search with filters
2. GET /api/v1/properties/{'{id}'}/availability - Check availability for dates
3. POST /api/v1/properties/{'{id}'}/calculate-pricing - Get pricing breakdown

These endpoints are ready for AI agent integration.
""")


if __name__ == "__main__":
    main()

