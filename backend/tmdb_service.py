import os
import random
import requests
from dotenv import load_dotenv
from pathlib import Path


# =========================
# LOAD ENV VARIABLES
# =========================

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    print("[ERROR] TMDB API KEY NOT FOUND")
else:
    print("[OK] TMDB KEY LOADED")


BASE_URL = "https://api.themoviedb.org/3"


# =========================
# GENERIC TMDB REQUEST
# =========================

def tmdb_request(endpoint, params=None):

    if params is None:
        params = {}

    params["api_key"] = TMDB_API_KEY

    url = f"{BASE_URL}{endpoint}"

    try:

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print("TMDB Error:", response.status_code)
            return {"results": []}

        return response.json()

    except Exception as e:
        print("Request Error:", e)
        return {"results": []}


# =========================
# TRENDING
# =========================

def get_trending(media_type="all", time_window="day"):

    data = tmdb_request(f"/trending/{media_type}/{time_window}")

    return data


# =========================
# SEARCH
# =========================

def search_content(query):

    params = {
        "query": query,
        "include_adult": False
    }

    return tmdb_request("/search/multi", params)


# =========================
# DETAILS
# =========================

def get_details(media_type, content_id):

    params = {
        "append_to_response": "credits,videos"
    }

    return tmdb_request(f"/{media_type}/{content_id}", params)


# =========================
# GET TV SEASONS
# =========================

def get_seasons(tv_id):

    data = tmdb_request(f"/tv/{tv_id}")

    seasons = data.get("seasons", [])

    seasons = [s for s in seasons if s.get("season_number") != 0]

    return seasons


# =========================
# SEASON EPISODES
# =========================

def get_season_episodes(tv_id, season_number):

    data = tmdb_request(f"/tv/{tv_id}/season/{season_number}")

    episodes = data.get("episodes", [])

    formatted = []

    for ep in episodes:

        formatted.append({
            "episode_id": ep.get("id"),
            "episode_number": ep.get("episode_number"),
            "name": ep.get("name"),
            "overview": ep.get("overview"),
            "still_path": ep.get("still_path"),
            "vote_average": ep.get("vote_average"),
            "air_date": ep.get("air_date")
        })

    return {
        "season_number": season_number,
        "episodes": formatted
    }


# =========================
# EPISODE DETAILS
# =========================

def get_episode_details(tv_id, season_number, episode_number):

    params = {
        "append_to_response": "credits,videos"
    }

    return tmdb_request(
        f"/tv/{tv_id}/season/{season_number}/episode/{episode_number}",
        params
    )


# =========================
# RANDOM EPISODE
# =========================

def get_random_episode():
    """Pick a random trending TV show, then a random episode from it."""
    try:
        trending = get_trending("tv", "week")
        shows = trending.get("results", [])

        if not shows:
            return None

        # Try up to 5 shows in case one has no seasons
        for _ in range(5):
            show = random.choice(shows)
            show_id = show.get("id")
            show_name = show.get("name", "Unknown")

            seasons = get_seasons(show_id)
            if not seasons:
                continue

            season = random.choice(seasons)
            season_number = season.get("season_number", 1)

            ep_data = get_season_episodes(show_id, season_number)
            episodes = ep_data.get("episodes", [])

            if not episodes:
                continue

            episode = random.choice(episodes)

            return {
                "show_id": show_id,
                "show_name": show_name,
                "season": season_number,
                "episode": episode.get("episode_number", 1),
                "title": episode.get("name", "Unknown Episode"),
                "poster_path": show.get("poster_path"),
                "still_path": episode.get("still_path"),
                "vote_average": episode.get("vote_average")
            }

        return None

    except Exception as e:
        print("Random Episode Error:", e)
        return None



# =========================
# CHARACTERS / CAST
# =========================

def get_characters(show_id):
    """Get cast for a TV show and generate relationship data."""
    try:
        data = tmdb_request(f"/tv/{show_id}/credits")
        cast_full = list(data.get("cast", []))
        cast_list = cast_full[:20]

        if not cast_list:
            return {"characters": []}

        characters = []
        cast_names = [c.get("name", "") for c in cast_list]

        for i, member in enumerate(cast_list):
            name = member.get("name", f"Character {i}")
            character = member.get("character", "Unknown Role")
            image = member.get("profile_path")

            # Generate plausible relationships based on cast order proximity
            relationships = []
            for j, other in enumerate(cast_list):
                if i == j:
                    continue
                other_name = other.get("name", "")

                # Characters close in cast order are more likely related
                distance = abs(i - j)
                if distance <= 2:
                    rel_type = random.choice(["ally", "family", "colleague"])
                    relationships.append({
                        "target": other_name,
                        "type": rel_type
                    })
                elif distance <= 4 and random.random() > 0.5:
                    rel_type = random.choice(["rival", "friend", "acquaintance"])
                    relationships.append({
                        "target": other_name,
                        "type": rel_type
                    })

            characters.append({
                "name": name,
                "character": character,
                "image": f"https://image.tmdb.org/t/p/w185{image}" if image else None,
                "relationships": relationships
            })

        return {"characters": characters}

    except Exception as e:
        print("Characters Error:", e)
        return {"characters": []}


# =========================
# MOOD RECOMMENDATIONS
# =========================

MOOD_GENRE_MAP = {
    "happy": [35, 10751, 16],       # Comedy, Family, Animation
    "thriller": [53, 80, 9648],      # Thriller, Crime, Mystery
    "mind-bending": [878, 14, 9648], # Sci-Fi, Fantasy, Mystery
    "emotional": [18, 10749, 10751], # Drama, Romance, Family
    "action": [28, 10759, 10752],    # Action, Action&Adventure, War
}

def get_mood_recommendations(mood):
    """Return TV shows matching a mood using TMDB genre discovery."""
    try:
        genre_ids = MOOD_GENRE_MAP.get(mood.lower(), [18])

        # Use discover/tv with genre filtering
        params = {
            "with_genres": ",".join(str(g) for g in genre_ids),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 100,
            "page": 1
        }

        data = tmdb_request("/discover/tv", params)
        res_list = list(data.get("results", []))
        results = res_list[:12]

        # Add media_type for frontend card rendering
        for item in results:
            item["media_type"] = "tv"

        return results

    except Exception as e:
        print("Mood Recommendations Error:", e)
        return []

# =========================
# SMART RECOMMENDATIONS
# =========================

def get_smart_recommendations(media_type, content_id):
    """
    Get similar items using TMDB's recommendations endpoint first,
    which factors in keywords, cast, and genres.
    Fallback to similar endpoint if not enough results.
    """
    try:
        data = tmdb_request(f"/{media_type}/{content_id}/recommendations")
        recs = data.get("results", [])
        
        if len(recs) < 5:
            similar = tmdb_request(f"/{media_type}/{content_id}/similar")
            recs.extend(similar.get("results", []))
            
        return recs
    except Exception as e:
        print("Smart Recommendations Error:", e)
        return []

# =========================
# BOLLYWOOD SECTION
# =========================

def get_trending_bollywood():
    """Fetch trending Bollywood movies (Hindi language, India region)."""
    try:
        # Fetching popular Hindi movies from India
        params = {
            "with_original_language": "hi",
            "region": "IN",
            "sort_by": "popularity.desc"
        }
        data = tmdb_request("/discover/movie", params)
        return data.get("results", [])
    except Exception as e:
        print("Bollywood Trending Error:", e)
        return []


# =========================
# BLUR GUESS GAME
# =========================

def get_blur_game_item(category):
    """Fetch a random item for the blur guess game based on category."""
    try:
        page = random.randint(1, 5)
        params = {"page": page}
        endpoint = "/movie/popular"
        
        if category == 'bollywood':
            endpoint = "/discover/movie"
            params.update({"with_original_language": "hi", "region": "IN"})
        elif category == 'tv':
            endpoint = "/tv/popular"
        elif category == 'anime':
            endpoint = "/discover/tv"
            params.update({"with_genres": "16", "with_original_language": "ja"})
        elif category == 'hollywood':
            endpoint = "/discover/movie"
            params.update({"with_original_language": "en"})

        data = tmdb_request(endpoint, params)
        results = data.get("results", [])
        
        if not results:
            # Fallback to simple popular if no results
            data = tmdb_request("/movie/popular", {"page": 1})
            results = data.get("results", [])
            
        item = random.choice(results)
        
        # Determine title (movies use title, tv uses name)
        title = item.get("title") or item.get("name")
        image = item.get("poster_path") or item.get("backdrop_path")
        
        return {
            "title": title,
            "image": image,
            "id": item.get("id")
        }
    except Exception as e:
        print("Blur Game Item Error:", e)
        return None


# =========================
# SCENE GUESS GAME
# =========================

def get_scene_guess_item(category):
    """Fetch a random item with a backdrop/still for the scene guess game."""
    try:
        page = random.randint(1, 10)
        params = {"page": page}
        endpoint = "/movie/popular"
        
        if category == 'bollywood':
            endpoint = "/discover/movie"
            params.update({"with_original_language": "hi", "region": "IN"})
        elif category == 'tv':
            endpoint = "/tv/popular"
        elif category == 'anime':
            endpoint = "/discover/tv"
            params.update({"with_genres": "16", "with_original_language": "ja"})
        elif category == 'hollywood':
            endpoint = "/discover/movie"
            params.update({"with_original_language": "en"})

        data = tmdb_request(endpoint, params)
        results = [r for r in data.get("results", []) if r.get("backdrop_path")]
        
        if not results:
            data = tmdb_request("/movie/popular", {"page": 1})
            results = [r for r in data.get("results", []) if r.get("backdrop_path")]
            
        if not results:
            return None
            
        item = random.choice(results)
        
        title = item.get("title") or item.get("name")
        image = item.get("backdrop_path")
        
        return {
            "title": title,
            "image": image,
            "id": item.get("id")
        }
    except Exception as e:
        print("Scene Game Item Error:", e)
        return None