import sqlite3, datetime, json
from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)
app.secret_key = 'chirasin_premium_spa_v6_final_key_777'

def init_db():
    conn = sqlite3.connect('chirasin_local_market.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price REAL, phone TEXT, details TEXT, category TEXT, color TEXT, images_json TEXT, youtube_json TEXT, created_at TEXT)')
    conn.commit()
    conn.close()

# 📋 ฝังโครงสร้างดีไซน์ตึกสีน้ำเงิน-ส้ม 2 หน้าไว้ในไฟล์เครื่องโดยตรง ปราบหน้าขาวทิ้งเกลี้ยง 100%
FORM_TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CHIRASIN MARKET - ลงประกาศโฆษณาพรีเมียม</title><link rel="stylesheet" href="https://jsdelivr.net">
<style>
    body{background-color:#f4f6f9;font-family:sans-serif;padding-bottom:50px;}
    .ennxo-header{background-color:#fff;padding:15px 0;border-bottom:1px solid #dee2e6;}
    .ennxo-logo{color:#ff6600!important;font-weight:900;font-size:32px;text-decoration:none;}
    .big-input{font-size:18px!important;padding:12px 15px!important;border-radius:8px!important;background-color:#f8f9fa!important;}
    .big-label{font-size:16px!important;color:#212529!important;font-weight:bold!important;margin-bottom:8px;}
    .mockup-box{background-color:#fff;border:1px solid #dee2e6;border-radius:12px;padding:25px;position:relative;}
    .overlay-alert{position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(255,255,255,0.85);border-radius:12px;display:flex;align-items:center;justify-content:center;z-index:10;}
    .alert-pill{background-color:#e9ecef;color:#495057;font-weight:bold;padding:15px 30px;border-radius:30px;border:1px solid #ced4da;font-size:18px;box-shadow:0 4px 12px rgba(0,0,0,0.05);}
    .upload-zone{border:2px dashed #a0a0a0;border-radius:16px;background:#fff;padding:45px;text-align:center;cursor:pointer;}
    .splash-alert{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:9999;background:linear-gradient(135deg,#002d62,#ff6600);color:white;padding:40px 60px;border-radius:24px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.3);border:4px solid #fff;}
</style></head><body>
<div id="splashAlert" class="splash-alert"><h1 class="fw-bold mb-2">🔥 เผยแพร่หน้าโฆษณาสำเร็จ กดปั๊บ ขึ้นปุ๊บ แบบเร้าใจ! 🔥</h1><h2 class="fw-bold text-warning">✨ CHIRASIN MARKET ✨</h2></div>
<form action="/add" method="POST" onsubmit="document.getElementById('splashAlert').style.display='block';">
    <header class="ennxo-header shadow-sm"><div class="container d-flex justify-content-between align-items-center">
        <a href="/" class="ennxo-logo">CHIRASIN <span class="text-dark fs-3 fw-bold">MARKET</span></a>
        <button type="button" id="btnNext" class="btn btn-dark btn-lg px-5 fw-bold" style="border-radius:10px;background-color:#1a1a1a;" onclick="goToStep2()">ต่อไป</button>
    </div></header>
    <div id="step1" class="container mt-4" style="max-width:900px;">
        <div class="mb-4"><label class="big-label">ชื่อสินค้า</label><div class="position-relative">
            <input type="text" name="title" class="form-control big-input fw-bold" maxlength="150" placeholder="รับถ่ายวีดีโอสามพันเก้า" value="รับถ่ายวีดีโอราคาถูกสุดคุ้ม ถ่าย/ตัดต่อ/ครบจบที่เรา" required oninput="document.getElementById('charCount').innerText=this.value.length+'/150'">
            <span id="charCount" class="position-absolute text-muted small" style="bottom:12px;right:15px;">47/150</span>
        </div></div>
        <div class="mb-4"><label class="big-label">หมวดหมู่</label><div class="text-muted small mb-2">ลูกค้าจะตามหาสินค้าของคุณได้ง่ายขึ้น หากสินค้าอยู่ในหมวดหมู่ที่ถูกต้อง</div>
            <select name="category" id="ddlCategory" class="form-select big-input fw-bold" onchange="toggleMockup(this.value)">
                <option value="">-- กรุณาเลือกหมวดหมู่สินค้า/อาชีพ --</option>
                <option value="📸 มัลติมีเดีย/งานบริการ" selected>📸 มัลติมีเดีย/งานบริการ</option>
                <option value="🚗 ยานพาหนะ/รถมือสอง">🚗 ยานพาหนะ/รถมือสอง</option>
                <option value="🏠 อสังหาริมทรัพย์/ที่ดิน">🏠 อสังหาริมทรัพย์/ที่ดิน</option>
            </select>
        </div>
        <h5 class="fw-bold text-dark mb-2">ข้อมูลสินค้า</h5><div class="text-muted small mb-3">ลูกค้าจำเป็นต้องใช้ข้อมูลพวกนี้ในการตัดสินใจซื้อ</div>
        <div class="mockup-box">
            <div id="overlayAlert" class="overlay-alert" style="display:none;"><div class="alert-pill">กรุณาเลือกหมวดหมู่ก่อนกรอกข้อมูลเพิ่ม</div></div>
            <div class="mb-4"><label class="big-label">รายละเอียดคำอธิบายบริการ (แยกขาดจากคีย์เวิร์ด)</label>
                <textarea name="details" class="form-control big-input" rows="5" maxlength="1500" placeholder="พิมพ์อธิบายรายละเอียดผลงาน..." required>รับถ่ายวีดีโอสุดคุ้ม 3,900 พร้อมตัดต่อฟรี โทร 0923866522\nรับถ่ายวีดีโองานพิธีต่างๆ งานบวช งานแต่ง งานเลี้ยงสังสรรค์\nงานสัมมนา งานปาร์ตี้ คอร์สออนไลน์ คอนเสิร์ต และอื่นๆ รับทุกงานทั่วประเทศ\nงานไม่เกิน 5 ชั่วโมง 3,900 งานเต็มวัน 08.00-17.00 น. ราคา 5,500 บาท\n\nระบบถ่ายทอดสด OB Switching ราคาถูก\nพร้อมถ่ายทอดสดออกจอโปรเจ็คเตอร์ รับถ่ายทอดสดไลฟ์สดสตรีมมิ่งลงเพจไลฟ์สดต่างๆ\nงานไม่เกิน 5 ชั่วโมง 7,500 งานเต็มวัน 08.00-17.00 น. ราคา 9,000 บาท</textarea>
                <div id="detailsCount" class="text-end text-muted small mt-1">จำนวนตัวอักษร 634/1500</div>
            </div>
            <div class="row"><div class="col-6 mb-4"><label class="big-label">ราคาแพ็กเกจ (บาท)</label><input type="number" name="price" class="form-control big-input fw-bold" value="3900" required></div>
            <div class="col-6 mb-4"><label class="big-label">เบอร์โทรศัพท์ติดต่อ</label><input type="text" name="phone" class="form-control big-input fw-bold" value="0923866522" required></div></div>
            <div class="mb-2"><label class="big-label">🔑 คีย์เวิร์ดดัก Google</label><input type="text" name="keywords" class="form-control big-input" value="งานแต่ง, งานบวช, สัมมนา, OBSwitching" required></div>
            <input type="hidden" name="color" value="#ff6600">
        </div>
    </div>
    <div id="step2" class="container mt-4" style="max-width:900px; display:none;">
        <h4 class="fw-bold text-dark border-bottom pb-2 mb-4">กรอกข้อมูลสินค้า (ขั้นตอนที่ 2)</h4>
        <div class="mb-4"><label class="big-label">ใส่รูปภาพ</label><div class="text-muted small mb-3">คุณสามารถใส่รูปได้ถึง 20 รูป</div>
            <div class="upload-zone shadow-sm mb-3"><img src="https://flaticon.com" style="width:54px;opacity:0.7;" class="mb-3"><h5 class="fw-bold text-dark">ลากไฟล์มาใส่ที่นี่ หรือ กดปุ่มอัพโหลดรูป</h5><button type="button" class="btn btn-outline-dark fw-bold mt-2 px-4" style="border-radius:10px;">อัพโหลดรูป</button></div>
            <input type="url" name="img1" class="form-control big-input mb-2" placeholder="🖼️ ใส่ลิงก์รูปหน้าปกหลักชิ้นที่ 1" value="https://unsplash.com" required>
            <input type="url" name="img2" class="form-control big-input" placeholder="🖼️ ใส่ลิงก์รูปภาพผลงานชิ้นที่ 2" value="">
        </div>
        <div class="mb-4 bg-light p-3 rounded border shadow-sm"><label class="big-label text-danger">📺 บล็อกเครื่องเล่นวิดีโอฝัง YouTube (จัดเต็ม 5 บล็อกเรียงแถวตรงตามสั่ง)</label>
            <input type="url" name="yt1" class="form-control big-input mb-2" placeholder="🔗 ลิงก์คลิปผลงานยูทูบที่ 1" value="https://youtube.com">
            <input type="url" name="yt2" class="form-control big-input mb-2" placeholder="🔗 ลิงก์คลิปผลงานยูทูบที่ 2" value=""><input type="url" name="yt3" class="form-control big-input mb-2" placeholder="🔗 ลิงก์คลิปผลงานยูทูบที่ 3" value=""><input type="url" name="yt4" class="form-control big-input mb-2" placeholder="🔗 ลิงก์คลิปผลงานยูทูบที่ 4" value=""><input type="url" name="yt5" class="form-control big-input" value="">
        </div>
        <div class="d-flex gap-3 mt-5">
            <button type="button" class="btn btn-outline-secondary btn-lg w-50 py-3 fw-bold fs-5" style="border-radius:12px;" onclick="goToStep1()">⬅️ ย้อนกลับไปหน้าแรก</button>
            <button type="submit" class="btn btn-warning btn-lg w-50 py-3 shadow fw-bold text-dark fs-4" style="border-radius:12px;">🚀 กดบันทึกเพื่อเผยแพร่โฆษณาทันที</button>
        </div>
    </div>
</form>
<script>
    function toggleMockup(val){ document.getElementById('overlayAlert').style.display=(val==="")?"flex":"none"; }
    function goToStep2(){ document.getElementById('step1').style.display='none'; document.getElementById('step2').style.display='block'; document.getElementById('btnNext').style.display='none'; window.scrollTo(0,0); }
    function goToStep1(){ document.getElementById('step1').style.display='block'; document.getElementById('step2').style.display='none'; document.getElementById('btnNext').style.display='block'; window.scrollTo(0,0); }
    window.onload = function(){ toggleMockup(document.getElementById('ddlCategory').value); };
</script>
</body></html>"""

