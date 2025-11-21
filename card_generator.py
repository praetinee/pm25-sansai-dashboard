from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- Asset URLs ---
ICON_URLS = {
    'mask': "https://i.postimg.cc/cLt9Mhwq/Gemini-Generated-Image-rkwajtrkwajtrkwa.png",
    'activity': "https://i.postimg.cc/mDBm4GqW/Gemini-Generated-Image-16wol216wol216wo.png",
    'indoors': "https://i.postimg.cc/mg9jFDfp/Gemini-Generated-Image-8gbf4e8gbf4e8gbf.png",
    'risk_group': "https://i.postimg.cc/mrGw3sTL/Gemini-Generated-Image-4oj4z84oj4z84oj4.png"
}

@st.cache_data
def get_font(url):
    """Downloads a font file and caches it."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Font download failed: {e}")
        return None

@st.cache_data
def get_image_from_url(url, size=(150, 150)):
    """Downloads an image, resizes it, and caches it."""
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

def draw_gradient_rect(draw, img_width, height, color_hex):
    """Draws a vertical gradient rectangle (simulated)."""
    r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Create a simple gradient by darkening the color slightly towards the bottom
    for y in range(height):
        # Factor ranges from 1.0 (top) to 0.8 (bottom)
        factor = 1.0 - (0.2 * (y / height))
        nr = int(r * factor)
        ng = int(g * factor)
        nb = int(b * factor)
        draw.line([(0, y), (img_width, y)], fill=(nr, ng, nb), width=1)

def draw_gauge(draw, center_x, center_y, radius, percent, color_hex):
    """Draws a gauge arc."""
    start_angle = 135
    end_angle = 405
    total_angle = end_angle - start_angle
    
    # Draw background arc (gray)
    bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
    draw.arc(bbox, start=start_angle, end=end_angle, fill="#E0E0E0", width=25)
    
    # Draw active arc
    active_end_angle = start_angle + (total_angle * percent)
    draw.arc(bbox, start=start_angle, end=active_end_angle, fill=color_hex, width=25)
    
    # Draw rounded ends (optional polish)
    # Start point
    sx = center_x + radius * math.cos(math.radians(start_angle))
    sy = center_y + radius * math.sin(math.radians(start_angle))
    # draw.ellipse([sx-12, sy-12, sx+12, sy+12], fill=color_hex) 

def create_rounded_card(width, height, radius, fill_color):
    """Creates a rounded rectangle image."""
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)
    
    img = Image.new('RGBA', (width, height), fill_color)
    img.putalpha(mask)
    return img

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a modern, grid-layout report card with 3D icons."""
    
    # --- 1. Setup Canvas & Fonts ---
    width, height = 900, 1200 # Increased size for better layout
    img = Image.new('RGB', (width, height), color="#FFFFFF") # Clean white background
    draw = ImageDraw.Draw(img)

    # Load Fonts
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

    f_header = create_font(font_bold_bytes, 42)
    f_date = create_font(font_med_bytes, 26)
    f_pm_val = create_font(font_bold_bytes, 140)
    f_pm_unit = create_font(font_med_bytes, 36)
    f_level = create_font(font_bold_bytes, 52)
    f_card_title = create_font(font_bold_bytes, 28)
    f_card_desc = create_font(font_reg_bytes, 24)
    f_footer = create_font(font_reg_bytes, 20)

    # --- 2. Draw Header Section (Gradient) ---
    header_height = 420
    draw_gradient_rect(draw, width, header_height, color_hex)
    
    # Header Text
    draw.text((width/2, 50), t[lang]['header'], font=f_header, anchor="ms", fill="#FFFFFF")
    draw.text((width/2, 90), date_str, font=f_date, anchor="ms", fill="rgba(255, 255, 255, 200)")

    # --- 3. Hero Section (Gauge & Value) ---
    # Gauge Logic
    max_pm = 200 # Max value for gauge to be full
    gauge_percent = min(latest_pm25 / max_pm, 1.0)
    gauge_radius = 130
    gauge_center_y = 230
    
    # Draw white circle background for text readability
    draw.ellipse([width/2 - 180, gauge_center_y - 180, width/2 + 180, gauge_center_y + 180], fill="#FFFFFF")
    
    # Draw Gauge
    draw_gauge(draw, width/2, gauge_center_y, gauge_radius + 20, gauge_percent, color_hex)

    # Value & Unit
    draw.text((width/2, gauge_center_y + 20), f"{latest_pm25:.0f}", font=f_pm_val, anchor="ms", fill="#333333")
    draw.text((width/2, gauge_center_y + 70), "μg/m³", font=f_pm_unit, anchor="ms", fill="#777777")
    
    # Level Badge (Capsule) below gauge
    level_text = level
    # Calculate text size to size the badge
    bbox = draw.textbbox((0, 0), level_text, font=f_level)
    text_w = bbox[2] - bbox[0]
    badge_w = text_w + 80
    badge_h = 80
    badge_x = (width - badge_w) / 2
    badge_y = gauge_center_y + 110
    
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=40, fill=color_hex)
    draw.text((width/2, badge_y + 40), level_text, font=f_level, anchor="mm", fill="#FFFFFF")

    # --- 4. Advice Grid Section ---
    grid_start_y = header_height + 40
    
    # Layout Config
    col_gap = 30
    row_gap = 30
    margin_side = 40
    card_w = (width - (margin_side * 2) - col_gap) / 2
    card_h = 300
    
    # Define Cards Content
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        # Calculate Position
        col = i % 2
        row = i // 2
        x = margin_side + col * (card_w + col_gap)
        y = grid_start_y + row * (card_h + row_gap)
        
        # Draw Card Background (Soft Gray)
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=25, fill="#F7F9FC")
        # Optional: Add a subtle border
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=25, outline="#E8EDF2", width=2)

        # Load & Paste Icon
        icon_img = get_image_from_url(ICON_URLS[item['icon_key']], size=(140, 140))
        if icon_img:
            # Center icon horizontally in card, place near top
            icon_x = int(x + (card_w - 140) / 2)
            icon_y = int(y + 20)
            img.paste(icon_img, (icon_x, icon_y), icon_img)
        
        # Draw Text
        text_center_x = x + card_w / 2
        # Title (Bold, Dark)
        draw.text((text_center_x, y + 180), item['title'], font=f_card_title, anchor="ms", fill="#2C3E50")
        
        # Description (Regular, Lighter, Wrapped)
        # Simple wrapping logic
        desc_text = item['desc']
        words = desc_text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            # Check width
            line_str = " ".join(current_line)
            line_bbox = draw.textbbox((0, 0), line_str, font=f_card_desc)
            if (line_bbox[2] - line_bbox[0]) > (card_w - 30):
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Draw lines
        line_y = y + 210
        for line in lines:
            draw.text((text_center_x, line_y), line, font=f_card_desc, anchor="ms", fill="#5D6D7E")
            line_y += 30

    # --- 5. Footer ---
    footer_y = height - 50
    draw.text((width/2, footer_y), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill="#95A5A6")

    # --- 6. Finalize ---
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
