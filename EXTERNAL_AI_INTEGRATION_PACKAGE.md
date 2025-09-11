# 🚀 **Krib AI Platform - External Agent Integration Package**

## 📋 **Integration Essentials**

### **1. 🔑 API Keys & Authentication**

**Production API Base URL:**
```
https://your-backend-domain.com/api/v1/external/
```

**API Key Authentication:**
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Webhook Secret for Signature Verification:**
```
Webhook-Secret: your-webhook-secret-key
```

### **2. 📚 Complete API Documentation**

#### **Property Search & Booking APIs:**
- `GET /properties/search` - Search available properties
- `GET /properties/{id}` - Get property details
- `GET /properties/{id}/availability` - Check availability
- `GET /properties/{id}/pricing` - Get pricing info
- `POST /bookings` - Create new booking

#### **Webhook Management APIs:**
- `POST /webhook-subscriptions` - Register your webhooks
- `GET /webhook-subscriptions` - List your subscriptions
- `PUT /webhook-subscriptions/{id}` - Update subscription
- `DELETE /webhook-subscriptions/{id}` - Remove subscription

#### **Booking Management APIs:**
- `GET /hosts/{host_id}/pending-bookings` - Get pending bookings
- `PUT /bookings/{booking_id}/status` - Update booking status
- `POST /bookings/{booking_id}/auto-approve` - Auto-approve booking
- `GET /bookings/{booking_id}/status` - Get booking status

### **3. 🔗 Webhook Events**

**Supported Events:**
- `booking.created` - New booking created
- `booking.confirmed` - Booking confirmed by host
- `booking.cancelled` - Booking cancelled
- `payment.received` - Payment processed
- `host.response_needed` - Host action required

**Webhook Payload Example:**
```json
{
  "event": "booking.created",
  "timestamp": "2025-01-10T15:30:00Z",
  "data": {
    "booking_id": "uuid",
    "property_id": "uuid",
    "host_id": "uuid",
    "guest_info": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    },
    "check_in": "2025-02-01",
    "check_out": "2025-02-05",
    "total_amount": 1200.00,
    "status": "pending"
  },
  "signature": "hmac-sha256-signature"
}
```

### **4. 🧪 Testing Environment**

**Staging Base URL:**
```
https://your-staging-backend.com/api/v1/external/
```

**Test API Key:**
```
test_api_key_for_staging
```

**Test Webhook URL for Validation:**
```
POST /webhooks/test
```

### **5. ⚡ Rate Limiting Rules**

**Current Limits:**
- **Property Search**: 100 requests/minute
- **Booking Creation**: 20 requests/minute  
- **Webhook Delivery**: 50 requests/minute
- **Availability Checks**: 200 requests/minute

**Headers Returned:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641891600
```

### **6. 📊 Error Codes & Handling**

**Standard HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": {
    "code": "PROPERTY_NOT_FOUND",
    "message": "Property with ID xxx not found",
    "details": "Additional context if needed"
  }
}
```

### **7. 🔄 Integration Workflow**

1. **Register for API Access** → Get API key
2. **Setup Webhook Endpoint** → Register webhook URL
3. **Test Integration** → Use staging environment
4. **Go Live** → Switch to production endpoints
5. **Monitor** → Check webhook delivery stats

### **8. 🛠️ Code Examples**

**Python Integration:**
```python
import requests
import hmac
import hashlib

# API Setup
API_BASE = "https://your-backend.com/api/v1/external"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Search Properties
response = requests.get(f"{API_BASE}/properties/search", 
                       params={"location": "Dubai", "guests": 2}, 
                       headers=headers)

# Register Webhook
webhook_data = {
    "agent_name": "YourAI",
    "webhook_url": "https://your-ai.com/webhooks/krib",
    "events": ["booking.created", "booking.confirmed"],
    "secret_key": "your-webhook-secret"
}
requests.post(f"{API_BASE}/webhook-subscriptions", 
              json=webhook_data, headers=headers)
```

**JavaScript Integration:**
```javascript
const KRIB_API = {
  baseURL: 'https://your-backend.com/api/v1/external',
  apiKey: 'your-api-key',
  
  async searchProperties(location, guests) {
    const response = await fetch(`${this.baseURL}/properties/search?location=${location}&guests=${guests}`, {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  },
  
  async createBooking(bookingData) {
    const response = await fetch(`${this.baseURL}/bookings`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(bookingData)
    });
    return response.json();
  }
};
```

---

## 🚀 **Ready for Integration**

✅ **All external API endpoints are LIVE and production-ready**
✅ **Webhook system fully operational with retry logic**
✅ **Comprehensive documentation and examples provided**
✅ **Testing environment available for validation**
✅ **Rate limiting clearly defined**

**Contact**: Contact Krib team for API keys and webhook secrets
**Support**: Technical integration support available
**SLA**: 99.9% uptime with automatic failover

