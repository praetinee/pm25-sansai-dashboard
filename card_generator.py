from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import streamlit as st
import textwrap

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
    font_legend = create_font(font_reg_bytes, 20)
    font_legend_small = create_font(font_reg_bytes, 18)
    
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

    # --- PM2.5 Value (Centered) ---
    content_center_y = box_y_start + ((height - box_y_start - 200) / 2) # Adjusted for legend bar
    
    draw.text((width/2, content_center_y - 120), f"{latest_pm25:.1f}", font=font_pm_value, anchor="ms", fill="#111111")
    draw.text((width/2, content_center_y - 20), "μg/m³", font=font_unit, anchor="ms", fill="#555555")
    draw.text((width/2, content_center_y + 30), f"{level}", font=font_level, anchor="ms", fill="#111111")
    
    draw.line([(60, content_center_y + 80), (width - 60, content_center_y + 80)], fill="#EEEEEE", width=2)
    
    # --- Advice Section (Original Simple Layout) ---
    # Reconstruct the original advice string format for backward compatibility with old translation structure if needed
    if isinstance(advice, dict):
         advice_text = (
            f"<strong>{t[lang]['advice_cat_mask']}:</strong> {advice['mask']}<br>"
            f"<strong>{t[lang]['advice_cat_activity']}:</strong> {advice['activity']}<br>"
            f"<strong>{t[lang]['advice_cat_indoors']}:</strong> {advice['indoors']}<br>"
            f"<strong>{t[lang]['advice_cat_risk_group']}:</strong> {advice['risk_group']}"
        )
    else: # Fallback for very old string format
        advice_text = advice

    advice_text = advice_text.replace('<br>', '\n').replace('<strong>', '').replace('</strong>', '')
    y_text = content_center_y + 120 # Adjusted y position
    
    for line in advice_text.split('\n'):
        line = line.strip()
        if line:
            # Simple text rendering without complex logic
            draw.text((width/2, y_text), line, font=font_advice, fill="#333333", anchor="ms", align="center")
            y_text += 35

    # --- AQI Legend Bar ---
    legend_y = height - 160
    bar_height = 80
    segments = [
        (t[lang]['aqi_level_1'], "0-15", "#0099FF", "#FFFFFF"),
        (t[lang]['aqi_level_2'], "15-25", "#2ECC71", "#FFFFFF"),
        (t[lang]['aqi_level_3'], "25-37.5", "#F1C40F", "#000000"),
        (t[lang]['aqi_level_4_short'], "37.5-75", "#E67E22", "#FFFFFF"),
        (t[lang]['aqi_level_5_short'], ">75", "#E74C3C", "#FFFFFF")
    ]
    
    bar_width = width - 80
    segment_width = bar_width / len(segments)
    start_x = 40

    for i, (level_text, val_text, seg_color, text_color) in enumerate(segments):
        x0 = start_x + i * segment_width
        x1 = x0 + segment_width
        draw.rectangle([x0, legend_y, x1, legend_y + bar_height], fill=seg_color)
        
        center_x = x0 + segment_width / 2
        
        current_font = font_legend_small if len(level_text) > 8 else font_legend
        
        draw.text((center_x, legend_y + bar_height/2 - 10), level_text, font=current_font, anchor="mm", fill=text_color, align="center")
        draw.text((center_x, legend_y + bar_height/2 + 15), val_text, font=font_legend_small, anchor="mm", fill=text_color, align="center")

    # --- Footer ---
    footer_text = t[lang]['report_card_footer']
    draw.text((width - 40, height - 40), footer_text, font=font_footer, anchor="rs", fill="#AAAAAA")

    # --- Final Touches: Round the corners of the entire image ---
    radius = 30
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    
    final_img = Image.new('RGBA', (width, height))
    final_img.paste(img, (0, 0), mask=mask)

    buf = BytesIO()
    final_img.save(buf, format='PNG')
    return buf.getvalue()

