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

# --- Helper functions for drawing icons (New Professional Style) ---
def draw_mask_icon(draw, center_x, y, size=50, color="#333333"):
    s = size / 2
    width = 3
    top_y = y + s * 0.4
    bottom_y = y + s * 1.5
    left_x = center_x - s
    right_x = center_x + s
    
    draw.line([(left_x + s*0.2, top_y), (right_x - s*0.2, top_y)], fill=color, width=width)
    draw.line([(left_x + s*0.4, bottom_y), (right_x - s*0.4, bottom_y)], fill=color, width=width)
    draw.arc([(left_x, top_y), (left_x + s*0.8, bottom_y)], 90, 270, fill=color, width=width)
    draw.arc([(right_x - s*0.8, top_y), (right_x, bottom_y)], 270, 90, fill=color, width=width)
    draw.arc([(left_x - s*0.8, top_y - s*0.2), (left_x + s*0.2, bottom_y + s*0.2)], 120, 240, fill=color, width=width-1)
    draw.arc([(right_x - s*0.2, top_y - s*0.2), (right_x + s*0.8, bottom_y + s*0.2)], -60, 60, fill=color, width=width-1)

def draw_activity_icon(draw, center_x, y, size=50, color="#333333"):
    s = size / 2
    width = 3
    head_radius = s * 0.25
    head_center_x = center_x
    head_center_y = y + head_radius
    draw.ellipse([
        (head_center_x - head_radius, head_center_y - head_radius),
        (head_center_x + head_radius, head_center_y + head_radius)
    ], outline=color, width=width)

    body_start_y = head_center_y + head_radius
    body_end_y = y + s * 1.4
    draw.line([(center_x, body_start_y), (center_x, body_end_y)], fill=color, width=width)
    
    arm_y = body_start_y + s * 0.2
    draw.line([(center_x, arm_y), (center_x + s*0.8, arm_y + s * 0.2)], fill=color, width=width)
    draw.line([(center_x, arm_y), (center_x - s*0.7, arm_y - s * 0.3)], fill=color, width=width)

    draw.line([(center_x, body_end_y), (center_x + s*0.7, body_end_y + s * 0.5)], fill=color, width=width)
    draw.line([(center_x, body_end_y), (center_x - s*0.6, body_end_y + s * 0.2)], fill=color, width=width)

def draw_indoors_icon(draw, center_x, y, size=50, color="#333333"):
    s = size / 2
    width = 3
    draw.line([(center_x - s, y + s*0.6), (center_x, y), (center_x + s, y + s*0.6)], fill=color, width=width)
    draw.rectangle((center_x - s*0.8, y + s*0.6, center_x + s*0.8, y + s*1.8), outline=color, width=width)
    draw.rectangle((center_x - s*0.5, y + s*0.9, center_x, y + s*1.4), outline=color, width=width-1)

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
    font_pm_value = create_font(font_bold_bytes, 130) # Slightly smaller
    font_unit = create_font(font_reg_bytes, 30)
    font_level = create_font(font_bold_bytes, 40)
    font_advice_cat = create_font(font_bold_bytes, 22)
    font_advice_body = create_font(font_reg_bytes, 18)
    font_risk = create_font(font_reg_bytes, 20)
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

    # --- PM2.5 Value ---
    draw.text((width/2, box_y_start + 140), f"{latest_pm25:.1f}", font=font_pm_value, anchor="ms", fill="#111111")
    draw.text((width/2, box_y_start + 210), "μg/m³", font=font_unit, anchor="ms", fill="#555555")
    draw.text((width/2, box_y_start + 260), f"{level}", font=font_level, anchor="ms", fill="#111111")
    
    draw.line([(60, box_y_start + 310), (width - 60, box_y_start + 310)], fill="#EEEEEE", width=2)
    
    # --- Actionable Advice Section ---
    advice_details = advice # The advice object is now passed directly
    advice_y_start = box_y_start + 330
    
    categories = [
        ('mask', t[lang]['advice_cat_mask'], draw_mask_icon),
        ('activity', t[lang]['advice_cat_activity'], draw_activity_icon),
        ('indoors', t[lang]['advice_cat_indoors'], draw_indoors_icon)
    ]
    
    num_cols = len(categories)
    col_width = (width - 80) / num_cols
    
    for i, (key, title, icon_func) in enumerate(categories):
        center_x = 40 + (i * col_width) + (col_width / 2)
        
        # Draw Icon
        icon_func(draw, center_x, advice_y_start)
        
        # Draw Category Title
        cat_y = advice_y_start + 65
        draw.text((center_x, cat_y), title, font=font_advice_cat, anchor="ms", fill="#111111")
        
        # Draw Advice Body Text
        body_y = cat_y + 30
        advice_text = advice_details[key]
        
        # Wrap text
        wrapped_lines = textwrap.wrap(advice_text, width=18)
        
        current_y = body_y
        for line in wrapped_lines:
            draw.text((center_x, current_y), line, font=font_advice_body, anchor="ms", fill="#555555", align="center")
            current_y += 25

    # --- Risk Group Advice ---
    risk_y = advice_y_start + 200
    draw.line([(60, risk_y), (width - 60, risk_y)], fill="#EEEEEE", width=2)
    risk_text = f"🚨 {t[lang]['advice_cat_risk_group']}: {advice_details['risk_group']}"
    
    wrapped_risk_lines = textwrap.wrap(risk_text, width=60)
    current_risk_y = risk_y + 25
    for line in wrapped_risk_lines:
        draw.text((width/2, current_risk_y), line, font=font_risk, anchor="ms", fill="#333333", align="center")
        current_risk_y += 30

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

