"""
Stripe Connect API Routes
Handles host onboarding and Connect account management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.models.stripe_schemas import (
    ConnectAccountCreate,
    ConnectAccountStatus,
    OnboardingLinkResponse,
    DashboardLinkResponse,
)
from app.services.stripe_connect_service import stripe_connect_service
from app.api.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/host/create-account", response_model=Dict[str, Any])
async def create_connect_account(
    account_data: ConnectAccountCreate, current_user: dict = Depends(get_current_user)
):
    """
    Create a Stripe Connect Express account for the authenticated host

    Requires authentication
    """
    try:
        user_id = current_user["id"]
        email = account_data.email

        result = await stripe_connect_service.create_connect_account(
            user_id=user_id,
            email=email,
            country=account_data.country,
            business_type=account_data.business_type,
        )

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating Connect account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Stripe Connect account",
        )


@router.post("/host/onboarding-link", response_model=Dict[str, Any])
async def create_onboarding_link(current_user: dict = Depends(get_current_user)):
    """
    Generate hosted onboarding link for host to complete Stripe Connect setup

    Requires authentication
    Returns a URL that expires in ~30 minutes
    """
    try:
        user_id = current_user["id"]

        result = await stripe_connect_service.create_account_link(user_id)

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating onboarding link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create onboarding link",
        )


@router.get("/host/account-status", response_model=Dict[str, Any])
async def get_account_status(current_user: dict = Depends(get_current_user)):
    """
    Get current status of host's Stripe Connect account

    Requires authentication
    Returns account status, requirements, and bank account info
    """
    try:
        user_id = current_user["id"]

        result = await stripe_connect_service.get_account_status(user_id)

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting account status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get account status",
        )


@router.post("/host/dashboard-link", response_model=Dict[str, Any])
async def create_dashboard_link(current_user: dict = Depends(get_current_user)):
    """
    Create a login link to Stripe Express Dashboard for host

    Requires authentication
    Allows host to view payouts, update bank details, etc.
    """
    try:
        user_id = current_user["id"]

        result = await stripe_connect_service.create_login_link(user_id)

        return {"success": True, "data": result}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating dashboard link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dashboard link",
        )
