import os
import random
import json
import time

def get_ai_movie_debate(title: str, overview: str, reviews: list) -> dict:
    # -----------------------------
    # SIMULATED OPENAI API CALL
    # -----------------------------
    # Logic: Analyze movie details and user reviews to generate a structured pro/con debate.
    
    review_context = " ".join([r.get('review_text', '') for r in reviews[:3]])
    
    # Simulate thinking time
    time.sleep(1)
    
    # Simulated structured response based on input data
    return {
        "pros": [
            f"Breathtaking visual style that enhances the story of {title}.",
            "Stellar performances from the lead cast.",
            "A unique and thought-provoking narrative."
        ],
        "cons": [
            "The pacing can feel a bit uneven in the second act.",
            "Might be overly complex for casual viewers looking for light entertainment."
        ],
        "verdict": f"{title} is a must-watch for fans of deep storytelling, though its complexity may be polarizing."
    }


def get_ai_movie_recommendation_reason(movie_title: str) -> str:
    reasons = [
        f"Users who liked similar genres often enjoy {movie_title}.",
        f"{movie_title} perfectly combines incredible visual storytelling with a gripping narrative.",
        f"Based on your recent watch history, {movie_title} is a fantastic match.",
        f"This is an absolute masterpiece in its category.",
        f"With its stellar cast and brilliant direction, {movie_title} is highly recommended by our AI."
    ]
    return random.choice(reasons)

def generate_guess_game_clue(movie_title: str, overview: str) -> dict:
    clues_pool = {
        "Interstellar": [
            {"type": "emoji", "text": "🪐 🕰️ 👨‍👧 🚀"},
            {"type": "quote", "text": "We're not meant to save the world. We're meant to leave it."},
            {"type": "plot", "text": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."}
        ],
        "Inception": [
            {"type": "emoji", "text": "🌀 🎩 💤 🏦"},
            {"type": "quote", "text": "You mustn't be afraid to dream a little bigger, darling."},
            {"type": "plot", "text": "A thief who steals corporate secrets through use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO."}
        ],
        "The Matrix": [
            {"type": "emoji", "text": "💊 🕶️ 💻 🔫"},
            {"type": "quote", "text": "Free your mind."},
            {"type": "plot", "text": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers."}
        ],
        "The Dark Knight": [
            {"type": "emoji", "text": "🤡 🃏 🦇 🏙️"},
            {"type": "quote", "text": "Why so serious?"},
            {"type": "plot", "text": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice."}
        ],
        "Parasite": [
            {"type": "emoji", "text": "🍑 🏠 🍜 🩸"},
            {"type": "quote", "text": "Jessica, only child, Illinois, Chicago..."},
            {"type": "plot", "text": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan."}
        ],
        "Pulp Fiction": [
            {"type": "emoji", "text": "🍔 💼 💃 🔫"},
            {"type": "quote", "text": "Do you know what they call a Quarter Pounder with Cheese in France?"},
            {"type": "plot", "text": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption."}
        ],
        "Fight Club": [
            {"type": "emoji", "text": "🧼 🥊 🕴️ 🏢"},
            {"type": "quote", "text": "The first rule of Fight Club is: You do not talk about Fight Club."},
            {"type": "plot", "text": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more."}
        ],
        "Spirited Away": [
            {"type": "emoji", "text": "🏮 🐷 🐲 🛀"},
            {"type": "quote", "text": "I can't believe it! It's like a dream."},
            {"type": "plot", "text": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts."}
        ],
        "Joker": [
            {"type": "emoji", "text": "🤡 👠 🕺 📺"},
            {"type": "quote", "text": "I used to think that my life was a tragedy, but now I realize, it's a comedy."},
            {"type": "plot", "text": "In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution and bloody crime."}
        ],
        "Blade Runner 2049": [
            {"type": "emoji", "text": "🤖 🚁 🌆 🌧️"},
            {"type": "quote", "text": "I have memories, but they're not real. They're just stories someone told me."},
            {"type": "plot", "text": "Young Blade Runner K's discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard, who's been missing for thirty years."}
        ]
    }
    
    # If the specific movie has clues, use them
    if movie_title in clues_pool:
        clue = random.choice(clues_pool[movie_title])
        return {
            "clue_type": clue["type"],
            "clue_text": clue["text"],
            "answer_title": movie_title
        }
    
    # Fallback for other movies
    types = ["emoji", "quote", "plot"]
    clue_type = random.choice(types)
    
    if clue_type == "emoji":
        clue_text = "🕵️‍♂️ 🌆 🔍 🤯"
    elif clue_type == "quote":
        clue_text = f"An iconic moment happens when the main character realizes the truth in a dramatic scene."
    else:
        words = overview.split()[:15]
        clue_text = " ".join(words) + "..."
        
    return {
        "clue_type": clue_type,
        "clue_text": clue_text,
        "answer_title": movie_title
    }

def generate_daily_quiz(movie_title: str, details: dict = None) -> dict:
    # -----------------------------
    # SIMULATED AI QUIZ GENERATOR
    # -----------------------------
    # Logic: Based on movie details, generate a real question with 4 credible options.
    
    genres = [g["name"] for g in details.get("genres", [])] if details else []
    year = details.get("release_date", "2024")[:4] if details else "2024"
    
    # Pool of potential questions
    question_bank = [
        {
            "q": f"What year was the masterpiece '{movie_title}' released?",
            "options": [year, str(int(year)-2), str(int(year)+3), str(int(year)-5)],
            "correct": year
        },
        {
            "q": f"Which genre primarily defines the film '{movie_title}'?",
            "options": genres + ["Comedy", "Horror", "Documentary"] if genres else ["Action", "Drama", "Sci-Fi", "Thriller"],
            "correct": genres[0] if genres else "Drama"
        },
        {
            "q": f"Who is the main target audience for '{movie_title}' based on its themes?",
            "options": ["Adults", "Children", "Teens", "Seniors"],
            "correct": "Adults"
        }
    ]
    
    selected = random.choice(question_bank)
    opts = list(set(selected["options"]))[:4]
    
    # Ensure correct answer is in options
    if selected["correct"] not in opts:
        opts[0] = selected["correct"]
        
    random.shuffle(opts)
    
    ans_index = opts.index(selected["correct"])
    ans_letter = chr(65 + ans_index) # A, B, C, D
    
    return {
        "question": selected["q"],
        "option_a": opts[0],
        "option_b": opts[1],
        "option_c": opts[2],
        "option_d": opts[3],
        "correct_answer": ans_letter
    }

def generate_watch_challenges() -> list:
    pool = [
        {
            "title": "Nolan Enthusiast",
            "description": "Watch 5 Christopher Nolan movies.",
            "required_count": 5
        },
        {
            "title": "Sci-Fi Geek",
            "description": "Watch 3 sci-fi movies released after 2015.",
            "required_count": 3
        },
        {
            "title": "Masterpiece Hunter",
            "description": "Watch 4 movies with a rating above 8.5.",
            "required_count": 4
        },
        {
            "title": "Anime Explorer",
            "description": "Watch 3 anime series with rating above 8.5.",
            "required_count": 3
        },
        {
            "title": "Bollywood Thrillers",
            "description": "Watch 4 classic Bollywood thrillers.",
            "required_count": 4
        },
        {
            "title": "Binge Watcher",
            "description": "Watch 3 TV shows with more than 3 seasons.",
            "required_count": 3
        },
        {
            "title": "Director Spotlight",
            "description": "Watch 4 Denis Villeneuve films.",
            "required_count": 4
        },
        {
            "title": "Ghibli Magic",
            "description": "Watch 5 Studio Ghibli films.",
            "required_count": 5
        }
    ]
    return random.sample(pool, 3)

def get_ai_hidden_gem_reason() -> str:
    reasons = [
        "Highly rated by viewers but not widely known.",
        "A slow-burn thriller that critics overlooked.",
        "It features an incredible performance that flew under the radar.",
        "A brilliant indie film with a cult following."
    ]
    return random.choice(reasons)
