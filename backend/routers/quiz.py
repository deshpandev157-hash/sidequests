from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
import random

from backend.database import get_db
from backend import models
from backend import tmdb_service
from backend import ai_service

router = APIRouter(prefix="/quiz", tags=["Quiz"])

class QuizAnswer(BaseModel):
    quiz_id: int
    answer: str

@router.get("/today")
def get_daily_quiz(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    
    # Simple trick: just filter those starting with today's date
    quiz = db.query(models.MovieQuiz).filter(
        models.MovieQuiz.created_date >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).first()
    
    if not quiz:
        # Generate new one
        req = tmdb_service.tmdb_request("/movie/popular")
        movies = req.get("results", [])
        if not movies:
            raise HTTPException(status_code=500, detail="Cannot connect to TMDB")
            
        choice = random.choice(movies[:5])
        ai_q = ai_service.generate_daily_quiz(choice["title"])
        
        quiz = models.MovieQuiz(
            question=ai_q["question"],
            option_a=ai_q["option_a"],
            option_b=ai_q["option_b"],
            option_c=ai_q["option_c"],
            option_d=ai_q["option_d"],
            correct_answer=ai_q["correct_answer"]
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
    return {
        "id": quiz.id,
        "question": quiz.question,
        "options": {
            "A": quiz.option_a,
            "B": quiz.option_b,
            "C": quiz.option_c,
            "D": quiz.option_d
        }
    }

@router.post("/generate")
def force_generate_quiz(db: Session = Depends(get_db)):
    # Fetch random popular movie
    req = tmdb_service.tmdb_request("/movie/popular")
    movies = req.get("results", [])
    if not movies:
        raise HTTPException(status_code=500, detail="Cannot connect to TMDB")
        
    choice = random.choice(movies[:15])
    
    # Get details for extra context (genre, director, etc.)
    details = tmdb_service.get_details("movie", choice["id"])
    ai_q = ai_service.generate_daily_quiz(choice["title"], details)
    
    quiz = models.MovieQuiz(
        question=ai_q["question"],
        option_a=ai_q["option_a"],
        option_b=ai_q["option_b"],
        option_c=ai_q["option_c"],
        option_d=ai_q["option_d"],
        correct_answer=ai_q["correct_answer"]
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    return {
        "id": quiz.id,
        "question": quiz.question,
        "options": {
            "A": quiz.option_a,
            "B": quiz.option_b,
            "C": quiz.option_c,
            "D": quiz.option_d
        }
    }

@router.post("/answer")
def check_daily_quiz(payload: QuizAnswer, db: Session = Depends(get_db)):
    quiz = db.query(models.MovieQuiz).filter(models.MovieQuiz.id == payload.quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    correct = (payload.answer.upper() == quiz.correct_answer.upper())
    
    # Map letter to the actual text for cleaner frontend feedback
    mapping = {"A": quiz.option_a, "B": quiz.option_b, "C": quiz.option_c, "D": quiz.option_d}
    
    return {
        "correct": correct,
        "correct_answer": quiz.correct_answer,
        "correct_text": mapping.get(quiz.correct_answer.upper())
    }
