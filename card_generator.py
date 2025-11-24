from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Assets (Modern Icons) ---
# Using consistent filled style icons for better readability on print
ICON_URLS = {
    'mask': "https://img.icons8.com/ios-filled/100/ffffff/protection-mask.png",
    'activity': "https://img.icons8.com/ios-filled/100/ffffff/running.png",
    'indoors': "https://img.icons8.com/ios-filled/100/ffffff/home.png",
    'user': "https://img.icons8.com/fluency-systems-filled/100/1e293b/user.png", # Dark color for white bg
    'heart': "https://img.icons8.com/fluency-systems-filled/100/ef4444/like.png", # Red heart
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
    elif pm <= 37.5: return '#eab308' # Yellow (Moderate) - Adjusted for better contrast
    elif pm <= 75: return '#f97316' # Orange (Unhealthy)
    else: return '#ef4444' # Red (Hazardous)

def wrap_text(text, font, max_width, draw):
    """Simple text wrapper helper."""
    lines = []
    if not text:
        return lines
        
    words = text.split(' ') # Basic split by space (For Thai without spaces, this is limited but functional for basic sentences)
    current_line = words[0]
    
    for word in words[1:]:
        test_line = current_line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

# --- 3. Main Generator ---
def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a modern, premium PM2.5 report card image."""
    
    # Canvas Settings (High Res for Print)
    width, height = 1200, 1600
    bg_color = get_theme_color(latest_pm25)
    card_bg_color = "#ffffff"
    text_color_primary = "#1e293b"
    text_color_secondary = "#64748b"
    
    img = Image.new('RGB', (width, height), '#f1f5f9') # Very light slate background
    draw = ImageDraw.Draw(img)

    # Fonts
    # Using Sarabun for a modern, clean Thai look
    font_bold_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_med_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"
    font_reg_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    
    f_huge = get_font(font_bold_url, 260) # PM2.5 Number
    f_header = get_font(font_bold_url, 80) # Status Level
    f_title = get_font(font_bold_url, 40) # Section Titles
    f_subtitle = get_font(font_med_url, 32) # Subtitles
    f_body = get_font(font_reg_url, 30) # Body Text
    f_small = get_font(font_reg_url, 24) # Footer/Small text
    f_pill = get_font(font_med_url, 28) # Date Pill

    # --- 1. Top Section (Hero) ---
    # Create a curved header background
    header_h = 650
    draw.rectangle([0, 0, width, header_h - 80], fill=bg_color)
    # Draw arc for bottom curve
    draw.pieslice([-100, header_h - 200, width + 100, header_h], 0, 180, fill=bg_color)
    
    # Date Pill (Top Center)
    date_padding_x = 40
    date_padding_y = 15
    bbox_date = draw.textbbox((0, 0), date_str, font=f_pill)
    date_w = bbox_date[2] - bbox_date[0] + (date_padding_x * 2)
    date_h = bbox_date[3] - bbox_date[1] + (date_padding_y * 2)
    date_x = (width - date_w) // 2
    date_y = 60
    
    draw.rounded_rectangle(
        [date_x, date_y, date_x + date_w, date_y + date_h], 
        radius=30, 
        fill="rgba(255, 255, 255, 0.25)", 
        outline=None
    )
    draw.text((width//2, date_y + date_h//2 - 2), date_str, font=f_pill, fill="white", anchor="mm")

    # PM2.5 Value
    pm_y = 280
    draw.text((width//2, pm_y), f"{latest_pm25:.0f}", font=f_huge, fill="white", anchor="mm")
    
    # Unit
    unit_text = "µg/m³"
    draw.text((width//2, pm_y + 110), unit_text, font=f_title, fill="rgba(255,255,255,0.9)", anchor="mm")

    # Status Level with Emoji
    status_text = f"{emoji} {level}"
    draw.text((width//2, pm_y + 190), status_text, font=f_header, fill="white", anchor="mm")

    # --- 2. Main Content Card (Floating look) ---
    content_y_start = 620
    margin = 50
    card_width = width - (margin * 2)
    
    # We will draw "Advice" sections here
    
    # Helper to draw an advice row
    def draw_advice_row(start_y, title, desc, icon_key, is_risk=False):
        row_h = 200
        # Card Background
        bg = "#ffffff"
        border = "#e2e8f0"
        
        # Draw shadow (simulated with offset gray rect)
        shadow_offset = 8
        draw.rounded_rectangle(
            [margin + shadow_offset, start_y + shadow_offset, margin + card_width + shadow_offset, start_y + row_h + shadow_offset], 
            radius=30, fill="#cbd5e1"
        )
        
        # Main Card Rect
        draw.rounded_rectangle(
            [margin, start_y, margin + card_width, start_y + row_h], 
            radius=30, fill=bg, outline=border, width=2
        )
        
        # Left Accent Bar
        bar_color = bg_color # Use theme color for accents
        draw.rounded_rectangle(
            [margin, start_y, margin + 20, start_y + row_h], 
            radius=0, fill=bar_color, corners=(True, False, False, True)
        )
        
        # Icon Area
        icon_size = 90
        icon_x = margin + 50
        icon_y = start_y + (row_h - icon_size) // 2
        
        # Icon Background Circle
        draw.ellipse(
            [icon_x, icon_y, icon_x + icon_size, icon_y + icon_size], 
            fill="#f1f5f9" if not is_risk else "#fee2e2" # Light gray or light red for risk
        )
        
        # Load and paste icon
        icon_img = get_image_from_url(ICON_URLS[icon_key])
        if icon_img:
            # Resize
            icon_img = icon_img.resize((50, 50), Image.Resampling.LANCZOS)
            # Paste centered in circle
            paste_x = icon_x + (icon_size - 50)//2
            paste_y = icon_y + (icon_size - 50)//2
            img.paste(icon_img, (paste_x, paste_y), icon_img)

        # Text Area
        text_x = icon_x + icon_size + 40
        text_w = card_width - (text_x - margin) - 40
        
        # Title
        draw.text((text_x, start_y + 45), title, font=f_title, fill=text_color_primary, anchor="ls")
        
        # Description (Wrapped)
        lines = wrap_text(desc, f_body, text_w, draw)
        line_height = 40
        curr_text_y = start_y + 60
        for i, line in enumerate(lines[:3]): # Max 3 lines
            draw.text((text_x, curr_text_y + (i * line_height)), line, font=f_body, fill=text_color_secondary, anchor="ls")

        return start_y + row_h + 40 # Return next Y position

    # Get General Advice Text
    # Re-fetch advice object locally to ensure we have the summary
    # In a real scenario, advice_details is passed, but summary might be in a parent object. 
    # The current code structure passes 'advice_details' which is just the dict of actions.
    # We need the summary text. Let's try to get it from 't' using logic or generic text if missing.
    # Fallback logic:
    gen_desc = "ปฏิบัติตามคำแนะนำเพื่อสุขภาพ" # Default
    # Try to find the matching summary from t based on level string match is risky, 
    # instead, let's look at advice_details content or passed level. 
    # Ideally, the caller should pass the summary. 
    # Workaround: Use the 'advice' structure from translations if possible.
    # Since we can't easily access the full advice object from params, we reconstruct logic or use a generic placeholder 
    # that encourages looking at the details below.
    # ACTUALLY: Let's use the 'risk_group' text for risk, and for general, 
    # we can try to infer or just use a standard label like "คำแนะนำทั่วไป".
    # BUT wait, the original code used logic to fetch it.
    # Let's check 'advice_details'. It has 'risk_group' string.
    # It does NOT have general public summary string.
    # Let's use the 'risk_group' text for the risk card.
    # For General Public, we will use a text based on the level color/severity conceptually.
    
    if latest_pm25 <= 25:
        gen_desc = t[lang]['advice']['advice_1']['summary']
    elif latest_pm25 <= 37.5:
        gen_desc = t[lang]['advice']['advice_3']['summary'] # Use moderate
    elif latest_pm25 <= 75:
        gen_desc = t[lang]['advice']['advice_4']['summary']
    else:
        gen_desc = t[lang]['advice']['advice_5']['summary']

    current_y = content_y_start
    
    # 2.1 General Public Card
    current_y = draw_advice_row(current_y, t[lang]['general_public'], gen_desc, 'user')
    
    # 2.2 Risk Group Card
    current_y = draw_advice_row(current_y, t[lang]['risk_group'], advice_details['risk_group'], 'heart', is_risk=True)

    # --- 3. Action Grid (Footer) ---
    action_header_y = current_y + 20
    draw.text((width//2, action_header_y), t[lang]['advice_header'], font=f_subtitle, fill="#94a3b8", anchor="mm")
    
    grid_y = action_header_y + 60
    grid_gap = 30
    grid_total_w = width - (margin * 2)
    col_w = (grid_total_w - (grid_gap * 2)) / 3
    col_h = 240
    
    actions = [
        {'label': t[lang]['advice_cat_mask'], 'val': advice_details['mask'], 'icon': 'mask'},
        {'label': t[lang]['advice_cat_activity'], 'val': advice_details['activity'], 'icon': 'activity'},
        {'label': t[lang]['advice_cat_indoors'], 'val': advice_details['indoors'], 'icon': 'indoors'}
    ]
    
    for i, action in enumerate(actions):
        box_x = margin + i * (col_w + grid_gap)
        
        # Action Box
        draw.rounded_rectangle(
            [box_x, grid_y, box_x + col_w, grid_y + col_h],
            radius=30, fill="white", outline=bg_color, width=3
        )
        
        # Icon Circle
        ic_size = 80
        ic_cx = box_x + col_w/2
        ic_cy = grid_y + 60
        
        draw.ellipse(
            [ic_cx - ic_size/2, ic_cy - ic_size/2, ic_cx + ic_size/2, ic_cy + ic_size/2],
            fill=bg_color
        )
        
        # Icon
        act_icon = get_image_from_url(ICON_URLS[action['icon']])
        if act_icon:
            act_icon = act_icon.resize((45, 45), Image.Resampling.LANCZOS)
            img.paste(act_icon, (int(ic_cx - 22), int(ic_cy - 22)), act_icon)
            
        # Label
        draw.text((ic_cx, ic_cy + 60), action['label'], font=f_pill, fill=text_color_secondary, anchor="ms")
        
        # Value (Wrapped if long)
        val_lines = wrap_text(action['val'], f_subtitle, col_w - 20, draw)
        val_y = ic_cy + 100
        for j, vline in enumerate(val_lines[:2]): # limit 2 lines
            draw.text((ic_cx, val_y + (j*35)), vline, font=f_subtitle, fill=bg_color, anchor="ms")

    # --- 4. Footer Logo & Credit ---
    footer_y = height - 100
    
    # Logo
    logo_img = get_image_from_url(ICON_URLS['logo'])
    if logo_img:
        logo_h = 60
        aspect = logo_img.width / logo_img.height
        logo_w = int(logo_h * aspect)
        logo_img = logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Draw logo centered
        logo_x = (width - logo_w) // 2
        img.paste(logo_img, (logo_x, footer_y - 40), logo_img)
        
    draw.text((width//2, footer_y + 40), t[lang]['report_card_footer'], font=f_small, fill="#cbd5e1", anchor="mm")

    # Output
    buf = BytesIO()
    img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
