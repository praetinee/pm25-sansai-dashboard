from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Assets & Configurations ---
ICON_URLS = {
    'mask': "https://img.icons8.com/ios-filled/100/ffffff/protection-mask.png",
    'activity': "https://img.icons8.com/ios-filled/100/ffffff/running.png",
    'indoors': "https://img.icons8.com/ios-filled/100/ffffff/home.png",
    'user': "https://img.icons8.com/ios-filled/100/ffffff/user.png", 
    'heart': "https://img.icons8.com/ios-filled/100/ffffff/like.png",
    'logo': "https://www.cmuccdc.org/template/image/logo_ccdc.png"
}

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 2400 # High res vertical canvas

# --- Cache & Utils ---
@st.cache_data
def download_asset_bytes(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Download failed for {url}: {e}")
        return None

def get_font(url, size):
    font_bytes = download_asset_bytes(url)
    if font_bytes:
        try:
            return ImageFont.truetype(BytesIO(font_bytes), size)
        except Exception:
            return ImageFont.load_default()
    return ImageFont.load_default()

def get_image_from_url(url):
    img_bytes = download_asset_bytes(url)
    if img_bytes:
        try:
            img = Image.open(BytesIO(img_bytes))
            return img.convert("RGBA")
        except Exception:
            return None
    return None

def get_theme_color(pm):
    if pm <= 15: return '#10b981' # Emerald
    elif pm <= 25: return '#22c55e' # Green
    elif pm <= 37.5: return '#fbbf24' # Yellow
    elif pm <= 75: return '#f97316' # Orange
    else: return '#ef4444' # Red

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def wrap_text(text, font, max_width, draw):
    lines = []
    if not text: return lines
    
    words = text.split(' ')
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        
        if w <= max_width:
            current_line = test_line
        else:
            word_bbox = draw.textbbox((0, 0), word, font=font)
            if (word_bbox[2] - word_bbox[0]) > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                temp = ""
                for char in word:
                    if (draw.textbbox((0,0), temp + char, font=font)[2]) <= max_width:
                        temp += char
                    else:
                        lines.append(temp)
                        temp = char
                current_line = temp
            else:
                if current_line: lines.append(current_line)
                current_line = word
                
    if current_line: lines.append(current_line)
    return lines

def round_corners(im, radius):
    mask = Image.new('L', im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), im.size], radius=radius, fill=255)
    im = im.convert("RGBA")
    output = Image.new('RGBA', im.size, (0, 0, 0, 0))
    output.paste(im, (0, 0), mask=mask)
    return output

# --- Drawing Helpers ---
def draw_text_centered(draw, text, font, x, y, color):
    draw.text((x, y), text, font=font, fill=color, anchor="mm")

def draw_text_left(draw, text, font, x, y, color):
    draw.text((x, y), text, font=font, fill=color, anchor="lt")

# --- MAIN GENERATOR ---
def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    width, height = CANVAS_WIDTH, CANVAS_HEIGHT
    theme_rgb = hex_to_rgb(get_theme_color(latest_pm25))
    
    # Base Image
    img = Image.new('RGBA', (width, height), get_theme_color(latest_pm25))
    draw = ImageDraw.Draw(img)

    # Fonts
    font_bold_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_med_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"
    font_reg_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"

    f_huge = get_font(font_bold_url, 200)
    f_header = get_font(font_bold_url, 90)
    f_title = get_font(font_bold_url, 44)
    f_subtitle = get_font(font_med_url, 38)
    f_body = get_font(font_reg_url, 32)
    f_small = get_font(font_reg_url, 28)
    f_pill = get_font(font_med_url, 30)
    f_unit = get_font(font_med_url, 40)
    f_action_val = get_font(font_bold_url, 34)

    # ==========================================
    # 1. HEADER SECTION (Logo & Date)
    # ==========================================
    
    # --- LOGO (Top Left, Large, No Background) ---
    logo_img = get_image_from_url(ICON_URLS['logo'])
    if logo_img:
        logo_h = 150 # Enlarged Size
        aspect = logo_img.width / logo_img.height
        logo_w = int(logo_h * aspect)
        logo_img = logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Position: Top Left with padding
        logo_x = 60
        logo_y = 50
        
        # Paste directly (No pill background)
        img.paste(logo_img, (logo_x, logo_y), logo_img)
        
        # Removed "Supported by" text for cleaner look as requested

    # --- DATE PILL (Moved to Top Right for Balance) ---
    date_bbox = draw.textbbox((0, 0), date_str, font=f_pill)
    date_w = date_bbox[2] - date_bbox[0] + 80
    date_h = date_bbox[3] - date_bbox[1] + 30
    
    # Align Top Right
    date_x = width - date_w - 60 
    date_y = 80 # Vertically aligned roughly with logo center
    
    date_bg = Image.new('RGBA', (int(date_w), int(date_h)), (0,0,0,0))
    date_draw = ImageDraw.Draw(date_bg)
    date_draw.rounded_rectangle([0, 0, date_w, date_h], radius=30, fill=(255, 255, 255, 50))
    img.paste(date_bg, (int(date_x), int(date_y)), date_bg)
    draw_text_centered(draw, date_str, f_pill, date_x + date_w//2, date_y + date_h//2 - 4, (255,255,255,255))

    # ==========================================
    # 2. GAUGE SECTION
    # ==========================================
    gauge_cy = 550
    gauge_r = 230
    draw.ellipse([width//2 - gauge_r, gauge_cy - gauge_r, width//2 + gauge_r, gauge_cy + gauge_r], fill="white")
    draw.arc([width//2 - gauge_r, gauge_cy - gauge_r, width//2 + gauge_r, gauge_cy + gauge_r], 
             start=0, end=360, fill="#e2e8f0", width=25)
    percent = min((latest_pm25 / 120) * 360, 360)
    draw.arc([width//2 - gauge_r, gauge_cy - gauge_r, width//2 + gauge_r, gauge_cy + gauge_r], 
             start=-90, end=-90+percent, fill=theme_rgb, width=25)
    draw_text_centered(draw, f"{latest_pm25:.0f}", f_huge, width//2, gauge_cy - 20, theme_rgb)
    draw_text_centered(draw, "µg/m³", f_unit, width//2, gauge_cy + 100, theme_rgb)
    draw_text_centered(draw, level, f_header, width//2, gauge_cy + 290, "white")

    # ==========================================
    # 3. WHITE SHEET (Body)
    # ==========================================
    sheet_y = 920
    draw.rounded_rectangle([0, sheet_y, width, height + 200], radius=80, fill="white", corners=(True, True, False, False))

    content_y_start = sheet_y + 80
    margin_x = 70
    card_width = width - (margin_x * 2)

    def draw_advice_card(y_pos, title, desc, icon_key, is_risk=False):
        card_h = 240
        draw.rounded_rectangle([margin_x, y_pos, margin_x + card_width, y_pos + card_h], radius=40, fill="#f8fafc")
        
        icon_size = 100
        ic_x = margin_x + 40
        ic_y = y_pos + (card_h - icon_size) // 2
        draw.ellipse([ic_x, ic_y, ic_x+icon_size, ic_y+icon_size], fill=theme_rgb)
        
        icon_url = ICON_URLS[icon_key] if not is_risk else ICON_URLS['heart']
        icon_img = get_image_from_url(icon_url)
        if icon_img:
            icon_img = icon_img.resize((55, 55), Image.Resampling.LANCZOS)
            img.paste(icon_img, (ic_x+22, ic_y+22), icon_img)
            
        text_x = ic_x + icon_size + 40
        text_w = card_width - (text_x - margin_x) - 40
        
        draw_text_left(draw, title, f_title, text_x, y_pos + 40, "#1e293b")
        desc_lines = wrap_text(desc, f_body, text_w, draw)
        for i, line in enumerate(desc_lines[:3]):
            draw_text_left(draw, line, f_body, text_x, y_pos + 100 + (i * 45), "#64748b")
            
        return y_pos + card_h + 40

    gen_desc = t[lang]['advice']['advice_1']['summary']
    if latest_pm25 > 25: gen_desc = t[lang]['advice']['advice_2']['summary']
    if latest_pm25 > 37.5: gen_desc = t[lang]['advice']['advice_3']['summary']
    if latest_pm25 > 75: gen_desc = t[lang]['advice']['advice_4']['summary']
    
    current_y = draw_advice_card(content_y_start, t[lang]['general_public'], gen_desc, 'user')
    current_y = draw_advice_card(current_y, t[lang]['risk_group'], advice_details['risk_group'], 'heart', is_risk=True)

    # ==========================================
    # 4. ACTION GRID (Bottom)
    # ==========================================
    current_y += 40
    draw_text_left(draw, t[lang]['advice_header'], f_subtitle, margin_x + 10, current_y, "#94a3b8")
    
    grid_y = current_y + 60
    grid_gap = 30
    
    # Calculate column width here! (Correctly placed)
    col_w = (width - (margin_x * 2) - (grid_gap * 2)) / 3
    col_h = 450
    
    actions = [
        {'label': t[lang]['advice_cat_mask'], 'val': advice_details['mask'], 'icon': 'mask'},
        {'label': t[lang]['advice_cat_activity'], 'val': advice_details['activity'], 'icon': 'activity'},
        {'label': t[lang]['advice_cat_indoors'], 'val': advice_details['indoors'], 'icon': 'indoors'}
    ]
    
    tint_color = theme_rgb + (20,)
    
    for i, act in enumerate(actions):
        bx = margin_x + i * (col_w + grid_gap)
        by = grid_y
        
        tint_layer = Image.new('RGBA', (int(col_w), int(col_h)), (0,0,0,0))
        tint_draw = ImageDraw.Draw(tint_layer)
        tint_draw.rounded_rectangle([0, 0, col_w, col_h], radius=35, fill=tint_color)
        img.paste(tint_layer, (int(bx), int(by)), tint_layer)
        
        cx = bx + col_w / 2
        
        ic_size = 90
        ic_y_local = 50
        draw.ellipse([cx - ic_size/2, by + ic_y_local, cx + ic_size/2, by + ic_y_local + ic_size], fill=theme_rgb)
        
        act_icon = get_image_from_url(ICON_URLS[act['icon']])
        if act_icon:
            act_icon = act_icon.resize((50, 50), Image.Resampling.LANCZOS)
            img.paste(act_icon, (int(cx - 25), int(by + ic_y_local + 20)), act_icon)
            
        label_y = by + ic_y_local + ic_size + 30
        draw_text_centered(draw, act['label'], f_pill, cx, label_y, "#64748b")
        
        val_y_start = label_y + 50
        v_lines = wrap_text(act['val'], f_action_val, col_w - 30, draw)
        
        for k, vl in enumerate(v_lines[:4]):
            draw_text_centered(draw, vl, f_action_val, cx, val_y_start + (k * 45), theme_rgb)

    # ==========================================
    # 5. FOOTER
    # ==========================================
    draw_text_centered(draw, t[lang]['report_card_footer'], f_small, width//2, height - 80, "#cbd5e1")

    final_img = round_corners(img, 60)
    buf = BytesIO()
    final_img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
