from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import streamlit as st
import math

# --- Asset URLs (Latest 3D Icons) ---
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
def get_image_from_url(url, size=(150, 150)):
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

def create_drop_shadow(width, height, radius, offset=(0, 4), blur=15, opacity=50):
    """Creates a high-quality drop shadow image."""
    shadow = Image.new('RGBA', (width + abs(offset[0]) + blur*2, height + abs(offset[1]) + blur*2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    
    # Draw black rounded rect
    shadow_x = blur + max(0, offset[0])
    shadow_y = blur + max(0, offset[1])
    draw.rounded_rectangle(
        [shadow_x, shadow_y, shadow_x + width, shadow_y + height], 
        radius=radius, 
        fill=(0, 0, 0, opacity)
    )
    
    # Apply Gaussian blur
    return shadow.filter(ImageFilter.GaussianBlur(blur))

def draw_gauge_premium(draw, center_x, center_y, radius, percent, color_hex):
    """Draws a premium-looking gauge with round caps."""
    start_angle = 135
    end_angle = 405
    thickness = 22
    
    # 1. Draw Background Arc (Very faint, subtle)
    bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
    draw.arc(bbox, start=start_angle, end=end_angle, fill="#F3F4F6", width=thickness)
    
    # 2. Draw Active Arc
    # Determine end angle
    span = end_angle - start_angle
    active_end = start_angle + (span * percent)
    
    if percent > 0:
        draw.arc(bbox, start=start_angle, end=active_end, fill=color_hex, width=thickness)
        
        # 3. Draw Round Caps manually for smoother look
        # Start Cap
        sx = center_x + radius * math.cos(math.radians(start_angle))
        sy = center_y + radius * math.sin(math.radians(start_angle))
        cap_r = thickness / 2 - 0.5
        draw.ellipse([sx - cap_r, sy - cap_r, sx + cap_r, sy + cap_r], fill=color_hex)
        
        # End Cap
        ex = center_x + radius * math.cos(math.radians(active_end))
        ey = center_y + radius * math.sin(math.radians(active_end))
        draw.ellipse([ex - cap_r, ey - cap_r, ex + cap_r, ey + cap_r], fill=color_hex)
        
        # 4. Optional: Add a small "glow" dot at the end
        draw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill="#FFFFFF") # White center in the end dot

def get_contrast_text_color(hex_color):
    r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if brightness > 200 else "#FFFFFF"

def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    """Generates a Premium App-Style Report Card."""
    
    # Canvas Setup
    width, height = 900, 1300
    img = Image.new('RGB', (width, height), color="#F5F7FA") # Very light blue-grey background (not stark white)
    draw = ImageDraw.Draw(img)

    # --- Load Fonts ---
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_med = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Medium.ttf"

    font_reg_bytes = get_font(font_url_reg)
    font_bold_bytes = get_font(font_url_bold)
    font_med_bytes = get_font(font_url_med)

    if not all([font_reg_bytes, font_bold_bytes, font_med_bytes]):
        return None
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    f_header_title = create_font(font_bold_bytes, 38)
    f_header_date = create_font(font_med_bytes, 24)
    f_pm_val = create_font(font_bold_bytes, 150)
    f_pm_unit = create_font(font_med_bytes, 32)
    f_level = create_font(font_bold_bytes, 48)
    f_card_title = create_font(font_bold_bytes, 28)
    f_card_desc = create_font(font_reg_bytes, 22)
    f_footer = create_font(font_reg_bytes, 20)

    # --- 1. Header Background (Top Half) ---
    header_height = 450
    draw.rectangle([(0, 0), (width, header_height)], fill=color_hex)
    
    # Add a subtle gradient overlay to the header for depth
    gradient = Image.new('L', (width, header_height), color=0)
    g_draw = ImageDraw.Draw(gradient)
    for y in range(header_height):
        alpha = int(50 * (y / header_height)) # Darkens slightly towards bottom
        g_draw.line([(0, y), (width, y)], fill=alpha)
    
    # Composite gradient
    header_overlay = Image.new('RGB', (width, header_height), (0,0,0))
    img.paste(header_overlay, (0,0), mask=gradient)

    # Header Text
    txt_color = get_contrast_text_color(color_hex)
    draw.text((width/2, 70), t[lang]['header'], font=f_header_title, anchor="ms", fill=txt_color)
    
    # Date capsule (Semi-transparent background)
    date_w = draw.textlength(date_str, font=f_header_date) + 40
    date_bg_x = (width - date_w) / 2
    draw.rounded_rectangle(
        [date_bg_x, 100, date_bg_x + date_w, 145], 
        radius=20, 
        fill=(255, 255, 255, 40) # 40 is transparency
    )
    draw.text((width/2, 132), date_str, font=f_header_date, anchor="ms", fill=txt_color)

    # --- 2. Main White Sheet (With Shadow) ---
    sheet_y = 200
    sheet_margin = 30
    sheet_w = width - (sheet_margin * 2)
    sheet_h = height - sheet_y - sheet_margin
    sheet_radius = 45

    # Generate Shadow
    shadow = create_drop_shadow(sheet_w, sheet_h, sheet_radius, blur=30, opacity=40)
    img.paste(shadow, (sheet_margin - 30, sheet_y - 30 + 10), shadow) # Adjust offset

    # Draw White Sheet
    draw.rounded_rectangle(
        [(sheet_margin, sheet_y), (width - sheet_margin, height - sheet_margin)], 
        radius=sheet_radius, 
        fill="#FFFFFF"
    )

    # --- 3. Hero Gauge Section ---
    gauge_center_y = sheet_y + 160
    gauge_radius = 135
    max_pm = 200
    gauge_percent = min(latest_pm25 / max_pm, 1.0)

    # Draw Gauge
    draw_gauge_premium(draw, width/2, gauge_center_y, gauge_radius, gauge_percent, color_hex)

    # Text inside Gauge
    draw.text((width/2, gauge_center_y + 15), f"{latest_pm25:.0f}", font=f_pm_val, anchor="ms", fill="#2D3748")
    draw.text((width/2, gauge_center_y + 70), "μg/m³", font=f_pm_unit, anchor="ms", fill="#A0AEC0")

    # Level Badge (Floating)
    level_text = level
    bbox = draw.textbbox((0, 0), level_text, font=f_level)
    badge_w = (bbox[2] - bbox[0]) + 80
    badge_h = 70
    badge_x = (width - badge_w) / 2
    badge_y = gauge_center_y + 110

    # Badge Shadow
    badge_shadow = create_drop_shadow(badge_w, badge_h, 35, blur=15, opacity=30)
    img.paste(badge_shadow, (int(badge_x) - 15, int(badge_y) - 15 + 5), badge_shadow)

    # Badge Body
    # Create a tint color for badge background
    r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    tint = (int(r + (255-r)*0.9), int(g + (255-g)*0.9), int(b + (255-b)*0.9))
    
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=35, fill=tint)
    draw.text((width/2, badge_y + 32), level_text, font=f_level, anchor="mm", fill=color_hex)

    # --- 4. Advice Cards Grid ---
    grid_y = badge_y + 120
    
    col_gap = 30
    row_gap = 30
    grid_margin = 60 # Margin inside the white sheet
    
    avail_width = width - (grid_margin * 2)
    card_w = (avail_width - col_gap) / 2
    card_h = 290

    cards_data = [
        {'title': t[lang]['advice_cat_mask'], 'desc': advice_details['mask'], 'icon_key': 'mask'},
        {'title': t[lang]['advice_cat_activity'], 'desc': advice_details['activity'], 'icon_key': 'activity'},
        {'title': t[lang]['advice_cat_indoors'], 'desc': advice_details['indoors'], 'icon_key': 'indoors'},
        {'title': t[lang]['advice_cat_risk_group'] if 'advice_cat_risk_group' in t[lang] else t[lang]['risk_group'], 'desc': advice_details['risk_group'], 'icon_key': 'risk_group'},
    ]

    for i, item in enumerate(cards_data):
        col = i % 2
        row = i // 2
        x = grid_margin + col * (card_w + col_gap)
        y = grid_y + row * (card_h + row_gap)
        
        # Card Shadow (Subtle)
        c_shadow = create_drop_shadow(card_w, card_h, 30, blur=20, opacity=15)
        img.paste(c_shadow, (int(x) - 20, int(y) - 20 + 5), c_shadow)

        # Card Body (Very Light Gray Gradient-ish or Solid)
        draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=30, fill="#F8FAFC")

        # Icon
        icon_img = get_image_from_url(ICON_URLS.get(item['icon_key']), size=(130, 130))
        if icon_img:
            # Center icon
            ix = int(x + (card_w - 130) / 2)
            iy = int(y + 25)
            img.paste(icon_img, (ix, iy), icon_img)

        # Text
        tx = x + card_w / 2
        # Title
        draw.text((tx, y + 170), item['title'], font=f_card_title, anchor="ms", fill="#1A202C")
        
        # Desc (Wrap)
        desc = item['desc']
        words = desc.split()
        lines = []
        curr = []
        for w in words:
            curr.append(w)
            bbox = draw.textbbox((0,0), " ".join(curr), font=f_card_desc)
            if (bbox[2]-bbox[0]) > (card_w - 40):
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        lines.append(" ".join(curr))
        
        ly = y + 205
        for line in lines:
            draw.text((tx, ly), line, font=f_card_desc, anchor="ms", fill="#718096")
            ly += 28

    # --- 5. Footer ---
    draw.text((width/2, height - 50), t[lang]['report_card_footer'], font=f_footer, anchor="ms", fill="#CBD5E0")

    # --- Output ---
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
