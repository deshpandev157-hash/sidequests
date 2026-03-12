from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
import models
import ai_service

router = APIRouter(prefix="/challenges", tags=["Challenges"])

class ProgressUpdate(BaseModel):
    user_id: int
    challenge_id: int
    
@router.get("")
def get_challenges(db: Session = Depends(get_db)):
    challenges = db.query(models.Challenge).all()
    user_id = 1 # Stub
    
    if not challenges:
        ai_data = ai_service.generate_watch_challenges()
        for ch in ai_data:
            c = models.Challenge(**ch)
            db.add(c)
        db.commit()
        challenges = db.query(models.Challenge).all()
        
    results = []
    
    for ch in challenges:
        prog = db.query(models.ChallengeProgress).filter(
            models.ChallengeProgress.user_id == user_id,
            models.ChallengeProgress.challenge_id == ch.id
        ).first()
        
        results.append({
            "id": ch.id,
            "title": ch.title,
            "description": ch.description,
            "required_count": ch.required_count,
            "completed_count": prog.completed_count if prog else 0
        })
        
    return results

@router.post("/progress")
def mark_movie_watched(payload: ProgressUpdate, db: Session = Depends(get_db)):
    req = db.query(models.Challenge).filter(models.Challenge.id == payload.challenge_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Challenge not found")

    prog = db.query(models.ChallengeProgress).filter(
        models.ChallengeProgress.user_id == payload.user_id,
        models.ChallengeProgress.challenge_id == payload.challenge_id
    ).first()
    
    if not prog:
        prog = models.ChallengeProgress(
            user_id=payload.user_id,
            challenge_id=payload.challenge_id,
            completed_count=1
        )
        db.add(prog)
    else:
        if prog.completed_count < req.required_count:
            prog.completed_count += 1
            
    db.commit()
    db.refresh(prog)
    
    is_completed = (prog.completed_count >= req.required_count)
    
    return {
        "message": "Challenge Completed!" if is_completed else "Progress updated",
        "completed_count": prog.completed_count,
        "required_count": req.required_count,
        "is_completed": is_completed,
        "title": req.title
    }

@router.post("/shuffle")
def shuffle_challenges(db: Session = Depends(get_db)):
    # Simple logic: delete all and regenerate
    # In a real app we might only shuffle the ones the user hasn't started
    db.query(models.Challenge).delete()
    db.query(models.ChallengeProgress).delete() # Also clear progress for the clean start
    
    ai_data = ai_service.generate_watch_challenges()
    for ch in ai_data:
        c = models.Challenge(**ch)
        db.add(c)
    
    db.commit()
    return {"message": "Challenges shuffled successfully"}

