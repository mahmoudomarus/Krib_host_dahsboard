"""
External API Configuration
Configuration for third-party integrations and API keys
"""

import os
from typing import Dict, List


class ExternalAPIConfig:
    """Configuration for external API integrations"""

    PRODUCTION_API_KEY = os.getenv("KRIB_AI_AGENT_API_KEY", "")

    # Valid API Keys
    VALID_API_KEYS = {
        "krib_ai_agent": PRODUCTION_API_KEY,
    }

    # API Key Permissions
    API_PERMISSIONS = {
        "krib_ai_agent": [
            "read_properties",
            "create_bookings",
            "read_availability",
            "calculate_pricing",
            "read_property_details",
        ]
    }

    RATE_LIMITS = {
        "krib_ai_agent": int(os.getenv("RATE_LIMIT_AI_AGENT", "200")),
        "default": int(os.getenv("RATE_LIMIT_DEFAULT", "60")),
    }

    @classmethod
    def get_api_keys(cls) -> Dict[str, str]:
        """Get all valid API keys"""
        return cls.VALID_API_KEYS

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
