import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_CONNECTION     = os.getenv("DB_CONNECTION")

missing = [k for k,v in {
    "DB_CONNECTION":DB_CONNECTION,
}.items() if not v]
if missing:
    raise RuntimeError(f"Faltam estas env vars em .env: {missing}")

engine = create_engine(DB_CONNECTION, echo=False)
SessionLocal = sessionmaker(bind=engine)

