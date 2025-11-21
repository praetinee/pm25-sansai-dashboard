from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
from io import BytesIO
import streamlit as st
import math

# --- 3D Assets (Keep the same) ---
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

# --- Graphic Helpers ---

def create_gradient_background(width, height, start_color_hex):
    """Creates a smooth vertical gradient background."""
    base = Image.new('RGB', (width, height), start_color_hex)
    
    # Parse Hex
    try:
        r, g, b = tuple(int(start_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except:
        r, g, b = 100, 100, 100

    # Create gradient to a lighter/shifted version
    # We make the bottom slightly lighter/desaturated to simulate sky/atmosphere
    top_color = (r, g, b)
    bottom_color = (min(r + 30, 255), min(g + 30, 255), min(b + 30, 255))

    gradient = Image.new('RGB', (width, height), top_color)
    draw = ImageDraw.Draw(gradient)

    for y in range(height):
        ratio = y / height
        nr = int(r * (1 - ratio) + bottom_color[0] * ratio)
        ng = int(g * (1 - ratio) + bottom_color[1] * ratio)
        nb = int(b * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(nr, ng, nb))
    
    return gradient

def create_drop_shadow(width, height, radius, blur=20, opacity=50):
    """Creates a soft shadow."""
    w_int = int(width)
    h_int = int(height)
    shadow = Image.new('RGBA', (w_int + blur*4, h_int + blur*4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    
    # Draw centered shadow rect
    draw.rounded_rectangle(
        [blur*2, blur*2, blur*2 + w_int, blur*2 + h_int], 
        radius=radius, 
        fill=(0, 0, 0, opacity)
    )
    return shadow.filter(ImageFilter.GaussianBlur(blur))

def draw_modern_gauge(draw, cx, cy, radius, percent, color=(255,255,255)):
    """Draws a minimal, high-end circular track."""
    # Background Track (Semi-transparent white)
    thickness = 18
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    
    # Use a loop to draw semi-transparent arc manually or use simple solid for PIL
    # For clean look on colored background, we use a white track with low alpha
    # Since PIL draw.arc doesn't support alpha directly on RGB images easily without layers,
    # we will assume we are drawing on a layer or just use solid colors.
    
    # Here we draw "Track" in lighter shade of the background or pure white with transparency
    # Simulating transparency by mixing: 
    # Actually, let's just draw a White Ring with 30% opacity look? 
    # Hard to do without layers. Let's use Solid White for the Progress and Faint White for Track.
    
    draw.arc(bbox, start=135, end=405, fill=(255, 255, 255, 80), width=thickness) # Track
    
    # Active Progress
    start = 135
    span = 270
    end = start + (span * percent)
    
    if percent > 0:
        draw.arc(bbox, start=start, end=end, fill=(255, 255, 255, 255), width=thickness) # Bright White
        
        # End Cap Dot
        er = math.radians(end)
        ex = cx + radius * math.cos(er)
        ey = cy + radius * math.sin(er)
        # Glow effect on dot
        draw.ellipse([ex-12, ey-12, ex+12, ey+12], fill=(255,255,255, 100))
        draw.ellipse([ex-6, ey-6, ex+6, ey+6], fill=(255,255,255, 255))


def get_text_color_for_bg(hex_color):
    """Decides if text should be black or white based on bg brightness."""
    try:
        r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        # If background is very bright (Yellow), use Dark Text. Otherwise White.
        return "#2D3748" if brightness > 200 else "#FFFFFF"
    except:
        return "#FFFFFF"

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """
    Generates a 'Modern Editorial' style report card.
    Concept: Immersive Color Top + Clean White Bottom Sheet.
    """
    
    # --- Canvas Setup ---
    width, height = 900, 1350
    
    # 1. Create The Atmosphere (Background)
    # We use the AQI color as the base for the whole card's mood
    img = create_gradient_background(width, height, color_hex)
    draw = ImageDraw.Draw(img)

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

    # Typography Scale
    f_super_num = create_font(font_bold_bytes, 180)
    f_unit = create_font(font_med_bytes, 40)
    f_status = create_font(font_bold_bytes, 60)
    f_date = create_font(font_med_bytes, 24)
    f_header = create_font(font_bold_bytes, 32)
    
    f_card_title = create_font(font_bold_bytes, 28)
    f_card_desc = create_font(font_reg_bytes, 22)
    f_footer = create_font(font_reg_bytes, 20)

    # Text Color Logic (Dynamic)
    # The top part text color depends on the AQI color
    hero_txt_color = get_text_color_for_bg(color_hex)
    
    # --- 2. Top Section: The Mood (55% height) ---
    # Header Info
    draw.text((40, 50), "PM2.5 REPORT", font=f_header, anchor="ls", fill=hero_txt_color)
    draw.text((width - 40, 50), "San Sai Hospital", font=f_header, anchor="rs", fill=hero_txt_color)
    
    # Date Centered with opacity
    # We draw date slightly lower
    draw.text((width/2, 100), date_str, font=f_date, anchor="ms", fill=hero_txt_color)

    # Main Hero: The Number
    # Position: Center of the top section
    hero_cy = 380
    
    # Draw Gauge (White style)
    # If background is very bright (Yellow), maybe draw gauge in Dark Grey?
    # For simplicity, let's assume White Gauge looks good on most colors except Yellow.
    # If Yellow, we might need a backing circle.
    
    # Let's add a subtle "Glow" behind the number
    # Create a soft radial gradient overlay? (Skip for performance, use circle)
    
    gauge_radius = 160
    max_pm = 200
    percent = min(latest_pm25 / max_pm, 1.0)
    
    # If text is dark (Yellow bg), use Dark Gauge. Else White Gauge.
    gauge_color = (45, 55, 72) if hero_txt_color == "#2D3748" else (255, 255, 255)
    
    # Draw Gauge Ring
    # Track
    draw.arc([width/2 - gauge_radius, hero_cy - gauge_radius, width/2 + gauge_radius, hero_cy + gauge_radius], 
             start=135, end=405, fill=(255,255,255, 80) if hero_txt_color=="#FFFFFF" else (0,0,0, 20), width=18)
    # Progress
    active_end = 135 + (270 * percent)
    if percent > 0:
        draw.arc([width/2 - gauge_radius, hero_cy - gauge_radius, width/2 + gauge_radius, hero_cy + gauge_radius], 
                 start=135, end=active_end, fill=gauge_color, width=18)

    # PM2.5 Number
    draw.text((width/2, hero_cy + 10), f"{latest_pm25:.0f}", font=f_super_num, anchor="ms", fill=hero_txt_color)
    draw.text((width/2, hero_cy + 90), "μg/m³", font=f_unit, anchor="ms", fill=hero_txt_color)
    
    # Status Pill
    status_y = hero_cy + 160
    level_text = level
    l_bbox = draw.textbbox((0,0), level_text, font=f_status)
    l_w = l_bbox[2] - l_bbox[0] + 100
    l_h = 90
    
    # Pill Background: Semi-transparent white/black
    pill_fill = (255, 255, 255, 200) if hero_txt_color == "#2D3748" else (255, 255, 255, 40)
    pill_txt = "#2D3748" if hero_txt_color == "#2D3748" else "#FFFFFF"
    
    draw.rounded_rectangle(
        [(width-l_w)/2, status_y, (width+l_w)/2, status_y + l_h], 
        radius=45, fill=pill_fill
    )
    draw.text((width/2, status_y + 45), level_text, font=f_status, anchor="mm", fill=pill_txt)


    # --- 3. Bottom Section: The White Sheet (45% height) ---
    # This sheet slides up from bottom
    sheet_h = 600
    sheet_y = height - sheet_h
    
    # Draw Shadow for the sheet
    shadow = create_drop_shadow(int(width), int(sheet_h), 60, blur=40, opacity=60)
    img.paste(shadow, (0 - 40, int(sheet_y) - 20), shadow)

    # Draw The Sheet (White)
    # We draw a rectangle that extends below canvas to ensure bottom corners are square if needed, 
    # but let's make it a floating card with rounded top corners.
    draw.rounded_rectangle(
        [(0, sheet_y), (width, height + 50)], 
        radius=60, 
        fill="#FFFFFF"
    )
    
    # --- 4. Advice Grid ---
    # Layout configuration
    grid_start_y = sheet_y + 50
    col_gap = 30
    row_gap = 40
    margin_side = 50
    
    card_w = (width - (margin_side * 2) - col_gap) / 2
    card_h = 250 # Compact cards
    
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
        
        # Minimal Layout: Icon Left, Text Right? Or Stacked?
        # Let's do "Stacked" but clean.
        
        # Icon
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(120, 120))
        if icon_img:
            # Center horizontally
            ix = int(x + (card_w - 120) / 2)
            iy = int(y)
            img.paste(icon_img, (ix, iy), icon_img)
        
        # Text
        tx = x + card_w / 2
        ty_title = y + 130
        
        # Title
        draw.text((tx, ty_title), item['title'], font=f_card_title, anchor="ms", fill="#1A202C")
        
        # Description (Wrap)
        desc = item['desc']
        words = desc.split()
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            bbox = draw.textbbox((0,0), " ".join(curr), font=f_card_desc)
            if (bbox[2]-bbox[0]) > (card_w):
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        lines.append(" ".join(curr))
        
        ly = ty_title + 30
        for line in lines:
            draw.text((tx, ly), line, font=f_card_desc, anchor="ms", fill="#718096")
            ly += 26

    # --- 5. Footer ---
    # Placed at the very bottom of the white sheet
    draw.text((width/2, height - 40), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill="#CBD5E0")

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
