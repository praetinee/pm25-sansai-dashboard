from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from io import BytesIO
import streamlit as st
import math
import re

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
CANVAS_HEIGHT = 2400 # High res vertical canvas (Initial size, will be cropped)

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
    # Updated thresholds to match the new standards
    if pm <= 15: return '#0099FF' # Blue (Excellent) - Updated color code
    elif pm <= 25: return '#2ECC71' # Green (Good) - Updated color code
    elif pm <= 37.5: return '#F1C40F' # Yellow (Moderate/Starting to affect) - Updated color code
    elif pm <= 75: return '#E67E22' # Orange (Unhealthy/High Dust) - Updated color code
    else: return '#E74C3C' # Red (Hazardous) - Updated color code

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def has_thai_characters(text):
    """Checks if the text contains Thai characters."""
    return bool(re.search(r'[\u0E00-\u0E7F]', text))

def draw_thai_text(draw, text, font, x, y, color, anchor='lt'):
    """
    Custom renderer for Thai text to fix floating vowel/tone overlap issues.
    Only used when Thai characters are detected.
    """
    if not text: return

    # Thai characters that cause stacking issues
    upper_vowels = set(['\u0E31', '\u0E34', '\u0E35', '\u0E36', '\u0E37', '\u0E47', '\u0E4D'])
    tones = set(['\u0E48', '\u0E49', '\u0E4A', '\u0E4B', '\u0E4C'])
    
    # 1. Separate base text and problematic tones
    base_text_chars = []
    adjustments = [] 

    for i, char in enumerate(text):
        # Check for Tone atop Upper Vowel collision
        if i > 0 and char in tones and text[i-1] in upper_vowels:
            # Record this tone to draw manually later
            adjustments.append((char, len(base_text_chars) - 1))
        else:
            base_text_chars.append(char)
            
    base_text = "".join(base_text_chars)
    
    # 2. Calculate Base Position
    if anchor == 'mm':
        bbox = draw.textbbox((x, y), base_text, font=font, anchor='mm')
        start_x, start_y = bbox[0], bbox[1]
    else: # 'lt'
        start_x, start_y = x, y

    # 3. Draw Base Text (Tones stripped)
    draw.text((start_x, start_y), base_text, font=font, fill=color)
    
    # 4. Manual Tone Surgery (Draw stripped tones in correct position)
    for char, vowel_idx in adjustments:
        # Measure width up to the vowel
        prefix = base_text[:vowel_idx]
        prefix_w = font.getlength(prefix)
        
        # Get width of the vowel itself to center the tone
        vowel_char = base_text[vowel_idx]
        vowel_w = font.getlength(vowel_char)
        
        # Get width of the tone itself
        tone_w = font.getlength(char)
        
        # X Calculation: Start + Prefix + Center over vowel
        tone_x = start_x + prefix_w + (vowel_w - tone_w) / 2
        
        # Y Calculation: Lift it up!
        # Lift by ~25% of font size relative to the line top
        shift_amount = font.size * 0.25
        tone_y = start_y - shift_amount
        
        # Draw the tone
        draw.text((tone_x, tone_y), char, font=font, fill=color)

def is_thai_combining_char(char):
    """Check if the character is a Thai combining vowel or tone mark."""
    code = ord(char)
    return 0x0E31 <= code <= 0x0E4E or code == 0x0E30

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
                for i, char in enumerate(word):
                    check_str = temp + char
                    if (draw.textbbox((0,0), check_str, font=font)[2]) <= max_width:
                        temp += char
                    else:
                        if is_thai_combining_char(char) and len(temp) > 0:
                            last_char = temp[-1]
                            temp = temp[:-1]
                            lines.append(temp)
                            temp = last_char + char
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
    # INTELLIGENT SWITCH: 
    # Use custom Thai renderer ONLY if Thai characters are present.
    # Otherwise (Numbers, English) use standard PIL renderer to avoid layout breakage.
    if has_thai_characters(text):
        draw_thai_text(draw, text, font, x, y, color, anchor='mm')
    else:
        draw.text((x, y), text, font=font, fill=color, anchor="mm")

def draw_text_left(draw, text, font, x, y, color):
    if has_thai_characters(text):
        draw_thai_text(draw, text, font, x, y, color, anchor='lt')
    else:
        draw.text((x, y), text, font=font, fill=color, anchor="lt")

# --- MAIN GENERATOR ---
def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
    width, height = CANVAS_WIDTH, CANVAS_HEIGHT
    theme_rgb = hex_to_rgb(get_theme_color(latest_pm25))
    
    # Base Image
    img = Image.new('RGBA', (width, height), get_theme_color(latest_pm25))
    draw = ImageDraw.Draw(img)

    # Fonts - Using Sarabun (Proven Safe & Stable)
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
    f_action_val = get_font(font_bold_url, 30)

    # ==========================================
    # 1. HEADER SECTION (Logo & Date)
    # ==========================================
    
    # --- LOGO ---
    logo_img = get_image_from_url(ICON_URLS['logo'])
    if logo_img:
        logo_h = 220
        aspect = logo_img.width / logo_img.height
        logo_w = int(logo_h * aspect)
        logo_img = logo_img.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        
        logo_x = 50
        logo_y = 40
        img.paste(logo_img, (logo_x, logo_y), logo_img)

    # --- DATE PILL ---
    date_bbox = draw.textbbox((0, 0), date_str, font=f_pill)
    date_w = date_bbox[2] - date_bbox[0] + 80
    date_h = date_bbox[3] - date_bbox[1] + 30
    
    date_x = width - date_w - 60 
    date_y = 110
    
    date_bg = Image.new('RGBA', (int(date_w), int(date_h)), (0,0,0,0))
    date_draw = ImageDraw.Draw(date_bg)
    # Changed fill to more opaque white (220) to ensure black text contrast against dark themes
    date_draw.rounded_rectangle([0, 0, date_w, date_h], radius=30, fill=(255, 255, 255, 220))
    img.paste(date_bg, (int(date_x), int(date_y)), date_bg)
    
    # Changed text color to Black (#000000)
    draw_text_centered(draw, date_str, f_pill, date_x + date_w//2, date_y + date_h//2 - 4, "#000000")

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
    
    # Numbers and English units go through standard PIL drawing (via the check in draw_text_centered)
    draw_text_centered(draw, f"{latest_pm25:.0f}", f_huge, width//2, gauge_cy - 20, theme_rgb)
    draw_text_centered(draw, "µg/m³", f_unit, width//2, gauge_cy + 100, theme_rgb)
    
    # Thai level text goes through custom renderer
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
        
        # --- VERTICAL CENTERING LOGIC ---
        # 1. Wrap description text to see how many lines we have
        desc_lines = wrap_text(desc, f_body, text_w, draw)
        desc_lines = desc_lines[:3] # Limit to 3 lines max
        
        # 2. Calculate height of the text block
        # Title height approx (font size 44) + gap + Body height (lines * line height)
        title_h = 50 
        line_h = 45
        gap = 10
        
        total_text_h = title_h + gap + (len(desc_lines) * line_h)
        
        # 3. Calculate Starting Y to center vertically in the card
        # Center of card = y_pos + (card_h / 2)
        # Start Y = Center - (Total Height / 2)
        text_start_y = y_pos + (card_h - total_text_h) / 2
        
        # Draw Title
        draw_text_left(draw, title, f_title, text_x, text_start_y, "#1e293b")
        
        # Draw Description Lines
        current_y = text_start_y + title_h + gap
        for i, line in enumerate(desc_lines):
            draw_text_left(draw, line, f_body, text_x, current_y, "#64748b")
            current_y += line_h
            
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
    # Changed color to #000000 (Black)
    draw_text_left(draw, t[lang]['advice_header'], f_subtitle, margin_x + 10, current_y, "#000000")
    
    grid_y = current_y + 60
    grid_gap = 18 
    
    col_w = (width - (margin_x * 2) - (grid_gap * 2)) / 3
    col_h = 360 
    
    # --- Custom Logic: Override Indoors text based on PM2.5 Level ---
    indoors_val = advice_details['indoors']
    if 25 < latest_pm25 <= 37.5:
        indoors_val = "เลี่ยงเปิดหน้าต่าง / เปิดเครื่องฟอก"
    elif latest_pm25 > 37.5:
        indoors_val = "ปิดบ้านสนิท / เปิดเครื่องฟอก"
        
    actions = [
        {'label': t[lang]['advice_cat_mask'], 'val': advice_details['mask'], 'icon': 'mask'},
        {'label': t[lang]['advice_cat_activity'], 'val': advice_details['activity'], 'icon': 'activity'},
        {'label': t[lang]['advice_cat_indoors'], 'val': indoors_val, 'icon': 'indoors'}
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
        
        # --- NEW LAYOUT: Fixed Top Alignment ---
        # Instead of centering everything vertically, we lock the top position
        # so icons and titles always line up perfectly.
        
        padding_top = 40 
        
        ic_size = 110 
        gap_icon_label = 25 
        h_label = 30 
        gap_label_val = 15 
        line_height = 36 
        
        # 1. Icon Position (Fixed Top)
        icon_cy = by + padding_top + (ic_size / 2)
        draw.ellipse([cx - ic_size/2, icon_cy - ic_size/2, cx + ic_size/2, icon_cy + ic_size/2], fill=theme_rgb)
        
        act_icon = get_image_from_url(ICON_URLS[act['icon']])
        if act_icon:
            act_icon = act_icon.resize((75, 75), Image.Resampling.LANCZOS)
            icon_img_y = icon_cy - (75 / 2)
            img.paste(act_icon, (int(cx - 37), int(icon_img_y)), act_icon)
            
        # 2. Label Position (Fixed distance from Icon)
        label_cy = by + padding_top + ic_size + gap_icon_label + (h_label / 2)
        draw_text_centered(draw, act['label'], f_pill, cx, label_cy, "#64748b")
        
        # 3. Value Position (Fixed distance from Label, flowing down)
        val_start_y = by + padding_top + ic_size + gap_icon_label + h_label + gap_label_val
        
        v_lines = wrap_text(act['val'], f_action_val, col_w - 20, draw)
        for k, vl in enumerate(v_lines[:4]):
            line_cy = val_start_y + (k * line_height) + (line_height / 2)
            draw_text_centered(draw, vl, f_action_val, cx, line_cy, theme_rgb)

    # ==========================================
    # 5. FOOTER & RESIZE
    # ==========================================
    
    # Calculate position relative to the grid bottom
    grid_bottom = grid_y + col_h
    footer_y = grid_bottom + 80 # Reduced gap (Previously effectively ~300px+)
    
    # Changed color to #000000 (Black)
    draw_text_centered(draw, t[lang]['report_card_footer'], f_small, width//2, footer_y, "#000000")
    
    # Crop the image to fit content
    new_height = int(footer_y + 80) # Add padding below footer
    img = img.crop((0, 0, width, new_height))

    final_img = round_corners(img, 60)
    buf = BytesIO()
    final_img.save(buf, format='PNG', quality=95)
    return buf.getvalue()
