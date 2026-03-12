// =============================
// Get parameters from URL
// =============================

const params = new URLSearchParams(window.location.search);
const contentId = params.get("id");
const contentType = params.get("type");

let currentSeason = null;


// =============================
// Load Movie / TV Details
// =============================

async function loadDetails() {

    const data = await api.getDetails(contentType, contentId);

    if (!data) return;

    const title = data.title || data.name;

    document.getElementById("title").textContent = title;
    document.getElementById("overview").textContent =
        data.overview || "No overview available";

    document.getElementById("poster").src =
        getImageUrl(data.poster_path);

    const rating =
        data.vote_average
            ? data.vote_average.toFixed(1)
            : "N/A";

    document.getElementById("rating").textContent = `⭐ ${rating}`;


    // If TV show → load seasons
    if (contentType === "tv") {
        loadSeasons();
    }

}


// =============================
// Load Seasons
// =============================

async function loadSeasons() {

    const seasons = await api.getSeasons(contentId);

    if (!seasons) return;

    const container = document.getElementById("seasons");

    container.innerHTML = seasons.map(season => `

        <button class="season-btn"
            onclick="loadEpisodes(${season.season_number})">

            Season ${season.season_number}

        </button>

    `).join("");

}


// =============================
// Load Episodes
// =============================

async function loadEpisodes(seasonNumber) {

    currentSeason = seasonNumber;

    const data =
        await api.getSeasonEpisodes(contentId, seasonNumber);

    const container =
        document.getElementById("episodes-container");

    container.innerHTML = "";


    if (!data || !data.episodes || data.episodes.length === 0) {

        container.innerHTML =
            "<p>No episodes found.</p>";

        return;
    }


    data.episodes.forEach(ep => {

        const card = document.createElement("div");

        card.className = "episode-card";

        const rating =
            ep.vote_average
                ? ep.vote_average.toFixed(1)
                : "N/A";

        card.innerHTML = `

            <h3>
                Episode ${ep.episode_number}: ${ep.name}
            </h3>

            <p>
                ${ep.overview || "No description available."}
            </p>

            <p>
                ⭐ ${rating}
            </p>

            <button onclick="showEpisodeReviews(${seasonNumber}, ${ep.episode_number})">
                View Reviews
            </button>

        `;

        container.appendChild(card);

    });

}


// =============================
// Load Episode Reviews
// =============================

async function showEpisodeReviews(seasonNumber, episodeNumber) {

    const reviews =
        await api.getReviews(
            contentType,
            contentId,
            seasonNumber,
            episodeNumber
        );

    const container =
        document.getElementById("reviews");

    if (!reviews || reviews.length === 0) {

        container.innerHTML =
            "<p>No reviews yet.</p>";

        return;
    }


    container.innerHTML =
        reviews.map(review => `

        <div class="review">

            <strong>
                ${review.username}
            </strong>

            <p>
                ⭐ ${review.rating}
            </p>

            <p>
                ${review.review_text}
            </p>

            <small>
                ${new Date(review.date).toLocaleDateString()}
            </small>

        </div>

        `).join("");

}


// =============================
// Submit Review
// =============================

async function submitReview() {

    const rating =
        document.getElementById("review-rating").value;

    const reviewText =
        document.getElementById("review-text").value;

    const seasonNumber =
        document.getElementById("review-season").value || null;

    const episodeNumber =
        document.getElementById("review-episode").value || null;


    const reviewData = {

        user_id: 1, // temporary user

        content_id: parseInt(contentId),

        content_type: contentType,

        season_number:
            seasonNumber ? parseInt(seasonNumber) : null,

        episode_number:
            episodeNumber ? parseInt(episodeNumber) : null,

        rating: parseFloat(rating),

        review_text: reviewText

    };


    const result =
        await api.addReview(reviewData);


    if (result) {

        alert("Review submitted successfully!");

        if (seasonNumber && episodeNumber) {

            showEpisodeReviews(
                seasonNumber,
                episodeNumber
            );

        }

    } else {

        alert("Failed to submit review.");

    }

}


// =============================
// Start page
// =============================

document.addEventListener(
    "DOMContentLoaded",
    () => {
        loadDetails();
    }
);