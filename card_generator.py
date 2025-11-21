from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops
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
def get_image_from_url(url, size=(200, 200)):
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

def create_rounded_icon_bg(img, radius=50, size=(180, 180)):
    """
    Places image on a white square background and crops to rounded corners.
    Fixes the 'black background' issue.
    """
    # 1. Create White Base
    base = Image.new('RGBA', size, (255, 255, 255, 255))
    
    # 2. Resize and Center Icon onto Base
    # We scale the icon down slightly so it fits nicely inside the rounded shape
    icon_w, icon_h = img.size
    target_w, target_h = int(size[0] * 0.85), int(size[1] * 0.85)
    img_resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    offset_x = (size[0] - target_w) // 2
    offset_y = (size[1] - target_h) // 2
    
    # Use alpha_composite for proper transparency handling
    base.alpha_composite(img_resized, (offset_x, offset_y))
    
    # 3. Create Mask
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    
    # 4. Apply Mask
    base.putalpha(mask)
    return base

def create_soft_shadow(size, radius, blur=30, opacity=40):
    """Creates a diffused, soft shadow."""
    shadow_size = (size[0] + blur*4, size[1] + blur*4)
    shadow = Image.new('RGBA', shadow_size, (0,0,0,0))
    draw = ImageDraw.Draw(shadow)
    
    # Draw black shape
    draw.rounded_rectangle(
        [blur*2, blur*2, blur*2 + size[0], blur*2 + size[1]], 
        radius=radius, 
        fill=(0, 0, 0, opacity)
    )
    return shadow.filter(ImageFilter.GaussianBlur(blur))

def create_mesh_gradient(width, height, hex_color):
    """Creates a soft, airy background gradient."""
    # Parse color
    try:
        r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except:
        r, g, b = 200, 200, 200
        
    # Base: White
    base = Image.new('RGB', (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(base)
    
    # 1. Top Mesh (Main Color) - Large Soft Blob
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    o_draw = ImageDraw.Draw(overlay)
    
    # Large circle at top-left, bleeding out
    o_draw.ellipse([-300, -300, width, 600], fill=(r, g, b, 40))
    
    # Smaller circle at bottom-right
    o_draw.ellipse([width-600, height-600, width+200, height+200], fill=(r, g, b, 20))
    
    # Blur heavily
    overlay = overlay.filter(ImageFilter.GaussianBlur(150))
    
    return Image.alpha_composite(base.convert('RGBA'), overlay).convert('RGB')

def draw_clean_gauge(draw, cx, cy, radius, percent, color_hex):
    """Draws a super-clean, modern gauge."""
    thickness = 15
    
    # Background Track (Very Light Grey)
    draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=135, end=405, fill="#F0F0F0", width=thickness)
    
    # Active Progress
    active_end = 135 + (270 * percent)
    if percent > 0:
        # Draw with round cap simulation
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], start=135, end=active_end, fill=color_hex, width=thickness)
        
        # Add simple round ends using circles
        start_rad = math.radians(135)
        end_rad = math.radians(active_end)
        
        # Start Cap
        sx = cx + radius * math.cos(start_rad)
        sy = cy + radius * math.sin(start_rad)
        draw.ellipse([sx-thickness/2+1, sy-thickness/2+1, sx+thickness/2-1, sy+thickness/2-1], fill=color_hex)
        
        # End Cap
        ex = cx + radius * math.cos(end_rad)
        ey = cy + radius * math.sin(end_rad)
        draw.ellipse([ex-thickness/2+1, ey-thickness/2+1, ex+thickness/2-1, ey+thickness/2-1], fill=color_hex)

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a 'Soft & Modern' report card."""
    
    width, height = 1000, 1450
    
    # 1. Background: Airy Mesh Gradient
    img = create_mesh_gradient(width, height, color_hex)
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

    f_brand = create_font(font_bold_bytes, 28)
    f_date = create_font(font_med_bytes, 22)
    f_pm_val = create_font(font_bold_bytes, 160)
    f_pm_unit = create_font(font_med_bytes, 32)
    f_level = create_font(font_bold_bytes, 50)
    
    f_card_title = create_font(font_bold_bytes, 26)
    f_card_desc = create_font(font_reg_bytes, 22)
    f_footer = create_font(font_med_bytes, 18)

    # --- Header ---
    # Clean, Minimal Header
    draw.text((60, 60), "PM2.5 MONITOR", font=f_brand, anchor="ls", fill="#333333")
    draw.text((width-60, 60), "San Sai Hospital", font=f_brand, anchor="rs", fill="#333333")
    
    # Date line
    draw.line([(60, 80), (width-60, 80)], fill="#E0E0E0", width=2)
    draw.text((width/2, 110), date_str, font=f_date, anchor="ms", fill="#888888")

    # --- Hero Section (Gauge) ---
    hero_cy = 380
    gauge_radius = 150
    
    draw_clean_gauge(draw, width/2, hero_cy, gauge_radius, min(latest_pm25/200, 1.0), color_hex)
    
    # Value
    draw.text((width/2, hero_cy + 15), f"{latest_pm25:.0f}", font=f_pm_val, anchor="ms", fill="#333333")
    draw.text((width/2, hero_cy + 80), "μg/m³", font=f_pm_unit, anchor="ms", fill="#AAAAAA")
    
    # Status Pill
    pill_y = hero_cy + 140
    level_text = level
    bbox = draw.textbbox((0,0), level_text, font=f_level)
    l_w = bbox[2] - bbox[0] + 80
    
    # Draw Shadow for Pill
    pill_shadow = create_soft_shadow((l_w, 80), 40, blur=20, opacity=30)
    img.paste(pill_shadow, (int(width-l_w)//2 - 40, pill_y - 35), pill_shadow)
    
    # Draw Pill Body (White)
    draw.rounded_rectangle([(width-l_w)/2, pill_y, (width+l_w)/2, pill_y+80], radius=40, fill="#FFFFFF")
    # Text in Pill (Colored)
    draw.text((width/2, pill_y + 40), level_text, font=f_level, anchor="mm", fill=color_hex)

    # --- Widget Grid ---
    grid_start_y = pill_y + 140
    
    margin_x = 50
    col_gap = 40
    row_gap = 40
    
    card_w = (width - (margin_x * 2) - col_gap) / 2
    card_h = 340 # Tall enough for vertical layout
    
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
        y = grid_start_y + row * (card_h + row_gap)
        
        # 1. Widget Shadow
        w_shadow = create_soft_shadow((int(card_w), int(card_h)), 35, blur=25, opacity=15)
        img.paste(w_shadow, (int(x)-50, int(y)-40), w_shadow)
        
        # 2. Widget Body (White)
        draw.rounded_rectangle([x, y, x+card_w, y+card_h], radius=35, fill="#FFFFFF")
        
        # 3. Icon (Now with White BG Fix)
        icon_source = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(180, 180))
        if icon_source:
            # Convert to nice rounded icon with white bg
            icon_final = create_rounded_icon_bg(icon_source, radius=40, size=(140, 140))
            
            # Center Icon Top
            ix = int(x + (card_w - 140) / 2)
            iy = int(y + 30)
            img.paste(icon_final, (ix, iy), icon_final)
        
        # 4. Text
        tx = x + card_w / 2
        ty = y + 200
        
        draw.text((tx, ty), item['title'], font=f_card_title, anchor="ms", fill="#333333")
        
        # Desc Wrap
        desc = item['desc']
        words = desc.split()
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            bbox = draw.textbbox((0,0), " ".join(curr), font=f_card_desc)
            if (bbox[2]-bbox[0]) > (card_w - 40):
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        lines.append(" ".join(curr))
        
        ly = ty + 30
        for line in lines:
            draw.text((tx, ly), line, font=f_card_desc, anchor="ms", fill="#666666")
            ly += 28

    # --- Footer ---
    draw.text((width/2, height - 40), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill="#BBBBBB")

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
