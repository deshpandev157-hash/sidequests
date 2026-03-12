from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import random

from database import get_db
import models
import tmdb_service
import ai_service

router = APIRouter(prefix="/games", tags=["Games"])

class GuessAnswer(BaseModel):
    game_id: int
    answer: str

@router.get("/guess-movie")
def guess_movie(db: Session = Depends(get_db)):
    # Grab a generic popular movie to create a puzzle from
    req = tmdb_service.tmdb_request("/movie/popular")
    movies = req.get("results", [])
    
    if not movies:
        raise HTTPException(status_code=500, detail="Cannot connect to TMDB")
        
    choice = random.choice(movies[:15])
    
    # Send title and description (overview) to AI Generator
    ai_clue = ai_service.generate_guess_game_clue(choice["title"], choice["overview"])
    
    # Store game in database
    game = models.GuessGame(
        content_id=choice["id"],
        clue_type=ai_clue["clue_type"],
        clue_text=ai_clue["clue_text"],
        answer_title=choice["title"].lower()
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    
    return {
        "id": game.id,
        "clue_type": game.clue_type,
        "clue_text": game.clue_text
    }

@router.post("/guess-movie/answer")
def check_guess_answer(payload: GuessAnswer, db: Session = Depends(get_db)):
    game = db.query(models.GuessGame).filter(models.GuessGame.id == payload.game_id).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
        
    answer_stripped = payload.answer.strip().lower()
    if answer_stripped == game.answer_title:
        return {"correct": True, "correct_title": game.answer_title.title()}
    else:
        return {"correct": False, "correct_title": game.answer_title.title()}

@router.get("/blur-guess")
def get_blur_challenge(category: str = "hollywood"):
    item = tmdb_service.get_blur_game_item(category)
    if not item:
        raise HTTPException(status_code=500, detail="Could not fetch game item")
    return item

@router.get("/scene-guess")
def get_scene_challenge(category: str = "hollywood"):
    item = tmdb_service.get_scene_guess_item(category)
    if not item:
        raise HTTPException(status_code=500, detail="Could not fetch game item")
    return item
