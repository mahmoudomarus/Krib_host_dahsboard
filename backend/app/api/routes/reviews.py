"""
Reviews API routes for host dashboard
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies import get_current_user
from app.core.supabase_client import supabase_client

logger = logging.getLogger(__name__)
router = APIRouter()


class ReviewResponse(BaseModel):
    id: str
    booking_id: str
    property_id: str
    guest_id: str
    guest_name: Optional[str]
    rating: float
    cleanliness_rating: Optional[float]
    communication_rating: Optional[float]
    checkin_rating: Optional[float]
    accuracy_rating: Optional[float]
    location_rating: Optional[float]
    value_rating: Optional[float]
    comment: Optional[str]
    host_response: Optional[str]
    created_at: str
    responded_at: Optional[str]
    property_title: Optional[str]


class ReviewsListResponse(BaseModel):
    reviews: list[ReviewResponse]
    total: int
    page: int
    page_size: int
    average_rating: float


class HostResponseRequest(BaseModel):
    response: str = Field(..., min_length=10, max_length=1000)


@router.get("/properties/{property_id}/reviews", response_model=ReviewsListResponse)
async def get_property_reviews(
    property_id: str,
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get all reviews for a specific property"""
    try:
        property_result = (
            supabase_client.table("properties")
            .select("id")
            .eq("id", property_id)
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if not property_result.data:
            raise HTTPException(status_code=404, detail="Property not found")

        offset = (page - 1) * page_size

        reviews_result = (
            supabase_client.table("reviews")
            .select(
                """
                id,
                booking_id,
                property_id,
                guest_id,
                rating,
                cleanliness_rating,
                communication_rating,
                checkin_rating,
                accuracy_rating,
                location_rating,
                value_rating,
                comment,
                host_response,
                responded_at,
                created_at
            """
            )
            .eq("property_id", property_id)
            .order("created_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )

        count_result = (
            supabase_client.table("reviews")
            .select("id", count="exact")
            .eq("property_id", property_id)
            .execute()
        )

        total = count_result.count or 0

        reviews = []
        for review in reviews_result.data:
            guest_result = (
                supabase_client.table("users")
                .select("first_name, last_name")
                .eq("id", review["guest_id"])
                .single()
                .execute()
            )

            guest_name = None
            if guest_result.data:
                guest_name = f"{guest_result.data.get('first_name', '')} {guest_result.data.get('last_name', '')}".strip()

            reviews.append(
                ReviewResponse(**review, guest_name=guest_name, property_title=None)
            )

        avg_rating = 0
        if reviews_result.data:
            avg_rating = sum(r["rating"] for r in reviews_result.data) / len(
                reviews_result.data
            )

        return ReviewsListResponse(
            reviews=reviews,
            total=total,
            page=page,
            page_size=page_size,
            average_rating=round(avg_rating, 2),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get reviews for property {property_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")


@router.get("/reviews", response_model=ReviewsListResponse)
async def get_all_host_reviews(
    page: int = 1,
    page_size: int = 20,
    property_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Get all reviews for all properties owned by the host"""
    try:
        properties_result = (
            supabase_client.table("properties")
            .select("id, title")
            .eq("user_id", current_user["id"])
            .execute()
        )

        if not properties_result.data:
            return ReviewsListResponse(
                reviews=[], total=0, page=page, page_size=page_size, average_rating=0
            )

        property_ids = [p["id"] for p in properties_result.data]
        property_titles = {p["id"]: p["title"] for p in properties_result.data}

        offset = (page - 1) * page_size

        query = (
            supabase_client.table("reviews")
            .select("*")
            .in_("property_id", property_ids)
        )

        if property_id:
            query = query.eq("property_id", property_id)

        reviews_result = (
            query.order("created_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )

        count_query = (
            supabase_client.table("reviews")
            .select("id", count="exact")
            .in_("property_id", property_ids)
        )

        if property_id:
            count_query = count_query.eq("property_id", property_id)

        count_result = count_query.execute()
        total = count_result.count or 0

        reviews = []
        for review in reviews_result.data:
            review_data = {
                **review,
                "property_title": property_titles.get(review["property_id"]),
                "guest_id": review.get("guest_email", ""),
            }
            reviews.append(ReviewResponse(**review_data))

        avg_rating = 0
        if reviews_result.data:
            avg_rating = sum(r["rating"] for r in reviews_result.data) / len(
                reviews_result.data
            )

        return ReviewsListResponse(
            reviews=reviews,
            total=total,
            page=page,
            page_size=page_size,
            average_rating=round(avg_rating, 2),
        )

    except Exception as e:
        logger.error(f"Failed to get host reviews: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")


@router.post("/reviews/{review_id}/respond")
async def respond_to_review(
    review_id: str,
    response_data: HostResponseRequest,
    current_user: dict = Depends(get_current_user),
):
    """Add host response to a review"""
    try:
        review_result = (
            supabase_client.table("reviews")
            .select("id, property_id")
            .eq("id", review_id)
            .single()
            .execute()
        )

        if not review_result.data:
            raise HTTPException(status_code=404, detail="Review not found")

        property_result = (
            supabase_client.table("properties")
            .select("id")
            .eq("id", review_result.data["property_id"])
            .eq("user_id", current_user["id"])
            .single()
            .execute()
        )

        if not property_result.data:
            raise HTTPException(
                status_code=403, detail="Not authorized to respond to this review"
            )

        from datetime import datetime

        update_result = (
            supabase_client.table("reviews")
            .update(
                {
                    "host_response": response_data.response,
                    "responded_at": datetime.utcnow().isoformat(),
                }
            )
            .eq("id", review_id)
            .execute()
        )

        if not update_result.data:
            raise HTTPException(status_code=500, detail="Failed to update review")

        return {
            "success": True,
            "message": "Response added successfully",
            "review_id": review_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to respond to review {review_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add response")


@router.get("/reviews/stats")
async def get_review_stats(current_user: dict = Depends(get_current_user)):
    """Get review statistics for the host"""
    try:
        properties_result = (
            supabase_client.table("properties")
            .select("id")
            .eq("user_id", current_user["id"])
            .execute()
        )

        if not properties_result.data:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "pending_responses": 0,
                "ratings_breakdown": {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0},
            }

        property_ids = [p["id"] for p in properties_result.data]

        reviews_result = (
            supabase_client.table("reviews")
            .select("rating, host_response")
            .in_("property_id", property_ids)
            .execute()
        )

        total_reviews = len(reviews_result.data)
        pending_responses = sum(
            1 for r in reviews_result.data if not r.get("host_response")
        )

        ratings_breakdown = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        total_rating = 0

        for review in reviews_result.data:
            rating = review["rating"]
            total_rating += rating
            ratings_breakdown[str(int(rating))] += 1

        avg_rating = total_rating / total_reviews if total_reviews > 0 else 0

        return {
            "total_reviews": total_reviews,
            "average_rating": round(avg_rating, 2),
            "pending_responses": pending_responses,
            "ratings_breakdown": ratings_breakdown,
        }

    except Exception as e:
        logger.error(f"Failed to get review stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch review statistics")
