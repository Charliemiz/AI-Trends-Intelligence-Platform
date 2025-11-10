from backend.db.database import Base, engine
from backend.db import models

Base.metadata.create_all(bind=engine)
