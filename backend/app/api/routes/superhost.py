"""
Superhost Verification API Routes
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional

from app.api.dependencies import get_current_user, require_admin
from app.services.superhost_service import superhost_service

logger = logging.getLogger(__name__)

router = APIRouter()


class VerificationRequestCreate(BaseModel):
    """Request to become a superhost"""

    request_message: Optional[str] = Field(
        None, max_length=500, description="Optional message from host"
    )


class VerificationApproval(BaseModel):
    """Admin approval of verification request"""

    admin_notes: Optional[str] = Field(None, max_length=1000)


class VerificationRejection(BaseModel):
    """Admin rejection of verification request"""

    rejection_reason: str = Field(..., min_length=10, max_length=500)
    admin_notes: Optional[str] = Field(None, max_length=1000)


@router.get("/eligibility")
async def check_eligibility(current_user=Depends(get_current_user)):
    """
    Check if current host is eligible for superhost status

    Returns eligibility status, reasons if not eligible, and current metrics
    """
    try:
        result = await superhost_service.check_eligibility(current_user["id"])
        return result
    except Exception as e:
        logger.error(f"Error checking eligibility: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/metrics")
async def get_metrics(current_user=Depends(get_current_user)):
    """Get host performance metrics"""
    try:
        metrics = await superhost_service.get_host_metrics(current_user["id"])
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/status")
async def get_verification_status(current_user=Depends(get_current_user)):
    """Get current superhost verification status"""
    try:
        status_data = await superhost_service.get_verification_status(
            current_user["id"]
        )
        return status_data
    except Exception as e:
        logger.error(f"Error getting verification status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/request")
async def request_verification(
    data: VerificationRequestCreate, current_user=Depends(get_current_user)
):
    """
    Submit a request to become a superhost

    Host must meet eligibility criteria
    """
    try:
        result = await superhost_service.create_verification_request(
            user_id=current_user["id"], request_message=data.request_message
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error"),
                headers={"X-Ineligible-Reasons": ";".join(result.get("reasons", []))},
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating verification request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/admin/pending")
async def get_pending_requests(current_user=Depends(require_admin)):
    """
    Get all pending superhost verification requests (Admin only)
    """
    try:
        requests = await superhost_service.get_all_pending_requests()
        return {"requests": requests, "count": len(requests)}
    except Exception as e:
        logger.error(f"Error getting pending requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/admin/approve/{request_id}")
async def approve_verification(
    request_id: str, data: VerificationApproval, current_user=Depends(require_admin)
):
    """
    Approve a superhost verification request (Admin only)
    """
    try:
        result = await superhost_service.approve_request(
            request_id=request_id,
            admin_id=current_user["id"],
            admin_notes=data.admin_notes,
        )
        return result
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/admin/reject/{request_id}")
async def reject_verification(
    request_id: str, data: VerificationRejection, current_user=Depends(require_admin)
):
    """
    Reject a superhost verification request (Admin only)
    """
    try:
        result = await superhost_service.reject_request(
            request_id=request_id,
            admin_id=current_user["id"],
            rejection_reason=data.rejection_reason,
            admin_notes=data.admin_notes,
        )
        return result
    except Exception as e:
        logger.error(f"Error rejecting request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
