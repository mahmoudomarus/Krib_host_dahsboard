#!/usr/bin/env python3
"""
API Key Generator Script
Generates a secure API key and stores it in Supabase.

Usage: python scripts/generate_api_key.py

The generated key will be displayed ONCE - save it immediately!
"""

import secrets
import hashlib
import requests
from datetime import datetime

# =============================================================================
# SUPABASE CONFIGURATION
# =============================================================================
SUPABASE_URL = "https://bpomacnqaqzgeuahhlka.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWhobGthIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ1NzIyNSwiZXhwIjoyMDcxMDMzMjI1fQ.Esc_wEXe2WnbDiMpsHa3Za9eon6BVjdFYzBXftPBWAc"

# API Configuration
KRIB_API_URL = "https://api.host.krib.ae"

# =============================================================================
# KEY GENERATION
# =============================================================================

def generate_api_key(
    name: str = "Krib AI Agent Platform",
    tier: str = "full_access",
    rate_limit: int = 200,
    environment: str = "prod"
) -> tuple:
    """
    Generate a new API key and store it in Supabase.
    
    Returns:
        tuple: (plain_text_key, key_record)
    """
    # Generate secure random key
    random_part = secrets.token_hex(16)  # 32 character hex string
    full_key = f"krib_{environment}_{random_part}"
    
    # Create prefix for display (first 12 chars)
    key_prefix = full_key[:12]
    
    # Hash the key for storage (SHA-256)
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Define permissions based on tier
    permissions = {
        "read_only": [
            "read_properties",
            "read_property_details",
            "read_availability",
            "calculate_pricing",
            "read_host_profile",
            "read_reviews",
        ],
        "standard": [
            "read_properties",
            "read_property_details",
            "read_availability",
            "calculate_pricing",
            "read_host_profile",
            "read_reviews",
            "send_messages",
            "read_messages",
            "create_conversations",
        ],
        "full_access": [
            "read_properties",
            "read_property_details",
            "read_availability",
            "calculate_pricing",
            "read_host_profile",
            "read_reviews",
            "send_messages",
            "read_messages",
            "create_conversations",
            "create_bookings",
            "read_bookings",
            "update_booking_status",
            "process_payments",
            "receive_webhooks",
        ],
    }
    
    key_permissions = permissions.get(tier, permissions["read_only"])
    
    # Prepare the record for Supabase
    key_record = {
        "key_prefix": key_prefix,
        "key_hash": key_hash,
        "name": name,
        "description": f"API key for {name} - generated {datetime.utcnow().isoformat()}",
        "permissions": key_permissions,
        "tier": tier,
        "rate_limit_per_minute": rate_limit,
        "is_active": True,
        "total_requests": 0,
    }
    
    # Insert into Supabase
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/api_keys",
        headers=headers,
        json=key_record
    )
    
    if response.status_code == 201:
        created_record = response.json()[0]
        return full_key, created_record
    else:
        print(f"Error creating key: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None


def test_api_key(api_key: str) -> bool:
    """Test the API key against the deployed Krib API."""
    print("\n🧪 Testing API key against deployed API...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    all_passed = True
    
    # Test 1: Property search (the main endpoint)
    print("\n1️⃣ Testing property search...")
    try:
        response = requests.get(
            f"{KRIB_API_URL}/api/v1/properties/search?limit=5",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                properties = data.get("data", {}).get("properties", [])
                total = data.get("data", {}).get("total_count", 0)
                print(f"   ✅ Found {total} total properties!")
                for prop in properties[:3]:
                    print(f"      - {prop.get('title', 'N/A')} ({prop.get('bedrooms', '?')} BR, AED {prop.get('base_price_per_night', '?')}/night)")
            else:
                print(f"   ⚠️ Response: {data}")
                all_passed = False
        elif response.status_code == 401:
            print("   ❌ Authentication failed - key may not be valid")
            print(f"   Response: {response.text}")
            all_passed = False
        else:
            print(f"   ❌ Search failed: {response.text}")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_passed = False
    
    # Test 2: Availability check
    print("\n2️⃣ Testing availability check...")
    try:
        # Use a property from the search
        response = requests.get(
            f"{KRIB_API_URL}/api/v1/properties/search?limit=1",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            properties = data.get("data", {}).get("properties", [])
            if properties:
                prop_id = properties[0]["id"]
                avail_response = requests.get(
                    f"{KRIB_API_URL}/api/v1/properties/{prop_id}/availability?check_in=2025-01-12&check_out=2025-01-22&guests=2",
                    headers=headers
                )
                if avail_response.status_code == 200:
                    avail_data = avail_response.json()
                    is_available = avail_data.get("data", {}).get("is_available", False)
                    print(f"   ✅ Availability check works! Property available: {is_available}")
                else:
                    print(f"   ❌ Availability check failed: {avail_response.text}")
                    all_passed = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_passed = False
    
    # Test 3: Pricing calculation
    print("\n3️⃣ Testing pricing calculation...")
    try:
        if properties:
            prop_id = properties[0]["id"]
            pricing_response = requests.post(
                f"{KRIB_API_URL}/api/v1/properties/{prop_id}/calculate-pricing",
                headers=headers,
                json={"check_in": "2025-01-12", "check_out": "2025-01-22", "guests": 2}
            )
            if pricing_response.status_code == 200:
                pricing_data = pricing_response.json()
                total = pricing_data.get("data", {}).get("total_price", 0)
                nights = pricing_data.get("data", {}).get("nights", 0)
                print(f"   ✅ Pricing works! {nights} nights = AED {total}")
            else:
                print(f"   ❌ Pricing failed: {pricing_response.text}")
                all_passed = False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        all_passed = False
    
    if all_passed:
        print("\n✅ All API tests passed!")
    else:
        print("\n⚠️ Some tests failed - check the errors above")
    
    return all_passed


def main():
    print("=" * 60)
    print("🔑 KRIB API KEY GENERATOR")
    print("=" * 60)
    
    print("\n📝 Generating new API key...")
    print(f"   Supabase: {SUPABASE_URL}")
    print(f"   API: {KRIB_API_URL}")
    
    # Generate the key
    api_key, record = generate_api_key(
        name="Krib AI Agent Platform",
        tier="full_access",
        rate_limit=200,
        environment="prod"
    )
    
    if api_key and record:
        print("\n" + "=" * 60)
        print("✅ API KEY GENERATED SUCCESSFULLY!")
        print("=" * 60)
        print("\n⚠️  SAVE THIS KEY NOW - IT WILL NOT BE SHOWN AGAIN!")
        print("\n" + "-" * 60)
        print(f"🔑 API KEY: {api_key}")
        print("-" * 60)
        print(f"\n📋 Key Details:")
        print(f"   ID: {record.get('id')}")
        print(f"   Prefix: {record.get('key_prefix')}")
        print(f"   Name: {record.get('name')}")
        print(f"   Tier: {record.get('tier')}")
        print(f"   Rate Limit: {record.get('rate_limit_per_minute')} req/min")
        print(f"   Permissions: {len(record.get('permissions', []))} permissions")
        print(f"   Created: {record.get('created_at')}")
        
        # Test the key
        test_api_key(api_key)
        
        # Output for easy copy
        print("\n" + "=" * 60)
        print("📋 COPY THIS FOR YOUR AI AGENT PLATFORM:")
        print("=" * 60)
        print(f"""
# Krib API Configuration
KRIB_API_KEY={api_key}
KRIB_API_URL=https://api.host.krib.ae

# Example usage:
curl -X GET "https://api.host.krib.ae/api/v1/properties/search?bedrooms=2" \\
  -H "Authorization: Bearer {api_key}"

# Search for 2-bedroom apartments in Dubai:
curl -X GET "https://api.host.krib.ae/api/v1/properties/search?bedrooms=2&city=Dubai" \\
  -H "Authorization: Bearer {api_key}"

# Check availability:
curl -X GET "https://api.host.krib.ae/api/v1/properties/PROPERTY_ID/availability?check_in=2025-01-12&check_out=2025-01-22&guests=2" \\
  -H "Authorization: Bearer {api_key}"

# Calculate pricing:
curl -X POST "https://api.host.krib.ae/api/v1/properties/PROPERTY_ID/calculate-pricing" \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{"check_in": "2025-01-12", "check_out": "2025-01-22", "guests": 2}}'
""")
        
    else:
        print("\n❌ Failed to generate API key")
        print("   Check that the api_keys table exists in Supabase")


if __name__ == "__main__":
    main()

