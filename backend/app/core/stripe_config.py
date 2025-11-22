"""
Stripe Configuration
Manages Stripe API keys and platform settings
"""

import os
import stripe
from typing import Optional


class StripeConfig:
    """Stripe configuration and initialization"""

    # Stripe API Keys (load from environment variables)
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Platform settings
    PLATFORM_FEE_PERCENTAGE: float = float(os.getenv("PLATFORM_FEE_PERCENTAGE", "15.0"))
    CURRENCY: str = os.getenv("CURRENCY", "AED")

    # Payout settings
    PAYOUT_DELAY_DAYS: int = int(
        os.getenv("PAYOUT_DELAY_DAYS", "1")
    )  # Days after checkout before payout

    # Connect settings
    CONNECT_REFRESH_URL: str = os.getenv(
        "CONNECT_REFRESH_URL", "https://host.krib.ae/dashboard/financials"
    )
    CONNECT_RETURN_URL: str = os.getenv(
        "CONNECT_RETURN_URL", "https://host.krib.ae/dashboard/financials"
    )

    # API version
    STRIPE_API_VERSION: str = "2024-10-28.acacia"

    @classmethod
    def initialize(cls):
        """Initialize Stripe with API key"""
        if not cls.STRIPE_SECRET_KEY:
            print(
                "[STRIPE] WARNING: STRIPE_SECRET_KEY not configured, payment features disabled"
            )
            return

        if cls.STRIPE_SECRET_KEY.startswith("sk_test"):
            print("[STRIPE] Initialized in TEST mode")
        elif cls.STRIPE_SECRET_KEY.startswith("sk_live"):
            print("[STRIPE] Initialized in LIVE mode")
        else:
            print("[STRIPE] WARNING: Invalid key format detected")

        stripe.api_key = cls.STRIPE_SECRET_KEY
        stripe.api_version = cls.STRIPE_API_VERSION
        print(f"[STRIPE] API initialized, key prefix: {cls.STRIPE_SECRET_KEY[:12]}")

    @classmethod
    def is_test_mode(cls) -> bool:
        """Check if using test mode keys"""
        return cls.STRIPE_SECRET_KEY.startswith("sk_test_")


# Initialize Stripe on module import
StripeConfig.initialize()
