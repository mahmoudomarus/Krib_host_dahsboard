# 🤖 Krib AI Integration Package - READY FOR DEPLOYMENT

## 🚀 **PRODUCTION-READY API ACCESS**

### **🔑 API Keys for Krib AI**

#### **Test Environment (Working Now):**
```bash
API_KEY: krib_ai_test_key_12345
BASE_URL: https://krib-host-dahsboard-backend.onrender.com/api/v1
```

#### **Production Environment (Set These in Your Environment):**
```bash
API_KEY: [Generate your secure production key]
BASE_URL: https://krib-host-dahsboard-backend.onrender.com/api/v1
```

---

## 📡 **API Endpoints for Krib AI**

### **Base URL**: `https://krib-host-dahsboard-backend.onrender.com`

### **✅ Working Endpoints:**

#### **1. Property Search**
```http
GET /api/v1/properties/search
Authorization: Bearer krib_ai_test_key_12345
```

**Parameters:**
```
city: string (optional) - "Dubai", "Abu Dhabi"
state: string (optional) - UAE Emirate
min_price_per_night: number (optional) - AED
max_price_per_night: number (optional) - AED
bedrooms: integer (optional) - Minimum bedrooms
bathrooms: number (optional) - Minimum bathrooms
max_guests: integer (optional) - Minimum guest capacity
property_type: string (optional) - "apartment", "villa", "studio"
check_in: date (optional) - "2025-03-01"
check_out: date (optional) - "2025-03-05"
limit: integer (optional, default: 20) - Results per page
offset: integer (optional, default: 0) - Results offset
sort_by: string (optional, default: "price_asc") - Sort order
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "prop_123",
        "title": "Luxury 2BR in Dubai Marina",
        "description": "Beautiful waterfront apartment...",
        "base_price_per_night": 450.00,
        "bedrooms": 2,
        "bathrooms": 2.0,
        "max_guests": 4,
        "property_type": "apartment",
        "address": {
          "street": "Marina Walk",
          "area": "Dubai Marina", 
          "city": "Dubai",
          "emirate": "Dubai",
          "country": "UAE",
          "coordinates": {"latitude": 25.0657, "longitude": 55.1728}
        },
        "amenities": ["wifi", "pool", "gym", "parking"],
        "images": [
          {"url": "https://example.com/image1.jpg", "is_primary": true}
        ],
        "host": {
          "id": "host_456",
          "name": "Ahmed Al-Rashid",
          "response_rate": 98.5,
          "is_superhost": true
        },
        "instant_book": true,
        "minimum_nights": 2,
        "rating": 4.8,
        "review_count": 124
      }
    ],
    "total_count": 25,
    "has_more": true
  }
}
```

#### **2. Property Details**
```http
GET /api/v1/properties/{property_id}
Authorization: Bearer krib_ai_test_key_12345
```

**Response:** Complete property information with host details, amenities, images, and policies.

#### **3. Check Availability**
```http
GET /api/v1/properties/{property_id}/availability?check_in=2025-03-01&check_out=2025-03-05&guests=2
Authorization: Bearer krib_ai_test_key_12345
```

**Response:**
```json
{
  "success": true,
  "data": {
    "property_id": "prop_123",
    "check_in": "2025-03-01",
    "check_out": "2025-03-05",
    "guests": 2,
    "is_available": true,
    "reasons": [],
    "alternative_dates": []
  }
}
```

#### **4. Calculate Pricing**
```http
POST /api/v1/properties/{property_id}/calculate-pricing
Authorization: Bearer krib_ai_test_key_12345
Content-Type: application/json

{
  "check_in": "2025-03-01",
  "check_out": "2025-03-05",
  "guests": 2,
  "promo_code": "WELCOME10"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "base_total": 1800.00,
    "cleaning_fee": 150.00,
    "service_fee": 54.00,
    "tourism_tax": 40.00,
    "vat_amount": 102.20,
    "discount_amount": 180.00,
    "total_amount": 1966.20,
    "breakdown": "Detailed pricing breakdown"
  }
}
```

#### **5. Create Booking**
```http
POST /api/v1/bookings
Authorization: Bearer krib_ai_test_key_12345
Content-Type: application/json

{
  "property_id": "prop_123",
  "check_in": "2025-03-01",
  "check_out": "2025-03-05", 
  "guests": 2,
  "guest_info": {
    "first_name": "John",
    "last_name": "Doe", 
    "email": "john@example.com",
    "phone": "+971501234567"
  },
  "total_amount": 1966.20,
  "special_requests": "Late check-in requested"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "booking_id": "BK20250306001",
    "status": "pending",
    "confirmation_number": "KRIB-12345",
    "property": {
      "title": "Luxury 2BR in Dubai Marina",
      "address": "Marina Walk, Dubai Marina"
    },
    "booking_details": {
      "check_in": "2025-03-01",
      "check_out": "2025-03-05",
      "nights": 4,
      "guests": 2,
      "total_amount": 1966.20
    },
    "next_steps": [
      "Payment processing will begin within 24 hours",
      "Check-in instructions sent 24h before arrival"
    ]
  }
}
```

---

## 🔒 **Authentication**

### **Headers Required:**
```http
Authorization: Bearer krib_ai_test_key_12345
Content-Type: application/json
```

### **Rate Limits:**
- **Search**: 100 requests/minute
- **Details**: 200 requests/minute
- **Availability**: 150 requests/minute  
- **Pricing**: 150 requests/minute
- **Bookings**: 50 requests/minute

---

## 🧪 **Testing Commands**

### **1. Test Health Check**
```bash
curl "https://krib-host-dahsboard-backend.onrender.com/api/health"
```

### **2. Test Property Search**
```bash
curl -H "Authorization: Bearer krib_ai_test_key_12345" \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search?city=Dubai&bedrooms=2&max_price_per_night=500"
```

### **3. Test Availability**
```bash
curl -H "Authorization: Bearer krib_ai_test_key_12345" \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_123/availability?check_in=2025-03-01&check_out=2025-03-05&guests=2"
```

### **4. Test Pricing**
```bash
curl -X POST \
     -H "Authorization: Bearer krib_ai_test_key_12345" \
     -H "Content-Type: application/json" \
     -d '{"check_in": "2025-03-01", "check_out": "2025-03-05", "guests": 2}' \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_123/calculate-pricing"
```

### **5. Test Booking**
```bash
curl -X POST \
     -H "Authorization: Bearer krib_ai_test_key_12345" \
     -H "Content-Type: application/json" \
     -d '{
       "property_id": "prop_123",
       "check_in": "2025-03-01",
       "check_out": "2025-03-05",
       "guests": 2,
       "guest_info": {
         "first_name": "John",
         "last_name": "Doe",
         "email": "john@example.com", 
         "phone": "+971501234567"
       },
       "total_amount": 1200.00
     }' \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/bookings"
```

---

## 🔧 **Integration Code Examples**

### **Python Example for Krib AI**
```python
import requests
from datetime import date

class KribHostDashboardAPI:
    def __init__(self, api_key="krib_ai_test_key_12345"):
        self.api_key = api_key
        self.base_url = "https://krib-host-dahsboard-backend.onrender.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def search_properties(self, **filters):
        """Search for properties with filters"""
        response = requests.get(
            f"{self.base_url}/properties/search",
            headers=self.headers,
            params=filters
        )
        return response.json()
    
    def get_property_details(self, property_id):
        """Get detailed property information"""
        response = requests.get(
            f"{self.base_url}/properties/{property_id}",
            headers=self.headers
        )
        return response.json()
    
    def check_availability(self, property_id, check_in, check_out, guests=2):
        """Check if property is available"""
        params = {
            "check_in": check_in,
            "check_out": check_out, 
            "guests": guests
        }
        response = requests.get(
            f"{self.base_url}/properties/{property_id}/availability",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def calculate_pricing(self, property_id, check_in, check_out, guests, promo_code=None):
        """Calculate booking pricing"""
        data = {
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests
        }
        if promo_code:
            data["promo_code"] = promo_code
            
        response = requests.post(
            f"{self.base_url}/properties/{property_id}/calculate-pricing",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def create_booking(self, property_id, check_in, check_out, guests, guest_info, total_amount):
        """Create a booking"""
        data = {
            "property_id": property_id,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "guest_info": guest_info,
            "total_amount": total_amount
        }
        response = requests.post(
            f"{self.base_url}/bookings",
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage Example
api = KribHostDashboardAPI()

# Search properties in Dubai Marina
properties = api.search_properties(
    city="Dubai Marina",
    bedrooms=2,
    max_price_per_night=500,
    check_in="2025-03-01",
    check_out="2025-03-05"
)

print(f"Found {len(properties['data']['properties'])} properties")
```

### **JavaScript Example for Krib AI**
```javascript
class KribHostDashboardAPI {
    constructor(apiKey = 'krib_ai_test_key_12345') {
        this.apiKey = apiKey;
        this.baseURL = 'https://krib-host-dahsboard-backend.onrender.com/api/v1';
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async searchProperties(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(
            `${this.baseURL}/properties/search?${params}`,
            { headers: this.headers }
        );
        return response.json();
    }

    async getPropertyDetails(propertyId) {
        const response = await fetch(
            `${this.baseURL}/properties/${propertyId}`,
            { headers: this.headers }
        );
        return response.json();
    }

    async checkAvailability(propertyId, checkIn, checkOut, guests = 2) {
        const params = new URLSearchParams({
            check_in: checkIn,
            check_out: checkOut,
            guests: guests
        });
        const response = await fetch(
            `${this.baseURL}/properties/${propertyId}/availability?${params}`,
            { headers: this.headers }
        );
        return response.json();
    }

    async calculatePricing(propertyId, checkIn, checkOut, guests, promoCode = null) {
        const data = { check_in: checkIn, check_out: checkOut, guests };
        if (promoCode) data.promo_code = promoCode;

        const response = await fetch(
            `${this.baseURL}/properties/${propertyId}/calculate-pricing`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data)
            }
        );
        return response.json();
    }

    async createBooking(propertyId, checkIn, checkOut, guests, guestInfo, totalAmount) {
        const data = {
            property_id: propertyId,
            check_in: checkIn,
            check_out: checkOut,
            guests,
            guest_info: guestInfo,
            total_amount: totalAmount
        };

        const response = await fetch(
            `${this.baseURL}/bookings`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data)
            }
        );
        return response.json();
    }
}

// Usage
const api = new KribHostDashboardAPI();

// Search and book example
async function findAndBook() {
    // Search properties
    const properties = await api.searchProperties({
        city: 'Dubai Marina',
        bedrooms: 2,
        max_price_per_night: 500
    });

    console.log(`Found ${properties.data.properties.length} properties`);
}
```

---

## 📋 **For Krib AI Team - What You Need:**

### **1. API Access Details:**
```
Base URL: https://krib-host-dahsboard-backend.onrender.com/api/v1
API Key: krib_ai_test_key_12345
Authentication: Bearer Token
```

### **2. Key Features:**
- ✅ **Property Search**: Filter by location, price, amenities, dates
- ✅ **Real-time Availability**: Check exact dates and guest capacity  
- ✅ **Dynamic Pricing**: Calculate total cost with fees and taxes
- ✅ **Instant Booking**: Create bookings with guest information
- ✅ **UAE Focused**: Dubai, Abu Dhabi and other Emirates
- ✅ **Rate Limited**: Production-ready with proper limits

### **3. Critical Parameters:**
- ✅ **Date Format**: Use `check_in`/`check_out` (NOT `start_date`/`end_date`)
- ✅ **Pricing**: All amounts in AED (UAE Dirhams)
- ✅ **Location**: UAE Emirates and areas supported
- ✅ **Guest Info**: Full name, email, phone required for bookings

### **4. Response Format:**
All responses follow the standard format:
```json
{
  "success": true|false,
  "data": { /* response data */ },
  "message": "optional message"
}
```

---

## 🚀 **Status: PRODUCTION READY**

✅ **All endpoints tested and working**
✅ **Authentication configured**  
✅ **Error handling implemented**
✅ **Rate limiting active**
✅ **Documentation complete**

**Your short-term rental API is ready for Krib AI integration!** 🎉
