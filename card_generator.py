from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
from io import BytesIO
import streamlit as st

# --- Assets (3D Icons) ---
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

# --- Graphics Helpers ---

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    """Helper to draw rounded rectangle."""
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

def draw_linear_gauge(draw, x, y, width, height, percent, color_hex):
    """Draws a modern linear progress bar."""
    # Background Track
    draw_rounded_rect(draw, [x, y, x + width, y + height], height/2, fill="#F1F5F9")
    
    # Active Progress
    bar_w = max(height, width * percent) # Ensure at least a circle
    draw_rounded_rect(draw, [x, y, x + bar_w, y + height], height/2, fill=color_hex)

# --- Design Logic ---

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a 'Clinical Dashboard' style report card."""
    
    # Canvas Settings
    width, height = 800, 1200
    bg_color = "#FFFFFF" # Pure White for Clinical look
    
    img = Image.new('RGB', (width, height), bg_color)
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

    # Typography Hierarchy
    f_brand = create_font(font_bold, 32)
    f_date = create_font(font_med, 20)
    f_label = create_font(font_bold, 24)
    f_value_big = create_font(font_bold, 140)
    f_unit = create_font(font_med, 32)
    f_status_big = create_font(font_bold, 48)
    f_card_title = create_font(font_bold, 26)
    f_card_desc = create_font(font_reg, 22)
    f_footer = create_font(font_med, 18)

    # Layout Grid
    margin_x = 50
    content_w = width - (margin_x * 2)

    # --- 1. Header Section (Top Bar) ---
    header_y = 50
    
    # Hospital Name (Left)
    draw.text((margin_x, header_y), "รพ.สันทราย", font=f_brand, fill="#1E293B") # Slate-800
    draw.text((margin_x, header_y + 40), "Sansai Hospital", font=create_font(font_med, 18), fill="#94A3B8") # Slate-400
    
    # Date (Right)
    draw.text((width - margin_x, header_y + 10), date_str, font=f_date, anchor="rt", fill="#64748B") # Slate-500

    # Divider
    draw.line([(margin_x, header_y + 80), (width - margin_x, header_y + 80)], fill="#E2E8F0", width=2)

    # --- 2. Hero Data Section (The 'Vitals') ---
    hero_y = header_y + 120
    
    # PM2.5 Label
    draw.text((margin_x, hero_y), "ปริมาณฝุ่น PM2.5", font=f_label, fill="#64748B")
    
    # Big Value & Unit
    val_y = hero_y + 20
    draw.text((margin_x, val_y), f"{latest_pm25:.0f}", font=f_value_big, fill=color_hex) # Use Alert Color
    
    # Unit placement (Next to value)
    val_w = draw.textlength(f"{latest_pm25:.0f}", font=f_value_big)
    draw.text((margin_x + val_w + 20, val_y + 95), "μg/m³", font=f_unit, fill="#94A3B8")
    
    # Status Badge (Right Side aligned with value)
    status_bg_color = color_hex
    status_text = level
    status_w = draw.textlength(status_text, font=f_status_big) + 60
    status_h = 80
    status_x = width - margin_x - status_w
    status_y_pos = val_y + 40
    
    # Draw Pill
    draw_rounded_rect(draw, [status_x, status_y_pos, status_x + status_w, status_y_pos + status_h], 40, fill=status_bg_color)
    draw.text((status_x + status_w/2, status_y_pos + 40), status_text, font=f_status_big, anchor="mm", fill="white")
    
    # Linear Gauge (Progress Bar)
    gauge_y = val_y + 160
    gauge_h = 24
    max_pm = 200
    percent = min(latest_pm25 / max_pm, 1.0)
    draw_linear_gauge(draw, margin_x, gauge_y, content_w, gauge_h, percent, color_hex)
    
    # Gauge Scale Labels
    draw.text((margin_x, gauge_y + 35), "0", font=create_font(font_med, 16), fill="#CBD5E1")
    draw.text((width - margin_x, gauge_y + 35), "200+", font=create_font(font_med, 16), anchor="rt", fill="#CBD5E1")

    # --- 3. Advice Grid (Medical Cards) ---
    grid_title_y = gauge_y + 100
    draw.text((margin_x, grid_title_y), "คำแนะนำสุขภาพ (Health Advice)", font=f_label, fill="#1E293B")
    
    grid_y = grid_title_y + 50
    col_gap = 30
    row_gap = 30
    card_w = (content_w - col_gap) / 2
    card_h = 280
    
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
        y = grid_y + row * (card_h + row_gap)
        
        # Card Container (Bordered, no shadow for clean look)
        draw_rounded_rect(draw, [x, y, x + card_w, y + card_h], 20, fill="#F8FAFC", outline="#E2E8F0", width=2)
        
        # Icon
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(100, 100))
        if icon_img:
            # Place top-left with padding
            img.paste(icon_img, (int(x) + 20, int(y) + 20), icon_img)
            
        # Title
        # Positioned to the right of icon? No, let's put below to save horizontal space or specific layout
        # Layout: Icon Top-Left. Title Top-Right aligned or Next to Icon.
        # Let's put Title next to icon
        title_x = x + 130
        title_y = y + 40
        draw.text((title_x, title_y), item['title'], font=f_card_title, fill="#334155") # Slate-700
        
        # Description
        desc_y = y + 130
        desc_x = x + 25
        
        # Text Wrap
        words = item['desc'].split()
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            if draw.textlength(" ".join(curr), font=f_card_desc) > (card_w - 50):
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        lines.append(" ".join(curr))
        
        ly = desc_y
        for line in lines[:3]: # Max 3 lines
            draw.text((desc_x, ly), line, font=f_card_desc, fill="#64748B") # Slate-500
            ly += 30

    # --- 4. Footer ---
    footer_y = height - 80
    
    # Background Strip for Footer (Optional, keep white for clean look)
    # Just a separator line
    draw.line([(margin_x, footer_y), (width - margin_x, footer_y)], fill="#E2E8F0", width=2)
    
    # Footer Content
    draw.text((margin_x, footer_y + 25), "ด้วยความปรารถนาดีจาก กลุ่มงานอาชีวเวชกรรม", font=f_footer, fill="#94A3B8")
    
    # Tech Credits (Right)
    draw.text((width - margin_x, footer_y + 25), "Powered by DustBoy & CMU", font=create_font(font_bold, 18), anchor="rt", fill="#CBD5E1")

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
