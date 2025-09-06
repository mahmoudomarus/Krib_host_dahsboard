# 🔐 Krib AI Production Setup Instructions

## 🎯 **For Production Deployment**

### **Step 1: Generate Production API Key**
Create a secure production API key (32+ characters, random):
```bash
# Example production key (generate your own):
KRIB_AI_AGENT_API_KEY=krib_ai_prod_2025_secure_random_key_xyz789abc123def456
```

### **Step 2: Add to Render Environment Variables**
In your Render backend dashboard, add:
```bash
KRIB_AI_AGENT_API_KEY=your_generated_production_key_here
ENVIRONMENT=production
```

### **Step 3: Provide to Krib AI Team**
Give Krib AI team these production details:
```bash
# Production API Access
BASE_URL: https://krib-host-dahsboard-backend.onrender.com/api/v1
API_KEY: your_generated_production_key_here
ENVIRONMENT: production
```

---

## 📋 **Quick Reference for Krib AI**

### **✅ Ready-to-Use Endpoints:**
```
GET  /api/v1/properties/search
GET  /api/v1/properties/{id}
GET  /api/v1/properties/{id}/availability  
POST /api/v1/properties/{id}/calculate-pricing
POST /api/v1/bookings
```

### **✅ Authentication:**
```
Authorization: Bearer your_api_key_here
```

### **✅ Critical Parameters:**
```
✓ Use check_in/check_out (not start_date/end_date)
✓ All prices in AED
✓ UAE locations (Dubai, Abu Dhabi, etc.)
✓ Rate limits: 50-200 req/min per endpoint
```

### **✅ Test Commands:**
```bash
# Test with production key
curl -H "Authorization: Bearer YOUR_PRODUCTION_KEY" \
     "https://krib-host-dahsboard-backend.onrender.com/api/v1/properties/search?city=Dubai"
```

---

## 🚀 **Status: READY FOR INTEGRATION**

Your short-term rental platform is production-ready for Krib AI integration!
