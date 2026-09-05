from fastapi import FastAPI, UploadFile, File
import shutil
import os

app = FastAPI()

# ایجاد پوشه برای ذخیره ویدیوها
os.makedirs("videos", exist_ok=True)

@app.get("/")
def home():
    return {"message": "TikTok Clone API is running"}

# دریافت لیست ویدیوها
@app.get("/videos")
def get_videos():
    video_list = os.listdir("videos")
    return [{"id": i, "url": f"/videos/{name}"} for i, name in enumerate(video_list)]

# آپلود ویدیو جدید
@app.post("/upload")
def upload_video(file: UploadFile = File(...)):
    file_path = f"videos/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}
