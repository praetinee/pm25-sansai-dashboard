from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- Assets ---
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
def get_image_from_url(url, size=(180, 180)): # Increased fetch size for better quality
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

# --- Graphics Helpers ---

def mask_image_rounded(img, radius=40):
    """Crops an image into a rounded rectangle (Squircle)."""
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    
    # Apply mask
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

def create_premium_gradient(width, height, hex_color):
    """Creates a soft, luxurious mesh-like gradient."""
    try:
        r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except:
        r, g, b = 50, 50, 50

    # Base background (Slightly darker than main color for depth)
    base = Image.new('RGB', (width, height), (int(r*0.9), int(g*0.9), int(b*0.9)))
    
    # Create "Spotlights" using radial gradients
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    # Top-Left Highlight (White/Bright)
    draw.ellipse([-200, -200, 600, 600], fill=(255, 255, 255, 50))
    
    # Bottom-Right Shadow (Darker)
    draw.ellipse([width-600, height-600, width+200, height+200], fill=(0, 0, 0, 60))
    
    # Extreme Blur to blend
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    
    return Image.alpha_composite(base.convert('RGBA'), overlay).convert('RGB')

def draw_glass_panel(draw, x, y, w, h, radius=40, opacity=240):
    """Draws a high-quality glass panel with border."""
    # 1. Subtle Shadow
    shadow_offset = 10
    draw.rounded_rectangle([x, y+shadow_offset, x+w, y+h+shadow_offset], radius=radius, fill=(0,0,0, 30))
    
    # 2. Main Glass Body (White)
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=(255, 255, 255, opacity))
    
    # 3. Inner Border (Stroke) - Adds "crispness"
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, outline=(255, 255, 255, 255), width=2)

def draw_elegant_gauge(draw, cx, cy, radius, percent, color_hex):
    """Draws a thin, elegant gauge ring."""
    thickness = 12
    
    # Track (White with low opacity)
    draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=135, end=405, fill=(255,255,255, 60), width=thickness)
    
    # Progress
    active_end = 135 + (270 * percent)
    if percent > 0:
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=135, end=active_end, fill=(255,255,255, 255), width=thickness)
        
        # End Dot (Glossy)
        er = math.radians(active_end)
        ex = cx + radius * math.cos(er)
        ey = cy + radius * math.sin(er)
        
        # Outer Glow
        draw.ellipse([ex-10, ey-10, ex+10, ey+10], fill=(255,255,255, 100))
        # Core
        draw.ellipse([ex-5, ey-5, ex+5, ey+5], fill=(255,255,255, 255))

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a 'Premium & Shareable' report card."""
    
    # Canvas Size: Taller for better proportions
    width, height = 1000, 1500 
    
    # 1. Background
    img = create_premium_gradient(width, height, color_hex)
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

    # Optimized Font Sizes
    f_hero_val = create_font(font_bold_bytes, 160)
    f_hero_unit = create_font(font_med_bytes, 36)
    f_header = create_font(font_bold_bytes, 32)
    f_date = create_font(font_med_bytes, 22)
    f_status = create_font(font_bold_bytes, 50)
    
    f_card_title = create_font(font_bold_bytes, 26)
    f_card_desc = create_font(font_reg_bytes, 22)
    f_footer = create_font(font_med_bytes, 20)

    # --- Header Section ---
    # Brand Name
    draw.text((60, 70), "PM2.5 MONITOR", font=f_header, anchor="ls", fill=(255, 255, 255, 240))
    draw.text((width - 60, 70), "San Sai Hospital", font=f_header, anchor="rs", fill=(255, 255, 255, 240))
    
    # Date Pill (Centered, Glassy)
    date_w = draw.textlength(date_str, font=f_date) + 50
    draw.rounded_rectangle([(width-date_w)/2, 100, (width+date_w)/2, 150], radius=25, fill=(255,255,255, 40))
    draw.text((width/2, 125), date_str, font=f_date, anchor="mm", fill="white")

    # --- Hero Section (The Gauge) ---
    hero_cy = 420
    gauge_radius = 160
    
    # Draw Gauge
    draw_elegant_gauge(draw, width/2, hero_cy, gauge_radius, min(latest_pm25/200, 1.0), color_hex)
    
    # Value
    draw.text((width/2, hero_cy + 10), f"{latest_pm25:.0f}", font=f_hero_val, anchor="ms", fill="white")
    draw.text((width/2, hero_cy + 80), "μg/m³", font=f_hero_unit, anchor="ms", fill=(255,255,255, 200))
    
    # Status Badge (Below Gauge)
    status_y = hero_cy + 140
    level_text = level
    l_w = draw.textlength(level_text, font=f_status) + 80
    
    draw.rounded_rectangle([(width-l_w)/2, status_y, (width+l_w)/2, status_y+80], radius=40, fill="white")
    
    # Text Color logic for contrast inside white badge
    # Using a dark gray for best readability
    draw.text((width/2, status_y + 40), level_text, font=f_status, anchor="mm", fill="#2D3748")

    # --- Grid Layout (Perfectly Proportioned) ---
    grid_y_start = status_y + 140
    
    # Layout Math
    margin_x = 50
    col_gap = 30
    row_gap = 30
    
    # Two columns
    card_width = (width - (margin_x * 2) - col_gap) / 2
    card_height = 320 # Taller cards to fit text better
    
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        col = i % 2
        row = i // 2
        x = margin_x + col * (card_width + col_gap)
        y = grid_y_start + row * (card_height + row_gap)
        
        # 1. Draw Glass Card Background
        draw_glass_panel(draw, x, y, card_width, card_height, radius=35, opacity=245) # Nearly opaque white
        
        # 2. Icon (Round & Beautiful)
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(160, 160))
        if icon_img:
            # Apply rounding mask to icon
            icon_img = mask_image_rounded(icon_img, radius=30)
            
            # Centered horizontally, top padding
            ix = int(x + (card_width - 160) / 2)
            iy = int(y + 25)
            img.paste(icon_img, (ix, iy), icon_img)
            
        # 3. Text Content
        text_center_x = x + card_width / 2
        text_start_y = y + 200
        
        # Title (Bold, Dark)
        draw.text((text_center_x, text_start_y), item['title'], font=f_card_title, anchor="ms", fill="#1A202C")
        
        # Description (Lighter, wrapped)
        desc = item['desc']
        
        # Smart Wrapping
        words = desc.split()
        lines = []
        curr_line = []
        for w in words:
            curr_line.append(w)
            w_bbox = draw.textbbox((0,0), " ".join(curr_line), font=f_card_desc)
            if (w_bbox[2] - w_bbox[0]) > (card_width - 40):
                curr_line.pop()
                lines.append(" ".join(curr_line))
                curr_line = [w]
        lines.append(" ".join(curr_line))
        
        line_y = text_start_y + 35
        for line in lines:
            draw.text((text_center_x, line_y), line, font=f_card_desc, anchor="ms", fill="#4A5568")
            line_y += 28

    # --- Footer ---
    footer_y = height - 60
    draw.line([(100, footer_y - 40), (width-100, footer_y - 40)], fill=(255,255,255, 80), width=1)
    draw.text((width/2, footer_y), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill=(255,255,255, 200))

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
