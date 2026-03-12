from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from database import get_db
import models
import tmdb_service
import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/movie-debate/{content_type}/{content_id}")
def get_movie_debate(content_type: str, content_id: int, db: Session = Depends(get_db)):
    # 1. Check Cache
    cached = db.query(models.AiResponseCache).filter(
        models.AiResponseCache.content_id == content_id,
        models.AiResponseCache.content_type == content_type,
        models.AiResponseCache.feature_name == "movie-debate"
    ).first()
    
    if cached:
        return json.loads(cached.response_json)
    
    # 2. Fetch Data
    movie_details = tmdb_service.tmdb_request(f"/{content_type}/{content_id}")
    if not movie_details:
        raise HTTPException(status_code=404, detail="Content not found")
        
    title = movie_details.get("title") or movie_details.get("name")
    overview = movie_details.get("overview")
    
    # 3. Fetch User Reviews
    reviews = db.query(models.Review).filter(
        models.Review.content_id == content_id,
        models.Review.content_type == content_type
    ).all()
    
    # 4. Generate AI Debate
    review_list = [{"review_text": r.review_text} for r in reviews]
    ai_debate = ai_service.get_ai_movie_debate(title, overview, review_list)
    
    # 5. Save to Cache
    new_cache = models.AiResponseCache(
        content_id=content_id,
        content_type=content_type,
        feature_name="movie-debate",
        response_json=json.dumps(ai_debate)
    )
    db.add(new_cache)
    db.commit()
    
    return ai_debate
