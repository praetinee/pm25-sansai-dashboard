from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Scene Assets (ภาพฉากตามระดับฝุ่น) ---
# แนะนำให้ใช้รูป Isometric Scene (1:1 หรือ 4:3) พื้นหลังใส หรือพื้นหลังสีเดียวกับตัวการ์ดจะสวยมาก
# คุณสามารถเปลี่ยน Link ตรงนี้เป็นรูปที่คุณเจนมาใหม่ได้เลย
SCENE_URLS = {
    # อากาศดี: สวนสาธารณะ/เมืองสดใส
    'good': "https://img.freepik.com/free-vector/isometric-park-composition-with-view-public-garden-with-infrastructure-elements-walking-people_1284-59279.jpg?w=826", 
    # ปานกลาง: เริ่มมีเมฆ/หมอกจางๆ
    'moderate': "https://img.freepik.com/free-vector/smart-city-isometric-illustration_1284-20208.jpg?w=826",
    # แย่: เมืองที่มีมลพิษ/คนใส่หน้ากาก
    'unhealthy': "https://img.freepik.com/free-vector/polluted-city-isometric-composition_1284-25634.jpg?w=826",
    # อันตราย: โรงงาน/ควันพิษ
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

# --- 2. Theme & Colors ---

def get_aqi_color(pm):
    if pm <= 25: return '#2ECC71' # Green
    elif pm <= 37.5: return '#F1C40F' # Yellow
    elif pm <= 75: return '#E67E22' # Orange
    else: return '#E74C3C' # Red

# --- 3. Graphics Helpers ---

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

# --- 4. Main Generator ---

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates an 'Isometric Scene' report card like the reference image."""
    
    # Settings
    width, height = 900, 900 # Square-ish format like the reference
    bg_color = "#2C3E50" # Dark Slate Blue/Grey (เหมือนในรูปตัวอย่าง)
    
    img = Image.new('RGB', (width, height), bg_color)
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
    # Title: รายงานคุณภาพอากาศ (PM2.5)
    draw.text((margin, 50), "รายงานคุณภาพอากาศ (PM2.5)", font=f_title, fill="white")
    
    # Subtitle: อัปเดตล่าสุด...
    time_text = f"อัปเดตล่าสุด: {date_str.split(',')[1].strip()} น." if ',' in date_str else date_str
    draw.text((margin, 120), time_text, font=f_subtitle, fill="#BDC3C7")

    # --- 2. Scene Image (The Hero) ---
    # เลือกรูปตามระดับฝุ่น
    if latest_pm25 <= 25: scene_key = 'good'
    elif latest_pm25 <= 37.5: scene_key = 'moderate'
    elif latest_pm25 <= 75: scene_key = 'unhealthy'
    else: scene_key = 'hazardous'
    
    scene_img = get_image_from_url(SCENE_URLS.get(scene_key))
    
    if scene_img:
        # ปรับขนาดรูปให้เต็มความกว้าง (เว้นขอบนิดหน่อย)
        target_w = width - (margin * 2)
        ratio = scene_img.height / scene_img.width
        target_h = int(target_w * ratio)
        
        # จำกัดความสูงไม่ให้กินที่ส่วนล่างเกินไป
        max_h = 450
        if target_h > max_h:
            target_h = max_h
            target_w = int(target_h / ratio)
            
        scene_img = scene_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # วางกึ่งกลางแนวนอน
        img_x = (width - target_w) // 2
        img_y = 180 # ต่อจาก Header
        
        # สร้าง Mask ขอบมนให้รูปฉาก (Optional: ถ้าอยากให้รูปดู Soft ขึ้น)
        mask = Image.new("L", scene_img.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([(0,0), scene_img.size], radius=30, fill=255)
        
        img.paste(scene_img, (img_x, img_y), mask)
    
    # --- 3. Bottom Info Section ---
    bottom_y = 650 # พื้นที่ด้านล่าง
    
    # Status Pill (Label) - วางซ้อนทับมุมซ้ายล่างของรูปนิดๆ หรืออยู่เหนือตัวเลข
    # สีพื้นหลัง Pill ตามค่าฝุ่น
    pill_color = get_aqi_color(latest_pm25)
    label_text = f"{level}"
    pill_w = draw.textlength(label_text, font=f_badge) + 60
    pill_h = 50
    pill_x = margin
    pill_y = bottom_y - 40 
    
    draw_rounded_rect(draw, [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], 10, fill=pill_color)
    draw.text((pill_x + pill_w/2, pill_y + 25), label_text, font=f_badge, anchor="mm", fill="#FFFFFF") # White Text

    # Big PM2.5 Number
    # วางชิดซ้ายล่าง (เหมือนตัวอย่างเลข 8)
    num_y = bottom_y + 20
    draw.text((margin, num_y), f"{latest_pm25:.0f}", font=f_pm_val, anchor="lt", fill="white")
    
    # Unit (µg/m³) - วางข้างๆ ตัวเลข
    # คำนวณความกว้างตัวเลขเพื่อวางหน่วย
    num_w = draw.textlength(f"{latest_pm25:.0f}", font=f_pm_val)
    draw.text((margin + num_w + 20, num_y + 110), "µg/m³", font=f_unit, fill="#BDC3C7")

    # --- 4. Footer ---
    # Source Credit
    draw.text((margin, height - 60), "ข้อมูลจาก: โรงพยาบาลสันทราย (DustBoy)", font=f_footer, fill="#95A5A6")
    
    # Decor: Star/Sparkle at bottom right (เหมือนในรูปตัวอย่าง)
    star_x = width - 60
    star_y = height - 60
    star_size = 30
    # Draw simple 4-point star
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

    # Output
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
