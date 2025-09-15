#!/usr/bin/env python3
"""
Simple Test Data Creation via Render API
Uses the live Render deployment to create test properties through the API
No local dependencies required - just uses your deployed backend
"""

import requests
import json
import random
import time

# Live Render API Configuration
RENDER_API_BASE = "https://krib-host-dahsboard-backend.onrender.com/api/v1"
API_KEY = "krib_ai_test_key_12345"

# API Headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-API-Version": "1.0",
    "User-Agent": "KribAI-TestData-Creator/1.0"
}

# Dubai test data
DUBAI_AREAS = [
    "Dubai Marina", "Downtown Dubai", "Jumeirah Beach Residence (JBR)", 
    "Business Bay", "DIFC", "Palm Jumeirah", "Dubai Hills Estate",
    "City Walk", "Al Barsha", "The Greens"
]

PROPERTY_TYPES = ["studio", "apartment", "penthouse", "villa", "townhouse"]

def create_test_user():
    """Create a test user via the API"""
    user_data = {
        "name": "Dubai Test Host",
        "email": f"testhost{random.randint(1000, 9999)}@dubaiproperties.ae",
        "password": "TestPassword123!"
    }
    
    try:
        # Try to sign up user
        response = requests.post(
            f"{RENDER_API_BASE}/../auth/signup",  # Auth endpoint
            headers={"Content-Type": "application/json"},
            json=user_data
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Test user created: {user_data['email']}")
            return response.json().get("access_token")
        else:
            print(f"❌ User creation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None

def create_test_property_via_api(auth_token, property_number):
    """Create a single test property via the API"""
    
    # Random property data
    area = random.choice(DUBAI_AREAS)
    property_type = random.choice(PROPERTY_TYPES)
    bedrooms = random.randint(0, 4) if property_type != "studio" else 0
    bathrooms = max(1, bedrooms)
    max_guests = bedrooms * 2 if bedrooms > 0 else 2
    
    # Realistic Dubai pricing
    base_prices = {
        "studio": random.randint(300, 600),
        "apartment": random.randint(400, 1200),
        "penthouse": random.randint(1000, 3000),
        "villa": random.randint(1500, 5000),
        "townhouse": random.randint(800, 2000)
    }
    
    price = base_prices[property_type]
    
    # Generate property
    bedroom_text = f"{bedrooms}BR" if bedrooms > 0 else "Studio"
    
    property_data = {
        "title": f"Test {bedroom_text} {property_type.title()} in {area}",
        "description": f"Beautiful {property_type} located in {area}. Perfect for testing the Krib AI platform. Features modern amenities and great location.",
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "max_guests": max_guests,
        "price_per_night": price,
        "city": area,
        "state": "Dubai", 
        "country": "UAE",
        "address": f"Test Address {property_number}, {area}, Dubai, UAE",
        "latitude": 25.2048 + random.uniform(-0.1, 0.1),
        "longitude": 55.2708 + random.uniform(-0.1, 0.1),
        "amenities": ["WiFi", "Pool", "Gym", "Parking", "24/7 Security", "Central Air Conditioning"]
    }
    
    try:
        # Use authenticated user token
        auth_headers = HEADERS.copy()
        auth_headers["Authorization"] = f"Bearer {auth_token}"
        
        response = requests.post(
            f"{RENDER_API_BASE}/properties",
            headers=auth_headers,
            json=property_data
        )
        
        if response.status_code in [200, 201]:
            prop_id = response.json().get("data", {}).get("id")
            print(f"  ✅ Property {property_number}: {property_data['title']}")
            return prop_id
        else:
            print(f"  ❌ Property {property_number} failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Property {property_number} error: {e}")
        return None

def test_property_search():
    """Test the property search with created data"""
    print("\n🧪 Testing property search...")
    
    test_searches = [
        {"state": "Dubai", "limit": 10, "desc": "All Dubai properties"},
        {"state": "Dubai", "city": "Dubai Marina", "limit": 5, "desc": "Dubai Marina only"},
        {"state": "Dubai", "property_type": "apartment", "limit": 5, "desc": "Apartments only"},
        {"state": "Dubai", "bedrooms": 2, "limit": 5, "desc": "2+ bedrooms"},
        {"state": "Dubai", "max_price_per_night": 1000, "limit": 5, "desc": "Under AED 1000"}
    ]
    
    for search in test_searches:
        try:
            response = requests.get(
                f"{RENDER_API_BASE}/properties/search",
                headers=HEADERS,
                params={k: v for k, v in search.items() if k != "desc"}
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get("data", {}).get("total_count", 0)
                print(f"  ✅ {search['desc']}: {count} properties found")
                
                # Test first property details
                if count > 0:
                    properties = data.get("data", {}).get("properties", [])
                    if properties:
                        prop_id = properties[0]["id"]
                        detail_response = requests.get(
                            f"{RENDER_API_BASE}/properties/{prop_id}",
                            headers=HEADERS
                        )
                        if detail_response.status_code == 200:
                            prop = detail_response.json().get("data", {})
                            print(f"    📋 Sample: {prop.get('title', 'Unknown')} - AED {prop.get('price_per_night', 0)}/night")
            else:
                print(f"  ❌ {search['desc']}: Search failed")
                
        except Exception as e:
            print(f"  ❌ {search['desc']}: Error {e}")

def main():
    print("🏠 Dubai Test Data Creator (via Render API)")
    print("=" * 50)
    print("🎯 Target: Live Render deployment")
    print("📊 Creating: Test properties via API")
    print("🔑 Using: Test API key")
    print("=" * 50)
    
    # Step 1: Test API connectivity
    print("\n1️⃣ Testing API connectivity...")
    try:
        health_response = requests.get(f"{RENDER_API_BASE}/../health")
        if health_response.status_code == 200:
            print("✅ Render API is healthy and responding")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Render API: {e}")
        return
    
    # Step 2: Test search (might be empty)
    print("\n2️⃣ Testing current property search...")
    try:
        response = requests.get(
            f"{RENDER_API_BASE}/properties/search?state=Dubai&limit=5",
            headers=HEADERS
        )
        if response.status_code == 200:
            current_count = response.json().get("data", {}).get("total_count", 0)
            print(f"✅ Current properties in database: {current_count}")
        else:
            print(f"❌ Search test failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Search test error: {e}")
        return
    
    # Step 3: Create test user (for authenticated property creation)
    print("\n3️⃣ Creating test user...")
    auth_token = create_test_user()
    
    if not auth_token:
        print("❌ Cannot create user - trying with external API key instead")
        print("📝 You can manually add properties via your admin dashboard")
        print("🔗 Or check if user registration is working")
        
        # Still test search functionality
        test_property_search()
        return
    
    # Step 4: Create test properties
    print(f"\n4️⃣ Creating 10 test properties...")
    created_properties = []
    
    for i in range(10):
        prop_id = create_test_property_via_api(auth_token, i+1)
        if prop_id:
            created_properties.append(prop_id)
        time.sleep(0.2)  # Rate limiting
    
    print(f"\n✅ Created {len(created_properties)} test properties")
    
    # Step 5: Test search with new data
    test_property_search()
    
    # Step 6: Integration summary
    print(f"\n📋 INTEGRATION READY!")
    print(f"=" * 50)
    print(f"🔑 API Key: {API_KEY}")
    print(f"🌐 Base URL: {RENDER_API_BASE}")
    print(f"📊 Test Properties: {len(created_properties)} created")
    print(f"🏙️ Areas: {', '.join(DUBAI_AREAS[:3])}, etc.")
    print(f"🏠 Types: Studios, Apartments, Penthouses, Villas")
    
    print(f"\n🧪 YOUR AI AGENT CAN NOW TEST:")
    print(f'   curl -H "Authorization: Bearer {API_KEY}" \\')
    print(f'        "{RENDER_API_BASE}/properties/search?state=Dubai&limit=5"')
    
    print(f"\n✅ API Integration Ready for Krib AI Agent!")

if __name__ == "__main__":
    main()
