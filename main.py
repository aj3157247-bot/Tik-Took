from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
import boto3
import uuid
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tiktok_db")
ENDPOINT_URL = os.getenv("S3_ENDPOINT", "https://storage.iran.liara.space")
ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "YOUR_ACCESS_KEY")
SECRET_KEY = os.getenv("S3_SECRET_KEY", "YOUR_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET", "tik-took-videos")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserTable(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class VideoTable(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True)
    owner_username = Column(String)
    url = Column(String)
    caption = Column(String)
    sound_title = Column(String, default="Original Sound")
    filter_type = Column(String, default="normal")
    likes_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    score = Column(Float, default=0.0)

class SoundTable(Base):
    __tablename__ = "sounds"
    id = Column(String, primary_key=True)
    title = Column(String)
    url = Column(String)

Base.metadata.create_all(bind=engine)

s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

app = FastAPI(title="Tik-Took Advanced API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/videos/upload")
def upload_video(
    owner: str = Form(...),
    caption: str = Form(...),
    sound_title: str = Form("Original Sound"),
    filter_type: str = Form("normal"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    video_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1]
    object_name = f"{video_id}.{file_ext}"

    try:
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            object_name,
            ExtraArgs={"ACL": "public-read"}
        )
        video_url = f"{ENDPOINT_URL}/{BUCKET_NAME}/{object_name}"
    except Exception:
        os.makedirs("cdn_storage", exist_ok=True)
        local_path = f"cdn_storage/{object_name}"
        with open(local_path, "wb") as buffer:
            buffer.write(file.file.read())
        video_url = f"/stream/{object_name}"

    new_video = VideoTable(
        id=video_id,
        owner_username=owner,
        url=video_url,
        caption=caption,
        sound_title=sound_title,
        filter_type=filter_type,
        likes_count=0,
        views_count=0,
        score=0.0
    )
    db.add(new_video)
    db.commit()
    return {"status": "success", "video_id": video_id, "url": video_url}

@app.get("/feed/for-you")
def get_for_you_feed(db: Session = Depends(get_db)):
    # محاسبه امتیاز هوشمند برای ترتیب نمایش ویدیوها
    videos = db.query(VideoTable).all()
    for video in videos:
        video.score = (video.likes_count * 2.5) + (video.views_count * 0.1)
    db.commit()
    
    sorted_videos = db.query(VideoTable).order_by(VideoTable.score.desc()).all()
    return sorted_videos

@app.get("/sounds")
def get_sounds(db: Session = Depends(get_db)):
    return db.query(SoundTable).all()
