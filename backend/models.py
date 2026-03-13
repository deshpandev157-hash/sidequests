from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


# -----------------------------
# User Table
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("Review", back_populates="user")
    watchlist = relationship("Watchlist", back_populates="user")
    episode_ratings = relationship("EpisodeRating", back_populates="user")
    episode_reviews = relationship("EpisodeReview", back_populates="user")
    watched_episodes = relationship("WatchedEpisode", back_populates="user")
    content_ratings = relationship("ContentRating", back_populates="user")


# -----------------------------
# Reviews (Movies / Shows)
# -----------------------------
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    content_id = Column(Integer, index=True)
    content_type = Column(String, default="movie", nullable=False)
    media_type = Column(String, default="movie") # Keeping for compatibility if needed, but primary is content_type now

    season_number = Column(Integer, nullable=True)
    episode_number = Column(Integer, nullable=True)

    rating = Column(Float)
    review_text = Column(Text)

    date = Column(String)

    user = relationship("User", back_populates="reviews")


# -----------------------------
# Content Rating (Main Movies/Shows User Votes)
# -----------------------------
class ContentRating(Base):
    __tablename__ = "content_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) 

    content_id = Column(Integer, index=True)
    content_type = Column(String) # "movie" or "tv"
    
    rating_value = Column(Integer)  # 1 to 10
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="content_ratings")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "content_id",
            "content_type",
            name="unique_user_content_rating"
        ),
    )


# -----------------------------
# Watchlist
# -----------------------------
class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    content_id = Column(Integer, index=True)
    media_type = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist")


# -----------------------------
# Episode Ratings
# -----------------------------
class EpisodeRating(Base):
    __tablename__ = "episode_ratings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    show_id = Column(Integer, index=True)
    season_number = Column(Integer)
    episode_number = Column(Integer)

    rating = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="episode_ratings")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "show_id",
            "season_number",
            "episode_number",
            name="unique_episode_rating"
        ),
    )


# -----------------------------
# Episode Reviews
# -----------------------------
class EpisodeReview(Base):
    __tablename__ = "episode_reviews"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    show_id = Column(Integer, index=True)
    season_number = Column(Integer)
    episode_number = Column(Integer)

    review = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="episode_reviews")


# -----------------------------
# Watched Episodes (for achievements)
# -----------------------------
class WatchedEpisode(Base):
    __tablename__ = "watched_episodes"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    show_id = Column(Integer, index=True)
    show_name = Column(String, default="")
    season_number = Column(Integer)
    episode_number = Column(Integer)
    episode_name = Column(String, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watched_episodes")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "show_id",
            "season_number",
            "episode_number",
            name="unique_watched_episode"
        ),
    )


# -----------------------------
# Activity Log
# -----------------------------
class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    action = Column(String)

    target_id = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# Notifications
# -----------------------------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    message = Column(String)

    is_read = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

# -----------------------------
# Watch History
# -----------------------------
class WatchHistory(Base):
    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, index=True)
    content_type = Column(String) # "movie" | "tv" | "anime"
    watched_at = Column(DateTime, default=datetime.utcnow)

    # Optional relationship to use
    user = relationship("User", backref="watch_history")

# -----------------------------
# Review Likes
# -----------------------------
class ReviewLike(Base):
    __tablename__ = "review_likes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="unique_review_like"),
    )

# -----------------------------
# Discussions
# -----------------------------
class Discussion(Base):
    __tablename__ = "discussions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content_id = Column(Integer, index=True)
    content_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscussionComment(Base):
    __tablename__ = "discussion_comments"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# -----------------------------
# Weekly Awards
# -----------------------------
class WeeklyAward(Base):
    __tablename__ = "weekly_awards"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String) # "Movie of the Week", etc.
    content_id = Column(Integer)
    content_type = Column(String)
    week_start = Column(DateTime, default=datetime.utcnow)

class AwardVote(Base):
    __tablename__ = "award_votes"

    id = Column(Integer, primary_key=True, index=True)
    award_id = Column(Integer, ForeignKey("weekly_awards.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("award_id", "user_id", name="unique_award_vote"),
    )

# -----------------------------
# AI Games
# -----------------------------
class GuessGame(Base):
    __tablename__ = "guess_games"
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer)
    clue_type = Column(String)
    clue_text = Column(String)
    answer_title = Column(String)

class MovieQuiz(Base):
    __tablename__ = "movie_quiz"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)

class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    required_count = Column(Integer)

class ChallengeProgress(Base):
    __tablename__ = "challenge_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    completed_count = Column(Integer, default=0)

# -----------------------------
# AI Cache
# -----------------------------
class AiResponseCache(Base):
    __tablename__ = "ai_response_cache"
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, index=True)
    content_type = Column(String)
    feature_name = Column(String) # e.g., "movie-debate"
    response_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)