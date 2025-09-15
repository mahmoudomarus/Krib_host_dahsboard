#!/usr/bin/env python3
"""
Create Properties for Existing Confirmed Users
Use the users created in the previous run and create properties with correct types
"""

import requests
import json
import random
import time

# Configuration
RENDER_API_BASE = "https://krib-host-dahsboard-backend.onrender.com"
API_KEY = "krib_ai_test_key_12345"

# Existing confirmed users (from previous successful run)
EXISTING_USERS = [
    {"name": "Ahmed Al-Mansouri", "email": "ahmed.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Sarah Johnson", "email": "sarah.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Mohammed Al-Rashid", "email": "mohammed.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Emily Chen", "email": "emily.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Omar Al-Zahra", "email": "omar.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Jessica Smith", "email": "jessica.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Khalid Al-Dhaheri", "email": "khalid.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Anna Petrov", "email": "anna.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Hassan Al-Maktoum", "email": "hassan.host@kribdubai.com", "password": "TestPass123!"},
    {"name": "Maria Rodriguez", "email": "maria.host@kribdubai.com", "password": "TestPass123!"}
]

# Dubai areas - comprehensive list
DUBAI_AREAS = [
    "Downtown Dubai", "Dubai Marina", "Jumeirah Beach Residence (JBR)", 
    "Business Bay", "DIFC", "Palm Jumeirah", "Dubai Hills Estate",
    "City Walk", "Al Barsha", "The Greens", "Arabian Ranches",
    "Jumeirah", "Deira", "Bur Dubai", "Dubai Investment Park"
]

# Property types that work in BOTH Pydantic schema AND database constraint
PROPERTY_TYPES = ["studio", "apartment", "villa"]

# Dubai amenities
DUBAI_AMENITIES = [
    "Central Air Conditioning", "24/7 Security", "Covered Parking", 
    "Shared Pool", "Gym Access", "WiFi", "Metro Station Nearby",
    "Mall Nearby", "Sea View", "Marina View", "Burj Khalifa View",
    "Private Pool", "Maid's Room", "Concierge Service", "Beach Access"
]

def login_user(user_data):
    """Login user and get access token"""
    print(f"Logging in: {user_data['name']} ({user_data['email']})")
    
    try:
        response = requests.post(
            f"{RENDER_API_BASE}/api/auth/signin",
            headers={"Content-Type": "application/json"},
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            access_token = result.get("access_token")
            print(f"  ✅ Login successful!")
            return access_token
        else:
            print(f"  ❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Login error: {e}")
        return None

def create_property_for_user(user_data, access_token, property_number):
    """Create a property for a specific user"""
    
    area = random.choice(DUBAI_AREAS)
    property_type = random.choice(PROPERTY_TYPES)
    bedrooms = random.randint(0, 4) if property_type != "studio" else 0
    bathrooms = max(1, bedrooms) if bedrooms > 0 else 1
    max_guests = bedrooms * 2 if bedrooms > 0 else 2
    
    # Realistic Dubai pricing
    base_prices = {
        "studio": random.randint(300, 600),
        "apartment": random.randint(400, 1200), 
        "villa": random.randint(1500, 5000)
    }
    
    price = base_prices[property_type]
    bedroom_text = f"{bedrooms}BR" if bedrooms > 0 else "Studio"
    
    # Random amenities (3-8 amenities per property)
    selected_amenities = random.sample(DUBAI_AMENITIES, random.randint(3, 8))
    
    property_data = {
        "title": f"Luxury {bedroom_text} {property_type.title()} in {area}",
        "description": f"Beautiful {property_type} in the heart of {area}. Managed by {user_data['name']}. Perfect for business travelers and tourists visiting Dubai. Features modern amenities and prime location with easy access to Dubai's main attractions including Burj Khalifa, Dubai Mall, and pristine beaches.",
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": float(bathrooms),
        "max_guests": max_guests,
        "price_per_night": float(price),
        "cleaning_fee": float(random.randint(100, 300)),
        "city": area,
        "state": "Dubai",
        "country": "UAE", 
        "address": f"{random.randint(100, 999)} {area} Street, {area}, Dubai, UAE",
        "latitude": 25.2048 + random.uniform(-0.15, 0.15),
        "longitude": 55.2708 + random.uniform(-0.15, 0.15),
        "amenities": selected_amenities,
        "house_rules": ["No smoking", "No pets", "No parties", "Check-in after 3 PM", "Check-out before 11 AM"],
        "availability_start": "2025-01-01",
        "availability_end": "2025-12-31",
        "is_active": True,
        "instant_book": random.choice([True, False]),
        "minimum_stay": random.randint(1, 7)
    }
    
    # Create via backend API with user auth
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{RENDER_API_BASE}/api/properties",
            headers=auth_headers,
            json=property_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            prop_id = result.get("data", {}).get("id")
            print(f"    ✅ Property {property_number}: {property_data['title']} - AED {price}/night")
            return prop_id
        else:
            print(f"    ❌ Property {property_number} failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"    ❌ Property {property_number} error: {e}")
        return None

def test_api_integration():
    """Test the created data via the external API"""
    print(f"\n🧪 Testing API integration...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=10",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            total_count = data.get("data", {}).get("total_count", 0)
            properties = data.get("data", {}).get("properties", [])
            
            print(f"✅ Total properties found: {total_count}")
            
            if properties:
                print("📋 Sample properties for AI agent:")
                for i, prop in enumerate(properties[:5]):
                    print(f"   {i+1}. {prop.get('title', 'Unknown')} - AED {prop.get('price_per_night', 0)}/night")
                    print(f"      📍 {prop.get('city', 'Unknown')} | {prop.get('bedrooms', 0)}BR/{prop.get('bathrooms', 0)}BA | {prop.get('max_guests', 0)} guests")
                
                # Test property detail
                prop_id = properties[0]["id"]
                detail_response = requests.get(
                    f"{RENDER_API_BASE}/api/v1/properties/{prop_id}",
                    headers=headers
                )
                if detail_response.status_code == 200:
                    print("✅ Property detail API working")
                else:
                    print("❌ Property detail API failed")
            
            # Test search filters
            print(f"\n🔍 Testing search filters...")
            
            test_searches = [
                {"city": "Dubai Marina", "desc": "Dubai Marina properties"},
                {"property_type": "apartment", "desc": "Apartments only"},
                {"bedrooms": 2, "desc": "2+ bedrooms"},
                {"max_price_per_night": 1000, "desc": "Under AED 1000/night"}
            ]
            
            for search in test_searches:
                try:
                    search_params = {"state": "Dubai", "limit": 3, **{k: v for k, v in search.items() if k != "desc"}}
                    search_response = requests.get(
                        f"{RENDER_API_BASE}/api/v1/properties/search",
                        headers=headers,
                        params=search_params
                    )
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        count = search_data.get("data", {}).get("total_count", 0)
                        print(f"  ✅ {search['desc']}: {count} properties")
                    else:
                        print(f"  ❌ {search['desc']}: Search failed")
                        
                except Exception as e:
                    print(f"  ❌ {search['desc']}: Error {e}")
                    
        else:
            print(f"❌ Property search failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

def main():
    print("🏠 KRIB AI - Create Properties for Existing Users")
    print("=" * 60)
    print("🎯 Goal: Create properties for the 10 confirmed users")
    print("👥 Users: 10 existing authenticated accounts")
    print("🏠 Properties: 10 properties per user (100 total)")
    print("🔑 Method: Correct property types matching DB constraints")
    print("=" * 60)
    
    # Test API connectivity
    print("\n1️⃣ Testing API connectivity...")
    try:
        health_response = requests.get(f"{RENDER_API_BASE}/health")
        if health_response.status_code == 200:
            print("✅ Backend API is healthy")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    all_properties = []
    
    # Create properties for each existing user
    print(f"\n2️⃣ Creating properties for existing users...")
    for user_index, user in enumerate(EXISTING_USERS):
        print(f"\n{user_index+1}. Processing {user['name']}:")
        
        # Login user
        access_token = login_user(user)
        if not access_token:
            print(f"  ❌ Skipping {user['name']} - login failed")
            continue
        
        # Create 10 properties
        print(f"  Creating 10 properties...")
        user_properties = []
        for prop_num in range(10):
            prop_id = create_property_for_user(user, access_token, prop_num + 1)
            if prop_id:
                user_properties.append(prop_id)
            time.sleep(0.3)  # Rate limiting
        
        all_properties.extend(user_properties)
        print(f"  ✅ Created {len(user_properties)}/10 properties for {user['name']}")
    
    # Test the created data
    time.sleep(2)  # Let database sync
    test_api_integration()
    
    # Summary
    print(f"\n🎉 PROPERTY CREATION COMPLETE!")
    print(f"=" * 50)
    print(f"🏠 Total Properties Created: {len(all_properties)}")
    print(f"👥 Users Processed: {len(EXISTING_USERS)}")
    print(f"🌐 API Endpoint: {RENDER_API_BASE}")
    print(f"🔑 API Key: {API_KEY}")
    
    print(f"\n✅ Your Krib AI Agent is ready to test!")
    print(f'   curl -H "Authorization: Bearer {API_KEY}" \\')
    print(f'        "{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=10"')
    
    print(f"\n🗑️ To clean up: Delete users from Supabase Auth dashboard when done testing")

if __name__ == "__main__":
    main()
