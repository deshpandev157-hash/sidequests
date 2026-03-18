const API_BASE = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost" ? "http://127.0.0.1:8001" : "https://sidequests-8.onrender.com";
console.log("API_BASE:", API_BASE);

const IMAGE_BASE = "https://image.tmdb.org/t/p/w500";

/**
 * Generic API fetch helper
 */
async function apiFetch(url) {
    try {
        const res = await fetch(API_BASE + url);
        if (!res.ok) {
            console.error("API Error:", url);
            return null;
        }
        return await res.json();
    } catch (err) {
        console.error("Network Error:", err);
        return null;
    }
}

const api = {
    /**
     * AUTHENTICATION
     */
    async signup(data) {
        try {
            const res = await fetch(`${API_BASE}/auth/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            return await res.json();
        } catch (err) {
            console.error("Signup error:", err);
            return null;
        }
    },

    async login(data) {
        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            return await res.json();
        } catch (err) {
            console.error("Login error:", err);
            return null;
        }
    },

    /**
     * GET /trending/{type}
     */
    async getTrending(type = "all") {
        return await apiFetch(`/trending/${type}`);
    },

    /**
     * GET /search?query=
     */
    async search(query) {
        if (!query) return [];
        const data = await apiFetch(`/search?query=${encodeURIComponent(query)}`);
        return data || [];
    },

    /**
     * GET /content/{type}/{id}
     */
    async getDetails(type, id) {
        if (!type || !id) return null;
        return await apiFetch(`/content/${type}/${id}`);
    },

    /**
     * GET /tv/{tvId}/seasons
     */
    async getSeasons(tvId) {
        if (!tvId) return [];
        const data = await apiFetch(`/tv/${tvId}/seasons`);
        return data || [];
    },

    /**
     * GET /tv/{tvId}/season/{season}
     */
    async getEpisodes(tvId, season) {
        if (!tvId || season === undefined) return [];
        const data = await apiFetch(`/tv/${tvId}/season/${season}`);

        // Correct comparison: use .length, not === []
        if (!data || !data.episodes || data.episodes.length === 0) {
            return [];
        }
        return data.episodes;
    },

    /**
     * GET /tv/{tvId}/season/{season}/episode/{episode}
     */
    async getEpisodeDetails(tvId, season, episode) {
        if (!tvId || season === undefined || !episode) return null;
        return await apiFetch(`/tv/${tvId}/season/${season}/episode/${episode}`);
    },

    /**
     * POST /reviews/add (Optional but implemented for completeness)
     */
    async addReview(reviewData) {
        if (!reviewData) return null;
        try {
            const res = await fetch(`${API_BASE}/reviews/add`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(reviewData)
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (err) {
            console.error("Add Review Error:", err);
            return null;
        }
    },

    /**
     * GET /reviews/get/{media_type}/{content_id}
     */
    async getReviews(mediaType, contentId, season = null, episode = null) {
        if (!mediaType || !contentId) return [];
        let url = `/reviews/get/${mediaType}/${contentId}`;
        const params = new URLSearchParams();
        if (season !== null) params.append("season_number", season);
        if (episode !== null) params.append("episode_number", episode);

        if (params.toString()) {
            url += "?" + params.toString();
        }
        return await apiFetch(url) || [];
    },

    /**
     * Helper: Construct Image URL
     */
    getImageUrl(path, size = "w500") {
        const fallback = "https://placehold.co/500x750?text=No+Poster";

        if (!path) return fallback;

        const base = "https://image.tmdb.org/t/p/";
        return `${base}${size}${path}`;
    },

    /**
     * Helper: Create Media Card HTML
     */
    createMediaCard(item) {
        if (!item) return "";
        const title = item.title || item.name || "Unknown";
        const date = item.release_date || item.first_air_date || "";
        const year = date ? date.split("-")[0] : "";
        const rating = item.vote_average ? item.vote_average.toFixed(1) : "N/A";

        let type = "movie";
        if (item.media_type) {
            type = item.media_type;
        } else if (item.first_air_date || item.name) {
            type = "tv";
        } else if (item.release_date || item.title) {
            type = "movie";
        }

        return `
            <div class="card" onclick="window.location.href='details.html?type=${type}&id=${item.id}'">
                <img src="${this.getImageUrl(item.poster_path)}"
onerror="this.src='https://placehold.co/500x750?text=No+Poster'"
alt="${title.replace(/"/g, '&quot;')}">
                <div class="card-content">
                    <div class="card-title">${title}</div>
                    <div class="card-meta">
                        <span>${year}</span>
                        <span class="rating">★ ${rating}</span>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * FEATURE 1: Random Episode
     */
    async getRandomEpisode() {
        return await apiFetch(`/random-episode`);
    },


    /**
     * FEATURE 3: Character Relationships
     */
    async getCharacters(showId) {
        if (!showId) return null;
        return await apiFetch(`/characters/${showId}`);
    },

    /**
     * FEATURE 4: Watch Episode (Achievements)
     */
    async watchEpisode(watchData) {
        if (!watchData) return null;
        try {
            const res = await fetch(`${API_BASE}/watch-episode`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(watchData)
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (err) {
            console.error("Watch Episode Error:", err);
            return null;
        }
    },

    async getUserAchievements(userId = 1) { // Defaulting user_id to 1 for now
        return await apiFetch(`/user-achievements/${userId}`);
    },

    /**
     * FEATURE 5: Mood Based Recommendations
     */
    async getMoodRecommendations(mood) {
        if (!mood) return null;
        return await apiFetch(`/recommendations?mood=${encodeURIComponent(mood)}`);
    },

    /**
     * CONTENT RATINGS
     */
    async rateContent(ratingData) {
        if (!ratingData) return null;
        try {
            const res = await fetch(`${API_BASE}/rate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(ratingData)
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (err) {
            console.error("Rate Content Error:", err);
            return null;
        }
    },

    async getContentRating(contentType, contentId) {
        if (!contentType || !contentId) return null;
        return await apiFetch(`/rating/${contentType}/${contentId}`);
    },

    /**
     * USER DISCOVERY (Home Page)
     */
    async getUserTopRated() {
        return await apiFetch(`/top-rated`);
    },

    async getMostRated() {
        return await apiFetch(`/most-rated`);
    },

    async getUserTrending() {
        return await apiFetch(`/trending`);
    },

    /**
     * BECAUSE YOU WATCHED (AI RECOMMENDATIONS)
     */
    async addToWatchHistory(data) {
        if (!data) return null;
        try {
            const res = await fetch(`${API_BASE}/watch`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (err) {
            console.error("Watch History Error:", err);
            return null;
        }
    },

    async getBecauseYouWatched(userId) {
        return await apiFetch(`/recommendations/${userId}`);
    },

    /**
     * COMMUNITY FEATURES
     */
    async getCommunityTopRated() {
        return await apiFetch(`/community/top-rated`);
    },

    async getTrendingDiscussions() {
        return await apiFetch(`/discussions/trending`);
    },

    async getMoodMovieFinder(mood) {
        return await apiFetch(`/discover/mood/${encodeURIComponent(mood)}`);
    },

    async getCurrentAwards() {
        return await apiFetch(`/awards/current`);
    },

    async voteAward(data) {
        if (!data) return null;
        try {
            const res = await fetch(`${API_BASE}/awards/vote`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (err) {
            console.error("Vote Award Error:", err);
            return null;
        }
    },

    async submitCommunityReview(data) {
        if (!data) return null;
        try {
            const res = await fetch(`${API_BASE}/reviews`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (err) {
            console.error("Review Error:", err);
            return null;
        }
    },

    async getCommunityReviews(contentType, contentId) {
        if (!contentType || !contentId) return [];
        return await apiFetch(`/reviews/${contentType}/${contentId}`) || [];
    },

    async likeReview(reviewId, userId) {
        try {
            const res = await fetch(`${API_BASE}/reviews/${reviewId}/like?user_id=${userId}`, {
                method: "POST"
            });
            if (!res.ok) return null;
            return await res.json();
        } catch (err) {
            console.error("Like Review Error:", err);
            return null;
        }
    },

    /**
     * AI INTERACTIVE FEATURES
     */
    async getAIRandomMovie() {
        return await apiFetch(`/discover/random`);
    },

    async getGuessGame() {
        return await apiFetch(`/games/guess-movie`);
    },

    async submitGuessAnswer(gameId, answer) {
        try {
            const res = await fetch(`${API_BASE}/games/guess-movie/answer`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ game_id: gameId, answer: answer })
            });
            return await res.json();
        } catch (err) {
            console.error("Guess game error:", err);
            return null;
        }
    },

    async getDailyQuiz() {
        return await apiFetch(`/quiz/today`);
    },

    async submitQuizAnswer(quizId, answer) {
        try {
            const res = await fetch(`${API_BASE}/quiz/answer`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ quiz_id: quizId, answer: answer })
            });
            return await res.json();
        } catch (err) {
            console.error("Quiz error:", err);
            return null;
        }
    },

    async generateNewQuiz() {
        try {
            const res = await fetch(`${API_BASE}/quiz/generate`, { method: "POST" });
            return await res.json();
        } catch (err) {
            console.error("Quiz generation error:", err);
            return null;
        }
    },

    async getChallenges() {
        return await apiFetch(`/challenges`);
    },

    async shuffleChallenges() {
        try {
            const res = await fetch(`${API_BASE}/challenges/shuffle`, {
                method: "POST"
            });
            return await res.json();
        } catch (err) {
            console.error("Shuffle challenges error:", err);
            return null;
        }
    },

    async updateChallengeProgress(challengeId, userId = 1) {
        try {
            const res = await fetch(`${API_BASE}/challenges/progress`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, challenge_id: challengeId })
            });
            return await res.json();
        } catch (err) {
            console.error("Challenge progress error:", err);
            return null;
        }
    },

    async getHiddenGems() {
        return await apiFetch(`/discover/hidden-gems`);
    },

    async getMovieDebate(type, id) {
        return await apiFetch(`/ai/movie-debate/${type}/${id}`);
    },

    /**
     * FEATURE: Trending Bollywood
     */
    async getTrendingBollywood() {
        return await apiFetch(`/bollywood/trending`);
    },

    /**
     * FEATURE: Blur Guess Challenge
     */
    async getBlurGuessChallenge(category = 'hollywood') {
        const url = `/games/blur-guess?category=${encodeURIComponent(category)}`;
        return await apiFetch(url);
    },

    /**
     * FEATURE: Scene Guess Game
     */
    async getSceneGuessChallenge(category = 'hollywood') {
        const url = `/games/scene-guess?category=${encodeURIComponent(category)}`;
        return await apiFetch(url);
    },

    async getSpinRecommendation(category) {
        return await apiFetch(`/discover/spin-recommend?category=${encodeURIComponent(category)}`);
    }
};
