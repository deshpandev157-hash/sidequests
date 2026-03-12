from fastapi import APIRouter
import tmdb_service

router = APIRouter(prefix="/bollywood", tags=["Bollywood"])

@router.get("/trending")
def get_bollywood_trending():
    data = tmdb_service.get_trending_bollywood()
    results = []
    
    for item in data[:20]:
        results.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "type": "movie",
            "poster_path": item.get("poster_path"),
            "release_date": item.get("release_date"),
            "vote_average": item.get("vote_average")
        })
        
    return results
