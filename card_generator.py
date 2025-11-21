from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import requests
from io import BytesIO
import streamlit as st
import math

# --- 3D Assets ---
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
def get_image_from_url(url, size=(150, 150)):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGBA")
        img = img.resize(size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"Image download failed for {url}: {e}")
        return None

# --- Advanced Graphics ---

def create_vibrant_background(width, height, base_color_hex):
    """Creates a rich, atmospheric gradient background with depth."""
    # 1. Base Color
    try:
        r, g, b = tuple(int(base_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except:
        r, g, b = 40, 40, 40

    base = Image.new('RGB', (width, height), (r, g, b))
    
    # 2. Create Gradient Overlay (Top-Left Light to Bottom-Right Dark)
    # We use a radial gradient simulation by drawing large blurred circles
    
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    # Glow Orb Top-Left (Lighter/White tint)
    # Makes it look like sunlight/fresh air source
    orb_size = int(width * 1.2)
    draw.ellipse([-orb_size//2, -orb_size//2, orb_size//2, orb_size//2], fill=(255, 255, 255, 40))
    
    # Deep Orb Bottom-Right (Darker/Saturated tint)
    # Adds weight to the bottom
    draw.ellipse([width - orb_size//2, height - orb_size//2, width + orb_size//2, height + orb_size//2], fill=(0, 0, 0, 40))
    
    # Blur the orbs heavily to create smooth gradient
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=100))
    
    # Composite
    out = Image.alpha_composite(base.convert('RGBA'), overlay)
    return out.convert('RGB')

def draw_glass_card(draw, x, y, w, h, radius=30):
    """Draws a semi-transparent 'glass' rounded rectangle."""
    # Glass Body: White with low opacity
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=(255, 255, 255, 230))
    # Glass Border: White with higher opacity (Simulate edge light)
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, outline=(255, 255, 255, 180), width=2)

def draw_glowing_text(draw, x, y, text, font, fill="white", glow_color=(255,255,255,100), radius=10, anchor="ms"):
    """Draws text with a soft glow/shadow behind it."""
    # Since we can't easily blur just text in one pass, we draw text multiple times with offset/opacity
    # Or just simple offset shadow for sharpness
    
    # Draw Shadow
    off = 2
    draw.text((x+off, y+off), text, font=font, anchor=anchor, fill=(0,0,0, 30))
    
    # Draw Main Text
    draw.text((x, y), text, font=font, anchor=anchor, fill=fill)

def draw_futuristic_gauge(draw, cx, cy, radius, percent, color_hex):
    """Draws a segmented, high-tech gauge."""
    # Track
    draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=135, end=405, fill=(255,255,255, 60), width=15)
    
    # Active
    active_end = 135 + (270 * percent)
    if percent > 0:
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=135, end=active_end, fill=(255,255,255, 255), width=15)
        
        # Glow Effect on Active Arc (Simulated by drawing thicker, transparent line behind)
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=135, end=active_end, fill=(255,255,255, 50), width=25)

    # Center Decor
    # Small ticks
    for i in range(135, 406, 45):
        rad = math.radians(i)
        sx = cx + (radius - 30) * math.cos(rad)
        sy = cy + (radius - 30) * math.sin(rad)
        ex = cx + (radius - 10) * math.cos(rad)
        ey = cy + (radius - 10) * math.sin(rad)
        draw.line([sx, sy, ex, ey], fill=(255,255,255, 100), width=2)

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a 'Vibrant Glass' style report card."""
    
    width, height = 900, 1350
    
    # 1. Background: Vibrant Atmosphere
    img = create_vibrant_background(width, height, color_hex)
    draw = ImageDraw.Draw(img, 'RGBA')

    # Fonts
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_med = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"

    font_reg_bytes = get_font(font_url_reg)
    font_bold_bytes = get_font(font_url_bold)
    font_med_bytes = get_font(font_url_med)

    if not all([font_reg_bytes, font_bold_bytes, font_med_bytes]):
        return None
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    f_hero_num = create_font(font_bold_bytes, 160)
    f_unit = create_font(font_med_bytes, 40)
    f_level = create_font(font_bold_bytes, 55)
    f_date = create_font(font_med_bytes, 24)
    f_header = create_font(font_bold_bytes, 32)
    f_card_title = create_font(font_bold_bytes, 26)
    f_card_desc = create_font(font_reg_bytes, 22)
    f_footer = create_font(font_reg_bytes, 18)

    # --- Header ---
    # Floating Header
    draw.text((50, 60), "PM2.5 REPORT", font=f_header, anchor="ls", fill="white")
    draw.text((width - 50, 60), "San Sai Hospital", font=f_header, anchor="rs", fill="white")
    draw.text((width/2, 110), date_str, font=f_date, anchor="ms", fill=(255,255,255, 200))
    
    draw.line([(50, 75), (width-50, 75)], fill=(255,255,255, 50), width=2)

    # --- Hero Section ---
    hero_cy = 400
    gauge_radius = 150
    max_pm = 200
    percent = min(latest_pm25 / max_pm, 1.0)
    
    # Gauge
    draw_futuristic_gauge(draw, width/2, hero_cy, gauge_radius, percent, color_hex)
    
    # Number with Shadow
    draw_glowing_text(draw, width/2, hero_cy + 10, f"{latest_pm25:.0f}", f_hero_num, anchor="ms")
    draw.text((width/2, hero_cy + 90), "μg/m³", font=f_unit, anchor="ms", fill=(255,255,255, 200))

    # Status Pill (Floating Glass)
    level_text = level
    bbox = draw.textbbox((0,0), level_text, font=f_level)
    l_w = bbox[2] - bbox[0] + 80
    l_h = 80
    pill_y = hero_cy + 160
    
    # Draw Pill Shape
    px1 = (width - l_w) / 2
    py1 = pill_y
    px2 = px1 + l_w
    py2 = py1 + l_h
    
    draw.rounded_rectangle([px1, py1, px2, py2], radius=40, fill=(255, 255, 255, 255))
    # Text in Pill (colored same as background concept, or dark grey)
    # We use a dark grey for contrast since pill is white
    draw.text((width/2, pill_y + 40), level_text, font=f_level, anchor="mm", fill="#333333")


    # --- Grid Section ---
    grid_start_y = pill_y + 120
    col_gap = 20
    row_gap = 20
    margin_side = 40
    
    # Calculate Card Size
    card_w = (width - (margin_side * 2) - col_gap) / 2
    card_h = 280
    
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        col = i % 2
        row = i // 2
        x = margin_side + col * (card_w + col_gap)
        y = grid_start_y + row * (card_h + row_gap)
        
        # Draw Glass Card
        draw_glass_card(draw, x, y, card_w, card_h, radius=35)
        
        # Icon
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(120, 120))
        if icon_img:
            ix = int(x + (card_w - 120) / 2)
            iy = int(y + 20)
            img.paste(icon_img, (ix, iy), icon_img)
        
        # Text
        tx = x + card_w / 2
        ty_title = y + 155
        
        draw.text((tx, ty_title), item['title'], font=f_card_title, anchor="ms", fill="#333333")
        
        # Wrap Desc
        desc = item['desc']
        words = desc.split()
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            bbox = draw.textbbox((0,0), " ".join(curr), font=f_card_desc)
            if (bbox[2]-bbox[0]) > (card_w - 30):
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        lines.append(" ".join(curr))
        
        ly = ty_title + 30
        for line in lines:
            draw.text((tx, ly), line, font=f_card_desc, anchor="ms", fill="#555555")
            ly += 26

    # --- Footer ---
    draw.text((width/2, height - 40), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill=(255,255,255, 150))

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
