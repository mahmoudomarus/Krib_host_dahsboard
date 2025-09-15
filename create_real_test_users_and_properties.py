#!/usr/bin/env python3
"""
Create Real Test Users and Properties for Krib AI Platform
This script creates REAL authenticated users in Supabase Auth + properties for each user
"""

import requests
import json
import random
import time
import uuid
from datetime import datetime

# Configuration
SUPABASE_URL = "https://bpomacnqaqzgeuahhlka.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWhobGthIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjM5ODczNzksImV4cCI6MjAzOTU2MzM3OX0.4TfHg1dNJr4LUO2YnAFW02-EBwkYCvAmxiOgECN8Aeo"
RENDER_API_BASE = "https://krib-host-dahsboard-backend.onrender.com/api/v1"
API_KEY = "krib_ai_test_key_12345"

# Test user data
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

def create_supabase_user(user_data):
    """Create a real authenticated user in Supabase Auth"""
    print(f"Creating user: {user_data['name']} ({user_data['email']})")
    
    # Supabase Auth signup endpoint
    auth_url = f"{SUPABASE_URL}/auth/v1/signup"
    
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
    }
    
    signup_payload = {
        "email": user_data["email"],
        "password": user_data["password"],
        "data": {  # User metadata
            "full_name": user_data["name"],
            "role": "host",
            "country": "UAE",
            "city": "Dubai"
        }
    }
    
    try:
        response = requests.post(auth_url, headers=headers, json=signup_payload)
        
        if response.status_code in [200, 201]:
            result = response.json()
            user_id = result.get("user", {}).get("id")
            access_token = result.get("access_token")
            
            print(f"  ✅ User created successfully: {user_id}")
            
            # Also create user profile in users table
            if user_id and access_token:
                create_user_profile(user_id, user_data, access_token)
            
            return {
                "user_id": user_id,
                "access_token": access_token,
                "email": user_data["email"],
                "name": user_data["name"]
            }
        else:
            print(f"  ❌ User creation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ User creation error: {e}")
        return None

def create_user_profile(user_id, user_data, access_token):
    """Create user profile in the users table"""
    
    # Direct Supabase insert to users table
    profile_url = f"{SUPABASE_URL}/rest/v1/users"
    
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Prefer": "return=minimal"
    }
    
    profile_data = {
        "id": user_id,
        "email": user_data["email"],
        "full_name": user_data["name"],
        "role": "host",
        "is_active": True,
        "country": "UAE",
        "city": "Dubai",
        "phone": f"+971{random.randint(50, 59)}{random.randint(1000000, 9999999)}",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        response = requests.post(profile_url, headers=headers, json=profile_data)
        if response.status_code in [200, 201]:
            print(f"    ✅ User profile created in users table")
        else:
            print(f"    ⚠️ Profile creation response: {response.status_code}")
    except Exception as e:
        print(f"    ⚠️ Profile creation error: {e}")

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
    
    # Create via Supabase REST API directly with user auth
    property_url = f"{SUPABASE_URL}/rest/v1/properties"
    
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {user_data['access_token']}",
        "Prefer": "return=representation"
    }
    
    # Add user_id (host_id) to property
    property_data["host_id"] = user_data["user_id"]
    property_data["id"] = str(uuid.uuid4())
    property_data["created_at"] = datetime.utcnow().isoformat() + "Z"
    property_data["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    try:
        response = requests.post(property_url, headers=headers, json=property_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            prop_id = result[0]["id"] if isinstance(result, list) else result.get("id")
            print(f"    ✅ Property {property_number}: {property_data['title']} - AED {price}/night")
            return prop_id
        else:
            print(f"    ❌ Property {property_number} failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"    ❌ Property {property_number} error: {e}")
        return None

def test_created_data():
    """Test the created data via the external API"""
    print("\n🧪 Testing created data via API...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test property search
    try:
        response = requests.get(
            f"{RENDER_API_BASE}/properties/search?state=Dubai&limit=20",
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
            
            # Test property detail
            if properties:
                prop_id = properties[0]["id"]
                detail_response = requests.get(
                    f"{RENDER_API_BASE}/properties/{prop_id}",
                    headers=headers
                )
                if detail_response.status_code == 200:
                    print("✅ Property detail API working")
                else:
                    print("❌ Property detail API failed")
        else:
            print(f"❌ Property search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

def main():
    print("🏠 REAL Dubai Test Data Creator - Supabase Auth + Properties")
    print("=" * 65)
    print("🎯 Target: Live Supabase database with real authenticated users")
    print("👥 Creating: 10 real users in Supabase Auth")
    print("🏠 Creating: 10 properties per user (100 total)")
    print("🔑 Method: Direct Supabase API calls")
    print("=" * 65)
    
    all_users = []
    all_properties = []
    
    # Step 1: Create 10 real authenticated users
    print("\n1️⃣ Creating 10 authenticated users in Supabase...")
    for i, user_data in enumerate(TEST_USERS):
        print(f"\nUser {i+1}/10:")
        created_user = create_supabase_user(user_data)
        if created_user:
            all_users.append(created_user)
        time.sleep(1)  # Rate limiting
    
    print(f"\n✅ Successfully created {len(all_users)} authenticated users")
    
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
            time.sleep(0.3)  # Rate limiting
        
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
    
    print(f"\n📧 Created Users (will appear in Supabase Auth):")
    for user in all_users:
        print(f"   • {user['name']} - {user['email']}")
    
    print(f"\n✅ Your Krib AI Agent can now test with REAL data!")
    print(f'   curl -H "Authorization: Bearer {API_KEY}" \\')
    print(f'        "{RENDER_API_BASE}/properties/search?state=Dubai&limit=10"')
    
    print(f"\n🗑️ To clean up later, you can delete users from Supabase Auth dashboard")

if __name__ == "__main__":
    main()
