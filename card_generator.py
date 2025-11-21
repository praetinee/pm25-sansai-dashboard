from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- Asset URLs (Updated with User provided 3D Icons - Latest) ---
ICON_URLS = {
    'mask': "https://i.postimg.cc/wB0w9rd9/Gemini-Generated-Image-rkwajtrkwajtrkwa.png",
    'activity': "https://i.postimg.cc/FFdXnyj1/Gemini-Generated-Image-16wol216wol216wo.png",
    'indoors': "https://i.postimg.cc/RVw5vvpJ/Gemini-Generated-Image-8gbf4e8gbf4e8gbf.png",
    'risk_group': "https://i.postimg.cc/8CKxZccL/Gemini-Generated-Image-4oj4z84oj4z84oj4.png"
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
    """Draws a vertical gradient rectangle (simulated) for the header."""
    try:
        r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        # Fallback to grey if color code is invalid
        r, g, b = 100, 100, 100
    
    # Create a simple gradient by darkening the color slightly towards the bottom
    for y in range(height):
        # Factor ranges from 1.0 (top) to 0.8 (bottom)
        factor = 1.0 - (0.2 * (y / height))
        nr = int(r * factor)
        ng = int(g * factor)
        nb = int(b * factor)
        draw.line([(0, y), (img_width, y)], fill=(nr, ng, nb), width=1)

def draw_gauge(draw, center_x, center_y, radius, percent, color_hex):
    """Draws a circular gauge arc around the PM2.5 value."""
    start_angle = 135
    end_angle = 405
    total_angle = end_angle - start_angle
    
    # Draw background arc (gray)
    bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
    draw.arc(bbox, start=start_angle, end=end_angle, fill="#E0E0E0", width=25)
    
    # Draw active arc based on pollution level
    active_end_angle = start_angle + (total_angle * percent)
    draw.arc(bbox, start=start_angle, end=active_end_angle, fill=color_hex, width=25)
    
    # Optional: Draw small circles at the ends for a rounded look
    # (Simplified for clean code)

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a modern, grid-layout report card using 3D assets."""
    
    # --- 1. Setup Canvas & Fonts ---
    width, height = 900, 1200 # Increased size for better grid layout
    img = Image.new('RGB', (width, height), color="#FFFFFF") # Clean white background
    draw = ImageDraw.Draw(img)

    # Load Sarabun Fonts
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

    # Define Text Styles
    f_header = create_font(font_bold_bytes, 42)
    f_date = create_font(font_med_bytes, 26)
    f_pm_val = create_font(font_bold_bytes, 140)
    f_pm_unit = create_font(font_med_bytes, 36)
    f_level = create_font(font_bold_bytes, 52)
    f_card_title = create_font(font_bold_bytes, 28)
    f_card_desc = create_font(font_reg_bytes, 24)
    f_footer = create_font(font_reg_bytes, 20)

    # --- 2. Draw Header Section (Gradient Background) ---
    header_height = 420
    draw_gradient_rect(draw, width, header_height, color_hex)
    
    # Header Text
    draw.text((width/2, 50), t[lang]['header'], font=f_header, anchor="ms", fill="#FFFFFF")
    draw.text((width/2, 90), date_str, font=f_date, anchor="ms", fill="rgba(255, 255, 255, 200)")

    # --- 3. Hero Section (Gauge & PM2.5 Value) ---
    # Gauge Calculation
    max_pm = 200 # Value where gauge becomes full
    gauge_percent = min(latest_pm25 / max_pm, 1.0)
    gauge_radius = 130
    gauge_center_y = 230
    
    # Draw white circle background behind the gauge for better readability
    draw.ellipse([width/2 - 180, gauge_center_y - 180, width/2 + 180, gauge_center_y + 180], fill="#FFFFFF")
    
    # Draw the Gauge
    draw_gauge(draw, width/2, gauge_center_y, gauge_radius + 20, gauge_percent, color_hex)

    # PM2.5 Value & Unit
    draw.text((width/2, gauge_center_y + 20), f"{latest_pm25:.0f}", font=f_pm_val, anchor="ms", fill="#333333")
    draw.text((width/2, gauge_center_y + 70), "μg/m³", font=f_pm_unit, anchor="ms", fill="#777777")
    
    # Level Badge (Capsule shape)
    level_text = level
    bbox = draw.textbbox((0, 0), level_text, font=f_level)
    text_w = bbox[2] - bbox[0]
    badge_w = text_w + 80
    badge_h = 80
    badge_x = (width - badge_w) / 2
    badge_y = gauge_center_y + 110
    
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=40, fill=color_hex)
    draw.text((width/2, badge_y + 40), level_text, font=f_level, anchor="mm", fill="#FFFFFF")

    # --- 4. Advice Grid Section (2x2 Cards) ---
    grid_start_y = header_height + 40
    
    # Grid Config
    col_gap = 30
    row_gap = 30
    margin_side = 40
    card_w = (width - (margin_side * 2) - col_gap) / 2
    card_h = 300
    
    # Map advice data to icon keys
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        # Calculate Position
        col = i % 2
        row = i // 2
        x = margin_side + col * (card_w + col_gap)
        y = grid_start_y + row * (card_h + row_gap)
        
        # Draw Card Background
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=25, fill="#F7F9FC") # Soft grey background
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=25, outline="#E8EDF2", width=2) # Subtle border

        # Load & Paste 3D Icon
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(140, 140))
        if icon_img:
            # Place icon centered horizontally, near the top
            icon_x = int(x + (card_w - 140) / 2)
            icon_y = int(y + 20)
            img.paste(icon_img, (icon_x, icon_y), icon_img)
        
        # Draw Text
        text_center_x = x + card_w / 2
        # Title
        draw.text((text_center_x, y + 180), item['title'], font=f_card_title, anchor="ms", fill="#2C3E50")
        
        # Description (with basic text wrapping)
        desc_text = item['desc']
        words = desc_text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            # Measure width
            line_str = " ".join(current_line)
            line_bbox = draw.textbbox((0, 0), line_str, font=f_card_desc)
            if (line_bbox[2] - line_bbox[0]) > (card_w - 30): # 30px padding
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Render lines
        line_y = y + 210
        for line in lines:
            draw.text((text_center_x, line_y), line, font=f_card_desc, anchor="ms", fill="#5D6D7E")
            line_y += 30

    # --- 5. Footer ---
    footer_y = height - 50
    draw.text((width/2, footer_y), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill="#95A5A6")

    # --- 6. Save & Return ---
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
