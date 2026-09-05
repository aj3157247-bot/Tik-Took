from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
import boto3
import uuid
import os

# تنظیمات دیتابیس و S3 از طریق متغیرهای محیطی
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tiktok_db")
ENDPOINT_URL = os.getenv("S3_ENDPOINT", "https://storage.iran.liara.space")
ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "YOUR_ACCESS_KEY")
SECRET_KEY = os.getenv("S3_SECRET_KEY", "YOUR_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET", "tik-took-videos")

# ساخت اتصال دیتابیس PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# مدل‌های پایگاه داده
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
    likes_count = Column(Integer, default=0)

class CommentTable(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True)
    video_id = Column(String, ForeignKey("videos.id"))
    username = Column(String)
    text = Column(Text)

class MessageTable(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    sender = Column(String)
    receiver = Column(String)
    text = Column(Text)

Base.metadata.create_all(bind=engine)

# اتصال به S3
s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

app = FastAPI(title="Tik-Took Complete Backend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# مدل‌های ورودی Pydantic
class UserAuth(BaseModel):
    username: str
    password: str

class CommentCreate(BaseModel):
    video_id: str
    username: str
    text: str

class MessageSend(BaseModel):
    sender: str
    receiver: str
    text: str

@app.post("/auth/register")
def register(user: UserAuth, db: Session = Depends(get_db)):
    if db.query(UserTable).filter(UserTable.username == user.username).first():
        raise HTTPException(status_code=400, detail="نام کاربری قبلا ثبت شده است")
    new_user = UserTable(id=str(uuid.uuid4()), username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    return {"status": "success", "user_id": new_user.id}

@app.post("/videos/upload")
def upload_video(
    owner: str = Form(...),
    caption: str = Form(...),
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
        likes_count=0
    )
    db.add(new_video)
    db.commit()
    return {"status": "success", "video_id": video_id, "url": video_url}

@app.get("/feed/for-you")
def get_feed(db: Session = Depends(get_db)):
    videos = db.query(VideoTable).order_by(VideoTable.likes_count.desc()).all()
    return videos

@app.post("/videos/like/{video_id}")
def like_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(VideoTable).filter(VideoTable.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="ویدیو یافت نشد")
    video.likes_count += 1
    db.commit()
    return {"status": "success", "likes": video.likes_count}

@app.post("/videos/comment")
def add_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = CommentTable(
        id=str(uuid.uuid4()),
        video_id=comment.video_id,
        username=comment.username,
        text=comment.text
    )
    db.add(new_comment)
    db.commit()
    return {"status": "success"}

@app.post("/chat/send")
def send_message(msg: MessageSend, db: Session = Depends(get_db)):
    new_msg = MessageTable(
        id=str(uuid.uuid4()),
        sender=msg.sender,
        receiver=msg.receiver,
        text=msg.text
    )
    db.add(new_msg)
    db.commit()
    return {"status": "success"}

@app.get("/chat/history")
def get_chat_history(user1: str, user2: str, db: Session = Depends(get_db)):
    messages = db.query(MessageTable).filter(
        ((MessageTable.sender == user1) & (MessageTable.receiver == user2)) |
        ((MessageTable.sender == user2) & (MessageTable.receiver == user1))
    ).all()
    return messages
