from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://postgres.cyiofgibzuphlglwicra:irfan25postgress@db.cyiofgibzuphlglwicra.supabase.co:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fungsi untuk membuka koneksi setiap kali API dipanggil
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()