"""
Webhook service for external AI agent notifications
"""

import aiohttp
import asyncio
import logging
import json
import hmac
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.supabase_client import supabase_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.max_retries = 3

    async def send_webhook(
        self,
        event_type: str,
        booking_id: str,
        property_id: str,
        host_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send webhook to all subscribed external agents"""

        try:
            # Get active webhook subscriptions for this event
            subscriptions = await self._get_active_subscriptions(event_type)

            if not subscriptions:
                logger.info(f"No webhook subscriptions found for event: {event_type}")
                return {"status": "no_subscriptions", "event_type": event_type}

            results = []

            for subscription in subscriptions:
                try:
                    result = await self._send_single_webhook(
                        subscription, event_type, booking_id, property_id, host_id, data
                    )
                    results.append(result)

                except Exception as e:
                    logger.error(
                        f"Failed to send webhook to {subscription['agent_name']}: {e}"
                    )
                    results.append(
                        {
                            "agent_name": subscription["agent_name"],
                            "status": "failed",
                            "error": str(e),
                        }
                    )

            return {
                "status": "completed",
                "event_type": event_type,
                "results": results,
                "total_subscriptions": len(subscriptions),
                "successful_deliveries": len(
                    [r for r in results if r.get("status") == "success"]
                ),
            }

        except Exception as e:
            logger.error(f"Failed to send webhooks for event {event_type}: {e}")
            return {"status": "error", "event_type": event_type, "error": str(e)}

    async def _get_active_subscriptions(self, event_type: str) -> List[Dict[str, Any]]:
        """Get active webhook subscriptions for event type"""
        try:
            result = (
                supabase_client.table("webhook_subscriptions")
                .select("*")
                .eq("is_active", True)
                .contains("events", [event_type])
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(f"Failed to get webhook subscriptions: {e}")
            return []

    async def _send_single_webhook(
        self,
        subscription: Dict[str, Any],
        event_type: str,
        booking_id: str,
        property_id: str,
        host_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send webhook to a single subscription"""

        webhook_payload = {
            "event_type": event_type,
            "booking_id": booking_id,
            "property_id": property_id,
            "host_id": host_id,
            "external_agent_url": subscription["webhook_url"],
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "subscription_id": subscription["id"],
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {subscription['api_key']}",
            "X-Webhook-Event": event_type,
            "X-Webhook-Signature": self._generate_signature(webhook_payload),
            "X-Webhook-ID": subscription["id"],
            "X-Webhook-Timestamp": webhook_payload["timestamp"],
            "User-Agent": "Krib-AI-Webhook/1.0",
        }

        connector = aiohttp.TCPConnector(
            limit=100, limit_per_host=30, keepalive_timeout=30
        )

        async with aiohttp.ClientSession(
            timeout=self.timeout, connector=connector, trust_env=True
        ) as session:

            for attempt in range(self.max_retries):
                try:
                    logger.info(
                        f"Sending webhook attempt {attempt + 1} to {subscription['agent_name']}"
                    )

                    async with session.post(
                        subscription["webhook_url"],
                        json=webhook_payload,
                        headers=headers,
                        ssl=True,
                    ) as response:

                        response_text = await response.text()

                        if response.status == 200:
                            # Update successful call timestamp
                            await self._update_webhook_success(subscription["id"])

                            logger.info(
                                f"Webhook delivered successfully to {subscription['agent_name']}"
                            )

                            return {
                                "agent_name": subscription["agent_name"],
                                "status": "success",
                                "status_code": response.status,
                                "attempt": attempt + 1,
                                "response_time_ms": 0,  # Could add timing
                                "response_body": response_text[
                                    :500
                                ],  # Truncate for logging
                            }
                        else:
                            logger.warning(
                                f"Webhook failed with status {response.status} for {subscription['agent_name']}: {response_text}"
                            )

                            if attempt == self.max_retries - 1:
                                await self._update_webhook_failure(subscription["id"])

                except aiohttp.ClientError as e:
                    logger.error(
                        f"HTTP error on attempt {attempt + 1} to {subscription['agent_name']}: {e}"
                    )

                    if attempt == self.max_retries - 1:
                        await self._update_webhook_failure(subscription["id"])
                        raise e

                    # Wait before retry with exponential backoff
                    await asyncio.sleep(2**attempt)

                except Exception as e:
                    logger.error(
                        f"Unexpected error on attempt {attempt + 1} to {subscription['agent_name']}: {e}"
                    )

                    if attempt == self.max_retries - 1:
                        await self._update_webhook_failure(subscription["id"])
                        raise e

                    await asyncio.sleep(2**attempt)

        return {
            "agent_name": subscription["agent_name"],
            "status": "failed",
            "attempts": self.max_retries,
            "error": "Max retries exceeded",
        }

    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate webhook signature for security"""
        secret_key = getattr(
            settings, "webhook_secret_key", "default_webhook_secret_key"
        )
        payload_string = json.dumps(payload, sort_keys=True, separators=(",", ":"))

        signature = hmac.new(
            secret_key.encode("utf-8"), payload_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return f"sha256={signature}"

    async def _update_webhook_success(self, subscription_id: str):
        """Update webhook subscription with successful call"""
        try:
            supabase_client.table("webhook_subscriptions").update(
                {
                    "last_successful_call": datetime.utcnow().isoformat(),
                    "failed_attempts": 0,
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", subscription_id).execute()

        except Exception as e:
            logger.error(f"Failed to update webhook success for {subscription_id}: {e}")

    async def _update_webhook_failure(self, subscription_id: str):
        """Update webhook subscription with failed attempt"""
        try:
            # Get current failed attempts
            result = (
                supabase_client.table("webhook_subscriptions")
                .select("failed_attempts, max_failed_attempts, agent_name")
                .eq("id", subscription_id)
                .execute()
            )

            if result.data:
                current_failures = result.data[0]["failed_attempts"] + 1
                max_failures = result.data[0]["max_failed_attempts"]
                agent_name = result.data[0]["agent_name"]

                update_data = {
                    "failed_attempts": current_failures,
                    "updated_at": datetime.utcnow().isoformat(),
                }

                # Disable if too many failures
                if current_failures >= max_failures:
                    update_data["is_active"] = False
                    logger.warning(
                        f"Disabling webhook subscription {subscription_id} for {agent_name} due to {current_failures} consecutive failures"
                    )

                supabase_client.table("webhook_subscriptions").update(update_data).eq(
                    "id", subscription_id
                ).execute()

        except Exception as e:
            logger.error(f"Failed to update webhook failure for {subscription_id}: {e}")

    async def test_webhook_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Test a specific webhook subscription"""
        try:
            # Get subscription
            result = (
                supabase_client.table("webhook_subscriptions")
                .select("*")
                .eq("id", subscription_id)
                .execute()
            )

            if not result.data:
                return {"status": "error", "error": "Subscription not found"}

            subscription = result.data[0]

            # Send test webhook
            test_result = await self._send_single_webhook(
                subscription=subscription,
                event_type="test.webhook",
                booking_id="test-booking-123",
                property_id="test-property-456",
                host_id="test-host-789",
                data={
                    "test": True,
                    "message": "This is a test webhook from Krib AI",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return test_result

        except Exception as e:
            logger.error(f"Failed to test webhook subscription {subscription_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def get_webhook_statistics(self) -> Dict[str, Any]:
        """Get webhook delivery statistics"""
        try:
            # Get subscription counts
            total_result = (
                supabase_client.table("webhook_subscriptions")
                .select("id", count="exact")
                .execute()
            )
            active_result = (
                supabase_client.table("webhook_subscriptions")
                .select("id", count="exact")
                .eq("is_active", True)
                .execute()
            )
            failed_result = (
                supabase_client.table("webhook_subscriptions")
                .select("id", count="exact")
                .eq("is_active", False)
                .execute()
            )

            # Get recent successful calls
            from datetime import timedelta

            recent_success_result = (
                supabase_client.table("webhook_subscriptions")
                .select("id", count="exact")
                .gte(
                    "last_successful_call",
                    (datetime.utcnow() - timedelta(hours=24)).isoformat(),
                )
                .execute()
            )

            return {
                "total_subscriptions": total_result.count or 0,
                "active_subscriptions": active_result.count or 0,
                "failed_subscriptions": failed_result.count or 0,
                "recent_successful_calls_24h": recent_success_result.count or 0,
                "success_rate": round(
                    (recent_success_result.count or 0)
                    / max(active_result.count or 1, 1)
                    * 100,
                    2,
                ),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get webhook statistics: {e}")
            return {"error": str(e), "last_updated": datetime.utcnow().isoformat()}


# Global webhook service instance
webhook_service = WebhookService()
