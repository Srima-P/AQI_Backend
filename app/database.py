from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ❌ Check if DATABASE_URL is set
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)

# ✅ Fix old postgres:// format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ✅ IMPORTANT: Add SSL for Render/Railway
if "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

print("✅ Connecting to database...")

try:
    # ✅ FIXED ENGINE (handles dropped connections)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,   # reconnect if connection is dead
        pool_recycle=300,     # refresh connection every 5 mins
        pool_size=5,
        max_overflow=10
    )

    # ✅ Session
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    # ✅ Base model
    Base = declarative_base()

    # ✅ Table model
    class AQIRecord(Base):
        __tablename__ = "aqi_records"

        id = Column(Integer, primary_key=True, index=True)
        date = Column(Date, nullable=False, index=True)
        city = Column(String, nullable=False, index=True)
        aqi = Column(Float, nullable=False)
        source = Column(String, nullable=False)

    # ✅ Create tables (only if not exists)
    Base.metadata.create_all(bind=engine)

    print("✅ Database connected successfully")

except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

# ✅ Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()