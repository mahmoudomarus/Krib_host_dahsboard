#!/usr/bin/env python3
"""
Create Properties for Existing Users
Since users are already created, this logs in as each user and creates properties
"""

import requests
import json
import random
import time

# Configuration
RENDER_API_BASE = "https://krib-host-dahsboard-backend.onrender.com"

# Test user data (same as before)
TEST_USERS = [
    {"name": "Ahmed Al-Mansouri", "email": "ahmed.mansouri@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Sarah Johnson", "email": "sarah.johnson@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Mohammed Al-Rashid", "email": "mohammed.rashid@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Emily Chen", "email": "emily.chen@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Omar Al-Zahra", "email": "omar.zahra@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Jessica Smith", "email": "jessica.smith@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Khalid Al-Dhaheri", "email": "khalid.dhaheri@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Anna Petrov", "email": "anna.petrov@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Hassan Al-Maktoum", "email": "hassan.maktoum@dubaiproperties.ae", "password": "TestPass123!"},
    {"name": "Maria Rodriguez", "email": "maria.rodriguez@dubaiproperties.ae", "password": "TestPass123!"}
]

# Dubai property data
DUBAI_AREAS = [
    "Downtown Dubai", "Dubai Marina", "Jumeirah Beach Residence (JBR)", 
    "Business Bay", "DIFC", "Palm Jumeirah", "Dubai Hills Estate",
    "City Walk", "Al Barsha", "The Greens", "Arabian Ranches",
    "Jumeirah", "Deira", "Bur Dubai", "Dubai Investment Park"
]

PROPERTY_TYPES = ["studio", "apartment", "penthouse", "villa", "townhouse"]

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
        "penthouse": random.randint(1000, 3000),
        "villa": random.randint(1500, 5000),
        "townhouse": random.randint(800, 2000)
    }
    
    price = base_prices[property_type]
    bedroom_text = f"{bedrooms}BR" if bedrooms > 0 else "Studio"
    
    # Random amenities (3-8 amenities per property)
    selected_amenities = random.sample(DUBAI_AMENITIES, random.randint(3, 8))
    
    property_data = {
        "title": f"Luxury {bedroom_text} {property_type.title()} in {area}",
        "description": f"Beautiful {property_type} in the heart of {area}. Managed by {user_data['name']}. Perfect for business travelers and tourists. Modern amenities and prime location with easy access to Dubai's main attractions.",
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": float(bathrooms),
        "max_guests": max_guests,
        "price_per_night": float(price),
        "city": area,
        "state": "Dubai",
        "country": "UAE", 
        "address": f"{random.randint(100, 999)} {area} Street, {area}, Dubai, UAE",
        "latitude": 25.2048 + random.uniform(-0.15, 0.15),
        "longitude": 55.2708 + random.uniform(-0.15, 0.15),
        "amenities": selected_amenities
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

def main():
    print("🏠 Creating Properties for Existing Users")
    print("=" * 50)
    print("👥 Target: 10 existing authenticated users")
    print("🏠 Creating: 10 properties per user (100 total)")
    print("=" * 50)
    
    all_properties = []
    
    # Create properties for each user
    for user_index, user in enumerate(TEST_USERS):
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
    print(f"\n🧪 Testing created data...")
    API_KEY = "krib_ai_test_key_12345"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.get(
            f"{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=20",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            total_count = data.get("data", {}).get("total_count", 0)
            properties = data.get("data", {}).get("properties", [])
            
            print(f"✅ Total properties found: {total_count}")
            
            if properties:
                print("📋 Sample properties:")
                for i, prop in enumerate(properties[:5]):
                    print(f"   {i+1}. {prop.get('title', 'Unknown')} - AED {prop.get('price_per_night', 0)}/night in {prop.get('city', 'Unknown')}")
        else:
            print(f"❌ Property search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    # Summary
    print(f"\n🎉 PROPERTY CREATION COMPLETE!")
    print(f"=" * 40)
    print(f"🏠 Total Properties Created: {len(all_properties)}/100")
    print(f"👥 Users with Properties: {len(TEST_USERS)}")
    print(f"🌐 API Ready: {RENDER_API_BASE}")
    
    print(f"\n✅ Your Krib AI Agent can now test with REAL data!")
    print(f'   curl -H "Authorization: Bearer {API_KEY}" \\')
    print(f'        "{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=10"')

if __name__ == "__main__":
    main()
