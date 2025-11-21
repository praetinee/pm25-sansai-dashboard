from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- Assets ---
# เรายังใช้ 3D Icons เพราะมันช่วยเบรกความแข็งของข้อมูลได้ดี
# แต่จะปรับขนาดให้เล็กลงและจัดวางให้ดูแพงขึ้น
ICON_URLS = {
    'mask': "https://i.postimg.cc/wB0w9rd9/Gemini-Generated-Image-rkwajtrkwajtrkwa.png",
    'activity': "https://i.postimg.cc/FFdXnyj1/Gemini-Generated-Image-16wol216wol216wo.png",
    'indoors': "https://i.postimg.cc/RVw5vvpJ/Gemini-Generated-Image-8gbf4e8gbf4e8gbf.png",
    'risk_group': "https://i.postimg.cc/8CKxZccL/Gemini-Generated-Image-4oj4z84oj4z84oj4.png"
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

# --- Graphics Engine ---

def get_medical_theme(pm):
    """Returns color theme based on medical standards."""
    if pm <= 25:
        return {'main': '#10b981', 'bg': '#ecfdf5', 'label': 'ยอดเยี่ยม (Very Good)', 'gradient': ['#34d399', '#059669']}
    elif pm <= 37.5:
        return {'main': '#f59e0b', 'bg': '#fffbeb', 'label': 'ดี (Good)', 'gradient': ['#fbbf24', '#d97706']}
    elif pm <= 75:
        return {'main': '#f97316', 'bg': '#fff7ed', 'label': 'เริ่มมีผล (Unhealthy)', 'gradient': ['#fb923c', '#c2410c']}
    else:
        return {'main': '#ef4444', 'bg': '#fef2f2', 'label': 'อันตราย (Hazardous)', 'gradient': ['#f87171', '#b91c1c']}

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

def draw_gradient_ring(draw, cx, cy, radius, thickness, percent, colors):
    """Draws a premium gradient ring."""
    # 1. Background Track (Light Grey)
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.arc(bbox, start=135, end=405, fill="#F3F4F6", width=thickness)
    
    # 2. Active Arc (Solid Color for reliability in PIL)
    # Gradient simulation in PIL arc is hard, using solid main color looks cleaner and sharper
    active_end = 135 + (270 * percent)
    
    if percent > 0:
        # Main Arc
        draw.arc(bbox, start=135, end=active_end, fill=colors[1], width=thickness)
        
        # Caps (Rounded Ends)
        start_rad = math.radians(135)
        end_rad = math.radians(active_end)
        
        # Start Cap
        sx = cx + radius * math.cos(start_rad)
        sy = cy + radius * math.sin(start_rad)
        cap_r = thickness / 2 - 0.5
        draw.ellipse([sx-cap_r, sy-cap_r, sx+cap_r, sy+cap_r], fill=colors[1])
        
        # End Cap
        ex = cx + radius * math.cos(end_rad)
        ey = cy + radius * math.sin(end_rad)
        draw.ellipse([ex-cap_r, ey-cap_r, ex+cap_r, ey+cap_r], fill=colors[1])

# --- Main Generator ---

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a 'Medical Grade' Report Card."""
    
    width, height = 900, 1300
    theme = get_medical_theme(latest_pm25)
    
    # Canvas
    img = Image.new('RGB', (width, height), "#FFFFFF")
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

    f_header = create_font(font_bold, 32)
    f_sub = create_font(font_med, 20)
    f_pm_val = create_font(font_bold, 150)
    f_unit = create_font(font_med, 32)
    f_status = create_font(font_bold, 40)
    f_card_title = create_font(font_bold, 26)
    f_card_desc = create_font(font_med, 22)
    f_footer = create_font(font_med, 18)

    # --- 1. Header Section ---
    margin = 50
    
    # Hospital Logo Placeholder (Text based)
    # Draw a pill shape container for logo
    draw_rounded_rect(draw, [margin, 50, margin + 80, 130], 25, fill="#1E293B")
    draw.text((margin + 23, 75), "+", font=create_font(font_bold, 40), fill="white")
    
    # Text
    draw.text((margin + 100, 60), "รพ.สันทราย", font=f_header, fill="#1E293B")
    draw.text((margin + 100, 100), "Sansai Hospital", font=f_sub, fill="#94A3B8")
    
    # Date (Right aligned)
    draw.text((width - margin, 65), date_str, font=f_sub, anchor="rt", fill="#64748B")

    # Divider
    draw.line([(margin, 160), (width - margin, 160)], fill="#F1F5F9", width=2)

    # --- 2. Hero Section (Ring Chart) ---
    hero_cy = 420
    hero_cx = width / 2
    ring_radius = 160
    
    # Draw Ring
    percent = min(latest_pm25 / 200, 1.0)
    draw_gradient_ring(draw, hero_cx, hero_cy, ring_radius, 25, percent, theme['gradient'])
    
    # Value inside Ring
    draw.text((hero_cx, hero_cy + 10), f"{latest_pm25:.0f}", font=f_pm_val, anchor="ms", fill="#1E293B")
    draw.text((hero_cx, hero_cy + 90), "µg/m³", font=f_unit, anchor="ms", fill="#94A3B8")
    draw.text((hero_cx, hero_cy - 100), "PM 2.5", font=create_font(font_bold, 24), anchor="ms", fill="#CBD5E1")

    # Status Pill (Floating below ring)
    status_y = hero_cy + 190
    status_text = level
    
    # Dynamic Pill Width
    pill_w = draw.textlength(status_text, font=f_status) + 80
    pill_rect = [(width - pill_w)/2, status_y, (width + pill_w)/2, status_y + 80]
    
    # Draw Pill with theme color
    draw_rounded_rect(draw, pill_rect, 40, fill=theme['bg'])
    draw.text((width/2, status_y + 40), status_text, font=f_status, anchor="mm", fill=theme['main'])

    # --- 3. Advice Grid (Block Design) ---
    grid_y = status_y + 140
    
    draw.text((margin, grid_y), "คำแนะนำสุขภาพ (Health Advice)", font=create_font(font_bold, 24), fill="#1E293B")
    
    cards_start_y = grid_y + 50
    col_gap = 25
    row_gap = 25
    card_w = (width - (margin * 2) - col_gap) / 2
    card_h = 240 # Squarish look
    
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        col = i % 2
        row = i // 2
        x = margin + col * (card_w + col_gap)
        y = cards_start_y + row * (card_h + row_gap)
        
        # Card Background (Very subtle grey fill)
        draw_rounded_rect(draw, [x, y, x + card_w, y + card_h], 30, fill="#F8FAFC")
        
        # Icon (Top Left)
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(90, 90))
        if icon_img:
            # Add a white circle behind icon to make it pop
            icon_bg_r = 55
            center_icon_x = x + 70
            center_icon_y = y + 70
            draw.ellipse([center_icon_x - icon_bg_r, center_icon_y - icon_bg_r, center_icon_x + icon_bg_r, center_icon_y + icon_bg_r], fill="white")
            img.paste(icon_img, (int(center_icon_x - 45), int(center_icon_y - 45)), icon_img)
            
        # Text (Bottom Left aligned)
        text_start_y = y + 140
        draw.text((x + 30, text_start_y), item['title'], font=f_card_title, fill="#1E293B")
        
        # Desc (Wrap)
        desc = item['desc']
        words = desc.split()
        line1 = []
        curr = []
        for w in words:
            curr.append(w)
            if draw.textlength(" ".join(curr), font=f_card_desc) > (card_w - 50):
                curr.pop()
                line1 = curr
                break
        if not line1: line1 = curr
        
        # Show max 1 line for clean look, or 2 if space permits.
        # Let's show 1 line and '...' if too long to keep grid uniform
        final_desc = " ".join(line1)
        if len(line1) < len(words): final_desc += "..."
        
        draw.text((x + 30, text_start_y + 40), final_desc, font=f_card_desc, fill="#64748B")

    # --- 4. Footer ---
    footer_y = height - 60
    draw.text((width/2, footer_y), "Powered by DustBoy & CMU | Occupational Medicine Dept.", font=f_footer, anchor="ms", fill="#CBD5E1")

    # Output
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
