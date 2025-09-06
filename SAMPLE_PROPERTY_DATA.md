# 🏠 Sample Property IDs for Testing Krib AI Integration

## 📋 **Test Property IDs**

Here are 10 sample property IDs you can use for testing all endpoints:

### **Dubai Marina Properties**
```
1. prop_marina_luxury_001
2. prop_marina_studio_002
3. prop_marina_penthouse_003
```

### **Downtown Dubai Properties**
```
4. prop_downtown_apt_004
5. prop_downtown_loft_005
6. prop_burj_view_006
```

### **Palm Jumeirah Properties**
```
7. prop_palm_villa_007
8. prop_palm_apt_008
```

### **Business Bay Properties**
```
9. prop_business_suite_009
10. prop_business_tower_010
```

---

## 🧪 **Test Commands with Sample IDs**

### **Property Details Test**
```bash
curl -H "Authorization: Bearer krib_ai_test_key_12345" \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_marina_luxury_001"
```

### **Availability Test**
```bash
curl -H "Authorization: Bearer krib_ai_test_key_12345" \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_marina_luxury_001/availability?check_in=2025-03-01&check_out=2025-03-05&guests=2"
```

### **Pricing Test**
```bash
curl -X POST \
     -H "Authorization: Bearer krib_ai_test_key_12345" \
     -H "Content-Type: application/json" \
     -d '{"check_in": "2025-03-01", "check_out": "2025-03-05", "guests": 2}' \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/prop_marina_luxury_001/calculate-pricing"
```

### **Booking Test**
```bash
curl -X POST \
     -H "Authorization: Bearer krib_ai_test_key_12345" \
     -H "Content-Type: application/json" \
     -d '{
       "property_id": "prop_marina_luxury_001",
       "check_in": "2025-03-01",
       "check_out": "2025-03-05",
       "guests": 2,
       "guest_info": {
         "first_name": "John",
         "last_name": "Doe",
         "email": "john@example.com",
         "phone": "+971501234567"
       },
       "total_amount": 1800.00
     }' \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/bookings"
```

---

## 📊 **Expected Test Results**

Since these are sample IDs (no real properties yet), you'll get:

### **Property Details/Availability/Pricing:**
```json
{"detail": "Failed to verify property access"}
```
*This is expected - confirms error handling works correctly*

### **Property Search:**
```json
{
  "success": true,
  "data": {
    "properties": [],
    "total_count": 0
  }
}
```
*This confirms search endpoint works but database is empty*

### **Rate Limit Headers (New!):**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 60
X-RateLimit-Service: krib_ai_agent
```

---

## 🎯 **Ready for Real Data**

Once you add real properties to your database, these endpoints will return actual property data instead of error messages. The API structure is fully ready for integration!
