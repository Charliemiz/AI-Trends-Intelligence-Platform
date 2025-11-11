try:
	from backend.db.database import Base, engine
	from backend.db import models  # ensure model modules are imported so Base knows about them
except ModuleNotFoundError:
	import sys
	from pathlib import Path

	repo_root = Path(__file__).resolve().parents[2]
	sys.path.insert(0, str(repo_root))

	from backend.db.database import Base, engine
	from backend.db import models  # ensure model modules are imported so Base knows about them


def main() -> None:
	Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
	main()
