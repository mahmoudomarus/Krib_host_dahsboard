"""
External API Configuration
Configuration for third-party integrations and API keys

This module manages API keys and permissions for external AI agent platforms
that integrate with the Krib Host Dashboard.

API keys are stored securely in the database (hashed) and validated at runtime.
NO KEYS ARE STORED IN CODE.

Environment Variables:
- RATE_LIMIT_AI_AGENT: Requests per minute for AI agents (default: 200)
- RATE_LIMIT_DEFAULT: Default rate limit (default: 60)
"""

import os
from typing import List


class ExternalAPIConfig:
    """
    Configuration for external API integrations

    NOTE: API keys are NOT stored in this config.
    They are stored in the database (api_keys table) and validated via APIKeyService.
    """

    # Rate limits per minute
    RATE_LIMITS = {
        "default": int(os.getenv("RATE_LIMIT_DEFAULT", "60")),
        "standard": int(os.getenv("RATE_LIMIT_STANDARD", "100")),
        "premium": int(os.getenv("RATE_LIMIT_PREMIUM", "200")),
    }

    # Permission definitions
    ALL_PERMISSIONS = [
        # Property operations
        "read_properties",
        "read_property_details",
        "read_availability",
        "calculate_pricing",
        # Booking operations
        "create_bookings",
        "read_bookings",
        "update_booking_status",
        "process_payments",
        # Host information (public only)
        "read_host_profile",
        # Messaging operations
        "send_messages",
        "read_messages",
        "create_conversations",
        # Reviews
        "read_reviews",
        # Webhooks
        "receive_webhooks",
    ]

    # Permission sets for different tiers
    PERMISSION_TIERS = {
        "read_only": [
            "read_properties",
            "read_property_details",
            "read_availability",
            "calculate_pricing",
            "read_host_profile",
            "read_reviews",
        ],
        "standard": [
            "read_properties",
            "read_property_details",
            "read_availability",
            "calculate_pricing",
            "read_host_profile",
            "read_reviews",
            "send_messages",
            "read_messages",
            "create_conversations",
        ],
        "full_access": [
            "read_properties",
            "read_property_details",
            "read_availability",
            "calculate_pricing",
            "read_host_profile",
            "read_reviews",
            "send_messages",
            "read_messages",
            "create_conversations",
            "create_bookings",
            "read_bookings",
            "update_booking_status",
            "process_payments",
            "receive_webhooks",
        ],
    }

    @classmethod
    def get_rate_limit(cls, tier: str = "default") -> int:
        """Get rate limit for a specific tier"""
        return cls.RATE_LIMITS.get(tier, cls.RATE_LIMITS["default"])

    @classmethod
    def get_all_permissions(cls) -> List[str]:
        """Get list of all available permissions"""
        return cls.ALL_PERMISSIONS

    @classmethod
    def get_tier_permissions(cls, tier: str) -> List[str]:
        """Get permissions for a specific tier"""
        return cls.PERMISSION_TIERS.get(tier, cls.PERMISSION_TIERS["read_only"])

    @classmethod
    def validate_permission(
        cls, permissions: List[str], required_permission: str
    ) -> bool:
        """Check if a permission list includes the required permission"""
        return required_permission in permissions
