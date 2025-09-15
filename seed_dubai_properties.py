#!/usr/bin/env python3
"""
Comprehensive Dubai Property Seeding Script
Creates 10 realistic property hosts, each with 10 properties (100 total)
Includes cleanup functionality for testing purposes
Targets Render deployment: https://krib-host-dahsboard-backend.onrender.com
"""

import os
import uuid
import random
from datetime import datetime, timedelta
import requests
import json
import time

# Supabase Configuration  
SUPABASE_URL = "https://bpomacnqaqzgeuahhlka.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwb21hY25xYXF6Z2V1YWRobGthIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjEzMjU2NDEsImV4cCI6MjAzNjkwMTY0MX0.wJYmPEtqAVKg3BOgqH5kOiikbNStjb6zJJBb_FS-Q-Y"

# Test tracking
CREATED_USERS = []
CREATED_PROPERTIES = []
CREATED_IMAGES = []

# Dubai Host Companies (realistic property management companies)
DUBAI_HOST_COMPANIES = [
    {"name": "Emirates Luxury Properties", "domain": "emiratesluxury.ae"},
    {"name": "Dubai Marina Homes", "domain": "dubaimarinehomes.com"}, 
    {"name": "Downtown Dubai Rentals", "domain": "downtowndubairentals.ae"},
    {"name": "JBR Beach Properties", "domain": "jbrbeachproperties.com"},
    {"name": "Business Bay Suites", "domain": "businessbaysuites.ae"},
    {"name": "DIFC Executive Homes", "domain": "difcexecutive.com"},
    {"name": "Palm Jumeirah Villas", "domain": "palmjumerahvillas.ae"},
    {"name": "Dubai Hills Estates", "domain": "dubaihillsestates.com"},
    {"name": "City Walk Apartments", "domain": "citywalkapartments.ae"},
    {"name": "Al Barsha Residences", "domain": "albarsharesidences.com"}
]

# Dubai Areas with realistic property distributions
DUBAI_AREAS = [
    "Dubai Marina", "Downtown Dubai", "Jumeirah Beach Residence (JBR)", 
    "Business Bay", "DIFC", "Palm Jumeirah", "Dubai Hills Estate",
    "City Walk", "Al Barsha", "The Greens", "Jumeirah", "Deira",
    "Dubai Investment Park", "International City", "Discovery Gardens",
    "Jumeirah Village Circle (JVC)", "Motor City", "Dubai Silicon Oasis"
]

# Property types with realistic distributions
PROPERTY_TYPES = [
    {"type": "studio", "weight": 15, "bedrooms": 0, "bathrooms": 1, "guests": 2},
    {"type": "apartment", "weight": 50, "bedrooms": [1,2,3], "bathrooms": [1,2,3], "guests": [2,4,6]},
    {"type": "penthouse", "weight": 10, "bedrooms": [2,3,4], "bathrooms": [2,3,4], "guests": [4,6,8]},
    {"type": "villa", "weight": 15, "bedrooms": [3,4,5], "bathrooms": [3,4,5], "guests": [6,8,10]},
    {"type": "townhouse", "weight": 10, "bedrooms": [2,3], "bathrooms": [2,3], "guests": [4,6]}
]

# UAE-specific amenities
UAE_AMENITIES = [
    "WiFi", "Pool", "Gym", "Parking", "24/7 Security", "Concierge Service",
    "Sea View", "Marina View", "City View", "Burj Khalifa View", "Golf Course View",
    "Beach Access", "Metro Access", "Mall Nearby", "Restaurant Nearby",
    "Central Air Conditioning", "Maid's Room", "Balcony", "Garden", "Private Pool",
    "Valet Parking", "Business Center", "Children's Play Area", "BBQ Area"
]

def create_realistic_users():
    """Create 10 realistic Dubai property host users"""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    created_users = []
    
    for i, company in enumerate(DUBAI_HOST_COMPANIES):
        user_id = str(uuid.uuid4())
        
        # Generate realistic contact person name
        first_names = ["Ahmed", "Fatima", "Mohammed", "Aisha", "Omar", "Mariam", "Khalid", "Noura", "Ali", "Sarah"]
        last_names = ["Al-Maktoum", "Al-Mansouri", "Al-Zaabi", "Al-Shamsi", "Al-Kaabi", "Al-Muhairi", "Al-Blooshi", "Al-Mazrouei", "Al-Nuaimi", "Al-Qasimi"]
        
        contact_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"host{i+1}@{company['domain']}"
        
        user_data = {
            "id": user_id,
            "name": contact_name,
            "email": email,
            "company": company['name'],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=headers,
            json=user_data
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ User created: {contact_name} ({company['name']})")
            created_users.append(user_id)
            CREATED_USERS.append(user_id)
            time.sleep(0.1)  # Rate limiting
        else:
            print(f"❌ User creation failed for {company['name']}: {response.text}")
    
    return created_users

def generate_realistic_property(user_id, company_name, property_number):
    """Generate a single realistic Dubai property"""
    
    # Select property type based on weights
    property_type_choice = random.choices(
        PROPERTY_TYPES, 
        weights=[pt["weight"] for pt in PROPERTY_TYPES], 
        k=1
    )[0]
    
    property_type = property_type_choice["type"]
    
    if property_type == "studio":
        bedrooms = 0
        bathrooms = 1
        max_guests = 2
    else:
        bedrooms = random.choice(property_type_choice["bedrooms"])
        bathrooms = random.choice(property_type_choice["bathrooms"])
        max_guests = random.choice(property_type_choice["guests"])
    
    # Select area
    area = random.choice(DUBAI_AREAS)
    
    # Generate realistic pricing based on area and type
    base_prices = {
        "studio": {"min": 300, "max": 600},
        "apartment": {"min": 400, "max": 1200},
        "penthouse": {"min": 1000, "max": 3000},
        "villa": {"min": 1500, "max": 5000},
        "townhouse": {"min": 800, "max": 2000}
    }
    
    area_multipliers = {
        "Downtown Dubai": 1.8, "Dubai Marina": 1.6, "Palm Jumeirah": 2.2,
        "Jumeirah Beach Residence (JBR)": 1.7, "DIFC": 1.8, "Business Bay": 1.4,
        "City Walk": 1.5, "Jumeirah": 1.6, "Dubai Hills Estate": 1.3,
        "Al Barsha": 1.0, "The Greens": 1.1, "Deira": 0.8
    }
    
    base_price = random.randint(
        base_prices[property_type]["min"],
        base_prices[property_type]["max"]
    )
    
    multiplier = area_multipliers.get(area, 1.0)
    final_price = round(base_price * multiplier, 0)
    
    # Generate coordinates (approximate for Dubai areas)
    area_coordinates = {
        "Dubai Marina": (25.077479, 55.138206),
        "Downtown Dubai": (25.197525, 55.274288),
        "Jumeirah Beach Residence (JBR)": (25.084847, 55.127754),
        "Business Bay": (25.189492, 55.267708),
        "DIFC": (25.214131, 55.279178),
        "Palm Jumeirah": (25.112676, 55.138358)
    }
    
    base_lat, base_lng = area_coordinates.get(area, (25.2048, 55.2708))
    # Add small random offset
    latitude = base_lat + random.uniform(-0.01, 0.01)
    longitude = base_lng + random.uniform(-0.01, 0.01)
    
    # Generate realistic amenities
    essential_amenities = ["WiFi", "Central Air Conditioning", "24/7 Security", "Parking"]
    area_specific_amenities = {
        "Dubai Marina": ["Marina View", "Sea View", "Beach Access"],
        "Downtown Dubai": ["Burj Khalifa View", "City View", "Metro Access", "Dubai Mall Nearby"],
        "Jumeirah Beach Residence (JBR)": ["Beach Access", "Sea View", "Restaurant Nearby"],
        "Business Bay": ["City View", "Business Center", "Metro Access"],
        "DIFC": ["City View", "Concierge Service", "Valet Parking", "Metro Access"],
        "Palm Jumeirah": ["Sea View", "Beach Access", "Private Pool", "Garden"]
    }
    
    property_amenities = essential_amenities.copy()
    property_amenities.extend(area_specific_amenities.get(area, []))
    
    # Add random amenities
    additional_amenities = random.sample(
        [a for a in UAE_AMENITIES if a not in property_amenities], 
        k=random.randint(3, 8)
    )
    property_amenities.extend(additional_amenities)
    
    # Generate title and description
    bedroom_text = f"{bedrooms}BR" if bedrooms > 0 else "Studio"
    area_short = area.replace("Jumeirah Beach Residence (JBR)", "JBR")
    
    title_templates = [
        f"Modern {bedroom_text} {property_type.title()} in {area_short}",
        f"Luxury {bedroom_text} {area_short} {property_type.title()}",
        f"Premium {bedroom_text} {property_type.title()} - {area_short}",
        f"Stunning {bedroom_text} {area_short} {property_type.title()}",
        f"Executive {bedroom_text} {property_type.title()} {area_short}"
    ]
    
    title = random.choice(title_templates)
    
    description_templates = [
        f"Beautiful {bedrooms if bedrooms > 0 else 1}-bedroom {property_type} located in the heart of {area}. Perfect for {'business travelers' if area in ['Business Bay', 'DIFC'] else 'families and tourists'}. Features modern amenities and premium location.",
        f"Spacious {property_type} in {area} with {max_guests} guest capacity. Ideal for {'short business stays' if property_type in ['studio', 'apartment'] else 'family vacations'}. High-quality furnishing and excellent location.",
        f"Elegant {property_type} offering {max_guests}-guest accommodation in {area}. {'Prime business location' if area in ['Business Bay', 'DIFC', 'Downtown Dubai'] else 'Tourist-friendly area'} with easy access to major attractions."
    ]
    
    description = random.choice(description_templates)
    
    # Generate realistic address
    street_numbers = [f"{random.randint(1, 999)}", f"Building {random.randint(1, 50)}", f"Tower {random.randint(1, 30)}"]
    street_names = ["Sheikh Zayed Road", "Al Khaleej Street", "Dubai Marina Walk", "The Boulevard", "Al Seef Street"]
    
    address = f"{random.choice(street_numbers)} {random.choice(street_names)}, {area}, Dubai, UAE"
    
    # High-quality property images
    property_images = [
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1600607687644-aac4c119fe23?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?w=1200&h=800&fit=crop",
        "https://images.unsplash.com/photo-1600566752734-f6b8e4fa8a88?w=1200&h=800&fit=crop"
    ]
    
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "description": description,
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "max_guests": max_guests,
        "price_per_night": final_price,
        "city": area,
        "state": "Dubai",
        "country": "UAE",
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "amenities": property_amenities,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "images": [
            {
                "url": random.choice(property_images),
                "alt_text": f"{area} {property_type} interior view",
                "is_primary": True,
                "order": 0
            }
        ]
    }

def create_properties_for_user(user_id, company_name):
    """Create 10 realistic properties for a single user"""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    created_properties = []
    
    for i in range(10):
        try:
            property_data = generate_realistic_property(user_id, company_name, i+1)
            
            # Extract images before creating property
            images_data = property_data.pop("images")
            
            # Create property
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/properties",
                headers=headers,
                json=property_data
            )
            
            if response.status_code in [200, 201]:
                property_id = property_data["id"]
                print(f"    ✅ Property {i+1}: {property_data['title'][:50]}...")
                created_properties.append(property_id)
                CREATED_PROPERTIES.append(property_id)
                
                # Create property images
                for img in images_data:
                    image_id = str(uuid.uuid4())
                    image_record = {
                        "id": image_id,
                        "property_id": property_id,
                        "url": img["url"],
                        "alt_text": img["alt_text"],
                        "is_primary": img["is_primary"],
                        "order": img["order"],
                        "created_at": datetime.utcnow().isoformat()
                    }
                    
                    img_response = requests.post(
                        f"{SUPABASE_URL}/rest/v1/property_images",
                        headers=headers,
                        json=image_record
                    )
                    
                    if img_response.status_code in [200, 201]:
                        CREATED_IMAGES.append(image_id)
                    
                time.sleep(0.1)  # Rate limiting
                
            else:
                print(f"    ❌ Property {i+1} creation failed: {response.text}")
                
        except Exception as e:
            print(f"    ❌ Error creating property {i+1}: {str(e)}")
    
    return created_properties

def cleanup_test_data():
    """Delete all test data created during seeding"""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    print("\n🧹 Cleaning up test data...")
    
    # Delete property images
    for image_id in CREATED_IMAGES:
        try:
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/property_images?id=eq.{image_id}",
                headers=headers
            )
            if response.status_code in [200, 204]:
                print(f"  🗑️ Deleted image: {image_id}")
        except Exception as e:
            print(f"  ❌ Failed to delete image {image_id}: {e}")
    
    # Delete properties
    for property_id in CREATED_PROPERTIES:
        try:
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/properties?id=eq.{property_id}",
                headers=headers
            )
            if response.status_code in [200, 204]:
                print(f"  🗑️ Deleted property: {property_id}")
        except Exception as e:
            print(f"  ❌ Failed to delete property {property_id}: {e}")
    
    # Delete users
    for user_id in CREATED_USERS:
        try:
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}",
                headers=headers
            )
            if response.status_code in [200, 204]:
                print(f"  🗑️ Deleted user: {user_id}")
        except Exception as e:
            print(f"  ❌ Failed to delete user {user_id}: {e}")
    
    print(f"✅ Cleanup complete!")
    print(f"   Deleted: {len(CREATED_IMAGES)} images, {len(CREATED_PROPERTIES)} properties, {len(CREATED_USERS)} users")

def test_render_api_endpoints():
    """Test the Render API endpoints with created data"""
    api_key = "krib_ai_test_key_12345"
    base_url = "https://krib-host-dahsboard-backend.onrender.com/api/v1"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-API-Version": "1.0",
        "User-Agent": "KribAI-Test-Client/1.0"
    }
    
    print("\n🧪 Testing Render API endpoints...")
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        health_response = requests.get("https://krib-host-dahsboard-backend.onrender.com/health")
        if health_response.status_code == 200:
            print("   ✅ Health check successful")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Property search - Dubai Marina
    print("2️⃣ Testing property search (Dubai Marina)...")
    search_params = {
        "state": "Dubai",
        "city": "Dubai Marina", 
        "limit": 10
    }
    
    try:
        response = requests.get(f"{base_url}/properties/search", headers=headers, params=search_params)
        if response.status_code == 200:
            data = response.json()
            count = data['data']['total_count']
            print(f"   ✅ Dubai Marina search: {count} properties found")
            
            if count > 0:
                # Test property details
                property_id = data["data"]["properties"][0]["id"]
                property_title = data["data"]["properties"][0]["title"]
                
                print("3️⃣ Testing property details...")
                detail_response = requests.get(f"{base_url}/properties/{property_id}", headers=headers)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(f"   ✅ Property details successful: {property_title}")
                    
                    # Display sample property for verification
                    prop = detail_data["data"]
                    print(f"   📋 Sample Property:")
                    print(f"      Title: {prop['title']}")
                    print(f"      Type: {prop['property_type']} | {prop['bedrooms']}BR | {prop['bathrooms']}BA")
                    print(f"      Price: AED {prop['price_per_night']}/night")
                    print(f"      Location: {prop['city']}, {prop['state']}")
                    print(f"      Guests: {prop['max_guests']} | Amenities: {len(prop['amenities'])}")
                    
                else:
                    print(f"   ❌ Property details failed: {detail_response.text}")
            
        else:
            print(f"   ❌ Property search failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Property search error: {e}")
    
    # Test 3: Different area searches
    test_areas = ["Downtown Dubai", "Business Bay", "DIFC"]
    
    for area in test_areas:
        print(f"4️⃣ Testing {area} search...")
        try:
            search_params = {"state": "Dubai", "city": area, "limit": 5}
            response = requests.get(f"{base_url}/properties/search", headers=headers, params=search_params)
            
            if response.status_code == 200:
                count = response.json()['data']['total_count']
                print(f"   ✅ {area}: {count} properties")
            else:
                print(f"   ❌ {area} search failed")
        except Exception as e:
            print(f"   ❌ {area} search error: {e}")
    
    # Test 4: Filter testing
    print("5️⃣ Testing filters...")
    filter_tests = [
        {"bedrooms": 2, "max_price_per_night": 1000, "desc": "2BR under AED 1000"},
        {"property_type": "villa", "desc": "Villa properties"},
        {"min_price_per_night": 500, "max_price_per_night": 800, "desc": "AED 500-800 range"}
    ]
    
    for test in filter_tests:
        try:
            params = {"state": "Dubai", "limit": 5}
            params.update({k: v for k, v in test.items() if k != "desc"})
            
            response = requests.get(f"{base_url}/properties/search", headers=headers, params=params)
            if response.status_code == 200:
                count = response.json()['data']['total_count']
                print(f"   ✅ {test['desc']}: {count} properties")
            else:
                print(f"   ❌ {test['desc']}: Failed")
        except Exception as e:
            print(f"   ❌ {test['desc']}: Error {e}")
    
    return True

if __name__ == "__main__":
    print("🏠 Comprehensive Dubai Property Seeding Script")
    print("=" * 60)
    print("🎯 Target: Render deployment")
    print("📊 Creating: 10 users × 10 properties = 100 total properties")
    print("🧪 Testing: Full API integration with your Krib AI agent")
    print("=" * 60)
    
    try:
        # Step 1: Create 10 realistic users
        print("\n1️⃣ Creating 10 realistic Dubai property hosts...")
        created_users = create_realistic_users()
        
        if len(created_users) == 0:
            print("❌ Failed to create any users. Exiting.")
            exit(1)
        
        print(f"✅ Successfully created {len(created_users)} users")
        
        # Step 2: Create 10 properties for each user
        print(f"\n2️⃣ Creating 10 properties for each user (100 total)...")
        total_properties = 0
        
        for i, user_id in enumerate(created_users):
            company_name = DUBAI_HOST_COMPANIES[i]["name"]
            print(f"\n  👤 {company_name} (User {i+1}/{len(created_users)}):")
            
            user_properties = create_properties_for_user(user_id, company_name)
            total_properties += len(user_properties)
            
            print(f"    ✅ Created {len(user_properties)} properties")
        
        print(f"\n🎉 SEEDING COMPLETE!")
        print(f"   📊 Total: {len(created_users)} users, {total_properties} properties, {len(CREATED_IMAGES)} images")
        
        # Step 3: Test Render API endpoints comprehensively
        print(f"\n3️⃣ Testing Render API integration...")
        test_render_api_endpoints()
        
        # Step 4: Display integration summary
        print(f"\n📋 INTEGRATION READY!")
        print(f"=" * 50)
        print(f"🔑 API Key: krib_ai_test_key_12345")
        print(f"🌐 Base URL: https://krib-host-dahsboard-backend.onrender.com/api/v1")
        print(f"📊 Database: {total_properties} Dubai properties available")
        print(f"🏙️ Areas: Dubai Marina, Downtown, JBR, Business Bay, DIFC, etc.")
        print(f"🏠 Types: Studios, Apartments, Penthouses, Villas, Townhouses")
        print(f"💰 Pricing: AED 300-5000+ per night (realistic Dubai rates)")
        
        print(f"\n🧪 QUICK TESTS:")
        print(f'   Health: curl "https://krib-host-dahsboard-backend.onrender.com/health"')
        print(f'   Search: curl -H "Authorization: Bearer krib_ai_test_key_12345" \\')
        print(f'           "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search?state=Dubai&limit=5"')
        
        # Step 5: Ask about cleanup
        print(f"\n🔄 CLEANUP OPTIONS:")
        print(f"   ✅ Data created successfully - ready for AI agent integration")
        print(f"   🗑️  To cleanup later, run: cleanup_test_data()")
        print(f"   ⚠️  Keep data for testing, cleanup when done")
        
        cleanup_choice = input(f"\n❓ Do you want to cleanup test data now? (y/N): ").lower().strip()
        
        if cleanup_choice in ['y', 'yes']:
            cleanup_test_data()
            print(f"\n✅ All test data cleaned up!")
        else:
            print(f"\n✅ Test data preserved for integration testing")
            print(f"   📝 Run cleanup_test_data() when finished testing")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Script interrupted by user")
        print(f"🧹 Cleaning up partially created data...")
        cleanup_test_data()
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print(f"🧹 Cleaning up any created data...")
        cleanup_test_data()
        
    print(f"\n🏁 Script execution complete!")
