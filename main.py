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
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import boto3
import os
import uuid

app = FastAPI(title="Tik-Took Production API")

# --- تنظیمات ذخیره‌سازی ابری S3 / Liara ---
ENDPOINT_URL = os.getenv("S3_ENDPOINT", "https://storage.iran.liara.space")
ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "YOUR_ACCESS_KEY")
SECRET_KEY = os.getenv("S3_SECRET_KEY", "YOUR_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET", "tik-took-videos")

s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

# --- مدل‌های داده (Pydantic Models) ---
class UserRegister(BaseModel):
    username: str
    password: str

class CommentModel(BaseModel):
    video_id: str
    username: str
    text: str

class MessageModel(BaseModel):
    sender: str
    receiver: str
    text: str

class VideoModel(BaseModel):
    id: str
    owner: str
    url: str
    caption: str
    likes: List[str] = []
    views: int = 0
    score: float = 0.0

# --- پایگاه داده موقت پیشرفته ---
db_users = {}
db_videos = {}
db_comments = []
db_messages = []

# --- ۱. مدیریت کاربران و احراز هویت ---
@app.post("/auth/register")
def register(user: UserRegister):
    if user.username in db_users:
        raise HTTPException(status_code=400, detail="این نام کاربری قبلاً ثبت شده است")
    user_id = str(uuid.uuid4())
    db_users[user.username] = {
        "id": user_id,
        "password": user.password,
        "followers": [],
        "following": []
    }
    return {"status": "success", "user_id": user_id}

@app.post("/users/follow")
def follow_user(follower: str, target: str):
    if follower in db_users and target in db_users:
        if target not in db_users[follower]["following"]:
            db_users[follower]["following"].append(target)
            db_users[target]["followers"].append(follower)
            return {"status": "followed"}
        return {"status": "already_following"}
    raise HTTPException(status_code=404, detail="کاربر یافت نشد")

# --- ۲. آپلود ویدیو به S3 و مدیریت فید (For You) ---
@app.post("/videos/upload")
def upload_video(owner: str, caption: str, file: UploadFile = File(...)):
    if owner not in db_users:
        raise HTTPException(status_code=401, detail="کاربر یافت نشد")

    video_id = str(uuid.uuid4())
    file_ext = file.filename.split(".")[-1]
    object_name = f"{video_id}.{file_ext}"

    try:
        # آپلود مستقیم به فضای ابری S3
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            object_name,
            ExtraArgs={"ACL": "public-read"}
        )
        video_url = f"{ENDPOINT_URL}/{BUCKET_NAME}/{object_name}"
    except Exception as e:
        # در صورت عدم تنظیم S3، ذخیره محلی انجام می‌شود
        os.makedirs("cdn_storage", exist_ok=True)
        local_path = f"cdn_storage/{object_name}"
        with open(local_path, "wb") as buffer:
            buffer.write(file.file.read())
        video_url = f"/stream/{object_name}"

    new_video = VideoModel(
        id=video_id,
        owner=owner,
        url=video_url,
        caption=caption
    )
    db_videos[video_id] = new_video
    return {"status": "success", "video": new_video}

@app.get("/feed/for-you")
def get_for_you_feed():
    # الگوریتم پیشنهاد ویدیو بر اساس تعاملات (امتیاز لایک و بازدید)
    for v_id, video in db_videos.items():
        video.score = (len(video.likes) * 3) + (video.views * 0.5)
        
    sorted_videos = sorted(db_videos.values(), key=lambda x: x.score, reverse=True)
    return sorted_videos

# --- ۳. تعاملات (لایک و کامنت) ---
@app.post("/videos/like/{video_id}")
def like_video(video_id: str, username: str):
    if video_id not in db_videos:
        raise HTTPException(status_code=404, detail="ویدیو یافت نشد")
    
    video = db_videos[video_id]
    if username in video.likes:
        video.likes.remove(username)
        return {"status": "unliked", "total_likes": len(video.likes)}
    else:
        video.likes.append(username)
        return {"status": "liked", "total_likes": len(video.likes)}

@app.post("/videos/comment")
def add_comment(comment: CommentModel):
    if comment.video_id not in db_videos:
        raise HTTPException(status_code=404, detail="ویدیو یافت نشد")
    
    comment_data = {
        "id": str(uuid.uuid4()),
        "video_id": comment.video_id,
        "username": comment.username,
        "text": comment.text
    }
    db_comments.append(comment_data)
    return {"status": "success", "comment": comment_data}

# --- ۴. چت و پیام مستقیم (Direct Messages) ---
@app.post("/chat/send")
def send_message(msg: MessageModel):
    db_messages.append(msg.dict())
    return {"status": "sent"}

@app.get("/chat/history")
def get_chat_history(user1: str, user2: str):
    chats = [
        m for m in db_messages 
        if (m["sender"] == user1 and m["receiver"] == user2) or (m["sender"] == user2 and m["receiver"] == user1)
    ]
    return chats
 {"status": "success", "user_id": new_user.id}
