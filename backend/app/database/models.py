from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///../../database/harmix.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UploadRecord(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processed")

class APIInventory(Base):
    __tablename__ = "api_inventory"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer)
    endpoint = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    response_time = Column(Integer)
    auth_detected = Column(String)
    
class AIAnalysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer)
    summary = Column(Text)
    recommendations = Column(JSON)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()