from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend import models
from backend import tmdb_service

router = APIRouter(prefix="/discussions", tags=["Discussions"])

class DiscussionCreate(BaseModel):
    user_id: int
    title: str
    content_id: int
    content_type: str

class CommentCreate(BaseModel):
    user_id: int
    comment: str

@router.post("")
def create_discussion(data: DiscussionCreate, db: Session = Depends(get_db)):
    discussion = models.Discussion(
        user_id=data.user_id,
        title=data.title,
        content_id=data.content_id,
        content_type=data.content_type
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)
    return {"message": "Discussion created", "id": discussion.id}

@router.get("/trending")
def get_trending_discussions(db: Session = Depends(get_db)):
    since_24h = datetime.utcnow() - timedelta(days=1)
    
    discussions = db.query(models.Discussion).all()
    result = []
    
    for d in discussions:
        recent_comments = db.query(models.DiscussionComment).filter(
            models.DiscussionComment.discussion_id == d.id,
            models.DiscussionComment.created_at >= since_24h
        ).count()
        
        total_comments = db.query(models.DiscussionComment).filter(
            models.DiscussionComment.discussion_id == d.id
        ).count()
        
        details = tmdb_service.get_details(d.content_type, d.content_id)
        related_title = details.get("title") or details.get("name") or "Unknown" if details else "Unknown"
        
        result.append({
            "id": d.id,
            "title": d.title,
            "content_id": d.content_id,
            "content_type": d.content_type,
            "related_title": related_title,
            "comment_count": total_comments,
            "recent_comments": recent_comments,
            "last_activity": d.created_at.isoformat()
        })
    
    result.sort(key=lambda x: x["recent_comments"], reverse=True)
    return result

@router.post("/{discussion_id}/comment")
def add_comment(discussion_id: int, data: CommentCreate, db: Session = Depends(get_db)):
    comment = models.DiscussionComment(
        discussion_id=discussion_id,
        user_id=data.user_id,
        comment=data.comment
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"message": "Comment added", "id": comment.id}
