from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL is set
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("Please add PostgreSQL database in Railway and link it to your service.")
    sys.exit(1)

# Fix for Railway PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"✅ Connecting to database...")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    class AQIRecord(Base):
        __tablename__ = "aqi_records"
        
        id = Column(Integer, primary_key=True, index=True)
        date = Column(Date, nullable=False, index=True)
        city = Column(String, nullable=False, index=True)
        aqi = Column(Integer, nullable=False)
        source = Column(String, nullable=False)

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected successfully")

except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
