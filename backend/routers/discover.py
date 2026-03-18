from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import random

from backend.database import get_db
from backend import models
from backend import tmdb_service
from backend import ai_service

router = APIRouter(prefix="/discover", tags=["Discover"])

MOOD_GENRE_MAP = {
    "feel-good": [35, 10751], # Comedy, Family
    "mind-blowing": [878, 53], # Sci-Fi, Thriller
    "emotional": [18, 10749], # Drama, Romance
    "horror-night": [27], # Horror
    "comedy-night": [35] # Comedy
}

@router.get("/mood/{mood}")
def discover_by_mood(mood: str):
    normalized_mood = mood.lower().replace(" ", "-")
    genres = MOOD_GENRE_MAP.get(normalized_mood)
    
    if not genres:
        return []
        
    genre_str = ",".join(map(str, genres))
    # TMDB discover using custom request
    data = tmdb_service.tmdb_request("/discover/movie", {"with_genres": genre_str, "sort_by": "popularity.desc"})
    
    results = []
    for item in data.get("results", [])[:20]:
        results.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "type": "movie",
            "poster": item.get("poster_path"),
            "rating": round(item.get("vote_average", 0), 1) if item.get("vote_average") else 0
        })
    return results

@router.get("/random")
def get_ai_random_movie(db: Session = Depends(get_db)):
    # 1. Fetch random popular movie
    page = random.randint(1, 10)
    data = tmdb_service.tmdb_request("/movie/popular", {"page": page})
    movies = data.get("results", [])
    
    if not movies:
        return None
        
    choice = random.choice(movies)
    
    # 2. Add AI Reason
    ai_reason = ai_service.get_ai_movie_recommendation_reason(choice["title"])
    
    return {
        "id": choice.get("id"),
        "type": "movie",
        "title": choice.get("title"),
        "poster": choice.get("poster_path"),
        "rating": round(choice.get("vote_average", 0), 1),
        "year": choice.get("release_date", "").split("-")[0] if choice.get("release_date") else "Unknown",
        "ai_reason": ai_reason
    }

@router.get("/hidden-gems")
def get_hidden_gems(db: Session = Depends(get_db)):
    # 1. Fetch highly rated movies with low vote counts (simulated filters)
    # Randomize page to support shuffle
    page = random.randint(1, 5)
    data = tmdb_service.tmdb_request("/discover/movie", {
        "vote_count.gte": 100,
        "vote_count.lte": 5000,
        "vote_average.gte": 7.5,
        "sort_by": "vote_average.desc",
        "page": page
    })
    
    movies = data.get("results", [])[:10]
    
    results = []
    for m in movies:
        results.append({
            "id": m.get("id"),
            "title": m.get("title"),
            "type": "movie",
            "poster": m.get("poster_path"),
            "rating": round(m.get("vote_average", 0), 1),
            "votes": m.get("vote_count"),
            "ai_reason": ai_service.get_ai_hidden_gem_reason()
        })
        
    return results

@router.get("/spin-recommend")
def get_spin_recommendation(category: str):
    """Fetch a random recommendation based on the selected spin wheel category."""
    page = random.randint(1, 10)
    params = {"page": page}
    endpoint = "/movie/popular"
    media_type = "movie"
    
    if category == 'bollywood':
        endpoint = "/discover/movie"
        params.update({"with_original_language": "hi", "region": "IN", "sort_by": "popularity.desc"})
    elif category == 'tv':
        endpoint = "/tv/popular"
        media_type = "tv"
    elif category == 'anime':
        endpoint = "/discover/tv"
        media_type = "tv"
        # Genre 16 is Animation, adding Japanese language for anime feel
        params.update({"with_genres": "16", "with_original_language": "ja", "sort_by": "popularity.desc"})
    elif category == 'hollywood':
        endpoint = "/discover/movie"
        params.update({"with_original_language": "en", "sort_by": "popularity.desc"})
    elif category == 'hidden-gems':
        endpoint = "/discover/movie"
        # High rating, low popularity
        params.update({
            "vote_average.gte": 7.5,
            "vote_count.gte": 100,
            "vote_count.lte": 3000,
            "sort_by": "vote_average.desc"
        })
        
    data = tmdb_service.tmdb_request(endpoint, params)
    results = data.get("results", [])
    
    if not results:
        # Fallback to general popular
        data = tmdb_service.tmdb_request("/movie/popular", {"page": 1})
        results = data.get("results", [])
        media_type = "movie"
        
    if not results:
        return None
        
    choice = random.choice(results)
    
    # Format result for frontend
    title = choice.get("title") or choice.get("name")
    poster = choice.get("poster_path")
    rating = round(choice.get("vote_average", 0), 1)
    year = (choice.get("release_date") or choice.get("first_air_date") or "2024")[:4]
    
    return {
        "id": choice.get("id"),
        "title": title,
        "type": media_type,
        "poster": poster,
        "rating": rating,
        "year": year,
        "category": category
    }
