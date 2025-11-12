import sys
import os
from pathlib import Path
from urllib.parse import urlparse

script_dir = Path(__file__).resolve().parent  # Current directory
project_root = script_dir.parent.parent       # Go up to project root
sys.path.insert(0, str(project_root))

from backend.db.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ""