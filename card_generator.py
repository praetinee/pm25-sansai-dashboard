from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Assets (Modern Icons) ---
ICON_URLS = {
    'mask': "https://img.icons8.com/ios-filled/100/ffffff/protection-mask.png",
    'activity': "https://img.icons8.com/ios-filled/100/ffffff/running.png",
    'indoors': "https://img.icons8.com/ios-filled/100/ffffff/home.png",
    'user': "https://img.icons8.com/ios-filled/100/ffffff/user.png", 
    'heart': "https://img.icons8.com/ios-filled/100/ffffff/like.png",
    'mask_dark': "https://img.icons8.com/ios-filled/100/64748b/protection-mask.png",
    'activity_dark': "https://img.icons8.com/ios-filled/100/64748b/running.png",
    'indoors_dark': "https://img.icons8.com/ios-filled/100/64748b/home.png",
    'logo': "https://www.cmuccdc.org/template/image/logo_ccdc.png"
}

# --- Cache Bytes ---
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
        except Exception as e:
            print(f"Font creation failed: {e}")
            return ImageFont.load_default()
    return ImageFont.load_default()

def get_image_from_url(url):
    img_bytes = download_asset_bytes(url)
    if img_bytes:
        try:
            img = Image.open(BytesIO(img_bytes))
            return img.convert("RGBA")
        except Exception as e:
            print(f"Image creation failed: {e}")
            return None
    return None

# --- 2. Color Themes & Utils ---
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
        test_line_with_space = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line_with_space, font=font)
        w = bbox[2] - bbox[0]
        
        if w <= max_width:
            current_line = test_line_with_space
        else:
            bbox_word = draw.textbbox((0, 0), word, font=font)
            word_w = bbox_word[2] - bbox_word[0]
            
            if word_w <= max_width:
                if current_line: lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                
                chars = list(word)
                temp_line = ""
                for char in chars:
                    test_char_line = temp_line + char
                    c_bbox = draw.textbbox((0, 0), test_char_line, font=font)
                    if (c_bbox[2] - c_bbox[0]) <= max_width:
                        temp_line = test_char_line
                    else:
                        lines.append(temp_line)
                        temp_line = char
                current_line = temp_line

    if current_line: lines.append(current_line)
    return lines

def round_corners(im, radius):
    """Rounds the corners of an image using a transparent mask."""
    mask = Image.new('L', im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), im.size], radius=radius, fill=255)
    
    # Ensure image has alpha channel
    im = im.convert("RGBA")
    
    # Create a new transparent image
    output = Image.new('RGBA', im.size, (0, 0, 0, 0))
    
    # Paste the original image using the mask
    output.paste(im, (0, 0), mask=mask)
    return output

# --- 3. Main Generator ---
def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    # Canvas - 2000px height for good spacing
    width, height = 1200, 2000
    bg_color_hex = get_theme_color(latest_pm25)
    bg_rgb = hex_to_rgb(bg_color_hex)
    
    img = Image.new('RGBA', (width, height), bg_color_hex) # Background is theme color
    draw = ImageDraw.Draw(img)

    # --- Fonts (Sarabun All) ---
    # Using Sarabun for ALL text elements as requested
    font_bold_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_med_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"
    font_reg_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    
    f_huge = get_font(font_bold_url, 220) 
    f_header = get_font(font_bold_url, 90)
    f_title = get_font(font_bold_url, 42)
    f_unit_label = get_font(font_med_url, 36) 
    f_subtitle = get_font(font_med_url, 36)
    f_body = get_font(font_reg_url, 30)
    f_small = get_font(font_reg_url, 26)
    f_pill = get_font(font_med_url, 28)
    f_action_val = get_font(font_bold_url, 34) 

    # ==========================================
    # 1. TOP SECTION (Status)
    # ==========================================
    
    # --- A. Logo Area ---
    logo_y = 60
    logo_img = get_image_from_url(ICON_URLS['logo'])
    if logo_img:
        logo_h = 60
        aspect = logo_img.width / logo_img.height
        logo_w = int(logo_h * aspect)
        logo_img = logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Pill for logo
        lp_w, lp_h = logo_w + 60, logo_h + 30
        lp_x = (width - lp_w) // 2
        draw.rounded_rectangle([lp_x, logo_y, lp_x+lp_w, logo_y+lp_h], radius=20, fill=(255, 255, 255, 240))
        img.paste(logo_img, (lp_x + 30, logo_y + 15), logo_img)
        
        # Removed language='th' to fix crash
        draw.text((width//2, logo_y - 30), "สนับสนุนข้อมูลโดย", font=f_small, fill=(255,255,255, 220), anchor="ms")

    # --- B. Date ---
    bbox_date = draw.textbbox((0, 0), date_str, font=f_pill)
    date_w = int(bbox_date[2] - bbox_date[0] + 80)
    date_h = int(bbox_date[3] - bbox_date[1] + 30)
    date_x = (width - date_w) // 2
    date_y = 180
    
    # Date Pill
    pill_img = Image.new('RGBA', (date_w, date_h), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(pill_img)
    p_draw.rounded_rectangle([0, 0, date_w, date_h], radius=30, fill=(255, 255, 255, 50))
    img.paste(pill_img, (date_x, date_y), pill_img)
    draw.text((width//2, date_y + date_h//2 - 3), date_str, font=f_pill, fill=(255,255,255,255), anchor="mm")

    # --- C. Modern Gauge (Semi-Transparent White) ---
    gauge_cy = 480
    gauge_r = 220 
    g_box = [width//2 - gauge_r, gauge_cy - gauge_r, width//2 + gauge_r, gauge_cy + gauge_r]
    
    # 1. Background Disc
    draw.ellipse(g_box, fill=(255, 255, 255, 235))
    
    # 2. Track Ring
    draw.arc(g_box, start=0, end=360, fill=(241, 245, 249, 100), width=25)
    
    # 3. Progress Arc
    percent = min((latest_pm25 / 120) * 360, 360)
    draw.arc(g_box, start=-90, end=-90+percent, fill=bg_rgb, width=25)
    
    # 4. Value & Unit
    # Adjusted Y offset manually to avoid overlapping
    draw.text((width//2, gauge_cy - 30), f"{latest_pm25:.0f}", font=f_huge, fill=bg_rgb, anchor="mm")
    draw.text((width//2, gauge_cy + 90), "µg/m³", font=f_unit_label, fill=bg_rgb, anchor="mm")
    
    # Status Text
    # Added extra padding for Thai characters
    draw.text((width//2, gauge_cy + 270), f"{level}", font=f_header, fill="white", anchor="mm")

    # ==========================================
    # 2. BOTTOM SHEET (White Card Layout)
    # ==========================================
    sheet_y = 820
    draw.rounded_rectangle([0, sheet_y, width, height+100], radius=60, fill="white", corners=(True, True, False, False))
    
    content_y = sheet_y + 60
    margin = 60
    card_w = width - (margin * 2)

    # Helper: Modern Row Card
    def draw_modern_card(start_y, title, desc, icon_key, is_risk=False):
        c_h = 180
        
        box = [margin, start_y, margin+card_w, start_y+c_h]
        draw.rounded_rectangle(box, radius=30, fill="#f8fafc")
        
        icon_size = 90
        ic_x = margin + 30
        ic_y = start_y + (c_h - icon_size)//2
        
        draw.ellipse([ic_x, ic_y, ic_x+icon_size, ic_y+icon_size], fill=bg_rgb)
        
        icon_url = ICON_URLS[icon_key] if not is_risk else ICON_URLS['heart']
        icon_img = get_image_from_url(icon_url)
        if icon_img:
            icon_img = icon_img.resize((50, 50), Image.Resampling.LANCZOS)
            img.paste(icon_img, (ic_x+20, ic_y+20), icon_img)
            
        # Text
        tx = ic_x + icon_size + 30
        tw = card_w - (tx - margin) - 20
        
        # TITLE: Move down slightly (+10) to clear top bounding box
        draw.text((tx, ic_y + 10), title, font=f_title, fill="#1e293b", anchor="lt")
        
        desc_lines = wrap_text(desc, f_body, tw, draw)
        
        # BODY: Start further down (+90) to create clear separation from Title
        # LINE HEIGHT: Increased to 50px per line to prevent vowel overlap between lines
        for i, line in enumerate(desc_lines[:2]):
            draw.text((tx, ic_y + 90 + (i*50)), line, font=f_body, fill="#64748b", anchor="lt")
            
        return start_y + c_h + 30

    # Descriptions
    gen_desc = t[lang]['advice']['advice_1']['summary'] if latest_pm25 <= 25 else \
               t[lang]['advice']['advice_3']['summary'] if latest_pm25 <= 37.5 else \
               t[lang]['advice']['advice_4']['summary'] if latest_pm25 <= 75 else \
               t[lang]['advice']['advice_5']['summary']

    curr_y = draw_modern_card(content_y, t[lang]['general_public'], gen_desc, 'user')
    curr_y = draw_modern_card(curr_y, t[lang]['risk_group'], advice_details['risk_group'], 'heart', is_risk=True)

    # ==========================================
    # 3. ACTION GRID (Modern Tinted Boxes)
    # ==========================================
    
    action_y = curr_y + 60 
    draw.text((margin + 10, action_y), t[lang]['advice_header'], font=f_subtitle, fill="#94a3b8", anchor="ls")
    
    grid_y = action_y + 40
    grid_gap = 30
    col_w = (width - (margin*2) - (grid_gap*2)) / 3
    col_h = 380
    
    actions = [
        {'label': t[lang]['advice_cat_mask'], 'val': advice_details['mask'], 'icon': 'mask'},
        {'label': t[lang]['advice_cat_activity'], 'val': advice_details['activity'], 'icon': 'activity'},
        {'label': t[lang]['advice_cat_indoors'], 'val': advice_details['indoors'], 'icon': 'indoors'}
    ]
    
    tint_color = bg_rgb + (20,)

    for i, act in enumerate(actions):
        bx = margin + i * (col_w + grid_gap)
        by = grid_y
        
        tint_img = Image.new('RGBA', (int(col_w), int(col_h)), (0,0,0,0))
        t_draw = ImageDraw.Draw(tint_img)
        t_draw.rounded_rectangle([0, 0, col_w, col_h], radius=30, fill=tint_color, outline=None)
        img.paste(tint_img, (int(bx), int(by)), tint_img)
        
        cx = bx + col_w/2
        ic_bg_size = 80
        ic_y = by + 40
        
        draw.ellipse([cx-ic_bg_size/2, ic_y, cx+ic_bg_size/2, ic_y+ic_bg_size], fill=bg_rgb)
        
        act_icon = get_image_from_url(ICON_URLS[act['icon']])
        if act_icon:
            act_icon = act_icon.resize((45, 45), Image.Resampling.LANCZOS)
            img.paste(act_icon, (int(cx-22), int(ic_y+17)), act_icon)
        
        # LABEL: Move down (+115)
        draw.text((cx, ic_y + 115), act['label'], font=f_pill, fill="#64748b", anchor="ms")
        
        # VALUE: Move down (+190) to separate from Label
        v_lines = wrap_text(act['val'], f_action_val, col_w-20, draw)
        
        # VALUE LINES: Increased spacing (50px)
        for k, vl in enumerate(v_lines[:3]):
             draw.text((cx, vy + 190 + (k*50)), vl, font=f_action_val, fill=bg_rgb, anchor="ms")

    # Footer
    draw.text((width//2, height - 80), t[lang]['report_card_footer'], font=f_small, fill="#cbd5e1", anchor="mm")

    # Final Rounding
    final_img = round_corners(img, 40)

    # Final Output
    buf = BytesIO()
    final_img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
