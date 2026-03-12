import auth
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, Base, get_db
import models
import tmdb_service

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from routers import reviews as reviews_router
from routers import discussions as discussions_router
from routers import awards as awards_router
from routers import discover as discover_router
from routers import games as games_router
from routers import quiz as quiz_router
from routers import challenges as challenges_router
from routers import ai as ai_router
from routers import bollywood as bollywood_router


# =========================
# CREATE DATABASE TABLES
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="SideQuest API",
    version="2.0",
    description="Movie, TV and Anime tracking API with achievements and recommendations"
)

app.include_router(reviews_router.router)
app.include_router(discussions_router.router)
app.include_router(awards_router.router)
app.include_router(discover_router.router)
app.include_router(games_router.router)
app.include_router(quiz_router.router)
app.include_router(challenges_router.router)
app.include_router(ai_router.router)
app.include_router(bollywood_router.router)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Pydantic Schemas
# =========================

class ReviewCreate(BaseModel):
    user_id: int
    content_id: int
    content_type: str = "movie"
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    rating: float
    review_text: str


class ContentRatingCreate(BaseModel):
    content_id: int
    content_type: str
    rating: int

class WatchHistoryCreate(BaseModel):
    user_id: int
    content_id: int
    content_type: str


class EpisodeRatingCreate(BaseModel):
    show_id: int
    season_number: int
    episode_number: int
    rating: float
    user_id: Optional[int] = None


class EpisodeReviewCreate(BaseModel):
    show_id: int
    season_number: int
    episode_number: int
    review: str
    user_id: Optional[int] = None


class WatchlistAdd(BaseModel):
    user_id: int
    content_id: int
    media_type: str


class UserSignup(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class WatchEpisodeCreate(BaseModel):
    user_id: int
    show_id: int
    show_name: str = ""
    season_number: int
    episode_number: int
    episode_name: str = ""


# =========================
# ROOT
# =========================

@app.get("/")
def home():
    return {"message": "SideQuest API Running"}


# =========================
# TMDB ROUTES
# =========================

@app.get("/trending/{media_type}")
def get_trending(media_type: str):

    if media_type not in ["movie", "tv", "all"]:
        raise HTTPException(status_code=400, detail="Invalid media type")

    data = tmdb_service.get_trending(media_type)

    if not data:
        return {"results": []}

    return data


@app.get("/search")
def search(query: str):

    if not query:
        return {"results": []}

    return tmdb_service.search_content(query)


@app.get("/content/{media_type}/{content_id}")
def get_content_details(media_type: str, content_id: int):

    if media_type not in ["movie", "tv"]:
        raise HTTPException(status_code=400, detail="Invalid media type")

    data = tmdb_service.get_details(media_type, content_id)

    if not data:
        raise HTTPException(status_code=404, detail="Content not found")

    return data


# =========================
# TV SHOW ROUTES
# =========================

@app.get("/tv/{tv_id}/seasons")
def get_tv_seasons(tv_id: int):

    data = tmdb_service.get_seasons(tv_id)

    if not data:
        return []

    return data


@app.get("/tv/{tv_id}/season/{season_number}")
def get_season_episodes(tv_id: int, season_number: int):

    data = tmdb_service.get_season_episodes(tv_id, season_number)

    if not data:
        return {"episodes": []}

    return data


@app.get("/tv/{tv_id}/season/{season_number}/episode/{episode_number}")
def get_episode_details(tv_id: int, season_number: int, episode_number: int):

    data = tmdb_service.get_episode_details(tv_id, season_number, episode_number)

    if not data:
        raise HTTPException(status_code=404, detail="Episode not found")

    return data


# =========================
# FULL SHOW DATA
# =========================

@app.get("/tv/{tv_id}/full")
def get_full_show(tv_id: int):

    seasons = tmdb_service.get_seasons(tv_id)

    if not seasons:
        return {"tv_id": tv_id, "seasons": []}

    full_data = []

    for season in seasons:

        season_number = season["season_number"]

        episodes = tmdb_service.get_season_episodes(tv_id, season_number)

        full_data.append({
            "season_number": season_number,
            "episodes": episodes.get("episodes", [])
        })

    return {
        "tv_id": tv_id,
        "seasons": full_data
    }


# =========================
# CONTENT RATING (Movies / Shows)
# =========================

@app.post("/rate")
def rate_content(data: ContentRatingCreate, db: Session = Depends(get_db)):
    """Rate a movie or TV show 1-10."""
    
    # We enforce a pseudo user ID for now, normally grabbed from Auth token
    user_id = 1

    # Check for existing vote
    existing = db.query(models.ContentRating).filter(
        models.ContentRating.user_id == user_id,
        models.ContentRating.content_id == data.content_id,
        models.ContentRating.content_type == data.content_type
    ).first()

    if existing:
        existing.rating_value = data.rating
        db.commit()
    else:
        new_rating = models.ContentRating(
            user_id=user_id,
            content_id=data.content_id,
            content_type=data.content_type,
            rating_value=data.rating
        )
        db.add(new_rating)
        db.commit()

    # Recalculate average immediately
    ratings = db.query(models.ContentRating.rating_value).filter(
        models.ContentRating.content_id == data.content_id,
        models.ContentRating.content_type == data.content_type
    ).all()
    
    vals = [float(r[0]) for r in ratings]
    avg = sum(vals) / len(vals) if vals else 0.0

    return {
        "average_rating": round(float(avg), 1),
        "total_votes": len(vals)
    }

@app.get("/rating/{content_type}/{content_id}")
def get_rating(content_type: str, content_id: int, db: Session = Depends(get_db)):
    """Get the current rating average and total votes."""
    
    ratings = db.query(models.ContentRating.rating_value).filter(
        models.ContentRating.content_id == content_id,
        models.ContentRating.content_type == content_type
    ).all()
    
    if not ratings:
        return {
            "average_rating": 0.0,
            "total_votes": 0
        }
        
    vals = [float(r[0]) for r in ratings]
    avg = sum(vals) / len(vals)
    
    return {
        "average_rating": round(float(avg), 1),
        "total_votes": len(vals)
    }

# =========================
# USER DISCOVERY ROUTES (Top Rated, Most Rated, Trending)
# =========================

@app.get("/top-rated")
@app.get("/community/top-rated")
def get_user_top_rated(db: Session = Depends(get_db)):
    results = db.query(
        models.ContentRating.content_id,
        models.ContentRating.content_type,
        func.avg(models.ContentRating.rating_value).label('avg_rating'),
        func.count(models.ContentRating.id).label('vote_count')
    ).group_by(
        models.ContentRating.content_id, 
        models.ContentRating.content_type
    ).having(
        func.count(models.ContentRating.id) >= 20
    ).order_by(
        func.avg(models.ContentRating.rating_value).desc()
    ).limit(20).all()
    
    response = []
    for r in results:
        details = tmdb_service.get_details(r.content_type, r.content_id)
        if details:
            avg_val = float(r.avg_rating) if r.avg_rating else 0.0
            response.append({
                "id": r.content_id,
                "type": r.content_type,
                "title": str(details.get("title") or details.get("name") or "Unknown"),
                "poster": details.get("poster_path"),
                "average_rating": round(float(avg_val), 1),
                "votes": int(r.vote_count)
            })
    return response

@app.get("/most-rated")
def get_most_rated(db: Session = Depends(get_db)):
    results = db.query(
        models.ContentRating.content_id,
        models.ContentRating.content_type,
        func.avg(models.ContentRating.rating_value).label('avg_rating'),
        func.count(models.ContentRating.id).label('vote_count')
    ).group_by(
        models.ContentRating.content_id, 
        models.ContentRating.content_type
    ).order_by(
        func.count(models.ContentRating.id).desc()
    ).limit(20).all()
    
    response = []
    for r in results:
        details = tmdb_service.get_details(r.content_type, r.content_id)
        if details:
            avg_val = float(r.avg_rating) if r.avg_rating else 0.0
            response.append({
                "id": r.content_id,
                "type": r.content_type,
                "title": str(details.get("title") or details.get("name") or "Unknown"),
                "poster": details.get("poster_path"),
                "average_rating": round(float(avg_val), 1),
                "votes": int(r.vote_count)
            })
    return response

@app.get("/trending")
def get_user_trending(db: Session = Depends(get_db)):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    results = db.query(
        models.ContentRating.content_id,
        models.ContentRating.content_type,
        func.avg(models.ContentRating.rating_value).label('avg_rating'),
        func.count(models.ContentRating.id).label('recent_votes')
    ).filter(
        models.ContentRating.created_at >= seven_days_ago
    ).group_by(
        models.ContentRating.content_id, 
        models.ContentRating.content_type
    ).order_by(
        func.count(models.ContentRating.id).desc()
    ).limit(20).all()
    
    response = []
    for r in results:
        details = tmdb_service.get_details(r.content_type, r.content_id)
        if details:
            avg_val = float(r.avg_rating) if r.avg_rating else 0.0
            response.append({
                "id": r.content_id,
                "type": r.content_type,
                "title": details.get("title") or details.get("name") or "Unknown",
                "poster": details.get("poster_path"),
                "average_rating": round(avg_val, 1),
                "votes_last_7_days": r.recent_votes
            })
    return response


# =========================
# REVIEWS
# =========================

@app.post("/reviews/add")
def add_review(review: ReviewCreate, db: Session = Depends(get_db)):

    db_review = models.Review(
        user_id=review.user_id,
        content_id=review.content_id,
        content_type=review.content_type,
        media_type=review.content_type,
        season_number=review.season_number,
        episode_number=review.episode_number,
        rating=review.rating,
        review_text=review.review_text,
        date=datetime.now().isoformat()
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return db_review


@app.get("/reviews/get/{content_type}/{content_id}")
def get_reviews(
    content_type: str,
    content_id: int,
    season_number: Optional[int] = None,
    episode_number: Optional[int] = None,
    db: Session = Depends(get_db)
):

    query = db.query(models.Review).filter(
        models.Review.content_id == content_id,
        models.Review.content_type == content_type
    )

    if season_number is not None:
        query = query.filter(models.Review.season_number == season_number)

    if episode_number is not None:
        query = query.filter(models.Review.episode_number == episode_number)

    return query.all()



# ==================================
# FEATURE 1: RANDOM EPISODE
# ==================================

@app.get("/random-episode")
def random_episode():
    """Pick a random episode from a trending TV show."""
    data = tmdb_service.get_random_episode()

    if not data:
        raise HTTPException(status_code=404, detail="Could not find a random episode")

    return data


# ==================================
# FEATURE 3: CHARACTER RELATIONSHIPS
# ==================================

@app.get("/characters/{show_id}")
def get_characters(show_id: int):
    """Get characters and relationships for a TV show."""
    data = tmdb_service.get_characters(show_id)

    if not data or not data.get("characters"):
        raise HTTPException(status_code=404, detail="No characters found")

    return data


# ==================================
# FEATURE 4: WATCH EPISODE / ACHIEVEMENTS
# ==================================

@app.post("/watch-episode")
def watch_episode(data: WatchEpisodeCreate, db: Session = Depends(get_db)):
    """Mark an episode as watched for a user."""

    # Check if already watched
    existing = db.query(models.WatchedEpisode).filter(
        models.WatchedEpisode.user_id == data.user_id,
        models.WatchedEpisode.show_id == data.show_id,
        models.WatchedEpisode.season_number == data.season_number,
        models.WatchedEpisode.episode_number == data.episode_number,
    ).first()

    if existing:
        return {"message": "Already marked as watched", "id": existing.id}

    watched = models.WatchedEpisode(
        user_id=data.user_id,
        show_id=data.show_id,
        show_name=data.show_name,
        season_number=data.season_number,
        episode_number=data.episode_number,
        episode_name=data.episode_name,
    )

    db.add(watched)
    db.commit()
    db.refresh(watched)

    return {"message": "Episode marked as watched", "id": watched.id}


@app.get("/user-achievements/{user_id}")
def get_user_achievements(user_id: int, db: Session = Depends(get_db)):
    """Calculate achievements for a user based on watch history."""

    watched = db.query(models.WatchedEpisode).filter(
        models.WatchedEpisode.user_id == user_id
    ).all()

    total_episodes = len(watched)

    unique_shows = len(set(w.show_id for w in watched))

    # Define achievements
    achievements = []

    # Episode count achievements
    if total_episodes >= 1:
        achievements.append({
            "id": "first_step",
            "icon": "footprints",
            "title": "First Step",
            "description": "Watched your first episode",
            "unlocked": True
        })

    if total_episodes >= 10:
        achievements.append({
            "id": "binge_starter",
            "icon": "play_circle",
            "title": "Binge Starter",
            "description": "Watched 10 episodes",
            "unlocked": True
        })

    if total_episodes >= 20:
        achievements.append({
            "id": "binge_master",
            "icon": "local_fire_department",
            "title": "Binge Master",
            "description": "Watched 20 episodes",
            "unlocked": True
        })

    if total_episodes >= 50:
        achievements.append({
            "id": "tv_addict",
            "icon": "tv",
            "title": "TV Addict",
            "description": "Watched 50 episodes",
            "unlocked": True
        })

    if total_episodes >= 100:
        achievements.append({
            "id": "legendary_viewer",
            "icon": "emoji_events",
            "title": "Legendary Viewer",
            "description": "Watched 100 episodes",
            "unlocked": True
        })

    # Show diversity achievements
    if unique_shows >= 3:
        achievements.append({
            "id": "explorer",
            "icon": "explore",
            "title": "Explorer",
            "description": "Watched 3 different shows",
            "unlocked": True
        })

    if unique_shows >= 10:
        achievements.append({
            "id": "series_explorer",
            "icon": "travel_explore",
            "title": "Series Explorer",
            "description": "Watched 10 different shows",
            "unlocked": True
        })

    if unique_shows >= 25:
        achievements.append({
            "id": "genre_master",
            "icon": "military_tech",
            "title": "Genre Master",
            "description": "Watched 25 different shows",
            "unlocked": True
        })

    # Locked achievements (goals to work toward)
    locked_achievements = [
        {
            "id": "first_step",
            "icon": "footprints",
            "title": "First Step",
            "description": "Watch your first episode",
            "unlocked": False,
            "progress": f"{min(total_episodes, 1)}/1"
        },
        {
            "id": "binge_starter",
            "icon": "play_circle",
            "title": "Binge Starter",
            "description": "Watch 10 episodes",
            "unlocked": False,
            "progress": f"{min(total_episodes, 10)}/10"
        },
        {
            "id": "binge_master",
            "icon": "local_fire_department",
            "title": "Binge Master",
            "description": "Watch 20 episodes",
            "unlocked": False,
            "progress": f"{min(total_episodes, 20)}/20"
        },
        {
            "id": "tv_addict",
            "icon": "tv",
            "title": "TV Addict",
            "description": "Watch 50 episodes",
            "unlocked": False,
            "progress": f"{min(total_episodes, 50)}/50"
        },
        {
            "id": "legendary_viewer",
            "icon": "emoji_events",
            "title": "Legendary Viewer",
            "description": "Watch 100 episodes",
            "unlocked": False,
            "progress": f"{min(total_episodes, 100)}/100"
        },
        {
            "id": "explorer",
            "icon": "explore",
            "title": "Explorer",
            "description": "Watch 3 different shows",
            "unlocked": False,
            "progress": f"{min(unique_shows, 3)}/3"
        },
        {
            "id": "series_explorer",
            "icon": "travel_explore",
            "title": "Series Explorer",
            "description": "Watch 10 different shows",
            "unlocked": False,
            "progress": f"{min(unique_shows, 10)}/10"
        },
        {
            "id": "genre_master",
            "icon": "military_tech",
            "title": "Genre Master",
            "description": "Watch 25 different shows",
            "unlocked": False,
            "progress": f"{min(unique_shows, 25)}/25"
        },
    ]

    # Merge: show unlocked ones first, then locked ones that aren't achieved yet
    unlocked_ids = set(a["id"] for a in achievements)
    for la in locked_achievements:
        if la["id"] not in unlocked_ids:
            achievements.append(la)

    return {
        "user_id": user_id,
        "total_episodes_watched": total_episodes,
        "unique_shows_watched": unique_shows,
        "achievements": achievements,
        "recent_watches": [
            {
                "show_id": w.show_id,
                "show_name": w.show_name,
                "season": w.season_number,
                "episode": w.episode_number,
                "episode_name": w.episode_name,
                "watched_at": w.created_at.isoformat() if w.created_at else ""
            }
            for w in sorted(watched, key=lambda x: x.created_at or datetime.min, reverse=True)[:20]
        ]
    }


# ==================================
# FEATURE 5: MOOD RECOMMENDATIONS
# ==================================

@app.get("/recommendations")
def get_recommendations(mood: str):
    """Return TV show recommendations based on mood."""
    valid_moods = ["happy", "thriller", "mind-bending", "emotional", "action"]

    if mood.lower() not in valid_moods:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mood. Choose from: {', '.join(valid_moods)}"
        )

    results = tmdb_service.get_mood_recommendations(mood)

    return {"mood": mood, "results": results}


# =========================
# BECAUSE YOU WATCHED (AI RECOMMENDATIONS)
# =========================

@app.post("/watch")
def add_watch_history(data: WatchHistoryCreate, db: Session = Depends(get_db)):
    """Save watched content for AI recommendations."""
    if data.content_type not in ["movie", "tv", "anime"]:
        raise HTTPException(status_code=400, detail="Invalid content type")
        
    existing = db.query(models.WatchHistory).filter(
        models.WatchHistory.user_id == data.user_id,
        models.WatchHistory.content_id == data.content_id,
        models.WatchHistory.content_type == data.content_type
    ).first()
    
    if existing:
        existing.watched_at = datetime.utcnow()
    else:
        new_watch = models.WatchHistory(
            user_id=data.user_id,
            content_id=data.content_id,
            content_type=data.content_type
        )
        db.add(new_watch)
        
    db.commit()
    return {"message": "Watch history updated"}


@app.get("/recommendations/{user_id}")
def get_user_recommendations(user_id: int, db: Session = Depends(get_db)):
    """AI-style 'Because You Watched' recommendations."""
    watched = db.query(models.WatchHistory).filter(
        models.WatchHistory.user_id == user_id
    ).order_by(models.WatchHistory.watched_at.desc()).limit(5).all()
    
    if not watched:
        return []
        
    watched_ids = {w.content_id for w in db.query(models.WatchHistory).filter(models.WatchHistory.user_id == user_id).all()}
    
    recommendations = []
    seen_recs = set()
    
    for w in watched:
        # Use TMDB to find similar content (by keywords, genre, cast)
        recs = tmdb_service.get_smart_recommendations(w.content_type, w.content_id)
        
        # Determine source title for frontend display
        source_details = tmdb_service.get_details(w.content_type, w.content_id)
        source_title = source_details.get("title") or source_details.get("name") or "Unknown" if source_details else "Unknown"
        
        for r in recs:
            r_id = r.get("id")
            if r_id not in watched_ids and r_id not in seen_recs:
                seen_recs.add(r_id)
                
                recommendations.append({
                    "id": r_id,
                    "type": w.content_type,
                    "title": r.get("title") or r.get("name") or "Unknown",
                    "poster": r.get("poster_path"),
                    "rating": round(r.get("vote_average", 0.0), 1) if r.get("vote_average") else 0.0,
                    "popularity": r.get("popularity", 0.0),
                    "reason_title": source_title
                })
                
    # Sort first by popularity, then rating
    recommendations.sort(key=lambda x: (x["popularity"], x["rating"]), reverse=True)
    
    return recommendations[:20]


# =========================
# WATCHLIST
# =========================

@app.post("/watchlist/add")
def add_to_watchlist(data: WatchlistAdd, db: Session = Depends(get_db)):

    item = models.Watchlist(
        user_id=data.user_id,
        content_id=data.content_id,
        media_type=data.media_type
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {"message": "Added to watchlist", "data": item}


@app.get("/watchlist/{user_id}")
def get_watchlist(user_id: int, db: Session = Depends(get_db)):

    return db.query(models.Watchlist).filter(
        models.Watchlist.user_id == user_id
    ).all()


# =========================
# AUTH
# =========================

@app.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):

    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created", "user_id": new_user.id}


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = auth.create_access_token({"user_id": db_user.id})

    return {
        "access_token": token,
        "user_id": db_user.id
    }