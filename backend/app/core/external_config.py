"""
External API Configuration
Configuration for third-party integrations and API keys
"""

import os
from typing import Dict, List


class ExternalAPIConfig:
    """Configuration for external API integrations"""
    
    # Production API Keys (load from environment)
    PRODUCTION_API_KEYS = {
        "krib_ai_agent": os.getenv("KRIB_AI_AGENT_API_KEY"),
        "chatgpt_agent": os.getenv("CHATGPT_AGENT_API_KEY"),
        "claude_agent": os.getenv("CLAUDE_AGENT_API_KEY"),
        "booking_service": os.getenv("BOOKING_SERVICE_API_KEY"),
    }
    
    # Development/Test API Keys
    TEST_API_KEYS = {
        "krib_ai_agent": "krib_ai_test_key_12345",
        "chatgpt_agent": "chatgpt_test_key_67890", 
        "claude_agent": "claude_test_key_abcde",
        "booking_service": "booking_test_key_fghij",
    }
    
    # API Key Permissions
    API_PERMISSIONS = {
        "krib_ai_agent": [
            "read_properties",
            "create_bookings", 
            "read_availability",
            "calculate_pricing",
            "read_property_details"
        ],
        "chatgpt_agent": [
            "read_properties",
            "read_availability", 
            "calculate_pricing"
        ],
        "claude_agent": [
            "read_properties",
            "read_availability",
            "calculate_pricing"
        ],
        "booking_service": [
            "read_properties",
            "create_bookings",
            "read_availability",
            "calculate_pricing"
        ]
    }
    
    # Rate Limits per service (requests per minute)
    RATE_LIMITS = {
        "krib_ai_agent": 200,
        "chatgpt_agent": 100,
        "claude_agent": 100, 
        "booking_service": 150,
        "default": 60
    }
    
    @classmethod
    def get_api_keys(cls) -> Dict[str, str]:
        """Get API keys based on environment"""
        is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
        
        if is_production:
            # Filter out None values from production keys
            return {k: v for k, v in cls.PRODUCTION_API_KEYS.items() if v is not None}
        else:
            return cls.TEST_API_KEYS
    
    @classmethod
    def get_service_permissions(cls, service_name: str) -> List[str]:
        """Get permissions for a specific service"""
        return cls.API_PERMISSIONS.get(service_name, [])
    
    @classmethod
    def get_rate_limit(cls, service_name: str) -> int:
        """Get rate limit for a specific service"""
        return cls.RATE_LIMITS.get(service_name, cls.RATE_LIMITS["default"])
    
    @classmethod
    def is_valid_api_key(cls, api_key: str) -> tuple[bool, str]:
        """Check if API key is valid and return service name"""
        api_keys = cls.get_api_keys()
        
        for service_name, key in api_keys.items():
            if key == api_key:
                return True, service_name
        
        return False, ""
    
    @classmethod
    def validate_permission(cls, service_name: str, permission: str) -> bool:
        """Check if service has specific permission"""
        service_permissions = cls.get_service_permissions(service_name)
        return permission in service_permissions


# Example usage and deployment instructions
DEPLOYMENT_INSTRUCTIONS = """
🔐 EXTERNAL API KEYS SETUP

1. For Production Deployment:
   Add these environment variables to your deployment platform (Render, Heroku, etc.):
   
   KRIB_AI_AGENT_API_KEY=your_secure_production_key_here
   CHATGPT_AGENT_API_KEY=your_chatgpt_integration_key
   CLAUDE_AGENT_API_KEY=your_claude_integration_key
   BOOKING_SERVICE_API_KEY=your_booking_service_key
   ENVIRONMENT=production

2. For Development:
   Add to your .env file:
   
   ENVIRONMENT=development
   # Test keys will be used automatically

3. Generate Secure API Keys:
   Use tools like: openssl rand -hex 32
   Or online generators with sufficient entropy

4. API Key Format Recommendation:
   service_environment_purpose_random
   Example: krib_prod_api_a1b2c3d4e5f6...

5. Security Best Practices:
   - Rotate keys quarterly
   - Use different keys per environment
   - Monitor usage and set alerts
   - Implement key expiration if needed
"""

print(DEPLOYMENT_INSTRUCTIONS)
