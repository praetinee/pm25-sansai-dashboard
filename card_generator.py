from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math

# --- 1. Assets (Modern Icons - Reusing similar logic/style) ---
# Using placeholder URLs for icons, ideally these should be local files or reliable URLs
# For this generator, we will draw simple shapes or text if icons fail, or use these URLs
ICON_URLS = {
    'mask': "https://img.icons8.com/ios-filled/100/ffffff/protection-mask.png",
    'activity': "https://img.icons8.com/ios-filled/100/ffffff/running.png",
    'indoors': "https://img.icons8.com/ios-filled/100/ffffff/home.png",
    'user': "https://img.icons8.com/ios-filled/100/ffffff/user.png",
    'heart': "https://img.icons8.com/ios-filled/100/ffffff/like.png", # Heart icon for sensitive group
    'logo': "https://www.cmuccdc.org/template/image/logo_ccdc.png"
}

@st.cache_data
def get_font(url, size):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return ImageFont.truetype(BytesIO(response.content), size)
    except Exception as e:
        print(f"Font download failed: {e}")
        return ImageFont.load_default()

@st.cache_data
def get_image_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img.convert("RGBA")
    except Exception as e:
        print(f"Image download failed for {url}: {e}")
        return None

# --- 2. Color Themes (Consistent with Web) ---
def get_theme_color(pm):
    if pm <= 15: return '#10b981' # Emerald (Excellent)
    elif pm <= 25: return '#10b981' # Green (Good)
    elif pm <= 37.5: return '#fbbf24' # Amber (Moderate)
    elif pm <= 75: return '#f97316' # Orange (Unhealthy)
    else: return '#ef4444' # Red (Hazardous)

# --- 3. Main Generator ---
def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a modern, premium PM2.5 report card image."""
    
    # Canvas Settings
    width, height = 1200, 1600 # High resolution for print
    bg_color = get_theme_color(latest_pm25)
    
    # Create base image
    img = Image.new('RGB', (width, height), '#f8fafc') # Light gray background for card body
    draw = ImageDraw.Draw(img)

    # Fonts (Sarabun from Google Fonts)
    font_bold_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_reg_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    
    f_header = get_font(font_bold_url, 50)
    f_date = get_font(font_reg_url, 36)
    f_pm_val = get_font(font_bold_url, 220)
    f_pm_unit = get_font(font_reg_url, 50)
    f_status = get_font(font_bold_url, 70)
    f_card_title = get_font(font_bold_url, 42)
    f_card_desc = get_font(font_reg_url, 34)
    f_action_label = get_font(font_bold_url, 28)
    f_action_val = get_font(font_bold_url, 32)
    f_footer = get_font(font_reg_url, 24)

    # --- Top Section (Status Card) ---
    # Draw a large colored rectangle at the top with rounded bottom corners logic (simulated by drawing full rect then pasting body over bottom if needed, or just a big rect)
    # Let's make the top section take 45% of height
    top_h = int(height * 0.45)
    draw.rectangle([0, 0, width, top_h], fill=bg_color)
    
    # Add Gradient-like overlay (Subtle shine)
    overlay = Image.new('RGBA', (width, top_h), (255,255,255,0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_overlay.ellipse([-width*0.2, -top_h*0.5, width*0.8, top_h*0.8], fill=(255,255,255,40))
    img.paste(Image.alpha_composite(img.crop((0,0,width,top_h)).convert('RGBA'), overlay), (0,0))

    # Supporter Logo (Top Center)
    logo_img = get_image_from_url(ICON_URLS['logo'])
    if logo_img:
        # Resize logo
        logo_h = 70
        aspect = logo_img.width / logo_img.height
        logo_w = int(logo_h * aspect)
        logo_img = logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        # Draw white pill background for logo
        pill_w = logo_w + 60
        pill_h = logo_h + 30
        pill_x = (width - pill_w) // 2
        pill_y = 60
        draw.rounded_rectangle([pill_x, pill_y, pill_x+pill_w, pill_y+pill_h], radius=20, fill="white")
        
        # Paste logo
        img.paste(logo_img, (pill_x + 30, pill_y + 15), logo_img)
        
        # Label "Supported by"
        draw.text((width//2, pill_y - 25), "สนับสนุนข้อมูลโดย", font=get_font(font_reg_url, 24), fill="rgba(255,255,255,0.9)", anchor="ms")

    # Date Pill
    date_pill_y = 220
    date_text_w = draw.textlength(date_str, font=f_date)
    dp_w = date_text_w + 60
    dp_h = 60
    dp_x = (width - dp_w) // 2
    draw.rounded_rectangle([dp_x, date_pill_y, dp_x+dp_w, date_pill_y+dp_h], radius=30, fill=(0,0,0,40)) # Semi-transparent black
    draw.text((width//2, date_pill_y + dp_h//2), date_str, font=f_date, fill="white", anchor="mm")

    # PM2.5 Value (Center)
    pm_y = 400
    draw.text((width//2, pm_y), f"{latest_pm25:.0f}", font=f_pm_val, fill="white", anchor="mm")
    
    # Unit & Status
    unit_y = pm_y + 110
    draw.text((width//2, unit_y), "µg/m³", font=f_pm_unit, fill="rgba(255,255,255,0.9)", anchor="mm")
    
    status_y = unit_y + 80
    draw.text((width//2, status_y), level, font=f_status, fill="white", anchor="mm")

    # --- Bottom Section (Advice) ---
    content_start_y = top_h + 50
    margin_side = 60
    card_gap = 30
    
    # General Public Card
    card_h = 220
    draw.rounded_rectangle([margin_side, content_start_y, width-margin_side, content_start_y+card_h], radius=30, fill="white", outline="#e2e8f0", width=2)
    # Left Color Bar
    draw.rounded_rectangle([margin_side, content_start_y, margin_side+15, content_start_y+card_h], radius=0, fill=bg_color, corners=(True, False, False, True)) # Left border trick needs adjustment for rounded corners, simplistic rect is fine for now or custom polygon
    # Icon Box
    icon_box_size = 100
    ib_x = margin_side + 50
    ib_y = content_start_y + (card_h - icon_box_size)//2
    draw.rounded_rectangle([ib_x, ib_y, ib_x+icon_box_size, ib_y+icon_box_size], radius=25, fill=bg_color)
    
    user_icon = get_image_from_url(ICON_URLS['user'])
    if user_icon:
        user_icon = user_icon.resize((60, 60))
        img.paste(user_icon, (ib_x+20, ib_y+20), user_icon)
        
    # Text
    text_x = ib_x + icon_box_size + 40
    draw.text((text_x, ib_y + 20), t[lang]['general_public'], font=f_card_title, fill="#1e293b", anchor="ls")
    
    # Wrap text logic for description
    desc = t[lang]['advice']['advice_1']['summary'] if 'advice_1' in t[lang]['advice'] else "ปฏิบัติตามคำแนะนำ" # Fallback logic needed to match realtime value
    # Re-fetch advice logic simply
    _, _, _, advice_obj = get_aqi_level(latest_pm25, lang, t)
    desc_gen = advice_obj['summary']
    
    # Simple text wrap
    words = desc_gen.split()
    line1 = ""
    line2 = ""
    for w in words:
        if draw.textlength(line1 + w, font=f_card_desc) < (width - text_x - margin_side - 20):
            line1 += w + " "
        else:
            line2 += w + " "
            
    draw.text((text_x, ib_y + 60), line1, font=f_card_desc, fill="#64748b", anchor="ls")
    draw.text((text_x, ib_y + 100), line2, font=f_card_desc, fill="#64748b", anchor="ls")


    # Risk Group Card
    risk_y = content_start_y + card_h + card_gap
    draw.rounded_rectangle([margin_side, risk_y, width-margin_side, risk_y+card_h], radius=30, fill="white", outline="#e2e8f0", width=2)
    draw.rounded_rectangle([margin_side, risk_y, margin_side+15, risk_y+card_h], fill=bg_color) # Left bar
    
    ib_y_risk = risk_y + (card_h - icon_box_size)//2
    draw.rounded_rectangle([ib_x, ib_y_risk, ib_x+icon_box_size, ib_y_risk+icon_box_size], radius=25, fill=bg_color)
    
    heart_icon = get_image_from_url(ICON_URLS['heart'])
    if heart_icon:
        heart_icon = heart_icon.resize((60, 60))
        img.paste(heart_icon, (ib_x+20, ib_y_risk+22), heart_icon) # Nudge down slightly
        
    draw.text((text_x, ib_y_risk + 20), t[lang]['risk_group'], font=f_card_title, fill="#1e293b", anchor="ls")
    
    desc_risk = advice_details['risk_group']
    # Simple text wrap for risk
    words_r = desc_risk.split()
    r_line1, r_line2 = "", ""
    for w in words_r:
        if draw.textlength(r_line1 + w, font=f_card_desc) < (width - text_x - margin_side - 20):
            r_line1 += w + " "
        else:
            r_line2 += w + " "
    draw.text((text_x, ib_y_risk + 60), r_line1, font=f_card_desc, fill="#64748b", anchor="ls")
    draw.text((text_x, ib_y_risk + 100), r_line2, font=f_card_desc, fill="#64748b", anchor="ls")


    # --- Action Grid (Footer) ---
    action_y = risk_y + card_h + 50
    draw.text((margin_side, action_y), t[lang]['advice_header'], font=get_font(font_bold_url, 30), fill="#94a3b8")
    
    grid_y = action_y + 50
    grid_h = 200
    col_w = (width - (margin_side*2) - (card_gap*2)) / 3
    
    actions_data = [
        {'label': t[lang]['advice_cat_mask'], 'val': advice_details['mask'], 'icon': ICON_URLS['mask']},
        {'label': t[lang]['advice_cat_activity'], 'val': advice_details['activity'], 'icon': ICON_URLS['activity']},
        {'label': t[lang]['advice_cat_indoors'], 'val': advice_details['indoors'], 'icon': ICON_URLS['indoors']}
    ]
    
    for i, action in enumerate(actions_data):
        ax = margin_side + i * (col_w + card_gap)
        # Card bg
        draw.rounded_rectangle([ax, grid_y, ax+col_w, grid_y+grid_h], radius=30, fill="white", outline=bg_color, width=3)
        
        # Icon (colored by theme) - For simplicity in PIL without complex masking, we use gray or black, or colorize if possible.
        # Here we just paste the white icon on a colored circle
        a_icon_size = 70
        ic_cx = ax + col_w//2
        ic_cy = grid_y + 60
        draw.ellipse([ic_cx-35, ic_cy-35, ic_cx+35, ic_cy+35], fill=bg_color)
        
        act_icon = get_image_from_url(action['icon'])
        if act_icon:
            act_icon = act_icon.resize((40, 40))
            img.paste(act_icon, (int(ic_cx-20), int(ic_cy-20)), act_icon)
            
        # Label
        draw.text((ic_cx, ic_cy + 55), action['label'], font=f_action_label, fill="#64748b", anchor="ms")
        # Value
        draw.text((ic_cx, ic_cy + 95), action['val'], font=f_action_val, fill=bg_color, anchor="ms")

    # Footer Text
    draw.text((width//2, height - 40), "Generated by PM2.5 Sansai Dashboard", font=f_footer, fill="#cbd5e1", anchor="ms")

    # Save to bytes
    buf = BytesIO()
    img.save(buf, format='PNG', quality=100)
    return buf.getvalue()
