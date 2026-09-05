from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid

app = FastAPI(title="TikTok Clone Full Backend")

# ساختارهای داده (برای محیط واقعی به SQLAlchemy / PostgreSQL متصل می‌شود)
class User(BaseModel):
    id: str
    username: str
    followers: List[str] = []
    following: List[str] = []

class Video(BaseModel):
    id: str
    owner: str
    url: str
    caption: str
    tags: List[str]
    likes: List[str] = []
    views: int = 0
    score: float = 0.0

class Comment(BaseModel):
    id: str
    video_id: str
    username: str
    text: str

class Message(BaseModel):
    sender: str
    receiver: str
    text: str

# دیتابیس موقت ساختاریافته
db_users = {}
db_videos = {}
db_comments = []
db_messages = []

# --- ۱. ثبت‌نام و پروفایل ---
@app.post("/auth/register")
def register(username: str):
    if username in db_users:
        raise HTTPException(status_code=400, detail="نام کاربری موجود است")
    user_id = str(uuid.uuid4())
    db_users[username] = User(id=user_id, username=username)
    return {"status": "success", "user_id": user_id}

@app.post("/users/follow")
def follow_user(follower: str, target: str):
    if follower in db_users and target in db_users:
        db_users[follower].following.append(target)
        db_users[target].followers.append(follower)
        return {"status": "followed"}
    raise HTTPException(status_code=404, detail="کاربر یافت نشد")

# --- ۲. آپلود و الگوریتم پیشنهادات (For You Feed) ---
@app.post("/videos/upload")
def upload_video(owner: str, caption: str, tags: str, file: UploadFile = File(...)):
    video_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    file_path = f"cdn_storage/{video_id}.{file_extension}"
    
    os.makedirs("cdn_storage", exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    tag_list = [t.strip() for t in tags.split(",") if t]
    new_video = Video(
        id=video_id,
        owner=owner,
        url=f"/stream/{video_id}.{file_extension}",
        caption=caption,
        tags=tag_list
    )
    db_videos[video_id] = new_video
    return {"status": "uploaded", "video": new_video}

@app.get("/feed/for-you")
def get_for_you_feed(username: Optional[str] = None):
    # الگوریتم پیشنهاد محتوا بر اساس امتیاز (تعامل + لایک + بازدید)
    for v_id, video in db_videos.items():
        video.score = (len(video.likes) * 3) + (video.views * 0.5)
        
    sorted_videos = sorted(db_videos.values(), key=lambda x: x.score, reverse=True)
    return sorted_videos

# --- ۳. سیستم چت و دایرکت ---
@app.post("/chat/send")
def send_message(msg: Message):
    db_messages.append(msg)
    return {"status": "sent"}

@app.get("/chat/history")
def get_chat(user1: str, user2: str):
    chats = [m for m in db_messages if (m.sender == user1 and m.receiver == user2) or (m.sender == user2 and m.receiver == user1)]
    return chats
