"""
Configuration management for the Daily Digest API
"""
from pydantic_settings import BaseSettings
from typing import List
import json
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables or fallback token files"""

    # API Keys
    ANTHROPIC_API_KEY: str = ""

    # Email Configuration (Gmail API example)
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REFRESH_TOKEN: str = ""

    # News API
    NEWS_API_KEY: str = ""

    # Google APIs (Calendar, Maps)
    GOOGLE_API_KEY: str = ""
    GOOGLE_CALENDAR_CREDENTIALS: str = ""

    # Weather API
    WEATHER_API_KEY: str = ""  # OpenWeatherMap or similar

    # Traffic API (Google Routes API)
    TRAFFIC_API_KEY: str = ""  # Routes API Key

    # Todo Service (Todoist example)
    TODOIST_API_KEY: str = ""

    # Application Settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    DEBUG: bool = False
    DEFAULT_LOCATION: str = "Marysville,US"  # Default location for weather/traffic (city,country format)

    # API Limits
    MAX_EMAILS_TO_FETCH: int = 20
    MAX_NEWS_ARTICLES: int = 10

    # Commute Routes Configuration (parsed from JSON env var)
    COMMUTE_ROUTES: List[dict] = []

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **values):
        super().__init__(**values)

        # Parse COMMUTE_ROUTES from JSON string if provided as env var
        commute_env = os.environ.get("COMMUTE_ROUTES", "")
        if commute_env and isinstance(commute_env, str):
            try:
                parsed = json.loads(commute_env)
                if isinstance(parsed, list):
                    self.COMMUTE_ROUTES = parsed
            except (json.JSONDecodeError, TypeError):
                pass

        # If any Google credentials are missing, try to load from tokens.json or token.json
        missing_google = not (self.GMAIL_CLIENT_ID and self.GMAIL_CLIENT_SECRET and self.GMAIL_REFRESH_TOKEN)
        if missing_google:
            token_paths = [
                'setup/google_credentials/tokens.json',
                'token.json',
            ]
            for token_path in token_paths:
                if os.path.exists(token_path):
                    try:
                        with open(token_path, 'r') as f:
                            tokens = json.load(f)
                        if not self.GMAIL_CLIENT_ID:
                            self.GMAIL_CLIENT_ID = tokens.get('client_id', '')
                        if not self.GMAIL_CLIENT_SECRET:
                            self.GMAIL_CLIENT_SECRET = tokens.get('client_secret', '')
                        if not self.GMAIL_REFRESH_TOKEN:
                            self.GMAIL_REFRESH_TOKEN = tokens.get('refresh_token', '')
                        if not self.GOOGLE_CALENDAR_CREDENTIALS:
                            self.GOOGLE_CALENDAR_CREDENTIALS = tokens.get('refresh_token', '')
                        print(f"✅ Loaded Google tokens from: {token_path}")
                        break
                    except Exception as e:
                        print(f"⚠️  Failed to load tokens from {token_path}: {e}")


# Initialize settings
settings = Settings()
