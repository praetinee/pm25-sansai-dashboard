from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Assets (Modern Icons) ---
ICON_URLS = {
    'mask': "https://img.icons8.com/ios-filled/100/ffffff/protection-mask.png", # White for colored bg or filled
    'activity': "https://img.icons8.com/ios-filled/100/ffffff/running.png",
    'indoors': "https://img.icons8.com/ios-filled/100/ffffff/home.png",
    'user': "https://img.icons8.com/ios-filled/100/ffffff/user.png", 
    'heart': "https://img.icons8.com/ios-filled/100/ffffff/like.png",
    # Icons for Action Grid (Dark version if needed, but we will colorize or use backgrounds)
    'mask_dark': "https://img.icons8.com/ios-filled/100/64748b/protection-mask.png",
    'activity_dark': "https://img.icons8.com/ios-filled/100/64748b/running.png",
    'indoors_dark': "https://img.icons8.com/ios-filled/100/64748b/home.png",
    'logo': "https://www.cmuccdc.org/template/image/logo_ccdc.png"
}

# --- Fix: Cache Bytes instead of Objects ---
@st.cache_data
def download_asset_bytes(url):
    """Downloads bytes from a URL. Cached to prevent re-downloading."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Download failed for {url}: {e}")
        return None

def get_font(url, size):
    """Creates a font object from cached bytes."""
    font_bytes = download_asset_bytes(url)
    if font_bytes:
        try:
            return ImageFont.truetype(BytesIO(font_bytes), size)
        except Exception as e:
            print(f"Font creation failed: {e}")
            return ImageFont.load_default()
    return ImageFont.load_default()

def get_image_from_url(url):
    """Creates an image object from cached bytes."""
    img_bytes = download_asset_bytes(url)
    if img_bytes:
        try:
            img = Image.open(BytesIO(img_bytes))
            return img.convert("RGBA")
        except Exception as e:
            print(f"Image creation failed: {e}")
            return None
    return None

# --- 2. Color Themes ---
def get_theme_color(pm):
    if pm <= 15: return '#10b981' # Emerald (Excellent)
    elif pm <= 25: return '#22c55e' # Green (Good)
    elif pm <= 37.5: return '#fbbf24' # Yellow (Moderate) - Matches Web
    elif pm <= 75: return '#f97316' # Orange (Unhealthy)
    else: return '#ef4444' # Red (Hazardous)

def wrap_text(text, font, max_width, draw):
    """
    Robust text wrapper helper that handles languages without spaces (like Thai).
    """
    lines = []
    if not text: return lines
    
    # 1. Try splitting by spaces first (for English or mixed)
    words = text.split(' ')
    current_line = ""
    
    for word in words:
        # Check if adding this word (with a space if needed) exceeds width
        # OR if the word itself is massive (common in Thai if no spaces present)
        
        test_line_with_space = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line_with_space, font=font)
        w = bbox[2] - bbox[0]
        
        if w <= max_width:
            current_line = test_line_with_space
        else:
            # If the word fits on a new line, push current line and start new
            bbox_word = draw.textbbox((0, 0), word, font=font)
            word_w = bbox_word[2] - bbox_word[0]
            
            if word_w <= max_width:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                # The word itself is too long (Thai sentence case), split by character
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                
                # Character-based splitting for long words
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

    if current_line:
        lines.append(current_line)
        
    return lines

# --- 3. Main Generator ---
def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a modern, web-alike PM2.5 report card image."""
    
    # Canvas Settings (High Res for Print)
    width, height = 1200, 1600
    bg_color = get_theme_color(latest_pm25)
    
    # Create base with RGBA to support transparency correctly
    img = Image.new('RGBA', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)

    # Fonts
    font_bold_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_med_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"
    font_reg_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    
    f_huge = get_font(font_bold_url, 240)
    f_header = get_font(font_bold_url, 80)
    f_title = get_font(font_bold_url, 38)
    f_subtitle = get_font(font_med_url, 32)
    f_body = get_font(font_reg_url, 28)
    f_small = get_font(font_reg_url, 24)
    f_pill = get_font(font_med_url, 28)

    # ==========================================
    # 1. TOP SECTION (Imitating Left Status Card)
    # ==========================================
    top_h = 750
    draw.rectangle([0, 0, width, top_h], fill=bg_color)
    
    # --- A. Logo & Supporter ---
    logo_img = get_image_from_url(ICON_URLS['logo'])
    if logo_img:
        logo_h = 60
        aspect = logo_img.width / logo_img.height
        logo_w = int(logo_h * aspect)
        logo_img = logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # White pill background for logo
        lp_w, lp_h = logo_w + 60, logo_h + 30
        lp_x = (width - lp_w) // 2
        lp_y = 50
        draw.rounded_rectangle([lp_x, lp_y, lp_x+lp_w, lp_y+lp_h], radius=20, fill="white")
        img.paste(logo_img, (lp_x + 30, lp_y + 15), logo_img)
        
        # "Supported by" text - Using Tuple for RGBA instead of string
        draw.text((width//2, lp_y - 25), "สนับสนุนข้อมูลโดย", font=f_small, fill=(255, 255, 255, 230), anchor="ms")

    # --- B. Date Pill ---
    date_padding_x, date_padding_y = 40, 15
    bbox_date = draw.textbbox((0, 0), date_str, font=f_pill)
    date_w = int(bbox_date[2] - bbox_date[0] + (date_padding_x * 2))
    date_h = int(bbox_date[3] - bbox_date[1] + (date_padding_y * 2))
    date_x = int((width - date_w) // 2)
    date_y = 180
    
    # Transparent Pill Trick
    pill_img = Image.new('RGBA', (date_w, date_h), (0, 0, 0, 0))
    pill_draw = ImageDraw.Draw(pill_img)
    pill_draw.rounded_rectangle([0, 0, date_w, date_h], radius=30, fill=(255, 255, 255, 50)) # ~20% opacity
    img.paste(pill_img, (date_x, date_y), pill_img)
    draw.text((width//2, date_y + date_h//2 - 2), date_str, font=f_pill, fill="white", anchor="mm")

    # --- C. Gauge & Value ---
    gauge_center_y = 480
    gauge_radius = 220
    
    # Draw Gauge Track (Faded White Circle)
    g_box = [width//2 - gauge_radius, gauge_center_y - gauge_radius, width//2 + gauge_radius, gauge_center_y + gauge_radius]
    
    # Track
    track_img = Image.new('RGBA', (width, height), (0,0,0,0))
    track_draw = ImageDraw.Draw(track_img)
    track_draw.ellipse(g_box, outline=(255,255,255, 70), width=25) # Track
    img.paste(track_img, (0,0), track_img)

    # Progress Arc (Solid White)
    percent = min((latest_pm25 / 120) * 360, 360)
    # Start from top (-90)
    draw.arc(g_box, start=-90, end=-90+percent, fill="white", width=25)

    # Value
    draw.text((width//2, gauge_center_y), f"{latest_pm25:.0f}", font=f_huge, fill="white", anchor="mm")
    
    # Unit - Using Tuple for RGBA
    draw.text((width//2, gauge_center_y + 100), "µg/m³", font=f_title, fill=(255, 255, 255, 230), anchor="mm")
    
    # Status Text
    draw.text((width//2, gauge_center_y + 200), f"{emoji} {level}", font=f_header, fill="white", anchor="mm")


    # ==========================================
    # 2. BOTTOM SECTION (Imitating Right Advice)
    # ==========================================
    content_y = top_h + 50
    margin = 50
    card_w = width - (margin * 2)

    # Helper for Web-Style Advice Card
    def draw_web_card(start_y, title, desc, icon_key, is_risk=False):
        c_h = 200
        
        # 1. Shadow
        draw.rounded_rectangle([margin+5, start_y+5, margin+card_w+5, start_y+c_h+5], radius=25, fill="#f1f5f9")
        
        # 2. Card Body (White/Light Gray)
        card_bg = "#f8fafc" # Very light gray like web secondary bg
        draw.rounded_rectangle([margin, start_y, margin+card_w, start_y+c_h], radius=25, fill=card_bg)
        
        # 3. Left Border Accent
        accent_color = bg_color # Use the theme color
        draw.rounded_rectangle([margin, start_y, margin+15, start_y+c_h], radius=0, fill=accent_color, corners=(True, False, False, True))
        
        # 4. Icon Box
        icon_box_size = 80
        ib_x = margin + 40
        ib_y = start_y + (c_h - icon_box_size)//2
        
        draw.rounded_rectangle([ib_x, ib_y, ib_x+icon_box_size, ib_y+icon_box_size], radius=20, fill=accent_color)
        
        # Icon
        icon_url = ICON_URLS[icon_key] if not is_risk else ICON_URLS['heart']
        icon_img = get_image_from_url(icon_url)
        if icon_img:
            icon_img = icon_img.resize((50, 50), Image.Resampling.LANCZOS)
            img.paste(icon_img, (ib_x+15, ib_y+15), icon_img)
            
        # 5. Text
        text_x = ib_x + icon_box_size + 30
        text_max_w = card_w - (text_x - margin) - 20
        
        draw.text((text_x, ib_y + 5), title, font=f_title, fill="#1e293b", anchor="lt")
        
        lines = wrap_text(desc, f_body, text_max_w, draw)
        for i, line in enumerate(lines[:3]):
            draw.text((text_x, ib_y + 55 + (i*35)), line, font=f_body, fill="#64748b", anchor="lt")
            
        return start_y + c_h + 30

    # Get Descriptions
    gen_desc = "ปฏิบัติตามคำแนะนำเพื่อสุขภาพ"
    if latest_pm25 <= 25: gen_desc = t[lang]['advice']['advice_1']['summary']
    elif latest_pm25 <= 37.5: gen_desc = t[lang]['advice']['advice_3']['summary']
    elif latest_pm25 <= 75: gen_desc = t[lang]['advice']['advice_4']['summary']
    else: gen_desc = t[lang]['advice']['advice_5']['summary']

    # Draw Cards
    curr_y = draw_web_card(content_y, t[lang]['general_public'], gen_desc, 'user')
    curr_y = draw_web_card(curr_y, t[lang]['risk_group'], advice_details['risk_group'], 'heart', is_risk=True)

    # --- Action Grid ---
    action_header_y = curr_y + 20
    draw.text((margin, action_header_y), t[lang]['advice_header'], font=f_subtitle, fill="#94a3b8", anchor="ls")
    
    grid_y = action_header_y + 20
    grid_gap = 25
    col_w = (width - (margin*2) - (grid_gap*2)) / 3
    col_h = 240
    
    actions = [
        {'label': t[lang]['advice_cat_mask'], 'val': advice_details['mask'], 'icon': 'mask_dark'},
        {'label': t[lang]['advice_cat_activity'], 'val': advice_details['activity'], 'icon': 'activity_dark'},
        {'label': t[lang]['advice_cat_indoors'], 'val': advice_details['indoors'], 'icon': 'indoors_dark'}
    ]
    
    # Explicitly map indices to the white icon keys we want for the circles
    white_icon_keys = ['mask', 'activity', 'indoors']

    for i, act in enumerate(actions):
        bx = margin + i * (col_w + grid_gap)
        
        # Box Border
        draw.rounded_rectangle([bx, grid_y, bx+col_w, grid_y+col_h], radius=25, outline=bg_color, width=3, fill="white")
        
        # Center Content
        cx = bx + col_w/2
        
        # Icon Background Circle
        ic_bg_size = 70
        ic_y = grid_y + 50
        draw.ellipse([cx-ic_bg_size/2, ic_y, cx+ic_bg_size/2, ic_y+ic_bg_size], fill=bg_color)
        
        # Load White Icon
        if i < len(white_icon_keys):
            white_key = white_icon_keys[i]
            act_icon = get_image_from_url(ICON_URLS[white_key])
            if act_icon:
                act_icon = act_icon.resize((40, 40), Image.Resampling.LANCZOS)
                img.paste(act_icon, (int(cx-20), int(ic_y+15)), act_icon)
            
        # Text
        draw.text((cx, ic_y + 90), act['label'], font=f_pill, fill="#64748b", anchor="ms")
        
        # Value
        v_lines = wrap_text(act['val'], f_title, col_w-20, draw)
        vy = ic_y + 130
        for k, vl in enumerate(v_lines[:2]):
             draw.text((cx, vy + (k*40)), vl, font=f_title, fill=bg_color, anchor="ms")

    # Footer Credit
    draw.text((width//2, height - 40), t[lang]['report_card_footer'], font=f_small, fill="#cbd5e1", anchor="mm")

    # Output
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
