document.addEventListener('DOMContentLoaded', async () => {
    const moviesContainer = document.getElementById('trending-movies');
    const tvContainer = document.getElementById('trending-tv');

    try {
        const movies = await api.getTrending('movie');
        if (movies && movies.results && movies.results.length > 0) {
            moviesContainer.innerHTML = movies.results
                .slice(0, 10)
                .map(item => api.createMediaCard(item))
                .join('');
        } else {
            moviesContainer.innerHTML = '<p>No trending movies found.</p>';
        }
    } catch (err) {
        console.error("Failed to load trending movies:", err);
        moviesContainer.innerHTML = '<p>Failed to load trending movies. Is the backend running?</p>';
    }

    try {
        const tv = await api.getTrending('tv');
        if (tv && tv.results && tv.results.length > 0) {
            tvContainer.innerHTML = tv.results
                .slice(0, 10)
                .map(item => api.createMediaCard(item))
                .join('');
        } else {
            tvContainer.innerHTML = '<p>No trending TV shows found.</p>';
        }
    } catch (err) {
        console.error("Failed to load trending TV shows:", err);
        tvContainer.innerHTML = '<p>Failed to load trending TV shows.</p>';
    }
});

function performSearch() {
    const q = document.getElementById('searchInput').value;
    if (q.trim()) {
        window.location.href = `search.html?q=${encodeURIComponent(q.trim())}`;
    }
}

async function generateRandomEpisode() {
    const btn = document.getElementById("surpriseMeBtn");
    const loader = document.getElementById("random-loading");

    btn.style.display = "none";
    loader.style.display = "block";

    try {
        const ep = await api.getRandomEpisode();
        if (ep && ep.show_id) {
            window.location.href = `episode.html?show_id=${ep.show_id}&season=${ep.season}&episode=${ep.episode}`;
        } else {
            alert("Couldn't find a random episode. Please try again.");
            btn.style.display = "inline-block";
            loader.style.display = "none";
        }
    } catch (err) {
        console.error(err);
        alert("Server error finding a random episode.");
        btn.style.display = "inline-block";
        loader.style.display = "none";
    }
}


// LOAD USER DISCOVERY SECTIONS
async function loadUserDiscovery() {
    try {
        // 1. User Trending
        const trendingData = await api.getUserTrending();
        const trendingEl = document.getElementById("user-trending");
        if (trendingData && trendingData.length > 0) {
            trendingEl.innerHTML = trendingData.map(item => createUserDiscoveryCard(item, 'recent')).join('');
        } else {
            trendingEl.innerHTML = "<p>No trending content yet. Be the first to vote!</p>";
        }

        // 2. Top Rated
        const topRatedData = await api.getUserTopRated();
        const topRatedEl = document.getElementById("user-top-rated");
        if (topRatedData && topRatedData.length > 0) {
            topRatedEl.innerHTML = topRatedData.map(item => createUserDiscoveryCard(item, 'avg')).join('');
        } else {
            topRatedEl.innerHTML = "<p>No top rated content yet. Be the first to vote!</p>";
        }

        // 3. Most Rated
        const mostRatedData = await api.getMostRated();
        const mostRatedEl = document.getElementById("user-most-rated");
        if (mostRatedData && mostRatedData.length > 0) {
            mostRatedEl.innerHTML = mostRatedData.map(item => createUserDiscoveryCard(item, 'count')).join('');
        } else {
            mostRatedEl.innerHTML = "<p>No most rated content yet. Be the first to vote!</p>";
        }

    } catch (err) {
        console.error("Failed to load user discovery:", err);
    }
}

function createUserDiscoveryCard(item, displayMode) {
    let metaDisplay = "";
    let ratingVal = item.average_rating || item.rating || 0;

    if (displayMode === 'recent') {
        metaDisplay = `⭐ ${ratingVal.toFixed(1)} (${item.votes_last_7_days} recent votes)`;
    } else if (displayMode === 'count') {
        metaDisplay = `⭐ ${ratingVal.toFixed(1)} (${item.votes} total votes)`;
    } else if (displayMode === 'ai') {
        metaDisplay = `⭐ ${ratingVal.toFixed(1)} | Because you watched ${item.reason_title}`;
    } else if (displayMode === 'ai_gem') {
        metaDisplay = `⭐ ${ratingVal.toFixed(1)} | ${item.ai_reason}`;
    } else {
        metaDisplay = `⭐ ${ratingVal.toFixed(1)} (${item.votes} votes)`;
    }

    return `
        <div class="card" onclick="window.location.href='details.html?type=${item.type}&id=${item.id}'">
           <img src="${api.getImageUrl(item.poster)}"
alt="${item.title.replace(/"/g, '&quot;')}"
onerror="this.onerror=null;this.src='https://placehold.co/300x169?text=No+Image';">
            <div class="card-content">
                <div class="card-title">${item.title}</div>
                <div class="card-meta">
                    <span class="rating" style="color: #f5c518; font-weight: bold; width: 100%;">${metaDisplay}</span>
                </div>
            </div>
        </div>
    `;
}

// LOAD AI RECOMMENDATIONS
async function loadBecauseYouWatched() {
    try {
        const results = await api.getBecauseYouWatched(1); // User ID 1 mocking
        const container = document.getElementById("advanced-recs");

        if (results && results.length > 0) {
            container.innerHTML = results.map(item => createUserDiscoveryCard(item, 'ai')).join('');
        } else {
            container.innerHTML = "<p>Watch some movies to get personalized recommendations!</p>";
        }
    } catch (err) {
        console.error("AI Recs error:", err);
    }
}

// LOAD DISCUSSIONS
async function loadDiscussions() {
    try {
        const data = await api.getTrendingDiscussions();
        const container = document.getElementById("trending-discussions");
        if (data && data.length > 0) {
            container.innerHTML = data.map(item => {
                const d = new Date(item.last_activity).toLocaleDateString();
                return `
                    <div class="card" style="padding: 20px; background: #222; cursor: default;">
                        <h3 style="margin-bottom: 10px; font-size: 1.1em;">${item.title}</h3>
                        <p style="color: #aaa; font-size: 0.9em; margin-bottom: 15px;">Discussion about: <span style="color: var(--accent-color);">${item.related_title}</span></p>
                        <div style="display: flex; justify-content: space-between; font-size: 0.85em; color: #888;">
                            <span>💬 ${item.comment_count} Comments (${item.recent_comments} new)</span>
                            <span>Active: ${d}</span>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = "<p>No trending discussions currently.</p>";
        }
    } catch (e) {
        console.error("Discussion load error:", e);
    }
}

// LOAD OVERALL AWARDS
async function loadCommunityAwards() {
    try {
        const data = await api.getCurrentAwards();
        const container = document.getElementById("community-awards");
        if (data && data.length > 0) {
            container.innerHTML = data.map(item => `
                <div class="card" style="text-align: center;">
                    <img src="${api.getImageUrl(item.poster)}" alt="${item.title.replace(/"/g, '&quot;')}">
                    <div class="card-content">
                        <div style="color: gold; font-weight: bold; margin-bottom: 5px; font-size: 0.85em; text-transform: uppercase;">${item.category}</div>
                        <div class="card-title" style="font-size: 1.1em; margin-bottom: 10px;">${item.title}</div>
                        <div style="margin-bottom: 15px; color: #ccc;">${item.votes} Votes</div>
                        <button class="btn" style="width: 100%; border-radius: 5px;" onclick="castAwardVote(${item.id})">Vote for this</button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = "<p>No awards scheduled for this week.</p>";
        }
    } catch (e) {
        console.error("Awards load error:", e);
    }
}

async function castAwardVote(awardId) {
    const pass = confirm("Cast your vote for this feature?");
    if (!pass) return;
    const res = await api.voteAward({ user_id: 1, award_id: awardId });
    if (res && res.message) {
        alert(res.message);
        loadCommunityAwards(); // Reload votes
    } else {
        alert("Failed to vote, you may have already voted.");
    }
}


// --- AI CHALLENGES ---
async function loadChallenges() {
    const container = document.getElementById("ai-challenges");
    try {
        const data = await api.getChallenges();
        if (data && data.length > 0) {
            container.innerHTML = data.map(ch => {
                const percent = Math.min(100, (ch.completed_count / ch.required_count) * 100);
                const isDone = ch.completed_count >= ch.required_count;
                return `
                    <div class="card" style="padding: 20px; background: #1a1a1a; cursor: default;">
                        <h3 style="margin-bottom: 10px;">${ch.title}</h3>
                        <p style="font-size: 0.9em; color: #aaa; margin-bottom: 15px;">${ch.description}</p>
                        
                        <div style="display: flex; justify-content: space-between; font-size: 0.85em; font-weight: bold; margin-bottom: 5px;">
                            <span>${ch.completed_count} / ${ch.required_count} Watched</span>
                            <span>${Math.round(percent)}%</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${percent}%"></div>
                        </div>

                        ${isDone ? `
                            <div class="challenge-completed">
                                <span>🎉 Challenge Completed!</span>
                            </div>
                        ` : `
                            <button class="btn" onclick="updateChallenge(${ch.id})" style="width: 100%; border-radius: 5px; margin-top: 10px;">
                                Mark Movie Watched
                            </button>
                        `}
                    </div>
                `;
            }).join('');
        }
    } catch (e) {
        container.innerHTML = "<p>Error loading challenges.</p>";
    }
}

async function updateChallenge(id) {
    try {
        const res = await api.updateChallengeProgress(id);
        if (res) {
            if (res.is_completed) {
                alert(`🎉 Challenge Completed! You finished the ${res.title} challenge.`);
            }
            loadChallenges(); // Refresh UI
        }
    } catch (e) {
        console.error(e);
    }
}

// --- AI HIDDEN GEMS ---
async function loadHiddenGems() {
    const container = document.getElementById("ai-hidden-gems");
    try {
        const data = await api.getHiddenGems();
        if (data && data.length > 0) {
            container.innerHTML = data.map(item => createUserDiscoveryCard(item, 'ai_gem')).join('');
        } else {
            container.innerHTML = "<p>No hidden gems found today.</p>";
        }
    } catch (e) {
        container.innerHTML = "<p>Error loading gems.</p>";
    }
}

async function loadFeaturedDebate() {
    const container = document.getElementById("ai-featured-debate");
    const movieInfo = document.getElementById("debate-movie-info");
    const prosList = document.getElementById("debate-pros");
    const consList = document.getElementById("debate-cons");
    const verdictText = document.getElementById("debate-verdict");

    try {
        // Get a popular movie to debate
        const res = await api.getTrending('movie', 'week');
        const movies = res.results || [];
        if (movies.length === 0) return;

        const target = movies[0]; // Take the top trending one
        const debate = await api.getMovieDebate('movie', target.id);

        if (debate) {
            container.style.display = "block";
            movieInfo.innerHTML = `
                <div style="display: flex; gap: 15px; align-items: start;">
                   <img src="${api.getImageUrl(target.poster_path)}"
style="width: 100px; border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.5);"
onerror="this.onerror=null;this.src='https://placehold.co/300x169?text=No+Image';">
                    <div>
                        <h3 style="margin-bottom: 5px;">${target.title}</h3>
                        <p style="font-size: 0.8rem; color: #888; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical;">${target.overview}</p>
                        <button class="btn" style="margin-top: 10px; padding: 5px 12px; font-size: 0.75rem;" onclick="window.location.href='details.html?type=movie&id=${target.id}'">Full Details</button>
                    </div>
                </div>
            `;
            prosList.innerHTML = debate.pros.map(p => `<li>${p}</li>`).join('');
            consList.innerHTML = debate.cons.map(c => `<li>${c}</li>`).join('');
            verdictText.innerText = debate.verdict;
        }
    } catch (e) {
        console.error("Featured debate error:", e);
    }
}

async function loadTrendingBollywood() {
    const container = document.getElementById("trending-bollywood");
    try {
        const results = await api.getTrendingBollywood();
        if (results && results.length > 0) {
            container.innerHTML = results.slice(0, 10).map(item => api.createMediaCard(item)).join('');
        } else {
            container.innerHTML = "<p>No trending Bollywood movies found.</p>";
        }
    } catch (e) {
        console.error(e);
        container.innerHTML = "<p>Error loading Bollywood movies.</p>";
    }
}

// Trigger Loads
document.addEventListener('DOMContentLoaded', () => {
    handleIntro();
    loadTrendingBollywood();
    loadUserDiscovery();
    loadBecauseYouWatched();
    loadDiscussions();
    loadCommunityAwards();
    loadChallenges();
    loadHiddenGems();
    loadFeaturedDebate();
});

// --- CINEMATIC INTRO HANDLER ---
function handleIntro() {
    const overlay = document.getElementById('intro-overlay');
    const audio = document.getElementById('intro-audio');
    const body = document.body;

    // Prevent scrolling during intro
    body.style.overflow = 'hidden';

    // Attempt to play audio
    const playPromise = audio.play();
    if (playPromise !== undefined) {
        playPromise.catch(error => {
            console.log("Autoplay was prevented. User interaction may be needed for sound.");
        });
    }

    // After 3 seconds, fade out the intro
    setTimeout(() => {
        overlay.classList.add('intro-hidden');
        body.style.overflow = 'auto';

        // Remove from DOM after transition
        setTimeout(() => {
            overlay.remove();
        }, 1000);
    }, 3200);
}

async function shuffleChallengesUI() {
    const container = document.getElementById("ai-challenges");
    const btn = document.getElementById("shuffleChallengesBtn");

    btn.disabled = true;
    btn.innerText = "🌀 Shuffling...";
    container.classList.add("fade-out");

    try {
        await api.shuffleChallenges();
        await loadChallenges();
        setTimeout(() => {
            container.classList.remove("fade-out");
            btn.disabled = false;
            btn.innerText = "🔀 Shuffle";
        }, 300);
    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.innerText = "🔀 Shuffle";
    }
}

async function shuffleHiddenGemsUI() {
    const container = document.getElementById("ai-hidden-gems");
    const btn = document.getElementById("shuffleGemsBtn");

    btn.disabled = true;
    btn.innerText = "🌀 Shuffling...";
    container.classList.add("fade-out");

    try {
        await loadHiddenGems();
        setTimeout(() => {
            container.classList.remove("fade-out");
            btn.disabled = false;
            btn.innerText = "🔀 Shuffle";
        }, 300);
    } catch (err) {
        console.error(err);
        btn.disabled = false;
        btn.innerText = "🔀 Shuffle";
    }
}
