# SideQuest

SideQuest is a dark-themed entertainment discovery platform where users can search for Movies, TV Shows, and Anime, view detailed information, and rate/review individual content. The application utilizes the TMDB API to fetch extensive entertainment data.

## Features
- **Trending:** View currently popular movies and TV shows/anime on the homepage.
- **Search:** Fully functional search for finding specific movies, TV shows, and animes.
- **Content Details:** Comprehensive detail pages showing posters, synopses, release dates, cast, and trailers.
- **TV Shows & Anime:** Structured season and episode browsing.
- **Reviews & Ratings:** Ability for users to leave reviews and 1-10 star ratings for movies, or specific individual episodes of TV Shows/Animes.

## Project Structure
- `backend/`: Python backend powered by FastAPI and SQLite for handling reviews and application API.
- `frontend/`: Vanilla HTML/CSS/JS frontend interacting with the backend.

## Requirements
- Python 3.9+
- A [TMDB API Key](https://developer.themoviedb.org/docs/getting-started)

## How to Run

### 1. Setup Backend
1. Open a terminal and navigate to the `backend` folder.
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your TMDB API Key. Create a `.env` file in the `backend` directory with:
   ```env
   TMDB_API_KEY=your_actual_api_key_here
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be running on `http://127.0.0.1:8000`

### 2. Setup Frontend
1. Open the `frontend` folder.
2. For testing, simply opening `index.html` in your web browser should work in most cases (as CORS is fully enabled on the backend).
3. If module issues happen or you prefer a local server, you can serve the frontend via python:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
4. Visit `http://localhost:8080` in your web browser to browse SideQuest!
