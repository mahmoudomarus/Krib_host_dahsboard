# 🤖 Krib AI External Integration Setup Guide

## 🚀 **Quick Start for External AI Platform**

After you deploy this to **Vercel** (frontend) and **Render** (backend), here's everything the external AI platform needs to integrate with your Krib property database.

---

## 🔐 **API Authentication**

### **Production API Key** (Set in Render Environment Variables)
```bash
# Add this to your Render backend environment variables:
KRIB_AI_AGENT_API_KEY=generate_your_own_secure_random_key_here
```

### **Test API Key** (Already configured for testing)
```bash
# This works immediately for testing:
Krib AI Agent: krib_ai_test_key_12345
```

**Note**: You only need ONE API key for your Krib AI platform to access the property database.

---

## 🌐 **API Endpoints**

### **Base URL**
```
Production: https://krib-host-dahsboard-backend.onrender.com/api/external
Testing: http://localhost:8000/api/external (if running locally)
```

### **Required Headers**
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

---

## 🏠 **Available Endpoints**

### **1. Health Check**
```http
GET /api/external/health
```

### **2. Property Search** 
```http
GET /api/external/properties/search?city=Dubai&min_price_per_night=100&max_price_per_night=500&bedrooms=2
```

### **3. Property Details**
```http
GET /api/external/properties/{property_id}
```

### **4. Check Availability**
```http
GET /api/external/properties/{property_id}/availability?start_date=2025-03-01&end_date=2025-03-05&guests=2
```

### **5. Calculate Pricing**
```http
POST /api/external/properties/{property_id}/calculate-pricing
{
  "start_date": "2025-03-01",
  "end_date": "2025-03-05", 
  "guests": 2,
  "discount_code": "WELCOME10"
}
```

### **6. Create Booking**
```http
POST /api/external/bookings
{
  "property_id": "123",
  "guest_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+971501234567"
  },
  "start_date": "2025-03-01",
  "end_date": "2025-03-05",
  "guests": 2,
  "total_amount": 1200.00
}
```

---

## 🔧 **Integration Code Examples**

### **Python Integration Example**
```python
import requests
import json
from datetime import date

# Configuration
API_KEY = "krib_ai_test_key_12345"  # Use your assigned key
BASE_URL = "https://krib-host-dahsboard-backend.onrender.com/api/external"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Search properties
def search_properties(city="Dubai", max_price=500):
    params = {
        "city": city,
        "max_price_per_night": max_price,
        "limit": 10
    }
    
    response = requests.get(
        f"{BASE_URL}/properties/search", 
        headers=headers, 
        params=params
    )
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Check availability
def check_availability(property_id, start_date, end_date, guests=2):
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "guests": guests
    }
    
    response = requests.get(
        f"{BASE_URL}/properties/{property_id}/availability",
        headers=headers,
        params=params
    )
    
    return response.json()

# Create booking
def create_booking(property_id, guest_info, start_date, end_date, guests, total_amount):
    booking_data = {
        "property_id": property_id,
        "guest_info": guest_info,
        "start_date": start_date,
        "end_date": end_date,
        "guests": guests,
        "total_amount": total_amount
    }
    
    response = requests.post(
        f"{BASE_URL}/bookings",
        headers=headers,
        json=booking_data
    )
    
    return response.json()

# Example usage
if __name__ == "__main__":
    # Search for properties
    properties = search_properties("Dubai Marina", 400)
    print(f"Found {len(properties)} properties")
    
    if properties:
        property_id = properties[0]["id"]
        
        # Check availability
        availability = check_availability(
            property_id, 
            "2025-03-01", 
            "2025-03-05", 
            2
        )
        print(f"Available: {availability['data']['is_available']}")
```

### **JavaScript/Node.js Integration Example**
```javascript
const axios = require('axios');

class KribAIIntegration {
    constructor(apiKey = 'krib_ai_test_key_12345') {
        this.apiKey = apiKey;
        this.baseURL = 'https://krib-host-dahsboard-backend.onrender.com/api/external';
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async searchProperties(filters = {}) {
        try {
            const response = await axios.get(
                `${this.baseURL}/properties/search`,
                { 
                    headers: this.headers,
                    params: filters
                }
            );
            return response.data.data;
        } catch (error) {
            console.error('Search error:', error.response?.data || error.message);
            return null;
        }
    }

    async checkAvailability(propertyId, startDate, endDate, guests = 2) {
        try {
            const response = await axios.get(
                `${this.baseURL}/properties/${propertyId}/availability`,
                {
                    headers: this.headers,
                    params: {
                        start_date: startDate,
                        end_date: endDate,
                        guests: guests
                    }
                }
            );
            return response.data.data;
        } catch (error) {
            console.error('Availability error:', error.response?.data || error.message);
            return null;
        }
    }

    async createBooking(bookingData) {
        try {
            const response = await axios.post(
                `${this.baseURL}/bookings`,
                bookingData,
                { headers: this.headers }
            );
            return response.data.data;
        } catch (error) {
            console.error('Booking error:', error.response?.data || error.message);
            return null;
        }
    }
}

// Example usage
const krib = new KribAIIntegration();

// Search and book example
async function findAndBook() {
    // Search properties
    const properties = await krib.searchProperties({
        city: 'Dubai Marina',
        bedrooms: 2,
        max_price_per_night: 500
    });

    if (properties?.length > 0) {
        const property = properties[0];
        console.log(`Found property: ${property.title}`);

        // Check availability
        const availability = await krib.checkAvailability(
            property.id,
            '2025-03-01',
            '2025-03-05',
            2
        );

        if (availability?.is_available) {
            // Create booking
            const booking = await krib.createBooking({
                property_id: property.id,
                guest_info: {
                    name: 'Jane Smith',
                    email: 'jane@example.com',
                    phone: '+971501234567'
                },
                start_date: '2025-03-01',
                end_date: '2025-03-05',
                guests: 2,
                total_amount: availability.total_price
            });

            console.log('Booking created:', booking);
        }
    }
}

findAndBook();
```

---

## 🚦 **Rate Limits**

- **Property Search**: 100 requests/minute
- **Property Details**: 200 requests/minute  
- **Availability Check**: 150 requests/minute
- **Pricing Calculation**: 150 requests/minute
- **Booking Creation**: 50 requests/minute

---

## 🧪 **Testing Instructions**

### **1. After Deployment**
Once you've deployed to Vercel and Render, test the health endpoint:

```bash
curl -H "Authorization: Bearer krib_ai_test_key_12345" \
     https://krib-host-dahsboard-backend.onrender.com/api/external/health
```

Expected response:
```json
{
  "success": true,
  "message": "External API is healthy",
  "data": {
    "service": "Krib AI External API",
    "version": "1.0.0",
    "timestamp": "2025-01-XX...",
    "authenticated_service": "krib_ai_agent"
  }
}
```

### **2. Run the Test Script**
Use the provided test script:

```bash
cd backend/
python test_external_api.py
```

### **3. Test Property Search**
```bash
curl -H "Authorization: Bearer krib_ai_test_key_12345" \
     "https://krib-host-dahsboard-backend.onrender.com/api/external/properties/search?city=Dubai&limit=5"
```

---

## 🔒 **Security & Best Practices**

### **API Key Management**
1. **Never expose API keys** in client-side code
2. **Store keys securely** in environment variables
3. **Rotate keys regularly** for production
4. **Use different keys** for different services/environments

### **Error Handling**
```python
def handle_api_response(response):
    if response.status_code == 200:
        return response.json()["data"]
    elif response.status_code == 401:
        print("Invalid API key")
    elif response.status_code == 429:
        print("Rate limit exceeded")
    elif response.status_code >= 500:
        print("Server error - try again later")
    else:
        print(f"API Error: {response.status_code}")
    
    return None
```

---

## 📞 **Support & Contact**

- **API Documentation**: See `EXTERNAL_API_GUIDE.md` for detailed endpoints
- **Test Script**: Use `backend/test_external_api.py`
- **Issues**: Check server logs and response error messages

---

## 🎯 **Next Steps**

1. **Deploy** to Vercel (frontend) and Render (backend)
2. **Set production API keys** in Render environment variables
3. **Test** the health endpoint and search functionality
4. **Integrate** using the code examples above
5. **Monitor** API usage and adjust rate limits if needed

**That's it! Your external AI platform can now access Krib's property database! 🚀**
