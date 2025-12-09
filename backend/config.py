"""Configuration helpers for environment-based settings.

This module loads environment variables and exposes a small ``Settings``
container used across the application. It raises on missing critical
configuration to fail fast during startup.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file

class Settings:  
    """Configuration container for critical API keys and database settings.

    Loads environment variables at startup and validates that all
    required settings are present. Fails fast on missing configuration.

    :ivar PERPLEXITY_API_KEY: API key for Perplexity API.
    :ivar DATABASE_URL: SQLAlchemy database connection URL.
    :ivar OPENAI_API_KEY: API key for OpenAI API.
    """
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    if not PERPLEXITY_API_KEY:
        raise ValueError("Missing PERPLEXITY_API_KEY environment variable.")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("Missing DATABASE_URL environment variable.")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Missing OPENAI_API_KEY environment variable.")
    
settings = Settings()