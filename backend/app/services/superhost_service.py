"""
Superhost Verification Service
Handles superhost requests, eligibility checks, and admin approval workflows
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class SuperhostService:
    """Service for managing superhost verifications"""

    @staticmethod
    async def check_eligibility(user_id: str) -> Dict[str, Any]:
        """
        Check if host is eligible for superhost status

        Criteria:
        - At least 1 active property
        - At least 5 completed bookings
        - Average rating >= 4.5
        - Response rate >= 90%
        - Cancellation rate <= 5%
        """
        try:
            result = await supabase_client.rpc(
                "check_superhost_eligibility", {"host_user_id": user_id}
            ).execute()

            if result.data:
                return result.data

            return {
                "eligible": False,
                "reasons": ["Unable to calculate eligibility"],
                "metrics": {},
            }
        except Exception as e:
            logger.error(
                f"Error checking superhost eligibility for user {user_id}: {e}"
            )
            raise Exception(f"Failed to check eligibility: {str(e)}")

    @staticmethod
    async def get_host_metrics(user_id: str) -> Dict[str, Any]:
        """Get host performance metrics"""
        try:
            result = await supabase_client.rpc(
                "calculate_host_metrics", {"host_user_id": user_id}
            ).execute()

            return result.data if result.data else {}
        except Exception as e:
            logger.error(f"Error getting host metrics for user {user_id}: {e}")
            raise Exception(f"Failed to get metrics: {str(e)}")

    @staticmethod
    async def create_verification_request(
        user_id: str, request_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new superhost verification request"""
        try:
            # Check eligibility first
            eligibility = await SuperhostService.check_eligibility(user_id)

            if not eligibility.get("eligible"):
                return {
                    "success": False,
                    "error": "Not eligible for superhost status",
                    "reasons": eligibility.get("reasons", []),
                    "metrics": eligibility.get("metrics", {}),
                }

            # Get current metrics
            metrics = eligibility.get("metrics", {})

            # Create verification request
            request_data = {
                "user_id": user_id,
                "status": "pending",
                "request_message": request_message,
                "total_properties": metrics.get("total_properties", 0),
                "total_bookings": metrics.get("total_bookings", 0),
                "total_revenue": float(metrics.get("total_revenue", 0)),
                "average_rating": float(metrics.get("average_rating", 0)),
                "response_rate": float(metrics.get("response_rate", 0)),
                "cancellation_rate": float(metrics.get("cancellation_rate", 0)),
            }

            result = (
                await supabase_client.table("superhost_verification_requests")
                .insert(request_data)
                .execute()
            )

            # Update user status to pending
            await supabase_client.table("users").update(
                {
                    "superhost_status": "pending",
                    "superhost_requested_at": datetime.utcnow().isoformat(),
                }
            ).eq("id", user_id).execute()

            logger.info(f"Superhost verification request created for user {user_id}")

            return {
                "success": True,
                "request": result.data[0] if result.data else None,
                "message": "Verification request submitted successfully",
            }
        except Exception as e:
            logger.error(f"Error creating verification request for user {user_id}: {e}")
            raise Exception(f"Failed to create verification request: {str(e)}")

    @staticmethod
    async def get_verification_status(user_id: str) -> Dict[str, Any]:
        """Get current verification status for a host"""
        try:
            # Get user's superhost status
            user_result = (
                await supabase_client.table("users")
                .select(
                    "is_superhost, superhost_status, superhost_requested_at, superhost_approved_at"
                )
                .eq("id", user_id)
                .execute()
            )

            if not user_result.data:
                return {"status": "regular", "is_superhost": False}

            user_data = user_result.data[0]

            # Get pending request if any
            request_result = (
                await supabase_client.table("superhost_verification_requests")
                .select("*")
                .eq("user_id", user_id)
                .eq("status", "pending")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            return {
                "is_superhost": user_data.get("is_superhost", False),
                "status": user_data.get("superhost_status", "regular"),
                "requested_at": user_data.get("superhost_requested_at"),
                "approved_at": user_data.get("superhost_approved_at"),
                "pending_request": (
                    request_result.data[0] if request_result.data else None
                ),
            }
        except Exception as e:
            logger.error(f"Error getting verification status for user {user_id}: {e}")
            raise Exception(f"Failed to get verification status: {str(e)}")

    @staticmethod
    async def get_all_pending_requests() -> List[Dict[str, Any]]:
        """Get all pending verification requests (Admin only)"""
        try:
            result = (
                await supabase_client.table("superhost_verification_requests")
                .select("*, users!inner(id, email, name, created_at)")
                .eq("status", "pending")
                .order("created_at", desc=True)
                .execute()
            )

            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting pending requests: {e}")
            raise Exception(f"Failed to get pending requests: {str(e)}")

    @staticmethod
    async def approve_request(
        request_id: str, admin_id: str, admin_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve a superhost verification request (Admin only)"""
        try:
            # Get the request
            request_result = (
                await supabase_client.table("superhost_verification_requests")
                .select("*")
                .eq("id", request_id)
                .execute()
            )

            if not request_result.data:
                raise Exception("Request not found")

            request_data = request_result.data[0]
            user_id = request_data["user_id"]

            # Update request status
            await supabase_client.table("superhost_verification_requests").update(
                {
                    "status": "approved",
                    "reviewed_at": datetime.utcnow().isoformat(),
                    "reviewed_by": admin_id,
                    "admin_notes": admin_notes,
                }
            ).eq("id", request_id).execute()

            # Update user to superhost
            await supabase_client.table("users").update(
                {
                    "is_superhost": True,
                    "superhost_status": "approved",
                    "superhost_approved_at": datetime.utcnow().isoformat(),
                    "superhost_verified_by": admin_id,
                }
            ).eq("id", user_id).execute()

            logger.info(f"Superhost request {request_id} approved by admin {admin_id}")

            return {
                "success": True,
                "message": "Superhost status approved successfully",
            }
        except Exception as e:
            logger.error(f"Error approving request {request_id}: {e}")
            raise Exception(f"Failed to approve request: {str(e)}")

    @staticmethod
    async def reject_request(
        request_id: str,
        admin_id: str,
        rejection_reason: str,
        admin_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reject a superhost verification request (Admin only)"""
        try:
            # Get the request
            request_result = (
                await supabase_client.table("superhost_verification_requests")
                .select("*")
                .eq("id", request_id)
                .execute()
            )

            if not request_result.data:
                raise Exception("Request not found")

            request_data = request_result.data[0]
            user_id = request_data["user_id"]

            # Update request status
            await supabase_client.table("superhost_verification_requests").update(
                {
                    "status": "rejected",
                    "reviewed_at": datetime.utcnow().isoformat(),
                    "reviewed_by": admin_id,
                    "rejection_reason": rejection_reason,
                    "admin_notes": admin_notes,
                }
            ).eq("id", request_id).execute()

            # Update user status
            await supabase_client.table("users").update(
                {"is_superhost": False, "superhost_status": "rejected"}
            ).eq("id", user_id).execute()

            logger.info(f"Superhost request {request_id} rejected by admin {admin_id}")

            return {"success": True, "message": "Superhost request rejected"}
        except Exception as e:
            logger.error(f"Error rejecting request {request_id}: {e}")
            raise Exception(f"Failed to reject request: {str(e)}")


superhost_service = SuperhostService()
