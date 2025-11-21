from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops, ImageSequence
import requests
from io import BytesIO
import streamlit as st
import math

# --- Assets ---
# ใช้รูปท้องฟ้าจริงที่มีแสงอาทิตย์สวยๆ เป็นฐาน
BG_SKY_URL = "https://images.unsplash.com/photo-1601297183305-6df142704ea2?q=80&w=1000&auto=format&fit=crop"

# [NEW] MASCOT URLs: ใส่ Link ไฟล์ GIF หรือ PNG ที่ต้องการแสดงผลตามค่าฝุ่นตรงนี้ได้เลย
# ระบบจะดึงภาพมาแสดงที่กึ่งกลางบน
MASCOT_URLS = {
    'good': "https://cdn-icons-png.flaticon.com/512/869/869869.png", 
    'moderate': "https://cdn-icons-png.flaticon.com/512/1163/1163661.png", 
    'unhealthy': "https://cdn-icons-png.flaticon.com/512/2892/2892769.png", 
    'hazardous': "https://cdn-icons-png.flaticon.com/512/9406/9406162.png", 
}

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
    """Fetches an image. Returns PIL Image object (RGBA). Handles static resizing."""
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

def get_raw_mascot_image(url):
    """Fetches the raw mascot image (GIF or PNG) without converting/resizing yet."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        print(f"Mascot download failed for {url}: {e}")
        return None

# --- Realistic Atmosphere Engine ---

def process_sky_background(base_img, width, height, pm25_val):
    # 1. Crop and Resize Base Image to fit canvas
    img_ratio = base_img.width / base_img.height
    canvas_ratio = width / height
    
    if img_ratio > canvas_ratio:
        new_width = int(base_img.height * canvas_ratio)
        offset = (base_img.width - new_width) // 2
        base_img = base_img.crop((offset, 0, offset + new_width, base_img.height))
    else:
        new_height = int(base_img.width / canvas_ratio)
        offset = (base_img.height - new_height) // 2
        base_img = base_img.crop((0, offset, base_img.width, offset + new_height))
        
    base_img = base_img.resize((width, height), Image.Resampling.LANCZOS).convert('RGB')

    # 2. Apply Atmosphere Effects
    overlay_color = None
    blur_radius = 0
    saturation = 1.0
    brightness = 1.0

    if pm25_val <= 25: 
        saturation = 1.2
        overlay_color = None 
    elif pm25_val <= 37.5: 
        overlay_color = (255, 240, 200) 
        opacity = 0.3
        blur_radius = 2
        saturation = 0.9
    elif pm25_val <= 75:
        overlay_color = (255, 160, 120) 
        opacity = 0.6
        blur_radius = 5
        saturation = 0.8
    else: 
        overlay_color = (100, 50, 50) 
        opacity = 0.7
        blur_radius = 10
        saturation = 0.6
        brightness = 0.8

    if blur_radius > 0:
        base_img = base_img.filter(ImageFilter.GaussianBlur(blur_radius))
        
    enhancer = ImageEnhance.Color(base_img)
    base_img = enhancer.enhance(saturation)
    
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(base_img)
        base_img = enhancer.enhance(brightness)

    if overlay_color:
        overlay = Image.new('RGB', base_img.size, overlay_color)
        base_img = Image.blend(base_img, overlay, opacity)

    return base_img

def draw_ios_glass_panel(img, x, y, w, h, radius=40):
    crop = img.crop((x, y, x+w, y+h))
    crop = crop.filter(ImageFilter.GaussianBlur(30))
    enhancer = ImageEnhance.Brightness(crop)
    crop = enhancer.enhance(1.1)
    img.paste(crop, (x, y))
    
    overlay = Image.new('RGBA', (w, h), (255, 255, 255, 40))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle([(0,0), (w, h)], radius=radius, outline=(255, 255, 255, 100), width=2)
    
    mask = Image.new('L', (w, h), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([(0,0), (w, h)], radius=radius, fill=255)
    
    img.paste(overlay, (x, y), mask=mask)

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a 'Real Sky Weather App' style card. Supports GIF output."""
    
    width, height = 1000, 1700 
    
    # --- 1. Prepare Static Base Layer (Everything EXCEPT Mascot) ---
    # Load Background
    base_sky = get_image_from_url(BG_SKY_URL)
    if not base_sky:
        base_img = Image.new('RGB', (width, height), "#4FACFE")
    else:
        base_img = process_sky_background(base_sky, width, height, latest_pm25)
        
    draw = ImageDraw.Draw(base_img, 'RGBA')

    # Fonts
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

    f_temp = create_font(font_light_bytes, 250)
    f_unit = create_font(font_reg_bytes, 36)
    f_status = create_font(font_reg_bytes, 55)
    f_loc = create_font(font_bold_bytes, 36)
    f_date = create_font(font_reg_bytes, 24)
    f_list_title = create_font(font_bold_bytes, 30)
    f_list_desc = create_font(font_reg_bytes, 26)
    f_footer = create_font(font_reg_bytes, 22)

    # Layout Config
    mascot_size = 250
    top_margin = 150
    mascot_y_start = 140
    num_y = mascot_y_start + mascot_size + 120 # Where number sits

    # --- Draw Static Content ---
    
    # Top Info
    draw.text((width/2, 60), "San Sai Hospital", font=f_loc, anchor="ms", fill="white")
    draw.text((width/2, 100), date_str, font=f_date, anchor="ms", fill=(255,255,255, 220))

    # Big Number (PM2.5)
    draw.text((width/2 + 2, num_y + 2), f"{latest_pm25:.0f}", font=f_temp, anchor="ms", fill=(0,0,0, 30))
    draw.text((width/2, num_y), f"{latest_pm25:.0f}", font=f_temp, anchor="ms", fill="white")
    draw.text((width/2, num_y + 100), "μg/m³", font=f_unit, anchor="ms", fill=(255,255,255, 220))

    # Status Pill
    status_y = num_y + 160
    pill_text = f"AQI {level}"
    l_w = draw.textlength(pill_text, font=f_status) + 80
    draw.rounded_rectangle([(width-l_w)/2, status_y, (width+l_w)/2, status_y+80], radius=40, fill=(255,255,255, 60))
    draw.text((width/2, status_y + 40), pill_text, font=f_status, anchor="mm", fill="white")

    # Bottom Glass Panel
    panel_h = 800
    panel_y = height - panel_h - 50
    panel_w = width - 60
    panel_x = 30
    
    draw_ios_glass_panel(base_img, panel_x, panel_y, panel_w, panel_h, radius=50)
    
    # Panel Content
    content_y = panel_y + 50
    content_x = panel_x + 40
    title_text = "คำแนะนำสุขภาพ" if lang == 'th' else "Health Advice"
    draw.text((content_x, content_y), title_text, font=f_loc, anchor="ls", fill="white")
    draw.line([(content_x, content_y + 15), (panel_x + panel_w - 40, content_y + 15)], fill=(255,255,255, 100), width=1)
    
    items = [
        (t[lang]['advice_cat_mask'], advice_details['mask'], 'mask'),
        (t[lang]['advice_cat_activity'], advice_details['activity'], 'activity'),
        (t[lang]['advice_cat_indoors'], advice_details['indoors'], 'indoors'),
        (t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], advice_details['risk_group'], 'risk_group')
    ]
    
    item_h = 150
    start_y = content_y + 50
    
    for i, (title, desc, icon_key) in enumerate(items):
        y = start_y + (i * item_h)
        icon = get_image_from_url(ICON_URLS.get(icon_key), size=(100, 100))
        if icon:
            base_img.paste(icon, (content_x, int(y) + 10), icon)
        tx = content_x + 130
        draw.text((tx, y + 30), title, font=f_list_title, anchor="lt", fill="white")
        
        max_w = panel_w - 200
        words = desc.split()
        line1, line2, curr = [], [], []
        curr = line1
        for w in words:
            curr.append(w)
            if draw.textlength(" ".join(curr), font=f_list_desc) > max_w:
                curr.pop()
                if curr == line1:
                    line1.append(w)
                    curr = line2
                    curr.append(w)
                else:
                    break
        draw.text((tx, y + 70), " ".join(line1), font=f_list_desc, anchor="lt", fill=(255,255,255, 210))
        if line2:
            draw.text((tx, y + 100), " ".join(line2) + "...", font=f_list_desc, anchor="lt", fill=(255,255,255, 210))
        if i < len(items) - 1:
            draw.line([(tx, y + item_h - 10), (panel_x + panel_w - 40, y + item_h - 10)], fill=(255,255,255, 40), width=1)

    draw.text((width/2, height - 25), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill=(255,255,255, 180))

    # --- 2. Add Mascot (Handle GIF/Static) ---
    
    if latest_pm25 <= 25: m_key = 'good'
    elif latest_pm25 <= 37.5: m_key = 'moderate'
    elif latest_pm25 <= 75: m_key = 'unhealthy'
    else: m_key = 'hazardous'
    
    # Fetch Raw Mascot (Don't resize yet to preserve frames)
    mascot_raw = get_raw_mascot_image(MASCOT_URLS.get(m_key))
    
    mx = (width - mascot_size) // 2

    if mascot_raw and getattr(mascot_raw, "is_animated", False):
        # --- Animated GIF Processing ---
        frames = []
        for frame in ImageSequence.Iterator(mascot_raw):
            # Resize frame
            frame = frame.convert("RGBA").resize((mascot_size, mascot_size), Image.Resampling.LANCZOS)
            
            # Create new composite for this frame
            new_frame = base_img.copy()
            new_frame.paste(frame, (mx, mascot_y_start), frame)
            
            # Optional: Convert to P mode for GIF compatibility (dithering)
            # This keeps file size reasonable but might add noise to gradient
            new_frame = new_frame.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
            frames.append(new_frame)
            
        # Save as GIF
        buf = BytesIO()
        frames[0].save(
            buf, 
            format='GIF', 
            save_all=True, 
            append_images=frames[1:], 
            duration=mascot_raw.info.get('duration', 100), 
            loop=0
        )
        return buf.getvalue()
        
    else:
        # --- Static PNG/JPG Processing ---
        if mascot_raw:
            mascot_img = mascot_raw.convert("RGBA").resize((mascot_size, mascot_size), Image.Resampling.LANCZOS)
            base_img.paste(mascot_img, (mx, mascot_y_start), mascot_img)
            
        # Save as PNG (High Quality)
        buf = BytesIO()
        base_img.save(buf, format='PNG', quality=95)
        return buf.getvalue()
