#!/usr/bin/env python3
"""
Create Test Users and Properties via Backend API
Uses your working Render backend which has proper Supabase credentials
"""

import requests
import json
import random
import time
import uuid

# Configuration
RENDER_API_BASE = "https://krib-host-dahsboard-backend.onrender.com"
API_KEY = "krib_ai_test_key_12345"

# Headers for API calls
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-API-Version": "1.0",
    "User-Agent": "KribAI-TestData-Creator/1.0"
}

# Test user data
TEST_USERS = [
    {"name": "Ahmed Al-Mansouri", "email": "ahmed.mansouri@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971501234567"},
    {"name": "Sarah Johnson", "email": "sarah.johnson@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971502345678"},
    {"name": "Mohammed Al-Rashid", "email": "mohammed.rashid@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971503456789"},
    {"name": "Emily Chen", "email": "emily.chen@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971504567890"},
    {"name": "Omar Al-Zahra", "email": "omar.zahra@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971505678901"},
    {"name": "Jessica Smith", "email": "jessica.smith@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971506789012"},
    {"name": "Khalid Al-Dhaheri", "email": "khalid.dhaheri@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971507890123"},
    {"name": "Anna Petrov", "email": "anna.petrov@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971508901234"},
    {"name": "Hassan Al-Maktoum", "email": "hassan.maktoum@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971509012345"},
    {"name": "Maria Rodriguez", "email": "maria.rodriguez@dubaiproperties.ae", "password": "TestPass123!", "phone": "+971501122334"}
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

def create_user_via_signup(user_data):
    """Create user via the backend signup endpoint"""
    print(f"Creating user: {user_data['name']} ({user_data['email']})")
    
    signup_payload = {
        "name": user_data["name"],
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        # Try auth signup endpoint
        response = requests.post(
            f"{RENDER_API_BASE}/api/auth/signup",
            headers={"Content-Type": "application/json"},
            json=signup_payload
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            access_token = result.get("access_token")
            user_info = result.get("user", {})
            
            print(f"  ✅ User created successfully!")
            return {
                "access_token": access_token,
                "user_id": user_info.get("id"),
                "email": user_data["email"],
                "name": user_data["name"]
            }
        else:
            print(f"  ❌ Signup failed: {response.status_code} - {response.text}")
            
            # Try alternative: direct user creation via admin API if it exists
            print(f"  🔄 Trying alternative user creation...")
            return create_user_alternative(user_data)
            
    except Exception as e:
        print(f"  ❌ Signup error: {e}")
        return create_user_alternative(user_data)

def create_user_alternative(user_data):
    """Alternative: create user via admin endpoint if available"""
    
    admin_payload = {
        "email": user_data["email"],
        "password": user_data["password"],
        "full_name": user_data["name"],
        "phone": user_data["phone"],
        "role": "host",
        "is_active": True,
        "country": "UAE",
        "city": "Dubai"
    }
    
    try:
        # Try admin users endpoint
        response = requests.post(
            f"{RENDER_API_BASE}/api/v1/admin/users",
            headers=HEADERS,  # Use API key
            json=admin_payload
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"  ✅ User created via admin endpoint!")
            
            # Now login to get access token
            login_response = requests.post(
                f"{RENDER_API_BASE}/api/auth/signin",
                headers={"Content-Type": "application/json"},
                json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                return {
                    "access_token": login_result.get("access_token"),
                    "user_id": result.get("data", {}).get("id"),
                    "email": user_data["email"],
                    "name": user_data["name"]
                }
            
        print(f"  ❌ Admin creation failed: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"  ❌ Admin creation error: {e}")
        return None

def create_property_for_user(user_data, property_number):
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
        "Authorization": f"Bearer {user_data['access_token']}",
        "Content-Type": "application/json",
        "X-API-Version": "1.0"
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

def test_api_endpoints():
    """Test if the required API endpoints exist"""
    print("🔍 Testing API endpoints...")
    
    # Test health
    try:
        response = requests.get(f"{RENDER_API_BASE}/health")
        if response.status_code == 200:
            print("  ✅ Health endpoint working")
        else:
            print(f"  ❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Health endpoint error: {e}")
    
    # Test property search
    try:
        response = requests.get(
            f"{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=1",
            headers=HEADERS
        )
        if response.status_code == 200:
            print("  ✅ Property search endpoint working")
        else:
            print(f"  ❌ Property search failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Property search error: {e}")

def test_created_data():
    """Test the created data via the external API"""
    print("\n🧪 Testing created data via API...")
    
    try:
        response = requests.get(
            f"{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=20",
            headers=HEADERS
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

def main():
    print("🏠 KRIB AI - Real Test Data Creator (via Backend API)")
    print("=" * 60)
    print("🎯 Target: Live Render backend with proper authentication")
    print("👥 Creating: 10 real users via backend signup/admin API")
    print("🏠 Creating: 10 properties per user (100 total)")
    print("🔑 Method: Backend API calls with authentication")
    print("=" * 60)
    
    # Test API first
    test_api_endpoints()
    
    all_users = []
    all_properties = []
    
    # Step 1: Create 10 users
    print(f"\n1️⃣ Creating 10 users via backend API...")
    for i, user_data in enumerate(TEST_USERS):
        print(f"\nUser {i+1}/10:")
        created_user = create_user_via_signup(user_data)
        if created_user:
            all_users.append(created_user)
        time.sleep(1)  # Rate limiting
    
    print(f"\n✅ Successfully created {len(all_users)} users")
    
    if not all_users:
        print("❌ No users created successfully - stopping")
        return
    
    # Step 2: Create 10 properties for each user  
    print(f"\n2️⃣ Creating 10 properties for each user...")
    for user_index, user in enumerate(all_users):
        print(f"\nCreating properties for {user['name']} ({user_index+1}/{len(all_users)}):")
        
        user_properties = []
        for prop_num in range(10):
            prop_id = create_property_for_user(user, prop_num + 1)
            if prop_id:
                user_properties.append(prop_id)
            time.sleep(0.5)  # Rate limiting
        
        all_properties.extend(user_properties)
        print(f"  ✅ Created {len(user_properties)} properties for {user['name']}")
    
    # Step 3: Test the created data
    time.sleep(2)  # Let database sync
    test_created_data()
    
    # Summary
    print(f"\n🎉 REAL TEST DATA CREATION COMPLETE!")
    print(f"=" * 50)
    print(f"👥 Real Users Created: {len(all_users)}/10")
    print(f"🏠 Total Properties: {len(all_properties)}/100")
    print(f"🌐 API Endpoint: {RENDER_API_BASE}")
    print(f"🔑 API Key: {API_KEY}")
    
    print(f"\n📧 Created Users (should appear in Supabase Auth):")
    for user in all_users:
        print(f"   • {user['name']} - {user['email']}")
    
    print(f"\n✅ Your Krib AI Agent can now test with REAL data!")
    print(f'   curl -H "Authorization: Bearer {API_KEY}" \\')
    print(f'        "{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=10"')
    
    print(f"\n🗑️ To clean up: Check Supabase Auth dashboard and delete test users")

if __name__ == "__main__":
    main()
