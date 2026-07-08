import uvicorn
import time
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="ENNXO Style Marketplace Engine")

# 📌 อัปเดตข้อมูลโฆษณาตัวจริงของพี่ ลงไปในฐานข้อมูลระบบเรียบร้อยครับ
DATABASE_PRODUCTS = [
    {
        "id": 1,
        "title": "รับถ่ายวีดีโอ 3,900 ฟรีค่าตัดต่อ โทร 092-4294814",
        "price": 3900.0,
        "location": "Bangkok",
        "phone": "092-4294814",
        "description": "รับถ่ายวีดีโองานพิธีต่างๆ งานบวช งานแต่ง งานเลี้ยงสังสรรค์ งานสัมมนา งานปาร์ตี้ คอร์สสอนออนไลน์ งานคอนเสิร์ต และอื่นๆ รับทุกงานทั่วประเทศ คุ้มสุดๆ ฟรีค่าตัดต่อให้เสร็จสรรพ!",
        "posted_time": "5 Hours Package"
    },
    {
        "id": 2,
        "title": "รับถ่ายวีดีโอ งานเต็มวัน (08.00 - 17.00 น.) - โทร 092-4294814",
        "price": 5500.0,
        "location": "Bangkok",
        "phone": "092-4294814",
        "description": "บริการถ่ายทำวิดีโอแบบเต็มวัน โดยทีมงานมืออาชีพ ครบจบที่เรา ได้งานคุณภาพสูง เหมาะสำหรับงานพิธีการ งานสัมมนาเต็มวัน หรือโปรดักชันที่ต้องการความละเอียด",
        "posted_time": "Full Day Package"
    },
    {
        "id": 3,
        "title": "รับถ่ายวีดีโอระบบ OB Switching พร้อมถ่ายทอดสดไลฟ์สด",
        "price": 7500.0,
        "location": "Bangkok",
        "phone": "092-4294814",
        "description": "รับถ่ายทำวิดีโอกล้อง OB Switching ราคาถูก พร้อมถ่ายทอดสดออกจอโปรเจ็คเตอร์ หรือไลฟ์สดลงเพจ/ยูทูบ คมชัด เสถียร (แพ็กเกจงานไม่เกิน 5 ชั่วโมง)",
        "posted_time": "OB Live 5 Hours"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketplace Dashboard - ENNXO Clone</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }
        body { background-color: #f4f6f9; color: #333; padding-bottom: 50px; }
        .navbar { background-color: #1e3a8a; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .navbar h1 { font-size: 22px; letter-spacing: 1px; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
        .main-panel, .form-panel { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }
        h2 { margin-bottom: 20px; color: #111827; border-bottom: 2px solid #f3f4f6; padding-bottom: 10px; font-size: 20px; }
        .product-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 20px; transition: 0.2s; position: relative; }
        .product-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
        .badge { background-color: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block; margin-bottom: 10px; }
        .prod-title { font-size: 18px; color: #1e3a8a; font-weight: bold; margin-bottom: 8px; }
        .prod-price { font-size: 20px; color: #10b981; font-weight: 700; margin-bottom: 10px; }
        .prod-desc { font-size: 14px; color: #4b5563; line-height: 1.5; margin-bottom: 15px; }
        .prod-meta { display: flex; gap: 15px; font-size: 12px; color: #9ca3af; border-top: 1px dashed #f3f4f6; padding-top: 10px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #374151; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; outline: none; }
        .form-submit-btn { width: 100%; background-color: #10b981; color: white; padding: 12px; border: none; border-radius: 6px; font-size: 15px; font-weight: bold; cursor: pointer; transition: 0.2s; text-align:center; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>ENNXO MARKETPLACE CLONE</h1>
        <div>Total Packages: <strong>{{ total_items }}</strong></div>
    </div>
    <div class="container">
        <div class="main-panel">
            <h2>พี่ชิระศิลป์ - โฆษณาบริการรับถ่ายวีดีโอตัวจริง</h2>
            {% for item in products %}
            <div class="product-card">
                <span class="badge">🔥 โปรสุดคุ้ม ฟรีค่าตัดต่อ</span>
                <div class="prod-title">{{ item.title }}</div>
                <div class="prod-price">฿{{ "{:,.2f}".format(item.price) }}</div>
                <div class="prod-desc">{{ item.description }}</div>
                <div class="prod-meta">
                    <div>📍 Area: <strong>{{ item.location }} / ทั่วประเทศ</strong></div>
                    <div>📞 โทรติดต่อ: <strong style="color:#10b981; font-size:14px;">{{ item.phone }}</strong></div>
                    <div>🕒 รูปแบบ: <strong>{{ item.posted_time }}</strong></div>
                </div>
            </div>
            {% endfor %}
        </div>
        <div class="form-panel">
            <h2>เพิ่มแพ็กเกจ/โฆษณาใหม่</h2>
            <form action="/submit-ad" method="post">
                <div class="form-group"><label>หัวข้อโฆษณา (Title)</label><input type="text" name="title" placeholder="เช่น รับถ่ายงานอีเวนต์ ราคาพิเศษ" required></div>
                <div class="form-group"><label>ราคาเงินบาท (THB)</label><input type="number" name="price" placeholder="3500" required></div>
                <div class="form-group"><label>เบอร์โทรศัพท์ติดต่อ (Phone)</label><input type="text" name="phone" value="092-4294814" required></div>
                <div class="form-group"><label>รายละเอียดโฆษณาเพิ่มเติม</label><textarea name="description" rows="5" placeholder="ใส่เงื่อนไข จำนวนชั่วโมง หรืออุปกรณ์ที่ใช้..." required></textarea></div>
                <button type="submit" class="form-submit-btn">PUBLISH ADVERTISEMENT</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def render_marketplace_dashboard(request: Request):
    from jinja2 import Template
    t = Template(HTML_TEMPLATE)
    return HTMLResponse(content=t.render(products=DATABASE_PRODUCTS, total_items=len(DATABASE_PRODUCTS)))

@app.post("/submit-ad", response_class=HTMLResponse)
async def process_new_advertisement(title: str = Form(...), price: float = Form(...), phone: str = Form(...), description: str = Form(...)):
    new_item = {"id": len(DATABASE_PRODUCTS) + 1, "title": title, "price": price, "location": "Bangkok", "phone": phone, "description": description, "posted_time": "Custom Package"}
    DATABASE_PRODUCTS.insert(0, new_item)
    from jinja2 import Template
    t = Template(HTML_TEMPLATE)
    return HTMLResponse(content=t.render(products=DATABASE_PRODUCTS, total_items=len(DATABASE_PRODUCTS)))

if __name__ == "__main__":
    print("[*] Launching ENNXO Web Engine Server Hub...")
    print("[*] Local URL link generated: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
