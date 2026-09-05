from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import shutil
import os

app = FastAPI()

os.makedirs("videos", exist_ok=True)

# پایگاه داده ساده موقت در حافظه (In-Memory Database)
users_db = {}
videos_db = []  # شامل اطلاعات ویدیو، لایک‌ها و کامنت‌ها

class UserRegister(BaseModel):
    username: str
    password: str

class CommentModel(BaseModel):
    video_id: int
    username: str
    text: str

@app.post("/register")
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="این نام کاربری قبلا ثبت شده است")
    users_db[user.username] = user.password
    return {"status": "success", "message": "ثبت‌نام با موفقیت انجام شد"}

@app.post("/upload")
def upload_video(username: str, file: UploadFile = File(...)):
    video_id = len(videos_db)
    file_path = f"videos/{video_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    video_data = {
        "id": video_id,
        "owner": username,
        "url": f"/videos/{video_id}_{file.filename}",
        "likes": 0,
        "liked_by": [],
        "comments": []
    }
    videos_db.append(video_data)
    return {"status": "success", "video": video_data}

@app.post("/like/{video_id}")
def like_video(video_id: int, username: str):
    if video_id >= len(videos_db):
        raise HTTPException(status_code=404, detail="ویدیو یافت نشد")
    
    video = videos_db[video_id]
    if username in video["liked_by"]:
        video["liked_by"].remove(username)
        video["likes"] -= 1
        return {"status": "unliked", "likes": video["likes"]}
    else:
        video["liked_by"].append(username)
        video["likes"] += 1
        return {"status": "liked", "likes": video["likes"]}

@app.post("/comment")
def add_comment(comment: CommentModel):
    if comment.video_id >= len(videos_db):
        raise HTTPException(status_code=404, detail="ویدیو یافت نشد")
    
    videos_db[comment.video_id]["comments"].append({
        "username": comment.username,
        "text": comment.text
    })
    return {"status": "success", "comments": videos_db[comment.video_id]["comments"]}

@app.get("/feed")
def get_feed():
    return videos_db
