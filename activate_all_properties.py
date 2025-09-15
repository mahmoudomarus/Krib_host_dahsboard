#!/usr/bin/env python3
"""
Activate All Draft Properties
Make all draft properties active so they're visible to the external API
"""

import requests
import json
import time

# Configuration
RENDER_API_BASE = "https://krib-host-dahsboard-backend.onrender.com"

# Users to process
USERS = [
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

def login_user(user_data):
    """Login user and get access token"""
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
            return result.get("access_token")
        else:
            print(f"  ❌ Login failed for {user_data['name']}")
            return None
            
    except Exception as e:
        print(f"  ❌ Login error for {user_data['name']}: {e}")
        return None

def get_user_properties(access_token):
    """Get all properties for a user"""
    try:
        response = requests.get(
            f"{RENDER_API_BASE}/api/properties",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
            
    except Exception as e:
        print(f"  ❌ Error getting properties: {e}")
        return []

def activate_property(access_token, property_id):
    """Activate a single property"""
    try:
        response = requests.put(
            f"{RENDER_API_BASE}/api/properties/{property_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={"status": "active"}
        )
        
        return response.status_code in [200, 201]
        
    except Exception as e:
        print(f"    ❌ Error activating property {property_id}: {e}")
        return False

def main():
    print("🔄 KRIB AI - Activate All Properties")
    print("=" * 50)
    print("🎯 Goal: Make all draft properties active for external API")
    print("👥 Users: 10 confirmed hosts")
    print("🔄 Action: Change status from 'draft' to 'active'")
    print("=" * 50)
    
    total_activated = 0
    
    for user_index, user in enumerate(USERS):
        print(f"\n{user_index+1}. Processing {user['name']}:")
        
        # Login user
        access_token = login_user(user)
        if not access_token:
            continue
        
        # Get user's properties
        properties = get_user_properties(access_token)
        if not properties:
            print(f"  ❌ No properties found for {user['name']}")
            continue
        
        print(f"  📋 Found {len(properties)} properties")
        
        # Activate each draft property
        activated_count = 0
        for prop in properties:
            if prop.get("status") == "draft":
                if activate_property(access_token, prop["id"]):
                    print(f"    ✅ Activated: {prop['title']}")
                    activated_count += 1
                    total_activated += 1
                else:
                    print(f"    ❌ Failed: {prop['title']}")
                time.sleep(0.1)  # Rate limiting
            else:
                print(f"    ✓ Already active: {prop['title']}")
        
        print(f"  ✅ Activated {activated_count} properties for {user['name']}")
    
    # Test the external API
    print(f"\n🧪 Testing external API...")
    time.sleep(2)  # Let database sync
    
    try:
        api_headers = {
            "Authorization": "Bearer krib_ai_test_key_12345",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=10",
            headers=api_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            total_count = data.get("data", {}).get("total_count", 0)
            properties = data.get("data", {}).get("properties", [])
            
            print(f"✅ External API now shows {total_count} active properties!")
            
            if properties:
                print(f"\n📋 Sample properties visible to Krib AI Agent:")
                for i, prop in enumerate(properties[:5]):
                    print(f"   {i+1}. {prop.get('title', 'Unknown')} - AED {prop.get('price_per_night', 0)}/night")
                    print(f"      📍 {prop.get('city', 'Unknown')} | {prop.get('bedrooms', 0)}BR | {prop.get('property_type', 'Unknown')}")
                
                # Test different search filters
                print(f"\n🔍 Testing search filters:")
                
                test_searches = [
                    {"city": "Dubai Marina", "desc": "Dubai Marina"},
                    {"property_type": "villa", "desc": "Villas"},
                    {"bedrooms": 2, "desc": "2+ bedrooms"},
                    {"max_price_per_night": 1000, "desc": "Under AED 1000/night"}
                ]
                
                for search in test_searches:
                    try:
                        search_params = {"state": "Dubai", "limit": 3, **{k: v for k, v in search.items() if k != "desc"}}
                        search_response = requests.get(
                            f"{RENDER_API_BASE}/api/v1/properties/search",
                            headers=api_headers,
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
            print(f"❌ External API test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    # Summary
    print(f"\n🎉 PROPERTY ACTIVATION COMPLETE!")
    print(f"=" * 50)
    print(f"🔄 Total Properties Activated: {total_activated}")
    print(f"🌐 External API: {RENDER_API_BASE}/api/v1/properties/search")
    print(f"🔑 API Key: krib_ai_test_key_12345")
    
    print(f"\n✅ Your Krib AI Agent can now test with active properties!")
    print(f'   curl -H "Authorization: Bearer krib_ai_test_key_12345" \\')
    print(f'        "{RENDER_API_BASE}/api/v1/properties/search?state=Dubai&limit=10"')

if __name__ == "__main__":
    main()
