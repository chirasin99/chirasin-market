import sqlite3
import os
import shutil
from datetime import datetime
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(title="CHIRASIN MARKET API")

# ปลดล็อกระบบรักษาความปลอดภัยข้ามไฟล์ ป้องกันเซิร์ฟเวอร์ค้าง
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_NAME = "video_platform.db"
UPLOAD_DIR = "static/uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT NOT NULL,
            phone TEXT NOT NULL,
            province TEXT NOT NULL,
            description TEXT,
            image_urls TEXT,
            youtube_links TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/api/ads")
async def create_ad(
    title: str = Form(...),
    price: str = Form(...),
    phone: str = Form(...),
    province: str = Form(...),
    description: str = Form(""),
    youtube_links: str = Form(""),
    images: List[UploadFile] = File(None)
):
    try:
        saved_image_paths = []
        if images:
            for idx, image in enumerate(images):
                if image.filename == "":
                    continue
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{idx}_{image.filename}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                saved_image_paths.append(f"/static/uploads/{filename}")

        images_str = "|".join(saved_image_paths) if saved_image_paths else ""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO platform_ads (title, price, phone, province, description, image_urls, youtube_links, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, price, phone, province, description, images_str, youtube_links, current_time))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# เปิดท่อส่งสากลดึงหน้า UI ล่าสุดสดๆ ร้อนๆ ขึ้นแสดงผล
@app.get("/", response_class=HTMLResponse)
def get_ui():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: ไม่พบไฟล์ index.html ในโฟลเดอร์จ้า</h1>"
