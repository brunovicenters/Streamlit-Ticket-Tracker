import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DB_NAME")

missing = [k for k,v in {
    "DB_USER":DB_USER,
    "DB_PASSWORD":DB_PASSWORD,
    "DB_HOST":DB_HOST,
    "DB_PORT":DB_PORT,
    "DB_NAME":DB_NAME
}.items() if not v]
if missing:
    raise RuntimeError(f"Faltam estas env vars em .env: {missing}")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

