from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend import models
from backend import tmdb_service

router = APIRouter(prefix="/awards", tags=["Awards"])

class AwardVoteRequest(BaseModel):
    user_id: int
    award_id: int

@router.get("/current")
def get_current_awards(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    awards = db.query(models.WeeklyAward).filter(models.WeeklyAward.week_start >= week_start).all()
    
    if not awards:
        seed_data = [
            {"category": "Movie of the Week", "content_id": 157336, "content_type": "movie"}, 
            {"category": "TV Show of the Week", "content_id": 1399, "content_type": "tv"}, 
            {"category": "Anime of the Week", "content_id": 31922, "content_type": "tv"}, 
            {"category": "Most Underrated", "content_id": 27205, "content_type": "movie"} 
        ]
        for item in seed_data:
            award = models.WeeklyAward(**item, week_start=week_start)
            db.add(award)
        db.commit()
        awards = db.query(models.WeeklyAward).filter(models.WeeklyAward.week_start >= week_start).all()
        
    results = []
    for a in awards:
        details = tmdb_service.get_details(a.content_type, a.content_id)
        title = details.get("title") or details.get("name") or "Unknown" if details else "Unknown"
        poster = details.get("poster_path") if details else None
            
        vote_count = db.query(models.AwardVote).filter(models.AwardVote.award_id == a.id).count()
        results.append({
            "id": a.id,
            "category": a.category,
            "content_id": a.content_id,
            "content_type": a.content_type,
            "title": title,
            "poster": poster,
            "votes": vote_count
        })
    
    return results

@router.post("/vote")
def vote_award(data: AwardVoteRequest, db: Session = Depends(get_db)):
    existing = db.query(models.AwardVote).filter(
        models.AwardVote.award_id == data.award_id,
        models.AwardVote.user_id == data.user_id
    ).first()
    
    if existing:
        return {"message": "Already voted"}
        
    vote = models.AwardVote(award_id=data.award_id, user_id=data.user_id)
    db.add(vote)
    db.commit()
    return {"message": "Vote submitted"}

@router.get("/results")
def get_award_results(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    awards = db.query(models.WeeklyAward).filter(models.WeeklyAward.week_start >= week_start).all()
    categories = {}
    
    for a in awards:
        vote_count = db.query(models.AwardVote).filter(models.AwardVote.award_id == a.id).count()
        if a.category not in categories:
            categories[a.category] = {"award": a, "votes": vote_count}
        else:
            if vote_count > categories[a.category]["votes"]:
                categories[a.category] = {"award": a, "votes": vote_count}
                
    results = []
    for cat, data in categories.items():
        a = data["award"]
        details = tmdb_service.get_details(a.content_type, a.content_id)
        title = details.get("title") or details.get("name") or "Unknown" if details else "Unknown"
        poster = details.get("poster_path") if details else None
            
        results.append({
            "category": cat,
            "title": title,
            "poster": poster,
            "votes": data["votes"]
        })
    return results
