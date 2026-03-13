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
# IMAGE BASE URLS
# =========================

IMAGE_BASE = "https://image.tmdb.org/t/p"
POSTER_SIZE = "w500"
PROFILE_SIZE = "w185"
BACKDROP_SIZE = "original"


def get_image_url(path, size=POSTER_SIZE):
    if not path:
        return None
    return f"{IMAGE_BASE}/{size}{path}"


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
    results = data.get("results", [])

    for item in results:
        item["poster_path"] = get_image_url(item.get("poster_path"))
        item["backdrop_path"] = get_image_url(item.get("backdrop_path"), BACKDROP_SIZE)

    return {"results": results}


# =========================
# SEARCH
# =========================

def search_content(query):

    params = {
        "query": query,
        "include_adult": False
    }

    data = tmdb_request("/search/multi", params)
    results = data.get("results", [])

    for item in results:
        item["poster_path"] = get_image_url(item.get("poster_path"))

    return {"results": results}


# =========================
# DETAILS
# =========================

def get_details(media_type, content_id):

    params = {
        "append_to_response": "credits,videos"
    }

    data = tmdb_request(f"/{media_type}/{content_id}", params)

    data["poster_path"] = get_image_url(data.get("poster_path"))
    data["backdrop_path"] = get_image_url(data.get("backdrop_path"), BACKDROP_SIZE)

    return data


# =========================
# GET TV SEASONS
# =========================

def get_seasons(tv_id):

    data = tmdb_request(f"/tv/{tv_id}")

    seasons = data.get("seasons", [])
    seasons = [s for s in seasons if s.get("season_number") != 0]

    for s in seasons:
        s["poster_path"] = get_image_url(s.get("poster_path"))

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
            "still_path": get_image_url(ep.get("still_path"), BACKDROP_SIZE),
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

    data = tmdb_request(
        f"/tv/{tv_id}/season/{season_number}/episode/{episode_number}",
        params
    )

    data["still_path"] = get_image_url(data.get("still_path"), BACKDROP_SIZE)

    return data


# =========================
# RANDOM EPISODE
# =========================

def get_random_episode():

    try:
        trending = get_trending("tv", "week")
        shows = trending.get("results", [])

        if not shows:
            return None

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
                "poster_path": get_image_url(show.get("poster_path")),
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

    try:

        data = tmdb_request(f"/tv/{show_id}/credits")
        cast_list = data.get("cast", [])[:20]

        characters = []

        for member in cast_list:

            characters.append({
                "name": member.get("name"),
                "character": member.get("character"),
                "image": get_image_url(member.get("profile_path"), PROFILE_SIZE)
            })

        return {"characters": characters}

    except Exception as e:
        print("Characters Error:", e)
        return {"characters": []}


# =========================
# MOOD RECOMMENDATIONS
# =========================

MOOD_GENRE_MAP = {
    "happy": [35, 10751, 16],
    "thriller": [53, 80, 9648],
    "mind-bending": [878, 14, 9648],
    "emotional": [18, 10749, 10751],
    "action": [28, 10759, 10752],
}


def get_mood_recommendations(mood):

    try:

        genre_ids = MOOD_GENRE_MAP.get(mood.lower(), [18])

        params = {
            "with_genres": ",".join(str(g) for g in genre_ids),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 100,
            "page": 1
        }

        data = tmdb_request("/discover/tv", params)
        results = data.get("results", [])[:12]

        for item in results:
            item["poster_path"] = get_image_url(item.get("poster_path"))
            item["media_type"] = "tv"

        return results

    except Exception as e:
        print("Mood Recommendations Error:", e)
        return []


# =========================
# SMART RECOMMENDATIONS
# =========================

def get_smart_recommendations(media_type, content_id):

    try:

        data = tmdb_request(f"/{media_type}/{content_id}/recommendations")
        recs = data.get("results", [])

        if len(recs) < 5:
            similar = tmdb_request(f"/{media_type}/{content_id}/similar")
            recs.extend(similar.get("results", []))

        for r in recs:
            r["poster_path"] = get_image_url(r.get("poster_path"))

        return recs

    except Exception as e:
        print("Smart Recommendations Error:", e)
        return []


# =========================
# BOLLYWOOD SECTION
# =========================

def get_trending_bollywood():

    try:

        params = {
            "with_original_language": "hi",
            "region": "IN",
            "sort_by": "popularity.desc"
        }

        data = tmdb_request("/discover/movie", params)
        results = data.get("results", [])

        for r in results:
            r["poster_path"] = get_image_url(r.get("poster_path"))

        return results

    except Exception as e:
        print("Bollywood Trending Error:", e)
        return []


# =========================
# BLUR GUESS GAME
# =========================

def get_blur_game_item(category):

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

        item = random.choice(results)

        title = item.get("title") or item.get("name")
        image = get_image_url(item.get("poster_path") or item.get("backdrop_path"), BACKDROP_SIZE)

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
            return None

        item = random.choice(results)

        title = item.get("title") or item.get("name")
        image = get_image_url(item.get("backdrop_path"), BACKDROP_SIZE)

        return {
            "title": title,
            "image": image,
            "id": item.get("id")
        }

    except Exception as e:
        print("Scene Game Item Error:", e)
        return None