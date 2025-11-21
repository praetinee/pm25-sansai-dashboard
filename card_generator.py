from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Scene Assets (ปรับรูปให้สื่อถึงคำแนะนำการปฏิบัติตัว) ---
SCENE_URLS = {
    # อากาศดี (0-25): แนะนำให้ทำกิจกรรมกลางแจ้งได้เต็มที่ -> รูปคนวิ่งเล่นในสวน สดใส
    'good': "https://img.freepik.com/free-vector/isometric-park-composition-with-view-public-garden-with-infrastructure-elements-walking-people_1284-59279.jpg?w=826", 
    
    # ปานกลาง (26-37.5): เริ่มระวัง -> รูปเมืองที่มีคนใช้ชีวิตปกติแต่ท้องฟ้าเริ่มไม่ใสมาก
    'moderate': "https://img.freepik.com/free-vector/isometric-city-street-composition-with-view-modern-city-block-with-buildings-transport-people_1284-63092.jpg?w=826",
    
    # เริ่มมีผล (37.6-75): ลดกิจกรรม/ใส่หน้ากาก -> รูปเมืองที่มีมลพิษ คนใส่หน้ากาก (ถ้าหาได้) หรือกิจกรรมในร่ม
    'unhealthy': "https://img.freepik.com/free-vector/polluted-city-isometric-composition_1284-25634.jpg?w=826",
    
    # อันตราย (>75): งดกิจกรรม/อยู่แต่ในบ้าน -> รูปเมืองที่ดูอันตราย หมอกควันหนา หรือเน้นตึกปิดทึบ
    'hazardous': "https://img.freepik.com/free-vector/air-pollution-isometric-composition_1284-25634.jpg?w=826" 
}

@st.cache_data
def get_font(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Font download failed: {e}")
        return None

@st.cache_data
def get_image_from_url(url, size=None):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGBA")
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"Image download failed for {url}: {e}")
        return None

# --- 2. Dynamic Background & Colors ---

def get_theme_settings(pm):
    """คืนค่าสีพื้นหลังและสี Pill ตามระดับฝุ่น (สอดคล้องกับคำแนะนำ)"""
    if pm <= 25: 
        return {
            'bg': '#1E3A2F', # Dark Green Slate (บรรยากาศร่มรื่น เหมาะแก่การออกกำลังกาย)
            'pill': '#2ECC71',
            'scene': 'good'
        }
    elif pm <= 37.5: 
        return {
            'bg': '#3E382C', # Dark Yellow/Brown Slate (เริ่มระวัง)
            'pill': '#F1C40F',
            'scene': 'moderate'
        }
    elif pm <= 75: 
        return {
            'bg': '#3E2E2C', # Dark Orange/Rust Slate (ลดกิจกรรม)
            'pill': '#E67E22',
            'scene': 'unhealthy'
        }
    else: 
        return {
            'bg': '#2C1E1E', # Dark Red/Purple Slate (งดกิจกรรม/อันตราย)
            'pill': '#E74C3C',
            'scene': 'hazardous'
        }

# --- 3. Graphics Helpers ---

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

# --- 4. Main Generator ---

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates an 'Isometric Scene' report card with dynamic atmosphere reflecting advice."""
    
    # Settings
    width, height = 900, 900 
    theme = get_theme_settings(latest_pm25)
    
    # สร้างพื้นหลังตามธีมสี (Dynamic Background)
    img = Image.new('RGB', (width, height), theme['bg'])
    draw = ImageDraw.Draw(img, 'RGBA')

    # Fonts
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_med = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"
    
    font_bold = get_font(font_url_bold)
    font_reg = get_font(font_url_reg)
    font_med = get_font(font_url_med)

    if not all([font_bold, font_reg, font_med]): return None
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    # Typography
    f_title = create_font(font_bold, 50)
    f_subtitle = create_font(font_reg, 24)
    f_pm_val = create_font(font_bold, 180)
    f_unit = create_font(font_med, 40)
    f_badge = create_font(font_bold, 24)
    f_footer = create_font(font_reg, 20)

    margin = 50

    # --- 1. Header ---
    draw.text((margin, 50), "รายงานคุณภาพอากาศ (PM2.5)", font=f_title, fill="white")
    
    time_text = f"อัปเดตล่าสุด: {date_str.split(',')[1].strip()} น." if ',' in date_str else date_str
    # สี subtitle จางๆ
    draw.text((margin, 120), time_text, font=f_subtitle, fill=(255,255,255, 180))

    # --- 2. Dynamic Scene Image (สะท้อนคำแนะนำ) ---
    # เลือกรูปจาก theme['scene'] ซึ่งผูกกับค่า PM2.5
    scene_img = get_image_from_url(SCENE_URLS.get(theme['scene']))
    
    if scene_img:
        target_w = width - (margin * 2)
        ratio = scene_img.height / scene_img.width
        target_h = int(target_w * ratio)
        
        max_h = 450
        if target_h > max_h:
            target_h = max_h
            target_w = int(target_h / ratio)
            
        scene_img = scene_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        img_x = (width - target_w) // 2
        img_y = 180 
        
        # Mask for softer edges
        mask = Image.new("L", scene_img.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([(0,0), scene_img.size], radius=30, fill=255)
        
        img.paste(scene_img, (img_x, img_y), mask)
    
    # --- 3. Bottom Info Section ---
    bottom_y = 650 
    
    # Status Pill (Label)
    label_text = f"{level}"
    pill_w = draw.textlength(label_text, font=f_badge) + 60
    pill_h = 50
    pill_x = margin
    pill_y = bottom_y - 40 
    
    draw_rounded_rect(draw, [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], 10, fill=theme['pill'])
    draw.text((pill_x + pill_w/2, pill_y + 25), label_text, font=f_badge, anchor="mm", fill="#FFFFFF")

    # Big PM2.5 Number
    num_y = bottom_y + 20
    draw.text((margin, num_y), f"{latest_pm25:.0f}", font=f_pm_val, anchor="lt", fill="white")
    
    # Unit
    num_w = draw.textlength(f"{latest_pm25:.0f}", font=f_pm_val)
    draw.text((margin + num_w + 20, num_y + 110), "µg/m³", font=f_unit, fill=(255,255,255, 150))

    # --- 4. Footer ---
    draw.text((margin, height - 60), "ข้อมูลจาก: โรงพยาบาลสันทราย (DustBoy)", font=f_footer, fill=(255,255,255, 150))
    
    # Sparkle Decor
    star_x = width - 60
    star_y = height - 60
    star_size = 30
    draw.polygon([
        (star_x, star_y - star_size), 
        (star_x + star_size/4, star_y - star_size/4),
        (star_x + star_size, star_y),
        (star_x + star_size/4, star_y + star_size/4),
        (star_x, star_y + star_size),
        (star_x - star_size/4, star_y + star_size/4),
        (star_x - star_size, star_y),
        (star_x - star_size/4, star_y - star_size/4)
    ], fill="white")

    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
