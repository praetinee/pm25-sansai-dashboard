from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- Asset URLs (User provided 3D Icons - Latest) ---
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

def draw_gauge_modern(draw, center_x, center_y, radius, percent, color_hex):
    """Draws a modern, slim circular gauge."""
    start_angle = 135
    end_angle = 405
    total_angle = end_angle - start_angle
    thickness = 20  # Slimmer gauge
    
    # Background Arc (Light Gray)
    bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
    draw.arc(bbox, start=start_angle, end=end_angle, fill="#F0F0F0", width=thickness)
    
    # Active Arc (Colored)
    active_end_angle = start_angle + (total_angle * percent)
    # Draw slightly rounded ends by drawing lines with round caps (simulated via arc for now)
    draw.arc(bbox, start=start_angle, end=active_end_angle, fill=color_hex, width=thickness)
    
    # Decor: Small dot at the end of the arc
    # Calculate position of the end of the active arc
    end_rad = math.radians(active_end_angle)
    dot_x = center_x + radius * math.cos(end_rad)
    dot_y = center_y + radius * math.sin(end_rad)
    dot_size = 14
    draw.ellipse([dot_x - dot_size, dot_y - dot_size, dot_x + dot_size, dot_y + dot_size], fill=color_hex)

def get_contrast_text_color(hex_color):
    """Returns white or black depending on background brightness."""
    r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 180 else "#FFFFFF"

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a modern 'App Style' report card."""
    
    # --- 1. Setup Canvas ---
    width, height = 900, 1250 
    img = Image.new('RGB', (width, height), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # --- Fonts ---
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

    f_header_title = create_font(font_bold_bytes, 36)
    f_header_date = create_font(font_med_bytes, 24)
    f_pm_val = create_font(font_bold_bytes, 150)
    f_pm_unit = create_font(font_med_bytes, 32)
    f_level = create_font(font_bold_bytes, 48)
    f_card_title = create_font(font_bold_bytes, 26)
    f_card_desc = create_font(font_reg_bytes, 22)
    f_footer = create_font(font_reg_bytes, 18)

    # --- 2. Design: "Split View" (Top Color, Bottom White) ---
    header_height = 350
    
    # Draw Top Color Block
    draw.rectangle([(0, 0), (width, header_height + 50)], fill=color_hex)
    
    # Text Color for Header (Contrast check)
    header_txt_color = get_contrast_text_color(color_hex)

    # Header Text
    draw.text((width/2, 60), t[lang]['header'], font=f_header_title, anchor="ms", fill=header_txt_color)
    draw.text((width/2, 100), date_str, font=f_header_date, anchor="ms", fill=header_txt_color)

    # --- 3. Main Content Card (White Sheet) ---
    sheet_y = 220
    draw.rounded_rectangle([(20, sheet_y), (width - 20, height - 20)], radius=40, fill="#FFFFFF")
    
    # --- 4. Hero Section (Gauge) ---
    # Centered relative to the top part of the white sheet
    gauge_center_y = sheet_y + 180
    max_pm = 200
    gauge_percent = min(latest_pm25 / max_pm, 1.0)
    gauge_radius = 140
    
    # Draw Gauge
    draw_gauge_modern(draw, width/2, gauge_center_y, gauge_radius, gauge_percent, color_hex)
    
    # Values
    draw.text((width/2, gauge_center_y + 20), f"{latest_pm25:.0f}", font=f_pm_val, anchor="ms", fill="#2C3E50")
    draw.text((width/2, gauge_center_y + 75), "μg/m³", font=f_pm_unit, anchor="ms", fill="#95A5A6")
    
    # Level Badge
    level_text = level
    bbox = draw.textbbox((0, 0), level_text, font=f_level)
    text_w = bbox[2] - bbox[0]
    badge_w = text_w + 100
    badge_h = 70
    badge_x = (width - badge_w) / 2
    badge_y = gauge_center_y + 130
    
    # Use a very light tint of the main color for the badge background
    # (Mixing color_hex with white)
    r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    tint_r = int(r + (255 - r) * 0.85)
    tint_g = int(g + (255 - g) * 0.85)
    tint_b = int(b + (255 - b) * 0.85)
    badge_bg = (tint_r, tint_g, tint_b)
    
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=35, fill=badge_bg)
    # Text in badge uses the main color for elegance
    draw.text((width/2, badge_y + 35), level_text, font=f_level, anchor="mm", fill=color_hex)

    # --- 5. Advice Grid (Clean Style) ---
    grid_start_y = gauge_center_y + 220
    
    col_gap = 25
    row_gap = 25
    margin_side = 50
    card_w = (width - (margin_side * 2) - col_gap) / 2
    card_h = 290
    
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
        
        # Minimalist Card Background (Very light grey, no border)
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=30, fill="#F8F9FA")

        # Load & Paste 3D Icon
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(130, 130))
        if icon_img:
            # Center icon horizontally
            icon_x = int(x + (card_w - 130) / 2)
            icon_y = int(y + 20)
            img.paste(icon_img, (icon_x, icon_y), icon_img)
        
        # Text
        text_center_x = x + card_w / 2
        
        # Title
        draw.text((text_center_x, y + 170), item['title'], font=f_card_title, anchor="ms", fill="#34495E")
        
        # Description (Wrapping)
        desc_text = item['desc']
        words = desc_text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            line_str = " ".join(current_line)
            line_bbox = draw.textbbox((0, 0), line_str, font=f_card_desc)
            if (line_bbox[2] - line_bbox[0]) > (card_w - 30):
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        line_y = y + 200
        for line in lines:
            draw.text((text_center_x, line_y), line, font=f_card_desc, anchor="ms", fill="#7F8C8D")
            line_y += 28

    # --- 6. Footer ---
    draw.text((width/2, height - 40), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill="#BDC3C7")

    # --- 7. Output ---
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
