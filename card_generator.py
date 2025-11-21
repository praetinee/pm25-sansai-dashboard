from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math
import random

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
def get_image_from_url(url, size=(100, 100)):
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

# --- Atmospheric Graphics Helpers ---

def draw_sun_flare(draw, width, height):
    """Draws a sun with lens flare effect at top center."""
    # Sun Core
    sun_x, sun_y = width // 2, 150
    
    # Glow layers (Large to small)
    draw.ellipse([sun_x-300, sun_y-300, sun_x+300, sun_y+300], fill=(255, 255, 255, 20))
    draw.ellipse([sun_x-150, sun_y-150, sun_x+150, sun_y+150], fill=(255, 255, 255, 40))
    draw.ellipse([sun_x-60, sun_y-60, sun_x+60, sun_y+60], fill=(255, 255, 255, 255))

def draw_dust_particles(draw, width, height, intensity=0.5, color=(200, 200, 200, 30)):
    """Draws random floating dust/haze particles."""
    num_particles = int(50 * intensity)
    for _ in range(num_particles):
        r = random.randint(20, 100)
        x = random.randint(0, width)
        y = random.randint(0, int(height * 0.6)) # Only in sky area
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

def create_atmospheric_bg(width, height, pm25_val):
    """
    Creates a dynamic weather background based on PM2.5 level.
    - Good: Blue Sky + Sun
    - Moderate: Hazy Yellow/Blue
    - Unhealthy: Orange/Grey Smog
    - Hazardous: Dark Purple/Red
    """
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    if pm25_val <= 25: # Good (Blue Sky)
        top_color = (79, 172, 254)  # Bright Blue
        bot_color = (0, 242, 254)   # Cyan
        has_sun = True
        dust_level = 0
    elif pm25_val <= 37.5: # Moderate (Yellow tint)
        top_color = (246, 211, 101) # Soft Yellow
        bot_color = (253, 160, 133) # Soft Orange/Pink
        has_sun = True
        dust_level = 0.3
    elif pm25_val <= 75: # Unhealthy (Orange/Grey)
        top_color = (255, 126, 95)  # Orange
        bot_color = (254, 180, 123) # Light Orange
        has_sun = False # Sun obscured
        dust_level = 0.8
    else: # Hazardous (Purple/Dark)
        top_color = (48, 43, 99)    # Dark Purple
        bot_color = (36, 36, 62)    # Dark Grey
        has_sun = False
        dust_level = 1.5

    # 1. Draw Gradient Sky
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bot_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bot_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bot_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Add Sun (if applicable)
    if has_sun:
        draw_sun_flare(draw, width, height)

    # 3. Add Dust/Clouds (Overlay)
    if dust_level > 0:
        # Haze layer
        haze = Image.new('RGBA', (width, height), (0,0,0,0))
        h_draw = ImageDraw.Draw(haze)
        
        # Draw random smog clouds
        color = (255, 255, 255, 40) if pm25_val < 75 else (50, 50, 50, 60)
        draw_dust_particles(h_draw, width, height, intensity=dust_level, color=color)
        
        # Blur the haze to make it look like gas/smoke
        haze = haze.filter(ImageFilter.GaussianBlur(40))
        img.paste(haze, (0,0), mask=haze)

    return img

def draw_glass_panel(width, height, radius=40):
    """Creates a semi-transparent glass sheet."""
    sheet = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(sheet)
    
    # 1. White tint with low opacity (Frosted Glass)
    draw.rounded_rectangle([(0,0), (width, height)], radius=radius, fill=(255, 255, 255, 40))
    
    # 2. Border/Stroke (Simulate edge light)
    draw.rounded_rectangle([(0,0), (width, height)], radius=radius, outline=(255, 255, 255, 120), width=2)
    
    return sheet

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates the 'Skycast' style report card."""
    
    width, height = 1000, 1600 # Tall ratio
    
    # 1. Create Atmospheric Background
    img = create_atmospheric_bg(width, height, latest_pm25)
    draw = ImageDraw.Draw(img, 'RGBA')

    # Fonts - Loading Sarabun (Light/Regular/Bold)
    font_url_light = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Light.ttf"
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"

    font_light_bytes = get_font(font_url_light)
    font_reg_bytes = get_font(font_url_reg)
    font_bold_bytes = get_font(font_url_bold)

    if not all([font_light_bytes, font_reg_bytes, font_bold_bytes]):
        return None
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    f_hero_num = create_font(font_light_bytes, 280) # Very thin, very big
    f_hero_unit = create_font(font_reg_bytes, 40)
    f_status = create_font(font_bold_bytes, 50)
    f_header = create_font(font_reg_bytes, 28)
    f_date = create_font(font_light_bytes, 24)
    
    f_advice_header = create_font(font_bold_bytes, 32)
    f_item_title = create_font(font_bold_bytes, 28)
    f_item_desc = create_font(font_reg_bytes, 24)
    f_footer = create_font(font_light_bytes, 20)

    # --- Top Section (Sky) ---
    
    # Header
    draw.text((width/2, 80), "San Sai Hospital", font=f_header, anchor="ms", fill="white")
    draw.text((width/2, 120), date_str, font=f_date, anchor="ms", fill=(255,255,255, 200))

    # Big Number (Center Sky)
    hero_y = 450
    # Add subtle shadow to text to make it pop against sun
    draw.text((width/2 + 2, hero_y + 2), f"{latest_pm25:.0f}", font=f_hero_num, anchor="ms", fill=(0,0,0, 20))
    draw.text((width/2, hero_y), f"{latest_pm25:.0f}", font=f_hero_num, anchor="ms", fill="white")
    
    draw.text((width/2, hero_y + 110), "μg/m³", font=f_hero_unit, anchor="ms", fill=(255,255,255, 220))

    # Status Pill (AQI Label)
    status_y = hero_y + 180
    l_w = draw.textlength(level, font=f_status) + 80
    draw.rounded_rectangle([(width-l_w)/2, status_y, (width+l_w)/2, status_y+90], radius=45, fill=(255,255,255, 60))
    draw.text((width/2, status_y + 45), level, font=f_status, anchor="mm", fill="white")


    # --- Bottom Section (Glass Sheet for Advice) ---
    sheet_h = 750
    sheet_y = height - sheet_h - 50 # Floating slightly above bottom
    margin_x = 40
    sheet_w = width - (margin_x * 2)
    
    # Draw Glass
    glass = draw_glass_panel(sheet_w, sheet_h, radius=50)
    img.paste(glass, (margin_x, int(sheet_y)), mask=glass)

    # Content inside Glass
    content_y = sheet_y + 50
    content_x = margin_x + 40
    
    # Title: "Health Advice"
    advice_title = "คำแนะนำการปฏิบัติตัว" if lang == 'th' else "Health Advice"
    draw.text((content_x, content_y), advice_title, font=f_advice_header, anchor="ls", fill="white")
    draw.line([(content_x, content_y + 15), (width - margin_x - 40, content_y + 15)], fill=(255,255,255, 100), width=1)
    
    # List Items
    items_start_y = content_y + 60
    row_height = 140
    
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        row_y = items_start_y + (i * row_height)
        
        # 1. Icon (Left)
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(100, 100))
        if icon_img:
            # Paste Icon
            img.paste(icon_img, (content_x, int(row_y)), icon_img)
            
        # 2. Text (Right)
        text_x = content_x + 130
        text_cy = row_y + 50 # Center of icon height
        
        # Title
        draw.text((text_x, text_cy - 15), item['title'], font=f_item_title, anchor="ls", fill="white")
        
        # Desc (Single line truncate or simple wrap? Let's wrap 1 line max for elegance, or 2 lines)
        # For list view, we usually keep it concise.
        desc = item['desc']
        # Wrap logic for list width
        max_text_w = sheet_w - 130 - 80
        
        # Simple wrap (2 lines max)
        words = desc.split()
        line1 = []
        line2 = []
        curr = line1
        for w in words:
            curr.append(w)
            if draw.textlength(" ".join(curr), font=f_item_desc) > max_text_w:
                curr.pop()
                if curr == line1: 
                    line1.append(w) # Keep at least one word if huge
                    curr = line2
                    curr.append(w)
                else:
                    break # truncate after 2 lines
        
        draw.text((text_x, text_cy + 10), " ".join(line1), font=f_item_desc, anchor="lt", fill=(255,255,255, 200))
        if line2:
            draw.text((text_x, text_cy + 40), " ".join(line2) + "...", font=f_item_desc, anchor="lt", fill=(255,255,255, 200))

        # Divider line (except last item)
        if i < len(cards_data) - 1:
             draw.line([(text_x, row_y + row_height - 20), (width - margin_x - 40, row_y + row_height - 20)], fill=(255,255,255, 40), width=1)


    # --- Footer ---
    draw.text((width/2, height - 30), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill=(255,255,255, 150))

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
