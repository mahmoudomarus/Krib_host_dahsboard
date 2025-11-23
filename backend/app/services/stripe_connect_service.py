"""
Stripe Connect Service
Handles Stripe Connect Express account creation, onboarding, and management for hosts
"""

import stripe
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from app.core.stripe_config import StripeConfig
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class StripeConnectService:
    """Service for managing Stripe Connect Express accounts"""

    @staticmethod
    async def create_connect_account(
        user_id: str,
        email: str,
        country: str = "AE",
        business_type: str = "company",  # UAE requires 'company'
    ) -> Dict[str, Any]:
        """
        Create a Stripe Connect Express account for a host

        Args:
            user_id: UUID of the host user
            email: Host's email address
            country: ISO country code (default: AE for UAE)
            business_type: Type of business (individual or company)

        Returns:
            Dictionary with stripe_account_id and status
        """
        try:
            # Check if user already has a Stripe account
            user_result = (
                supabase_client.table("users")
                .select("stripe_account_id, email, name")
                .eq("id", user_id)
                .execute()
            )

            if not user_result.data:
                raise ValueError(f"User {user_id} not found")

            user = user_result.data[0]

            # If account exists, verify it's still valid
            if user.get("stripe_account_id"):
                logger.info(
                    f"User {user_id} already has Stripe account: {user['stripe_account_id']}"
                )
                try:
                    status = await StripeConnectService.get_account_status(user_id)
                    # If status is "not_connected", the account was invalid and cleared
                    if status.get("status") != "not_connected":
                        return status
                    # Otherwise, continue to create a new account
                    logger.info(
                        f"Creating new Stripe account for user {user_id} (previous was invalid)"
                    )
                except Exception as e:
                    logger.warning(
                        f"Error checking existing account status: {e}. Creating new account."
                    )

            # Create Stripe Connect Express account
            logger.info(
                f"Creating Stripe Express account for user {user_id}, email {email}, country {country}"
            )

            # For UAE (AE), Express accounts can only receive transfers from platform
            # Platform account collects payments, then transfers to Express accounts
            # card_payments is NOT supported for UAE Express accounts
            capabilities = {}
            if country == "AE":
                # UAE: Only transfers capability (platform collects, transfers to host)
                capabilities = {"transfers": {"requested": True}}
                logger.info(f"UAE account detected - using transfers-only capability")
            else:
                # Other countries: Can accept card payments directly
                capabilities = {
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                }

            try:
                account = stripe.Account.create(
                    type="express",
                    country=country,
                    email=email,
                    business_type=business_type,
                    capabilities=capabilities,
                    settings={
                        "payouts": {
                            "schedule": {
                                "interval": "manual"  # We control payouts via API
                            }
                        }
                    },
                    metadata={"user_id": user_id, "platform": "krib_host_dashboard"},
                )
            except stripe.error.StripeError as e:
                logger.error(f"Stripe API error creating account: {str(e)}")
                raise ValueError(f"Stripe error: {str(e)}")

            logger.info(
                f"Created Stripe Connect account {account.id} for user {user_id}"
            )

            # Update user record with Stripe account ID
            supabase_client.table("users").update(
                {
                    "stripe_account_id": account.id,
                    "stripe_account_status": "pending",
                    "stripe_charges_enabled": account.charges_enabled,
                    "stripe_payouts_enabled": account.payouts_enabled,
                    "stripe_details_submitted": account.details_submitted,
                    "stripe_updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", user_id).execute()

            return {
                "stripe_account_id": account.id,
                "status": "pending",
                "charges_enabled": account.charges_enabled,
                "payouts_enabled": account.payouts_enabled,
                "details_submitted": account.details_submitted,
            }

        except stripe.StripeError as e:
            logger.error(f"Stripe error creating account for user {user_id}: {e}")
            raise Exception(f"Failed to create Stripe account: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating Connect account for user {user_id}: {e}")
            raise

    @staticmethod
    async def create_account_link(
        user_id: str,
        refresh_url: Optional[str] = None,
        return_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an Account Link for host onboarding

        Args:
            user_id: UUID of the host user
            refresh_url: URL to redirect if link expires
            return_url: URL to redirect after completion

        Returns:
            Dictionary with onboarding URL and expiration
        """
        try:
            # Get user's Stripe account ID
            user_result = (
                supabase_client.table("users")
                .select("stripe_account_id")
                .eq("id", user_id)
                .execute()
            )

            if not user_result.data or not user_result.data[0].get("stripe_account_id"):
                raise ValueError(
                    f"User {user_id} does not have a Stripe account. Create account first."
                )

            stripe_account_id = user_result.data[0]["stripe_account_id"]

            # Create account link
            try:
                account_link = stripe.AccountLink.create(
                    account=stripe_account_id,
                    refresh_url=refresh_url or StripeConfig.CONNECT_REFRESH_URL,
                    return_url=return_url or StripeConfig.CONNECT_RETURN_URL,
                    type="account_onboarding",
                )
            except stripe.error.PermissionError as e:
                # Account belongs to different API keys
                logger.error(
                    f"Stripe account {stripe_account_id} not accessible with current keys. "
                    f"Clearing invalid account. Error: {e}"
                )
                # Clear invalid account ID
                supabase_client.table("users").update(
                    {"stripe_account_id": None, "stripe_account_status": None}
                ).eq("id", user_id).execute()
                raise ValueError(
                    "Your Stripe account is no longer valid. Please create a new account."
                )

            logger.info(f"Created onboarding link for account {stripe_account_id}")

            return {
                "url": account_link.url,
                "expires_at": account_link.expires_at,
                "created": account_link.created,
            }

        except stripe.StripeError as e:
            logger.error(f"Stripe error creating account link for user {user_id}: {e}")
            raise Exception(f"Failed to create onboarding link: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating account link for user {user_id}: {e}")
            raise

    @staticmethod
    async def get_account_status(user_id: str) -> Dict[str, Any]:
        """
        Get current status of host's Stripe Connect account

        Args:
            user_id: UUID of the host user

        Returns:
            Dictionary with account status and requirements
        """
        try:
            # Get user's Stripe account ID
            user_result = (
                supabase_client.table("users")
                .select(
                    "stripe_account_id, stripe_account_status, stripe_charges_enabled, "
                    "stripe_payouts_enabled, stripe_details_submitted, stripe_onboarding_completed, "
                    "bank_account_last4, bank_account_country, stripe_requirements, stripe_updated_at"
                )
                .eq("id", user_id)
                .execute()
            )

            if not user_result.data:
                raise ValueError(f"User {user_id} not found")

            user = user_result.data[0]

            if not user.get("stripe_account_id"):
                return {
                    "status": "not_connected",
                    "charges_enabled": False,
                    "payouts_enabled": False,
                    "details_submitted": False,
                    "onboarding_completed": False,
                }

            # Fetch fresh data from Stripe
            stripe_account_id = user["stripe_account_id"]

            try:
                account = stripe.Account.retrieve(stripe_account_id)
            except stripe.error.PermissionError as e:
                # Account belongs to different API keys (e.g., switched from test to live)
                logger.warning(
                    f"Stripe account {stripe_account_id} not accessible with current keys "
                    f"for user {user_id}. Clearing invalid account ID. Error: {e}"
                )
                # Clear invalid Stripe account data
                supabase_client.table("users").update(
                    {
                        "stripe_account_id": None,
                        "stripe_account_status": None,
                        "stripe_charges_enabled": False,
                        "stripe_payouts_enabled": False,
                        "stripe_details_submitted": False,
                        "stripe_onboarding_completed": False,
                        "bank_account_last4": None,
                        "bank_account_country": None,
                        "stripe_requirements": None,
                        "stripe_updated_at": datetime.utcnow().isoformat(),
                    }
                ).eq("id", user_id).execute()

                return {
                    "status": "not_connected",
                    "charges_enabled": False,
                    "payouts_enabled": False,
                    "details_submitted": False,
                    "onboarding_completed": False,
                }

            # Determine overall status
            if account.charges_enabled and account.payouts_enabled:
                status = "active"
            elif account.details_submitted:
                status = "pending"
            else:
                status = "pending"

            # Check if restricted
            if (
                hasattr(account, "requirements")
                and account.requirements.disabled_reason
            ):
                status = "restricted"

            # Extract bank account info if available
            bank_last4 = None
            bank_country = None
            if hasattr(account, "external_accounts") and account.external_accounts.data:
                bank_account = account.external_accounts.data[0]
                if bank_account.object == "bank_account":
                    bank_last4 = bank_account.last4
                    bank_country = bank_account.country

            # Extract requirements
            requirements = {"currently_due": [], "eventually_due": [], "past_due": []}
            if hasattr(account, "requirements"):
                requirements = {
                    "currently_due": account.requirements.currently_due or [],
                    "eventually_due": account.requirements.eventually_due or [],
                    "past_due": account.requirements.past_due or [],
                }

            # Update database with fresh data
            supabase_client.table("users").update(
                {
                    "stripe_account_status": status,
                    "stripe_charges_enabled": account.charges_enabled,
                    "stripe_payouts_enabled": account.payouts_enabled,
                    "stripe_details_submitted": account.details_submitted,
                    "stripe_onboarding_completed": account.charges_enabled
                    and account.payouts_enabled,
                    "bank_account_last4": bank_last4,
                    "bank_account_country": bank_country,
                    "stripe_requirements": requirements,
                    "stripe_updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", user_id).execute()

            return {
                "stripe_account_id": stripe_account_id,
                "status": status,
                "charges_enabled": account.charges_enabled,
                "payouts_enabled": account.payouts_enabled,
                "details_submitted": account.details_submitted,
                "onboarding_completed": account.charges_enabled
                and account.payouts_enabled,
                "bank_account_last4": bank_last4,
                "bank_account_country": bank_country,
                "requirements": requirements,
                "updated_at": datetime.utcnow().isoformat(),
            }

        except stripe.StripeError as e:
            logger.error(f"Stripe error getting account status for user {user_id}: {e}")
            raise Exception(f"Failed to get account status: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting account status for user {user_id}: {e}")
            raise

    @staticmethod
    async def create_login_link(user_id: str) -> Dict[str, Any]:
        """
        Create a login link to Stripe Express Dashboard for host

        Args:
            user_id: UUID of the host user

        Returns:
            Dictionary with dashboard URL
        """
        try:
            # Get user's Stripe account ID
            user_result = (
                supabase_client.table("users")
                .select("stripe_account_id")
                .eq("id", user_id)
                .execute()
            )

            if not user_result.data or not user_result.data[0].get("stripe_account_id"):
                raise ValueError(f"User {user_id} does not have a Stripe account")

            stripe_account_id = user_result.data[0]["stripe_account_id"]

            # Create login link
            try:
                login_link = stripe.Account.create_login_link(stripe_account_id)
            except stripe.error.PermissionError as e:
                # Account belongs to different API keys
                logger.error(
                    f"Stripe account {stripe_account_id} not accessible with current keys. "
                    f"Clearing invalid account. Error: {e}"
                )
                # Clear invalid account ID
                supabase_client.table("users").update(
                    {"stripe_account_id": None, "stripe_account_status": None}
                ).eq("id", user_id).execute()
                raise ValueError(
                    "Your Stripe account is no longer valid. Please create a new account."
                )

            logger.info(f"Created dashboard login link for account {stripe_account_id}")

            return {"url": login_link.url, "created": login_link.created}

        except stripe.StripeError as e:
            logger.error(f"Stripe error creating login link for user {user_id}: {e}")
            raise Exception(f"Failed to create dashboard link: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating login link for user {user_id}: {e}")
            raise

    @staticmethod
    async def handle_account_updated_webhook(
        account_id: str, account_data: Dict[str, Any]
    ) -> None:
        """
        Handle account.updated webhook event

        Args:
            account_id: Stripe account ID
            account_data: Account data from webhook
        """
        try:
            # Find user with this Stripe account
            user_result = (
                supabase_client.table("users")
                .select("id")
                .eq("stripe_account_id", account_id)
                .execute()
            )

            if not user_result.data:
                logger.warning(f"No user found with Stripe account {account_id}")
                return

            user_id = user_result.data[0]["id"]

            # Update account status
            await StripeConnectService.get_account_status(user_id)

            logger.info(f"Updated account status for user {user_id} from webhook")

        except Exception as e:
            logger.error(
                f"Error handling account.updated webhook for {account_id}: {e}"
            )
            raise


stripe_connect_service = StripeConnectService()
