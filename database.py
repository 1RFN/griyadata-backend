from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Menggunakan domain Pooler dan Port 6543 khusus untuk jaringan IPv4 Back4App
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.cyiofgibzuphlglwicra:irfan25postgress@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# Tambahan pool_pre_ping=True memastikan SQLAlchemy mengecek koneksi sebelum mengirim perintah
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fungsi untuk membuka koneksi setiap kali API dipanggil
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()