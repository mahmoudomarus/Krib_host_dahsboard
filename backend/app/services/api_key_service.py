"""
API Key Service
Manages API key generation, validation, and revocation for external platforms.

Security:
- Keys are generated using cryptographically secure random bytes
- Only the SHA-256 hash is stored in the database
- The actual key is shown ONCE to the user and never stored
- Keys can be revoked at any time
"""

import secrets
import hashlib
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from app.core.supabase_client import supabase_client
from app.core.external_config import ExternalAPIConfig

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for managing external API keys"""

    # Key format: krib_{env}_{32_random_chars}
    KEY_PREFIX_LENGTH = 12  # e.g., "krib_prod_a1"
    KEY_RANDOM_LENGTH = 32  # Random part length

    @classmethod
    def generate_key(
        cls,
        name: str,
        description: Optional[str] = None,
        tier: str = "standard",
        permissions: Optional[List[str]] = None,
        rate_limit: int = 100,
        created_by: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        environment: str = "prod",
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a new API key

        Returns:
            Tuple of (plain_text_key, key_record)

        The plain_text_key is returned ONLY ONCE and should be shown to the user.
        It will NEVER be retrievable again.
        """
        try:
            # Generate secure random key
            random_part = secrets.token_hex(cls.KEY_RANDOM_LENGTH // 2)
            full_key = f"krib_{environment}_{random_part}"

            # Create prefix for display
            key_prefix = full_key[: cls.KEY_PREFIX_LENGTH]

            # Hash the key for storage
            key_hash = hashlib.sha256(full_key.encode()).hexdigest()

            # Get permissions for tier if not provided
            if permissions is None:
                permissions = ExternalAPIConfig.get_tier_permissions(tier)

            # Calculate expiration
            expires_at = None
            if expires_in_days:
                expires_at = (
                    datetime.utcnow() + timedelta(days=expires_in_days)
                ).isoformat()

            # Create database record
            key_record = {
                "key_prefix": key_prefix,
                "key_hash": key_hash,
                "name": name,
                "description": description,
                "permissions": permissions,
                "tier": tier,
                "rate_limit_per_minute": rate_limit,
                "created_by": created_by,
                "expires_at": expires_at,
                "is_active": True,
            }

            result = supabase_client.table("api_keys").insert(key_record).execute()

            if not result.data:
                raise Exception("Failed to create API key record")

            created_record = result.data[0]

            logger.info(f"API key created: {key_prefix}... for '{name}'")

            # Return the plain key (shown ONCE) and the record
            return full_key, {
                "id": created_record["id"],
                "key_prefix": key_prefix,
                "name": name,
                "description": description,
                "tier": tier,
                "permissions": permissions,
                "rate_limit_per_minute": rate_limit,
                "expires_at": expires_at,
                "created_at": created_record["created_at"],
            }

        except Exception as e:
            logger.error(f"Failed to generate API key: {e}")
            raise

    @classmethod
    def validate_key(cls, api_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate an API key

        Returns:
            Tuple of (is_valid, key_info)
            key_info contains permissions, tier, rate_limit if valid
        """
        try:
            # Hash the provided key
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            # Look up in database
            result = (
                supabase_client.table("api_keys")
                .select("*")
                .eq("key_hash", key_hash)
                .eq("is_active", True)
                .execute()
            )

            if not result.data:
                return False, None

            key_record = result.data[0]

            # Check if expired
            if key_record.get("expires_at"):
                expires_at = datetime.fromisoformat(
                    key_record["expires_at"].replace("Z", "+00:00")
                )
                if expires_at < datetime.now(expires_at.tzinfo):
                    logger.warning(f"API key expired: {key_record['key_prefix']}...")
                    return False, None

            # Update usage stats (async, don't wait)
            try:
                supabase_client.rpc(
                    "increment_api_key_usage", {"p_key_hash": key_hash}
                ).execute()
            except Exception:
                pass  # Don't fail validation if usage update fails

            return True, {
                "id": key_record["id"],
                "name": key_record["name"],
                "key_prefix": key_record["key_prefix"],
                "permissions": key_record["permissions"],
                "tier": key_record["tier"],
                "rate_limit_per_minute": key_record["rate_limit_per_minute"],
            }

        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False, None

    @classmethod
    def revoke_key(cls, key_id: str, revoked_by: Optional[str] = None) -> bool:
        """
        Revoke an API key

        Args:
            key_id: UUID of the key to revoke
            revoked_by: User ID who revoked the key
        """
        try:
            result = (
                supabase_client.table("api_keys")
                .update(
                    {
                        "is_active": False,
                        "revoked_at": datetime.utcnow().isoformat(),
                    }
                )
                .eq("id", key_id)
                .execute()
            )

            if result.data:
                logger.info(f"API key revoked: {key_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to revoke API key: {e}")
            return False

    @classmethod
    def list_keys(
        cls, include_revoked: bool = False, created_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all API keys (without the actual key values)

        Returns list of key records with metadata only
        """
        try:
            query = supabase_client.table("api_keys").select(
                "id, key_prefix, name, description, tier, permissions, "
                "rate_limit_per_minute, is_active, last_used_at, total_requests, "
                "expires_at, created_at, revoked_at"
            )

            if not include_revoked:
                query = query.eq("is_active", True)

            if created_by:
                query = query.eq("created_by", created_by)

            query = query.order("created_at", desc=True)

            result = query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            return []

    @classmethod
    def get_key_by_id(cls, key_id: str) -> Optional[Dict[str, Any]]:
        """Get key details by ID (without the actual key)"""
        try:
            result = (
                supabase_client.table("api_keys").select("*").eq("id", key_id).execute()
            )

            if result.data:
                key = result.data[0]
                # Remove the hash from response
                key.pop("key_hash", None)
                return key

            return None

        except Exception as e:
            logger.error(f"Failed to get API key: {e}")
            return None

    @classmethod
    def update_key(
        cls,
        key_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        rate_limit: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update API key metadata (not the key itself)"""
        try:
            updates = {}
            if name is not None:
                updates["name"] = name
            if description is not None:
                updates["description"] = description
            if permissions is not None:
                updates["permissions"] = permissions
            if rate_limit is not None:
                updates["rate_limit_per_minute"] = rate_limit
            if is_active is not None:
                updates["is_active"] = is_active
                if not is_active:
                    updates["revoked_at"] = datetime.utcnow().isoformat()

            if not updates:
                return cls.get_key_by_id(key_id)

            result = (
                supabase_client.table("api_keys")
                .update(updates)
                .eq("id", key_id)
                .execute()
            )

            if result.data:
                key = result.data[0]
                key.pop("key_hash", None)
                return key

            return None

        except Exception as e:
            logger.error(f"Failed to update API key: {e}")
            return None

    @classmethod
    def log_usage(
        cls,
        key_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Log API key usage for analytics"""
        try:
            supabase_client.table("api_key_usage_logs").insert(
                {
                    "api_key_id": key_id,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "response_time_ms": response_time_ms,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                }
            ).execute()
        except Exception as e:
            logger.warning(f"Failed to log API usage: {e}")

    @classmethod
    def get_usage_stats(cls, key_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for an API key"""
        try:
            # Get key info
            key = cls.get_key_by_id(key_id)
            if not key:
                return {}

            # Get recent usage count
            since = (datetime.utcnow() - timedelta(days=days)).isoformat()

            usage_result = (
                supabase_client.table("api_key_usage_logs")
                .select("id", count="exact")
                .eq("api_key_id", key_id)
                .gte("created_at", since)
                .execute()
            )

            return {
                "key_id": key_id,
                "name": key["name"],
                "total_requests_all_time": key.get("total_requests", 0),
                "requests_last_n_days": usage_result.count or 0,
                "days": days,
                "last_used_at": key.get("last_used_at"),
            }

        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {}


# Singleton instance
api_key_service = APIKeyService()
