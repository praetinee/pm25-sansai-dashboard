from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Minimalist Medical Glyphs (Icons8) ---
# ใช้ไอคอนเส้นบาง (Outline) สีดำ เพื่อความคมชัดและดูแพง
ICON_URLS = {
    'mask': "https://img.icons8.com/?size=200&id=9828&format=png&color=000000", # หน้ากากอนามัย
    'activity': "https://img.icons8.com/?size=200&id=9965&format=png&color=000000", # คนวิ่ง
    'indoors': "https://img.icons8.com/?size=200&id=5342&format=png&color=000000", # บ้าน
    'risk_group': "https://img.icons8.com/?size=200&id=43632&format=png&color=000000" # หัวใจ/การแพทย์
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
def get_image_from_url(url, size=None, colorize=None):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        
        # Resize
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
            
        # Colorize (เปลี่ยนสีไอคอนให้เข้ากับธีม)
        if colorize:
            r, g, b = tuple(int(colorize.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            color_layer = Image.new('RGBA', img.size, (r, g, b, 255))
            img = Image.composite(color_layer, Image.new('RGBA', img.size, (0,0,0,0)), img)
            
        return img
    except Exception as e:
        print(f"Image download failed for {url}: {e}")
        return None

# --- 2. Smart Color Theme (Medical Standard) ---

def get_theme(pm):
    """คืนค่าชุดสีตามระดับความรุนแรงของฝุ่น (มาตรฐานการแพทย์)"""
    if pm <= 25:
        return {
            'name': 'Good',
            'primary': '#059669',   # Emerald 600 (เขียวเข้ม)
            'light': '#D1FAE5',     # Emerald 100 (เขียวอ่อน)
            'bg': '#ECFDF5',        # Emerald 50 (พื้นหลังเขียวจางๆ)
            'text_main': '#064E3B', # Emerald 900 (ตัวหนังสือเขียวเกือบดำ)
            'text_sub': '#047857',  # Emerald 700
            'icon_tint': '#059669'
        }
    elif pm <= 37.5:
        return {
            'name': 'Moderate',
            'primary': '#D97706',   # Amber 600 (เหลืองเข้ม)
            'light': '#FEF3C7',     # Amber 100
            'bg': '#FFFBEB',        # Amber 50
            'text_main': '#78350F', # Amber 900
            'text_sub': '#B45309',  # Amber 700
            'icon_tint': '#D97706'
        }
    elif pm <= 50: 
        return {
            'name': 'Unhealthy',
            'primary': '#EA580C',   # Orange 600 (ส้มเข้ม)
            'light': '#FFEDD5',     # Orange 100
            'bg': '#FFF7ED',        # Orange 50
            'text_main': '#7C2D12', # Orange 900
            'text_sub': '#C2410C',  # Orange 700
            'icon_tint': '#EA580C'
        }
    else: # Hazardous
        return {
            'name': 'Hazardous',
            'primary': '#E11D48',   # Rose 600 (แดงเข้ม)
            'light': '#FFE4E6',     # Rose 100
            'bg': '#FFF1F2',        # Rose 50
            'text_main': '#881337', # Rose 900
            'text_sub': '#BE123C',  # Rose 700
            'icon_tint': '#E11D48'
        }

# --- 3. Graphic Helpers ---

def draw_card_shadow(draw, x, y, w, h, radius, color=(0,0,0,15)):
    """วาดเงาการ์ดแบบนุ่มนวล"""
    offset = 6
    draw.rounded_rectangle([x, y+offset/2, x+w, y+h+offset], radius=radius, fill=color)

def draw_progress_circle(draw, cx, cy, radius, percent, color, bg_color, thickness=25):
    """วาดวงแหวนวัดค่าแบบ Modern Thin"""
    bbox = [cx-radius, cy-radius, cx+radius, cy+radius]
    # วงแหวนพื้นหลัง
    draw.arc(bbox, start=135, end=405, fill=bg_color, width=thickness)
    # วงแหวนแสดงค่าจริง
    if percent > 0:
        end_angle = 135 + (270 * percent)
        draw.arc(bbox, start=135, end=end_angle, fill=color, width=thickness)
        
        # หัวมน (Round Caps)
        start_rad = math.radians(135)
        end_rad = math.radians(end_angle)
        cap_r = thickness/2 - 0.5
        
        # จุดเริ่ม
        sx = cx + radius * math.cos(start_rad)
        sy = cy + radius * math.sin(start_rad)
        draw.ellipse([sx-cap_r, sy-cap_r, sx+cap_r, sy+cap_r], fill=color)
        
        # จุดจบ
        ex = cx + radius * math.cos(end_rad)
        ey = cy + radius * math.sin(end_rad)
        draw.ellipse([ex-cap_r, ey-cap_r, ex+cap_r, ey+cap_r], fill=color)

# --- 4. Main Generator Function ---

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """สร้างการ์ดรายงานสไตล์ Clinical Dashboard (เน้นข้อมูล ไม่เน้นรูป)"""
    
    # ตั้งค่าหน้ากระดาษ
    width, height = 900, 1350
    theme = get_theme(latest_pm25)
    
    # พื้นหลังสีตามธีม (อ่อนๆ สบายตา)
    img = Image.new('RGB', (width, height), theme['bg'])
    draw = ImageDraw.Draw(img, 'RGBA')

    # โหลดฟอนต์ Sarabun
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

    # กำหนดขนาดตัวอักษร (Typography Scale)
    f_h1 = create_font(font_bold, 36)       # ชื่อโรงพยาบาล
    f_sub = create_font(font_med, 24)       # ชื่ออังกฤษ/หน่วยงาน
    f_hero_num = create_font(font_bold, 180) # ตัวเลข PM2.5 (ใหญ่มาก)
    f_hero_label = create_font(font_bold, 40) # สถานะอากาศ
    f_unit = create_font(font_med, 32)      # หน่วย ug/m3
    f_section = create_font(font_bold, 28)  # หัวข้อ section
    f_card_title = create_font(font_bold, 30) # หัวข้อการ์ดเล็ก
    f_card_desc = create_font(font_med, 24)   # เนื้อหาการ์ดเล็ก
    f_footer = create_font(font_reg, 20)      # เครดิตท้าย

    margin = 50
    
    # --- ส่วนที่ 1: Header (หัวกระดาษ) ---
    header_y = 60
    
    # โลโก้โรงพยาบาล (ใช้สัญลักษณ์ + แทนโลโก้จริง เพื่อความมินิมอล)
    logo_size = 80
    draw.rounded_rectangle([margin, header_y, margin+logo_size, header_y+logo_size], radius=25, fill=theme['primary'])
    draw.text((margin+23, header_y+15), "+", font=create_font(font_bold, 50), fill="white")
    
    # ข้อความชื่อโรงพยาบาล
    text_x = margin + logo_size + 25
    draw.text((text_x, header_y), "โรงพยาบาลสันทราย", font=f_h1, fill=theme['text_main'])
    draw.text((text_x, header_y+45), "Sansai Hospital", font=f_sub, fill=theme['text_sub'])
    
    # วันที่และเวลา (มุมขวาบน)
    date_w = draw.textlength(date_str, font=f_footer) + 40
    draw.rounded_rectangle([width-margin-date_w, header_y+15, width-margin, header_y+65], radius=25, fill="white")
    draw.text((width-margin-date_w/2, header_y+40), date_str, font=f_footer, anchor="mm", fill=theme['text_sub'])

    # --- ส่วนที่ 2: Hero Section (แสดงค่าฝุ่น) ---
    hero_cy = 450
    ring_r = 180
    
    # วงแหวนวัดค่า (Progress Ring)
    percent = min(latest_pm25 / 200, 1.0)
    # วงแหวนพื้นหลัง (สีอ่อน)
    draw_progress_circle(draw, width/2, hero_cy, ring_r, 1.0, theme['light'], theme['light'], thickness=25)
    # วงแหวนค่าจริง (สีเข้ม)
    draw_progress_circle(draw, width/2, hero_cy, ring_r, percent, theme['primary'], theme['light'], thickness=25)
    
    # ตัวเลขค่าฝุ่นตรงกลาง
    draw.text((width/2, hero_cy+10), f"{latest_pm25:.0f}", font=f_hero_num, anchor="ms", fill=theme['text_main'])
    draw.text((width/2, hero_cy+100), "μg/m³", font=f_unit, anchor="ms", fill=theme['text_sub'])
    
    # ป้ายสถานะ (Capsule) ใต้วงแหวน
    status_y = hero_cy + 220
    level_text = level
    l_w = draw.textlength(level_text, font=f_hero_label) + 80
    draw.rounded_rectangle([(width-l_w)/2, status_y, (width+l_w)/2, status_y+80], radius=40, fill=theme['primary'])
    draw.text((width/2, status_y+40), level_text, font=f_hero_label, anchor="mm", fill="white")

    # --- ส่วนที่ 3: Advice Section (คำแนะนำ) ---
    # รวมคำแนะนำเป็น 2 กลุ่มใหญ่ เพื่อความสะอาดตา: ประชาชนทั่วไป & กลุ่มเสี่ยง
    
    section_y = status_y + 130
    draw.text((margin, section_y), "คำแนะนำสุขภาพ (Health Advice)", font=f_section, fill=theme['text_main'])
    
    cards_y = section_y + 50
    card_h = 200
    card_w = width - (margin * 2)
    gap = 30
    
    # การ์ดที่ 1: ประชาชนทั่วไป
    c1_rect = [margin, cards_y, margin+card_w, cards_y+card_h]
    draw_card_shadow(draw, margin, cards_y, card_w, card_h, 30, color=(0,0,0,10)) # เงาบางๆ
    draw.rounded_rectangle(c1_rect, radius=30, fill="white")
    
    # กล่องไอคอน 1
    icon_box_size = 120
    ib1_x = margin + 40
    ib1_y = cards_y + (card_h - icon_box_size)//2
    draw.rounded_rectangle([ib1_x, ib1_y, ib1_x+icon_box_size, ib1_y+icon_box_size], radius=25, fill=theme['light'])
    
    # ไอคอน 1 (คนวิ่ง/กิจกรรม) - ย้อมสีตามธีม
    icon1 = get_image_from_url(ICON_URLS['activity'], size=(80, 80), colorize=theme['primary'])
    if icon1: img.paste(icon1, (ib1_x+20, ib1_y+20), icon1)
    
    # ข้อความ 1
    tx1 = ib1_x + icon_box_size + 30
    draw.text((tx1, ib1_y+15), "ประชาชนทั่วไป", font=f_card_title, fill=theme['text_main'])
    
    # ตัดคำอธิบายไม่ให้ยาวเกินไป
    desc1 = advice_details['activity']
    words1 = desc1.split()
    line1 = []
    for w in words1:
        line1.append(w)
        if draw.textlength(" ".join(line1), font=f_card_desc) > (card_w - icon_box_size - 100):
            line1.pop()
            break
    draw.text((tx1, ib1_y+65), " ".join(line1), font=f_card_desc, fill=theme['text_sub'])
    # ถ้าข้อความยาวเกิน ให้ใส่ "อ่านเพิ่มเติม..."
    if len(line1) < len(words1):
        draw.text((tx1, ib1_y+100), "อ่านเพิ่มเติม...", font=create_font(font_med, 20), fill=theme['primary'])

    # การ์ดที่ 2: กลุ่มเสี่ยง
    cards_y2 = cards_y + card_h + gap
    c2_rect = [margin, cards_y2, margin+card_w, cards_y2+card_h]
    draw_card_shadow(draw, margin, cards_y2, card_w, card_h, 30, color=(0,0,0,10))
    draw.rounded_rectangle(c2_rect, radius=30, fill="white")
    
    # กล่องไอคอน 2
    ib2_y = cards_y2 + (card_h - icon_box_size)//2
    # ใช้พื้นหลังสีแดงอ่อนๆ สำหรับกลุ่มเสี่ยงเสมอ เพื่อเตือนใจ
    draw.rounded_rectangle([ib1_x, ib2_y, ib1_x+icon_box_size, ib2_y+icon_box_size], radius=25, fill="#FFE4E6") # Light Rose
    
    # ไอคอน 2 (หัวใจ/การแพทย์) - สีแดงเสมอ
    icon2 = get_image_from_url(ICON_URLS['risk_group'], size=(80, 80), colorize="#E11D48") # Rose 600
    if icon2: img.paste(icon2, (ib1_x+20, ib2_y+20), icon2)
    
    # ข้อความ 2
    draw.text((tx1, ib2_y+15), "กลุ่มเสี่ยง", font=f_card_title, fill=theme['text_main'])
    
    desc2 = advice_details['risk_group']
    words2 = desc2.split()
    line2 = []
    for w in words2:
        line2.append(w)
        if draw.textlength(" ".join(line2), font=f_card_desc) > (card_w - icon_box_size - 100):
            line2.pop()
            break
    draw.text((tx1, ib2_y+65), " ".join(line2), font=f_card_desc, fill=theme['text_sub'])
    if len(line2) < len(words2):
        draw.text((tx1, ib2_y+100), "อ่านเพิ่มเติม...", font=create_font(font_med, 20), fill=theme['primary'])

    # --- ส่วนที่ 4: Footer (ท้ายกระดาษ) ---
    footer_y = height - 70
    # เส้นแบ่งบางๆ
    draw.line([(margin, footer_y-20), (width-margin, footer_y-20)], fill=theme['light'], width=2)
    
    draw.text((margin, footer_y), "Powered by DustBoy & CMU", font=f_footer, fill=theme['text_sub'])
    draw.text((width-margin, footer_y), "Occupational Medicine Dept.", font=f_footer, anchor="rt", fill=theme['text_sub'])

    # Output
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
