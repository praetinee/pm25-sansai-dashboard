from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops
import requests
from io import BytesIO
import streamlit as st
import math

# --- Assets ---
# ไอคอน 3D จะถูกนำมาใช้ แต่จะปรับแสงและเงาให้เข้ากับธีมใหม่
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

# --- Advanced Graphics Engine ---

def create_mesh_gradient(width, height, color_hex):
    """Creates a high-end mesh gradient background."""
    try:
        r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except:
        r, g, b = 200, 200, 200

    # Base: Slightly desaturated version of main color
    base_color = (int(r*0.95), int(g*0.95), int(b*0.95))
    base = Image.new('RGB', (width, height), base_color)
    
    # Overlay Layer for Orbs
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    # Orb 1: Top Left - Lighter/White Tint (Sunlight effect)
    draw.ellipse([-400, -400, 800, 800], fill=(255, 255, 255, 60))
    
    # Orb 2: Bottom Right - Main Color Saturated
    draw.ellipse([width-800, height-800, width+200, height+200], fill=(r, g, b, 80))
    
    # Orb 3: Center - Subtle glow
    draw.ellipse([width//2-400, height//2-400, width//2+400, height//2+400], fill=(255, 255, 255, 20))

    # Heavy Blur to blend everything into a mesh
    overlay = overlay.filter(ImageFilter.GaussianBlur(180))
    
    return Image.alpha_composite(base.convert('RGBA'), overlay).convert('RGB')

def draw_frosted_glass(img, x, y, w, h, radius=40, blur_strength=30, opacity=180):
    """
    Draws a realistic frosted glass panel.
    1. Blurs the background behind the panel.
    2. Adds a white tint with noise for texture.
    3. Adds a subtle border and shadow.
    """
    # Crop & Blur Background
    crop = img.crop((x, y, x+w, y+h))
    crop = crop.filter(ImageFilter.GaussianBlur(blur_strength))
    
    # Brighten slightly
    enhancer = ImageEnhance.Brightness(crop)
    crop = enhancer.enhance(1.1)
    
    # Paste blurred background back
    img.paste(crop, (x, y))
    
    # Create Glass Overlay
    glass = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(glass)
    
    # Fill with white tint
    draw.rounded_rectangle([(0,0), (w, h)], radius=radius, fill=(255, 255, 255, opacity))
    
    # Add subtle noise/texture (Optional, skipping for performance, using gradient stroke instead)
    
    # Border (Inner Glow)
    draw.rounded_rectangle([(0,0), (w, h)], radius=radius, outline=(255, 255, 255, 200), width=2)
    
    # Composite
    img.paste(glass, (x, y), glass)
    
    # Add Drop Shadow (External)
    # We need to draw shadow on the main image before pasting glass, technically.
    # But since we already pasted, we can't put shadow under.
    # Correct approach: Draw shadow first, then glass.
    # For this function, we assume shadow is handled outside or we draw a rim shadow inside.

def draw_soft_shadow(draw, x, y, w, h, radius, opacity=40):
    """Draws a soft shadow for a card."""
    # Simulate by drawing a black rect with blur
    # Since we can't blur on `draw` context directly, we skip true blur here.
    # Instead, we draw multiple offset rects with low opacity to simulate a shadow gradient.
    for i in range(10, 0, -1):
        alpha = int(opacity / 10)
        offset = i * 2
        draw.rounded_rectangle([x-2, y-2+offset/2, x+w+2, y+h+offset], radius=radius, fill=(0,0,0, alpha))

# --- Main Logic ---

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates the 'Neo-Glassmorphism' Report Card."""
    
    width, height = 1000, 1600
    
    # 1. Background: Dynamic Mesh
    img = create_mesh_gradient(width, height, color_hex)
    draw = ImageDraw.Draw(img, 'RGBA')

    # Fonts
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_med = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"
    font_url_light = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Light.ttf"

    font_bold = get_font(font_url_bold)
    font_reg = get_font(font_url_reg)
    font_med = get_font(font_url_med)
    font_light = get_font(font_url_light)

    if not all([font_bold, font_reg, font_med, font_light]): return None
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    # Typography
    f_hero = create_font(font_bold, 220)
    f_unit = create_font(font_med, 40)
    f_status = create_font(font_bold, 60)
    f_header = create_font(font_bold, 36)
    f_date = create_font(font_med, 24)
    f_card_title = create_font(font_bold, 28)
    f_card_desc = create_font(font_reg, 24)
    f_footer = create_font(font_light, 22)

    # --- Layout ---
    
    # 1. Header (Floating Glass Pill)
    header_w = 800
    header_h = 120
    header_x = (width - header_w) // 2
    header_y = 60
    
    # Shadow
    draw_soft_shadow(draw, header_x, header_y, header_w, header_h, 60, opacity=30)
    # Glass
    draw.rounded_rectangle([header_x, header_y, header_x+header_w, header_y+header_h], radius=60, fill=(255,255,255, 240))
    
    # Content
    draw.text((width/2, header_y + 35), "San Sai Hospital", font=f_header, anchor="ms", fill="#1E293B")
    draw.text((width/2, header_y + 80), date_str, font=f_date, anchor="ms", fill="#64748B")

    # 2. Hero Section (Center Stage)
    hero_cy = 450
    
    # Circular Gauge Background (Frosted)
    gauge_size = 500
    gx = (width - gauge_size) // 2
    gy = hero_cy - gauge_size // 2
    
    # Shadow for Gauge
    draw.ellipse([gx+20, gy+40, gx+gauge_size-20, gy+gauge_size+20], fill=(0,0,0, 20))
    # Gauge Disc (White)
    draw.ellipse([gx, gy, gx+gauge_size, gy+gauge_size], fill=(255,255,255, 255))
    
    # Ring
    track_r = 210
    thickness = 30
    draw.arc([width/2-track_r, hero_cy-track_r, width/2+track_r, hero_cy+track_r], start=135, end=405, fill="#F1F5F9", width=thickness)
    
    # Progress Ring
    percent = min(latest_pm25 / 200, 1.0)
    active_end = 135 + (270 * percent)
    if percent > 0:
        draw.arc([width/2-track_r, hero_cy-track_r, width/2+track_r, hero_cy+track_r], start=135, end=active_end, fill=color_hex, width=thickness)
        # Rounded Cap
        er = math.radians(active_end)
        ex = width/2 + track_r * math.cos(er)
        ey = hero_cy + track_r * math.sin(er)
        draw.ellipse([ex-thickness/2, ey-thickness/2, ex+thickness/2, ey+thickness/2], fill=color_hex)

    # Text
    draw.text((width/2, hero_cy + 20), f"{latest_pm25:.0f}", font=f_hero, anchor="ms", fill="#1E293B")
    draw.text((width/2, hero_cy + 120), "μg/m³", font=f_unit, anchor="ms", fill="#94A3B8")
    
    # Status Pill
    status_y = hero_cy + 280
    pill_w = 400
    pill_h = 90
    pill_x = (width - pill_w) // 2
    
    draw.rounded_rectangle([pill_x, status_y, pill_x+pill_w, status_y+pill_h], radius=45, fill=color_hex)
    draw.text((width/2, status_y + 45), level, font=f_status, anchor="mm", fill="white")

    # 3. Advice Grid (Modern Cards)
    grid_y = status_y + 160
    col_gap = 40
    row_gap = 40
    margin_x = 60
    
    card_w = (width - (margin_x * 2) - col_gap) / 2
    card_h = 320
    
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        col = i % 2
        row = i // 2
        x = margin_x + col * (card_w + col_gap)
        y = grid_y + row * (card_h + row_gap)
        
        # Card Shadow
        draw_soft_shadow(draw, x, y, card_w, card_h, 40, opacity=25)
        # Card Body (White)
        draw.rounded_rectangle([x, y, x+card_w, y+card_h], radius=40, fill="white")
        
        # Icon Circle (Top Left)
        circle_r = 50
        cx = x + 70
        cy = y + 70
        draw.ellipse([cx-circle_r, cy-circle_r, cx+circle_r, cy+circle_r], fill="#F8FAFC")
        
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(80, 80))
        if icon_img:
            img.paste(icon_img, (int(cx-40), int(cy-40)), icon_img)
            
        # Text
        title_x = x + 40
        title_y = y + 150
        draw.text((title_x, title_y), item['title'], font=f_card_title, fill="#334155")
        
        # Desc wrap
        desc = item['desc']
        words = desc.split()
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            if draw.textlength(" ".join(curr), font=f_card_desc) > (card_w - 60):
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        lines.append(" ".join(curr))
        
        ly = title_y + 45
        for line in lines[:2]: # Max 2 lines
            draw.text((title_x, ly), line, font=f_card_desc, fill="#64748B")
            ly += 30

    # 4. Footer
    footer_y = height - 60
    draw.text((width/2, footer_y), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill=(255,255,255, 200)) # Light text on gradient bg

    # Output
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
