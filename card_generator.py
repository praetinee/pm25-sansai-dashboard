from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import streamlit as st

# --- Assets ---
# ใช้ไอคอน 3D เดิมที่มีอยู่ แต่จะเอามาใส่ในกรอบสี่เหลี่ยมมนๆ แบบใหม่
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

# --- Helper Graphics ---

def create_gradient_fill(width, height, start_color, end_color):
    """Creates a vertical gradient image."""
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), start_color)
    bottom = Image.new('RGBA', (width, height), end_color)
    
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    
    base.paste(bottom, (0, 0), mask)
    return base

def draw_shadow(draw, x, y, w, h, radius, color=(0,0,0,20), blur=10):
    """Simulates a CSS box-shadow."""
    # In PIL, drawing real blur shadows is expensive. 
    # We simulate it with a simple offset translucent rounded rect for performance.
    draw.rounded_rectangle([x+2, y+4, x+w+2, y+h+4], radius=radius, fill=color)

# --- Logic Mapping ---

def get_theme_colors(pm_value):
    """Maps PM2.5 value to the specific Tailwind colors from the React code."""
    # Values based on user provided logic in React code
    # <= 25: Teal
    # <= 37: Yellow
    # <= 50: Orange
    # > 50: Red
    
    if pm_value <= 25:
        return {
            'name': 'teal',
            'gradient_start': '#14b8a6', # teal-500
            'gradient_end': '#10b981',   # emerald-500
            'text': '#0d9488',           # teal-600
            'bg': '#f0fdfa',             # teal-50
            'border': '#ccfbf1',         # teal-100
            'ring': '#14b8a6',           # teal-500
            'icon_bg': '#eff6ff',        # blue-50 (for user icon)
            'icon_text': '#2563eb',      # blue-600
        }
    elif pm_value <= 37.5:
        return {
            'name': 'yellow',
            'gradient_start': '#facc15', # yellow-400
            'gradient_end': '#f59e0b',   # amber-500
            'text': '#ca8a04',           # yellow-600
            'bg': '#fefce8',             # yellow-50
            'border': '#fef9c3',         # yellow-100
            'ring': '#facc15',           # yellow-400
            'icon_bg': '#eff6ff',
            'icon_text': '#2563eb',
        }
    elif pm_value <= 50: # Note: React code said <= 50 for Orange
        return {
            'name': 'orange',
            'gradient_start': '#fb923c', # orange-400
            'gradient_end': '#f87171',   # red-400
            'text': '#ea580c',           # orange-600
            'bg': '#fff7ed',             # orange-50
            'border': '#ffedd5',         # orange-100
            'ring': '#fb923c',           # orange-400
            'icon_bg': '#eff6ff',
            'icon_text': '#2563eb',
        }
    else:
        return {
            'name': 'red',
            'gradient_start': '#f43f5e', # rose-500
            'gradient_end': '#dc2626',   # red-600
            'text': '#e11d48',           # rose-600
            'bg': '#fff1f2',             # rose-50
            'border': '#ffe4e6',         # rose-100
            'ring': '#f43f5e',           # rose-500
            'icon_bg': '#fff1f2',        # rose-50 (for heart icon)
            'icon_text': '#e11d48',      # rose-600
        }

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a card replicating the React component style."""
    
    # --- Setup ---
    width, height = 800, 1200 # Scaled up slightly for high res
    img = Image.new('RGB', (width, height), "#F1F5F9") # bg-neutral-100
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

    f_h1 = create_font(font_bold, 36)       # Hospital Name
    f_sub = create_font(font_med, 20)       # Subtitles
    f_time = create_font(font_bold, 48)     # Time
    f_pm = create_font(font_bold, 160)      # PM Value
    f_label = create_font(font_bold, 32)    # Status Label
    f_card_title = create_font(font_bold, 28)
    f_card_desc = create_font(font_reg, 24)
    f_footer_bold = create_font(font_bold, 22)
    f_footer_small = create_font(font_reg, 18)

    # Get Theme Colors
    theme = get_theme_colors(latest_pm25)

    # --- 1. Main Card Container ---
    margin = 40
    card_w = width - (margin * 2)
    card_h = height - (margin * 2)
    card_x, card_y = margin, margin
    
    # Draw Main Card Shadow
    draw_shadow(draw, card_x, card_y, card_w, card_h, 60, color=(0,0,0,40))
    
    # Draw Main Card Body (White, Rounded)
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=60, fill="#FFFFFF")

    # --- 2. Header ---
    header_h = 160
    
    # Hospital Icon (Black Circle with Heart)
    icon_bg_size = 80
    icon_x = card_x + 50
    icon_y = card_y + 50
    draw.ellipse([icon_x, icon_y, icon_x+icon_bg_size, icon_y+icon_bg_size], fill="#0f172a") # Slate-900
    # Draw simple heart shape
    draw.text((icon_x + 22, icon_y + 18), "♥", font=create_font(font_bold, 40), fill="white")
    
    # Hospital Text
    text_x = icon_x + icon_bg_size + 20
    draw.text((text_x, icon_y + 10), "โรงพยาบาลสันทราย", font=f_h1, fill="#1e293b") # Slate-800
    draw.text((text_x, icon_y + 50), "SANSAI HOSPITAL", font=create_font(font_bold, 20), fill="#94a3b8") # Slate-400

    # Time & Date (Right aligned)
    # Parse date_str carefully or just split it
    # date_str format example: "21 November 2568, 10:00:00"
    try:
        date_part, time_part = date_str.split(', ')
        time_short = time_part[:5] # "10:00"
    except:
        time_short = "00:00"
        date_part = date_str

    time_w = draw.textlength(time_short, font=f_time)
    draw.text((card_x + card_w - 50, icon_y), time_short, font=f_time, anchor="rt", fill="#1e293b")
    draw.text((card_x + card_w - 50, icon_y + 55), date_part, font=f_sub, anchor="rt", fill="#64748b")

    # --- 3. Hero Section (Gradient + Ring) ---
    hero_h = 500
    hero_y = card_y + header_h
    
    # Background Gradient Fade (Top to Bottom)
    # Since PIL gradients are tricky, we draw a colored rect and mask it with a gradient alpha
    grad_bg = create_gradient_fill(card_w, hero_h, theme['gradient_start'], theme['gradient_end'])
    # Create opacity mask (Fade out)
    mask = Image.new('L', (card_w, hero_h))
    mask_data = []
    for y in range(hero_h):
        # Opacity goes from ~20 to 0
        opacity = int(30 * (1 - y/hero_h))
        mask_data.extend([opacity] * card_w)
    mask.putdata(mask_data)
    grad_bg.putalpha(mask)
    img.paste(grad_bg, (card_x, hero_y), grad_bg)

    # The Ring
    ring_cx = card_x + card_w // 2
    ring_cy = hero_y + 200
    ring_r = 180
    thickness = 8
    
    # Outer Glow
    draw.ellipse([ring_cx - ring_r - 20, ring_cy - ring_r - 20, ring_cx + ring_r + 20, ring_cy + ring_r + 20], fill=theme['bg']) # Simple colored bg glow simulation

    # Main Circle (White filled)
    draw.ellipse([ring_cx - ring_r, ring_cy - ring_r, ring_cx + ring_r, ring_cy + ring_r], fill="white", outline=theme['border'], width=8)
    
    # Inner Text
    draw.text((ring_cx, ring_cy - 90), "PM 2.5", font=create_font(font_bold, 24), anchor="ms", fill="#94a3b8") # Slate-400
    draw.text((ring_cx, ring_cy + 20), f"{latest_pm25:.0f}", font=f_pm, anchor="ms", fill=theme['text'])
    draw.text((ring_cx, ring_cy + 90), "µg/m³", font=f_sub, anchor="ms", fill="#94a3b8")

    # Status Pill (Floating at bottom of ring)
    pill_w = 300
    pill_h = 60
    pill_x = ring_cx - pill_w // 2
    pill_y = ring_cy + ring_r - 30
    
    # Gradient Pill
    pill_img = create_gradient_fill(pill_w, pill_h, theme['gradient_start'], theme['gradient_end'])
    
    # Mask for rounded pill
    pill_mask = Image.new('L', (pill_w, pill_h), 0)
    ImageDraw.Draw(pill_mask).rounded_rectangle([(0,0), (pill_w, pill_h)], radius=30, fill=255)
    pill_img.putalpha(pill_mask)
    
    img.paste(pill_img, (pill_x, pill_y), pill_img)
    draw.text((ring_cx, pill_y + 30), level, font=f_label, anchor="mm", fill="white")

    # Location Pin
    pin_y = pill_y + 80
    draw.rounded_rectangle([ring_cx - 150, pin_y, ring_cx + 150, pin_y + 40], radius=20, fill="#f8fafc", outline="#f1f5f9")
    draw.text((ring_cx, pin_y + 20), "จุดตรวจวัด: รพ.สันทราย", font=f_sub, anchor="mm", fill="#64748b")


    # --- 4. Advisory Cards ---
    cards_start_y = hero_y + 450
    # Logic for card content mapping
    # React code has: 
    # 1. General Public (User Icon)
    # 2. Risk Group (Heart Icon)
    
    # We map existing advice_details to these two
    public_advice = advice_details['activity']
    risk_advice = advice_details['risk_group']

    # Card Config
    card_gap = 30
    sub_card_h = 140
    sub_card_w = card_w - 100 # Padding inside
    sub_card_x = card_x + 50
    
    # --- Card 1: General Public ---
    c1_y = cards_start_y
    draw.rounded_rectangle([sub_card_x, c1_y, sub_card_x + sub_card_w, c1_y + sub_card_h], radius=30, fill="white", outline="#f1f5f9", width=2)
    
    # Icon Box (Blue-50)
    icon_box_size = 80
    ib_x = sub_card_x + 30
    ib_y = c1_y + 30
    draw.rounded_rectangle([ib_x, ib_y, ib_x + icon_box_size, ib_y + icon_box_size], radius=20, fill="#eff6ff")
    # Icon Image (Activity 3D)
    icon_act = get_image_from_url(ICON_URLS['activity'], size=(60, 60))
    if icon_act: img.paste(icon_act, (ib_x+10, ib_y+10), icon_act)
    
    # Text
    draw.text((ib_x + 100, ib_y + 10), "ประชาชนทั่วไป", font=f_card_title, fill="#1e293b")
    # Wrap desc logic
    words = public_advice.split()
    line1 = " ".join(words[:8]) + "..." if len(words) > 8 else public_advice # Simple truncate for design fidelity
    draw.text((ib_x + 100, ib_y + 45), line1, font=f_card_desc, fill="#64748b")

    # --- Card 2: Risk Group ---
    c2_y = c1_y + sub_card_h + 20
    draw.rounded_rectangle([sub_card_x, c2_y, sub_card_x + sub_card_w, c2_y + sub_card_h], radius=30, fill="white", outline="#f1f5f9", width=2)
    
    # Icon Box (Rose-50)
    ib_y2 = c2_y + 30
    draw.rounded_rectangle([ib_x, ib_y2, ib_x + icon_box_size, ib_y2 + icon_box_size], radius=20, fill="#fff1f2")
    # Icon Image (Risk 3D)
    icon_risk = get_image_from_url(ICON_URLS['risk_group'], size=(60, 60))
    if icon_risk: img.paste(icon_risk, (ib_x+10, ib_y2+10), icon_risk)
    
    # Text
    draw.text((ib_x + 100, ib_y2 + 10), "กลุ่มเสี่ยง", font=f_card_title, fill="#1e293b")
    words_r = risk_advice.split()
    line1_r = " ".join(words_r[:8]) + "..." if len(words_r) > 8 else risk_advice
    draw.text((ib_x + 100, ib_y2 + 45), line1_r, font=f_card_desc, fill="#64748b")

    # --- 5. Footer (Dark) ---
    footer_h = 140
    footer_y = card_y + card_h - footer_h
    
    # Draw bottom rounded corners by drawing full rect then masking? 
    # Or just draw a rect that overlaps the bottom part.
    # Easier: Draw rounded rect for whole card again but fill bottom part.
    
    # Let's draw a simple rect at bottom and clip it to rounded corners
    # Create a footer image
    footer_img = Image.new('RGBA', (card_w, footer_h), "#0f172a")
    
    # Add Footer Content
    d = ImageDraw.Draw(footer_img)
    # Left text
    d.text((40, 40), "ห่วงใยสุขภาพปอดของคุณ", font=f_footer_small, fill="#94a3b8")
    
    # Right: DustBoy Badge
    # Vertical line
    d.line([(card_w - 180, 20), (card_w - 180, 80)], fill="#334155", width=1)
    
    # Texts
    d.text((card_w - 190, 30), "MEASURED BY", font=create_font(font_bold, 12), anchor="rs", fill="#94a3b8")
    d.text((card_w - 190, 50), "DustBoy", font=create_font(font_bold, 18), anchor="rs", fill="#60a5fa") # blue-400
    
    # DB Icon Box
    d.rounded_rectangle([card_w - 170, 30, card_w - 130, 70], radius=10, fill="#3b82f6") # Blue-500
    d.text((card_w - 150, 50), "DB", font=create_font(font_bold, 16), anchor="mm", fill="white")
    
    # Bottom Credit
    d.line([(0, 90), (card_w, 90)], fill="#1e293b", width=1)
    d.text((card_w//2, 110), "Technology supported by Faculty of Engineering, CMU", font=create_font(font_reg, 14), anchor="mm", fill="#64748b")

    # Paste Footer onto main image (masking for rounded corners at bottom)
    # We need a mask that is white at bottom rounded corners.
    # Easier: Create a mask for the whole card (rounded rect) and paste footer using composite
    
    main_mask = Image.new('L', (card_w, card_h), 0)
    ImageDraw.Draw(main_mask).rounded_rectangle([(0,0), (card_w, card_h)], radius=60, fill=255)
    
    # Crop footer to only show where main mask allows (essentially cropping corners)
    # But footer is at bottom.
    
    # Place footer on a temporary full-card layer
    footer_layer = Image.new('RGBA', (card_w, card_h), (0,0,0,0))
    footer_layer.paste(footer_img, (0, card_h - footer_h))
    
    img.paste(footer_layer, (card_x, card_y), mask=main_mask)

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
