from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops
import requests
from io import BytesIO
import streamlit as st
import math
import random

# --- 1. Assets (Modern 3D Icons Only) ---
# ใช้ไอคอน 3D ที่มีอยู่ (เพราะมันเข้ากับสไตล์ Bento มากที่สุด)
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

# --- 2. Modern Theme Engine (Mesh Gradients) ---

def get_theme_config(pm):
    """คืนค่าสีสำหรับสร้าง Mesh Gradient ตามระดับฝุ่น"""
    if pm <= 25: # Teal/Mint/Cyan
        return {
            'base': '#ccfbf1', # Teal 100
            'orb1': '#2dd4bf', # Teal 400
            'orb2': '#3b82f6', # Blue 500
            'orb3': '#a7f3d0', # Emerald 200
            'text': '#0f766e', # Teal 700
            'pill_bg': '#0d9488',
            'pill_text': '#ffffff'
        }
    elif pm <= 37.5: # Yellow/Orange/Cream
        return {
            'base': '#fefce8', # Yellow 50
            'orb1': '#facc15', # Yellow 400
            'orb2': '#fb923c', # Orange 400
            'orb3': '#fef08a', # Yellow 200
            'text': '#a16207', # Yellow 700
            'pill_bg': '#ca8a04',
            'pill_text': '#ffffff'
        }
    elif pm <= 75: # Orange/Red/Peach
        return {
            'base': '#fff7ed', # Orange 50
            'orb1': '#fb923c', # Orange 400
            'orb2': '#f87171', # Red 400
            'orb3': '#ffedd5', # Orange 100
            'text': '#c2410c', # Orange 700
            'pill_bg': '#ea580c',
            'pill_text': '#ffffff'
        }
    else: # Red/Purple/Dark
        return {
            'base': '#fef2f2', # Red 50
            'orb1': '#f87171', # Red 400
            'orb2': '#c084fc', # Purple 400
            'orb3': '#fecaca', # Red 200
            'text': '#be123c', # Rose 700
            'pill_bg': '#e11d48',
            'pill_text': '#ffffff'
        }

# --- 3. Graphics Generators ---

def create_mesh_gradient_bg(width, height, theme):
    """Creates a trendy mesh gradient background with noise."""
    # Base Layer
    base = Image.new('RGB', (width, height), theme['base'])
    
    # Create Orbs Layer
    orbs = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(orbs)
    
    # Helper to draw soft orb
    def draw_orb(hex_color, bbox):
        r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        draw.ellipse(bbox, fill=(r, g, b, 180)) # Semi-transparent

    # Draw random-ish orbs
    draw_orb(theme['orb1'], [-200, -200, 600, 600]) # Top Left
    draw_orb(theme['orb2'], [width-600, height-600, width+200, height+200]) # Bottom Right
    draw_orb(theme['orb3'], [width//2-300, height//2-300, width//2+300, height//2+300]) # Center
    
    # Blur heavily to create mesh effect
    orbs = orbs.filter(ImageFilter.GaussianBlur(120))
    
    # Composite
    bg = Image.alpha_composite(base.convert('RGBA'), orbs).convert('RGB')
    
    # Add Noise (Film Grain) - Key for modern look
    noise = Image.effect_noise((width, height), 15).convert('RGB')
    bg = Image.blend(bg, noise, 0.03) # 3% Noise
    
    return bg

def draw_bento_card(draw, x, y, w, h, radius=35, fill=(255,255,255,180)):
    """Draws a glass-like bento card."""
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=fill)
    # Subtle border
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, outline=(255,255,255,200), width=2)

def draw_squircle_icon_bg(img, x, y, size, color, radius=30):
    """Draws a squircle background for icons."""
    draw = ImageDraw.Draw(img, 'RGBA')
    # Convert hex to rgba with opacity
    r, g, b = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    fill = (r, g, b, 30) # Very light tint
    draw.rounded_rectangle([x, y, x+size, y+size], radius=radius, fill=fill)

# --- 4. Main Generator ---

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates 'The Air Bento' report card."""
    
    width, height = 1000, 1600
    theme = get_theme_config(latest_pm25)
    
    # 1. Background
    img = create_mesh_gradient_bg(width, height, theme)
    draw = ImageDraw.Draw(img, 'RGBA')

    # Fonts
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_med = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"
    
    font_bold = get_font(font_url_bold)
    font_reg = get_font(font_url_reg)
    font_med = get_font(font_url_med)

    if not all([font_bold, font_reg, font_med]): return None
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    # Typography
    f_hero_num = create_font(font_bold, 280)
    f_hero_unit = create_font(font_med, 40)
    f_status = create_font(font_bold, 48)
    f_header = create_font(font_bold, 32)
    f_date = create_font(font_med, 22)
    f_card_title = create_font(font_bold, 26)
    f_card_desc = create_font(font_med, 22)
    f_footer = create_font(font_med, 18)

    margin = 50

    # --- Header Row ---
    # Hospital & Date Pill
    header_y = 60
    # Left: Hospital
    draw.text((margin, header_y), "San Sai Hospital", font=f_header, fill="#1e293b")
    
    # Right: Date Pill
    date_w = draw.textlength(date_str, font=f_date) + 40
    draw.rounded_rectangle([width-margin-date_w, header_y-5, width-margin, header_y+45], radius=25, fill="white")
    draw.text((width-margin-date_w/2, header_y+20), date_str, font=f_date, anchor="mm", fill="#64748b")

    # --- Hero Section (Big Number) ---
    hero_y = 200
    
    # PM2.5 Value (Massive)
    # Draw text with blend mode simulation (Darker theme text)
    draw.text((margin, hero_y), f"{latest_pm25:.0f}", font=f_hero_num, fill=theme['text'])
    
    # Unit (Next to number bottom)
    val_w = draw.textlength(f"{latest_pm25:.0f}", font=f_hero_num)
    draw.text((margin + val_w + 20, hero_y + 230), "μg/m³", font=f_hero_unit, fill="#64748b")
    
    # Status Pill (Next to number top)
    status_y = hero_y + 40
    label_text = level
    l_w = draw.textlength(label_text, font=f_status) + 60
    
    draw.rounded_rectangle([margin + val_w + 20, status_y, margin + val_w + 20 + l_w, status_y + 80], radius=40, fill=theme['pill_bg'])
    draw.text((margin + val_w + 20 + l_w/2, status_y + 40), label_text, font=f_status, anchor="mm", fill=theme['pill_text'])

    # --- Bento Grid (Advice) ---
    grid_start_y = 650
    col_gap = 30
    row_gap = 30
    
    # Grid Layout:
    # Row 1: Mask (Large Left) | Activity (Small Right Top)
    # Row 2: Risk Group (Small Right Bottom)
    # Let's make a uniform 2x2 grid for consistency and cleanliness
    
    card_w = (width - (margin * 2) - col_gap) / 2
    card_h = 360 # Tall cards
    
    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        col = i % 2
        row = i // 2
        x = margin + col * (card_w + col_gap)
        y = grid_start_y + row * (card_h + row_gap)
        
        # Draw Bento Card
        draw_bento_card(draw, x, y, card_w, card_h, fill=(255,255,255, 200)) # White Glass
        
        # Icon Area
        icon_size = 140
        icon_x = x + (card_w - icon_size) // 2
        icon_y = y + 40
        
        # Soft Glow behind icon
        glow_r = 60
        cx, cy = icon_x + icon_size//2, icon_y + icon_size//2
        draw.ellipse([cx-glow_r, cy-glow_r, cx+glow_r, cy+glow_r], fill=(255,255,255, 150))
        
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(icon_size, icon_size))
        if icon_img:
            img.paste(icon_img, (icon_x, icon_y), icon_img)
            
        # Text Content
        text_y = icon_y + icon_size + 30
        draw.text((x + card_w/2, text_y), item['title'], font=f_card_title, anchor="ms", fill="#1e293b")
        
        # Desc (Wrap)
        desc = item['desc']
        words = desc.split()
        line1, line2, curr = [], [], []
        curr = line1
        for w in words:
            curr.append(w)
            if draw.textlength(" ".join(curr), font=f_card_desc) > (card_w - 60):
                curr.pop()
                if curr == line1:
                    line1.append(w)
                    curr = line2
                    curr.append(w)
                else:
                    break
        
        draw.text((x + card_w/2, text_y + 40), " ".join(line1), font=f_card_desc, anchor="ms", fill="#64748b")
        if line2:
            draw.text((x + card_w/2, text_y + 75), " ".join(line2), font=f_card_desc, anchor="ms", fill="#64748b")

    # --- Footer ---
    footer_y = height - 60
    draw.text((width/2, footer_y), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill="#94a3b8")

    # Output
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
