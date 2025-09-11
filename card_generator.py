from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import streamlit as st

@st.cache_data
def get_font(url):
    """Downloads a font file and caches it."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        st.error(f"Font download failed: {e}")
        return None

def generate_report_card(latest_pm25, level, color, emoji, advice, date_str, lang, t):
    """Generates a new, modern, and clean report card image."""
    # --- Font Handling ---
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_light = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Light.ttf"

    font_reg_bytes = get_font(font_url_reg)
    font_bold_bytes = get_font(font_url_bold)
    font_light_bytes = get_font(font_url_light)

    if not all([font_reg_bytes, font_bold_bytes, font_light_bytes]):
        return None
    
    # --- Create Fonts ---
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    font_header = create_font(font_bold_bytes, 36)
    font_date = create_font(font_reg_bytes, 24)
    font_pm_value = create_font(font_bold_bytes, 150)
    font_unit = create_font(font_reg_bytes, 30)
    font_level = create_font(font_bold_bytes, 40)
    font_advice_header = create_font(font_bold_bytes, 26)
    font_advice = create_font(font_reg_bytes, 22)
    font_footer = create_font(font_light_bytes, 16)
    
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
    draw.text((width/2, box_y_start + 280), f"{level} {emoji}", font=font_level, anchor="ms", fill="#111111")
    
    draw.line([(60, box_y_start + 340), (width - 60, box_y_start + 340)], fill="#EEEEEE", width=2)
    
    # --- Advice Section ---
    advice_text = advice.replace('<br>', '\n').replace('<strong>', '').replace('</strong>', '')
    y_text = box_y_start + 380
    
    for line in advice_text.split('\n'):
        line = line.strip()
        if line:
            font_to_use = font_advice_header if t[lang]['general_public'] in line or t[lang]['risk_group'] in line else font_advice
            draw.text((width/2, y_text), line, font=font_to_use, fill="#333333", anchor="ms")
            y_text += 40 if font_to_use == font_advice_header else 35

    # --- Footer ---
    footer_text = t[lang]['report_card_footer']
    draw.text((width - 40, height - 40), footer_text, font=font_footer, anchor="rs", fill="#AAAAAA")

    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

