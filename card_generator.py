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

def draw_mask_icon(draw, x, y, size=30, color="#333333", width=3):
    """Draws the final surgical mask icon."""
    s = size / 4.0
    # Main body
    draw.line(((x - s*2.5, y - s), (x + s*2.5, y - s)), fill=color, width=width)
    draw.line(((x - s*2.5, y), (x + s*2.5, y)), fill=color, width=width)
    draw.line(((x - s*2.5, y + s), (x + s*2.5, y + s)), fill=color, width=width)
    # Straps
    draw.arc((x - s*3.5, y - s*2, x - s*1.5, y + s*2), 90, 270, fill=color, width=width)
    draw.arc((x + s*1.5, y - s*2, x + s*3.5, y + s*2), -90, 90, fill=color, width=width)


def draw_activity_icon(draw, x, y, size=30, color="#333333", width=3):
    """Draws the final cyclist icon."""
    s = size / 6.0
    # Wheels
    draw.ellipse((x - s*4, y + s, x - s, y + s*4), outline=color, width=width)
    draw.ellipse((x + s, y + s, x + s*4, y + s*4), outline=color, width=width)
    # Frame and body
    draw.line(((x - s*2.5, y + s*2.5), (x + s*0.5, y + s*2.5)), fill=color, width=width)
    draw.line(((x - s*1, y + s*2.5), (x, y - s*0.5)), fill=color, width=width)
    draw.line(((x, y - s*0.5), (x + s*2.5, y + s*2.5)), fill=color, width=width)
    draw.line(((x, y - s*0.5), (x + s*2, y - s*0.5)), fill=color, width=width) # Handlebar
    # Head
    draw.ellipse((x - s*1, y - s*3, x + s*1, y - s*1), outline=color, width=width)

def draw_indoors_icon(draw, x, y, size=30, color="#333333", width=3):
    """Draws a simple house icon."""
    s = size / 3.0
    points = [
        (x - s*1.5, y), (x, y - s*1.5), (x + s*1.5, y),
        (x + s*1.5, y + s*1.5), (x + s*0.5, y + s*1.5),
        (x + s*0.5, y + s*0.5), (x - s*0.5, y + s*0.5),
        (x - s*0.5, y + s*1.5), (x - s*1.5, y + s*1.5),
        (x - s*1.5, y)
    ]
    draw.line(points, fill=color, width=width, joint="miter")


def generate_report_card(latest_pm25, level, color, emoji, advice_details, date_str, lang, t):
    """Generates a new, modern, and clean report card image."""
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_url_light = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Light.ttf"

    font_reg_bytes = get_font(font_url_reg)
    font_bold_bytes = get_font(font_url_bold)
    font_light_bytes = get_font(font_url_light)

    if not all([font_reg_bytes, font_bold_bytes, font_light_bytes]):
        return None
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    font_header = create_font(font_bold_bytes, 36)
    font_date = create_font(font_reg_bytes, 24)
    font_pm_value = create_font(font_bold_bytes, 150)
    font_unit = create_font(font_reg_bytes, 30)
    font_level = create_font(font_bold_bytes, 40)
    font_advice_header = create_font(font_bold_bytes, 22)
    font_advice = create_font(font_reg_bytes, 18)
    font_risk_group = create_font(font_reg_bytes, 20)
    font_footer = create_font(font_light_bytes, 16)
    
    width_card, height_card = 800, 1000
    base_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    img = Image.new('RGB', (width_card, height_card), color=base_color)
    draw = ImageDraw.Draw(img)

    header_title = t[lang]['page_title']
    draw.text((width_card/2, 60), header_title, font=font_header, anchor="ms", fill="#FFFFFF")
    draw.text((width_card/2, 105), date_str, font=font_date, anchor="ms", fill=(255, 255, 255, 200))

    box_y_start = 150
    draw.rounded_rectangle([(20, box_y_start), (width_card - 20, height_card - 20)], radius=20, fill="#FFFFFF")

    pm_value_y = box_y_start + 140
    draw.text((width_card/2, pm_value_y), f"{latest_pm25:.1f}", font=font_pm_value, anchor="ms", fill="#111111")
    draw.text((width_card/2, pm_value_y + 80), "μg/m³", font=font_unit, anchor="ms", fill="#555555")
    draw.text((width_card/2, pm_value_y + 130), f"{level}", font=font_level, anchor="ms", fill="#111111")
    
    line_y = pm_value_y + 180
    draw.line([(60, line_y), (width_card - 60, line_y)], fill="#EEEEEE", width=2)
    
    # --- Advice Section with Icons ---
    advice_y_start = line_y + 80
    icon_size = 40
    icon_width = 3
    icon_color = "#333333"

    items = [
        (draw_mask_icon, t[lang]['advice_topics']['mask'], advice_details['mask']),
        (draw_activity_icon, t[lang]['advice_topics']['activity'], advice_details['activity']),
        (draw_indoors_icon, t[lang]['advice_topics']['indoors'], advice_details['indoors']),
    ]
    
    num_items = len(items)
    total_width = width_card - 120
    item_width = total_width / num_items
    
    for i, (icon_func, header, text) in enumerate(items):
        center_x = 60 + (item_width * i) + (item_width / 2)
        icon_func(draw, center_x, advice_y_start - 20, size=icon_size, color=icon_color, width=icon_width)
        draw.text((center_x, advice_y_start + 30), header, font=font_advice_header, anchor="ms", fill="#111111")
        draw.text((center_x, advice_y_start + 60), text, font=font_advice, anchor="ms", fill="#555555")

    risk_line_y = advice_y_start + 100
    draw.line([(60, risk_line_y), (width_card - 60, risk_line_y)], fill="#EEEEEE", width=2)
    
    risk_text = f"{t[lang]['risk_group']}: {advice_details['risk_group']}"
    draw.text((width_card/2, risk_line_y + 40), risk_text, font=font_risk_group, anchor="ms", fill="#333333")

    # --- Footer with AQI Bar ---
    aqi_bar_y = height_card - 160
    aqi_levels = [
        (t[lang]['aqi_level_1'], "0-15", "#0099FF", "#FFFFFF"),
        (t[lang]['aqi_level_2'], "15-25", "#2ECC71", "#FFFFFF"),
        (t[lang]['aqi_level_3'], "25-37.5", "#F1C40F", "#000000"),
        (t[lang]['aqi_level_4_short'], "37.5-75", "#E67E22", "#FFFFFF"),
        (t[lang]['aqi_level_5_short'], ">75", "#E74C3C", "#FFFFFF"),
    ]
    
    bar_width = width_card - 80
    segment_width = bar_width / len(aqi_levels)
    bar_height = 50
    
    for i, (level_text, val_text, seg_color, text_color) in enumerate(aqi_levels):
        x0 = 40 + (i * segment_width)
        x1 = x0 + segment_width
        draw.rectangle([(x0, aqi_bar_y), (x1, aqi_bar_y + bar_height)], fill=seg_color)
        draw.text((x0 + segment_width/2, aqi_bar_y + bar_height/2 - 8), level_text, font=font_advice, anchor="ms", fill=text_color)
        draw.text((x0 + segment_width/2, aqi_bar_y + bar_height/2 + 12), val_text, font=font_advice, anchor="ms", fill=text_color)
    
    footer_text = t[lang]['report_card_footer']
    draw.text((width_card / 2, height_card - 40), footer_text, font=font_footer, anchor="ms", fill="#AAAAAA")
    
    # --- Round corners ---
    mask = Image.new('L', (width_card, height_card), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, width_card, height_card), radius=30, fill=255)
    img.putalpha(mask)

    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

