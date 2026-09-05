from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid

# اتصال به دیتابیس PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost:5432/tiktok_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)

class VideoModel(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"))
    video_url = Column(String)
    likes_count = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(username: str, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="نام کاربری تکراری است")
    new_user = UserModel(username=username)
    db.add(new_user)
    db.commit()
    return {"status": "success", "user_id": new_user.id}
