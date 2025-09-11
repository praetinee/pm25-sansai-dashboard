from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import streamlit as st

@st.cache_data
def get_font_bytes(url):
    """Downloads font file bytes and caches them."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content # Return raw bytes, which are immutable and cache-safe
    except requests.exceptions.RequestException as e:
        st.error(f"Font download failed: {e}")
        return None

def generate_report_card(latest_pm25, level, color, emoji, advice, date_str, lang, t):
    """Generates a new, modern, and clean report card image."""
    # --- Font Handling ---
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_light = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Light.ttf"
    emoji_font_url = "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf"

    font_reg_content = get_font_bytes(font_url_reg)
    font_bold_content = get_font_bytes(font_url_bold)
    font_light_content = get_font_bytes(font_url_light)
    font_emoji_content = get_font_bytes(emoji_font_url)

    if not all([font_reg_content, font_bold_content, font_light_content, font_emoji_content]):
        return None
    
    # --- Create Fonts directly from bytes by wrapping in BytesIO ---
    font_header = ImageFont.truetype(BytesIO(font_bold_content), 36)
    font_date = ImageFont.truetype(BytesIO(font_reg_content), 24)
    font_pm_value = ImageFont.truetype(BytesIO(font_bold_content), 150)
    font_unit = ImageFont.truetype(BytesIO(font_reg_content), 30)
    font_level = ImageFont.truetype(BytesIO(font_bold_content), 40)
    font_advice_header = ImageFont.truetype(BytesIO(font_bold_content), 26)
    font_advice = ImageFont.truetype(BytesIO(font_reg_content), 22)
    font_footer = ImageFont.truetype(BytesIO(font_light_content), 16)
    font_emoji = ImageFont.truetype(BytesIO(font_emoji_content), 40)
    
    # --- Card Creation ---
    width, height = 800, 1000
    base_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    img = Image.new('RGB', (width, height), color=base_color)
    draw = ImageDraw.Draw(img)

    # --- Header ---
    header_title = t[lang]['page_title']
    draw.text((width/2, 60), header_title, font=font_header, anchor="ms", fill="#FFFFFF")
    draw.text((width/2, 105), date_str, font=font_date, anchor="ms", fill=(255, 255, 255, 200))

    # --- White Info Box ---
    box_y_start = 150
    draw.rounded_rectangle([(20, box_y_start), (width - 20, height - 20)], radius=20, fill="#FFFFFF")

    # --- PM2.5 Value ---
    draw.text((width/2, box_y_start + 140), f"{latest_pm25:.1f}", font=font_pm_value, anchor="ms", fill="#111111")
    draw.text((width/2, box_y_start + 220), "μg/m³", font=font_unit, anchor="ms", fill="#555555")
    
    # --- Level and Emoji (Side by side) ---
    level_bbox = draw.textbbox((0,0), level, font=font_level)
    emoji_bbox = draw.textbbox((0,0), emoji, font=font_emoji)
    total_width = level_bbox[2] + emoji_bbox[2] + 10 # 10 is spacing
    
    level_x = (width - total_width) / 2
    emoji_x = level_x + level_bbox[2] + 10
    
    draw.text((level_x, box_y_start + 280), level, font=font_level, anchor="ls", fill="#111111")
    draw.text((emoji_x, box_y_start + 280), emoji, font=font_emoji, anchor="ls", fill="#111111")
    
    draw.line([(60, box_y_start + 340), (width - 60, box_y_start + 340)], fill="#EEEEEE", width=2)
    
    # --- Advice Section ---
    advice_text = advice.replace('<br>', '\n').replace('<strong>', '').replace('</strong>', '')
    y_text = box_y_start + 380
    
    for line in advice_text.split('\n'):
        line = line.strip()
        if line:
            font_to_use = font_advice_header if t[lang]['general_public'] in line or t[lang]['risk_group'] in line else font_advice
            draw.text((width/2, y_text), line, font=font_to_use, fill="#333333", anchor="ms", align="center")
            y_text += 40 if font_to_use == font_advice_header else 35

    # --- Footer ---
    footer_text = t[lang]['report_card_footer']
    draw.text((width - 40, height - 40), footer_text, font=font_footer, anchor="rs", fill="#AAAAAA")

    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

