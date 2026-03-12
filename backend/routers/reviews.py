from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
import models

router = APIRouter(prefix="/reviews", tags=["Reviews"])

class ReviewCreateRequest(BaseModel):
    user_id: int
    content_id: int
    content_type: str
    review_text: str
    rating: float
    season_number: Optional[int] = None
    episode_number: Optional[int] = None

@router.post("")
def create_review(data: ReviewCreateRequest, db: Session = Depends(get_db)):
    review = models.Review(
        user_id=data.user_id,
        content_id=data.content_id,
        content_type=data.content_type,
        media_type=data.content_type,
        season_number=data.season_number,
        episode_number=data.episode_number,
        review_text=data.review_text,
        rating=data.rating,
        date=datetime.utcnow().isoformat()
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"message": "Review created", "review_id": review.id}

@router.get("/{content_type}/{content_id}")
def get_reviews(content_type: str, content_id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(
        models.Review.content_id == content_id,
        models.Review.content_type == content_type
    ).all()
    
    result = []
    for r in reviews:
        like_count = db.query(models.ReviewLike).filter(models.ReviewLike.review_id == r.id).count()
        username = r.user.username if r.user else f"User {r.user_id}"
        result.append({
            "id": r.id,
            "review_text": r.review_text,
            "rating": r.rating,
            "username": username,
            "like_count": like_count,
            "created_date": r.date
        })
    return result

@router.post("/{review_id}/like")
def like_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    existing = db.query(models.ReviewLike).filter(
        models.ReviewLike.review_id == review_id,
        models.ReviewLike.user_id == user_id
    ).first()
    if existing:
        return {"message": "Already liked"}
    
    new_like = models.ReviewLike(review_id=review_id, user_id=user_id)
    db.add(new_like)
    db.commit()
    return {"message": "Review liked"}
