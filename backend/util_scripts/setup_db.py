"""Utility script to create database tables.

This script is intended to be run manually when initializing a new
development database. It calls SQLAlchemy's ``create_all`` on the
declared metadata.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.db.database import Base, engine

def main() -> None:
	"""Create all tables declared in :mod:`backend.db.models`.

	This script is only intended for local development or one-off
	database initialization. It invokes SQLAlchemy's ``create_all``
	on the declared metadata.
	"""
	Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
	main()
