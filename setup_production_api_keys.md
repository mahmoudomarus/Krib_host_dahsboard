# 🏠 **Krib Property Platform - External API Integration Guide**

## 🎯 **Quick Start for AI Agents & External Platforms**

This guide shows you how to integrate with the Krib property rental platform to search properties, check availability, get pricing, and create bookings for your users.

---

## 🔑 **Step 1: Get Your API Key**

You'll need this API key for ALL requests:

```
krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8
```

**Important:** 
- ✅ This key is production-ready and verified working (Oct 20, 2025)
- ✅ Gives access to **171 active properties** in Dubai, UAE
- ✅ Rate limit: 200 requests per minute
- ✅ No expiration date

---

## 🌐 **Step 2: Base URL**

All API endpoints are prefixed with:

```
https://krib-host-dahsboard-backend.onrender.com
```

---

## 🔐 **Step 3: Authentication**

Every API request MUST include this authorization header:

```http
Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8
Content-Type: application/json
```

**Example in different languages:**

**cURL:**
```bash
curl -H "Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8" \
     -H "Content-Type: application/json" \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search"
```

**Python:**
```python
import requests

headers = {
    "Authorization": "Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8",
    "Content-Type": "application/json"
}

response = requests.get(
    "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search",
    headers=headers
)
```

**JavaScript/Node.js:**
```javascript
const response = await fetch(
  'https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search',
  {
    headers: {
      'Authorization': 'Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8',
      'Content-Type': 'application/json'
    }
  }
);
const data = await response.json();
```

---

## 📍 **Available API Endpoints**

### **1️⃣ Search Properties**
**Endpoint:** `GET /api/v1/properties/search`

Find properties based on location, price, dates, and more.

**Query Parameters:**
- `city` - City/area name (e.g., "Dubai Marina", "Downtown Dubai")
- `min_price_per_night` - Minimum price in AED
- `max_price_per_night` - Maximum price in AED
- `bedrooms` - Minimum number of bedrooms
- `bathrooms` - Minimum number of bathrooms
- `max_guests` - Minimum guest capacity
- `property_type` - Type (apartment, villa, studio, penthouse, townhouse)
- `check_in` - Check-in date (YYYY-MM-DD)
- `check_out` - Check-out date (YYYY-MM-DD)
- `limit` - Results per page (1-50, default: 20)
- `offset` - Pagination offset

**Example Request:**
```bash
curl -H "Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8" \
  "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search?city=Dubai%20Marina&bedrooms=2&max_price_per_night=500"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "090851a1-2cb6-4735-9561-60adb7e5fda9",
        "title": "Luxury 2BR Apartment in Dubai Marina",
        "description": "Beautiful apartment with marina views...",
        "base_price_per_night": 400.0,
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
          "coordinates": {
            "latitude": 25.0805,
            "longitude": 55.1390
          }
        },
        "amenities": ["WiFi", "Pool", "Gym", "Parking", "Beach Access"],
        "images": [
          {
            "url": "https://images.unsplash.com/photo-...",
            "is_primary": true,
            "order": 1
          }
        ],
        "check_in_time": "15:00",
        "check_out_time": "11:00",
        "minimum_nights": 1
      }
    ],
    "total_count": 171,
    "has_more": true
  }
}
```

---

### **2️⃣ Get Property Details**
**Endpoint:** `GET /api/v1/properties/{property_id}`

Get complete details about a specific property.

**Example:**
```bash
curl -H "Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8" \
  "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/090851a1-2cb6-4735-9561-60adb7e5fda9"
```

---

### **3️⃣ Check Availability**
**Endpoint:** `GET /api/v1/properties/{property_id}/availability`

Check if a property is available for specific dates.

**Query Parameters:**
- `check_in` - Check-in date (YYYY-MM-DD)
- `check_out` - Check-out date (YYYY-MM-DD)

**Example:**
```bash
curl -H "Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8" \
  "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/090851a1-2cb6-4735-9561-60adb7e5fda9/availability?check_in=2025-11-01&check_out=2025-11-05"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "available": true,
    "property_id": "090851a1-2cb6-4735-9561-60adb7e5fda9",
    "check_in": "2025-11-01",
    "check_out": "2025-11-05",
    "nights": 4
  }
}
```

---

### **4️⃣ Calculate Pricing**
**Endpoint:** `GET /api/v1/properties/{property_id}/pricing`

Get total price for a stay including all fees.

**Query Parameters:**
- `check_in` - Check-in date (YYYY-MM-DD)
- `check_out` - Check-out date (YYYY-MM-DD)
- `guests` - Number of guests

**Example:**
```bash
curl -H "Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8" \
  "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/090851a1-2cb6-4735-9561-60adb7e5fda9/pricing?check_in=2025-11-01&check_out=2025-11-05&guests=2"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subtotal": 1600.0,
    "service_fee": 160.0,
    "cleaning_fee": 100.0,
    "total": 1860.0,
    "currency": "AED",
    "breakdown": [
      {
        "description": "400 AED x 4 nights",
        "amount": 1600.0
      },
      {
        "description": "Service fee",
        "amount": 160.0
      },
      {
        "description": "Cleaning fee",
        "amount": 100.0
      }
    ]
  }
}
```

---

### **5️⃣ Create Booking**
**Endpoint:** `POST /api/v1/external/bookings`

Create a booking for a user.

**Request Body:**
```json
{
  "property_id": "090851a1-2cb6-4735-9561-60adb7e5fda9",
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "guest_phone": "+971501234567",
  "check_in": "2025-11-01",
  "check_out": "2025-11-05",
  "number_of_guests": 2,
  "total_price": 1860.0,
  "special_requests": "Early check-in if possible"
}
```

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer krib_prod_c4323aa1d8896254316e396995bf7f6fffacdaa8985ec09da4067da37f1e6ae8" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "090851a1-2cb6-4735-9561-60adb7e5fda9",
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "check_in": "2025-11-01",
    "check_out": "2025-11-05",
    "number_of_guests": 2,
    "total_price": 1860.0
  }' \
  "https://krib-host-dahsboard-backend.onrender.com/api/v1/external/bookings"
```

---

## 📊 **API Limits & Guidelines**

| Item | Value |
|------|-------|
| **Rate Limit** | 200 requests/minute |
| **Response Format** | JSON |
| **Authentication** | Bearer token (required for all endpoints) |
| **Total Properties** | 171 active properties |
| **Locations** | Dubai, UAE (all areas) |
| **Price Range** | 100 - 2000 AED per night |
| **Property Types** | Apartment, Villa, Studio, Penthouse, Townhouse |

---

## ⚠️ **Error Handling**

**Common Error Responses:**

**401 Unauthorized** - Invalid or missing API key
```json
{
  "detail": "Invalid API key"
}
```

**404 Not Found** - Property doesn't exist
```json
{
  "detail": "Property not found or not available"
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## 🎯 **Integration Checklist**

- [ ] Add API key to your application configuration
- [ ] Test property search with filters
- [ ] Test getting property details
- [ ] Test availability check
- [ ] Test pricing calculation
- [ ] Test creating a booking
- [ ] Implement error handling for 401, 404, 429
- [ ] Monitor rate limits (check response headers)

---

## 📞 **Support**

- **API Status**: ✅ Live and operational (verified Oct 20, 2025)
- **Properties**: 171 active listings in Dubai
- **Images**: All properties have 3-5 high-quality images
- **Last Updated**: October 20, 2025
