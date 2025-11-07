import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env file

class Settings:  
    PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
    if not PERPLEXITY_API_KEY:
        raise ValueError("Missing PERPLEXITY_API_KEY environment variable.")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("Missing DATABASE_URL environment variable.")
    
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # if not OPENAI_API_KEY:
    #     raise ValueError("Missing OPENAI_API_KEY environment variable.")
    
settings = Settings()