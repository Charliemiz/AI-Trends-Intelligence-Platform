import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.db.database import Base, engine
from backend.db import models

def main() -> None:
	Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
	main()
