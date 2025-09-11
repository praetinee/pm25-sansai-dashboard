from PIL import Image, ImageDraw, ImageFont, ImageOps
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

# --- Icon Drawing Functions ---
def draw_mask_icon(draw, center_x, y, size=48, color="#333333"):
    """Draws the custom mask icon using Pillow with standardized stroke width."""
    offset_x = center_x - size / 2
    offset_y = y
    stroke_width = 2 # Standardized stroke width

    def scale_point(px, py):
        return (px / 64 * size + offset_x, py / 64 * size + offset_y)

    # Replicate the drawing based on the provided SVG paths
    draw.line([scale_point(12, 24), scale_point(32, 10), scale_point(52, 24)], fill=color, width=stroke_width)
    draw.line([scale_point(52, 24), scale_point(54, 36), scale_point(52, 44)], fill=color, width=stroke_width)
    draw.line([scale_point(52, 44), scale_point(32, 58), scale_point(12, 44)], fill=color, width=stroke_width)
    draw.line([scale_point(12, 44), scale_point(10, 36), scale_point(12, 24)], fill=color, width=stroke_width)
    
    # Ear loops
    draw.line([scale_point(12, 28), scale_point(2, 32), scale_point(12, 40)], fill=color, width=stroke_width)
    draw.line([scale_point(52, 28), scale_point(62, 32), scale_point(52, 40)], fill=color, width=stroke_width)
    
    # Folds (thinner)
    fold_width = stroke_width - 1 if stroke_width > 1 else 1
    draw.line([scale_point(16, 30), scale_point(32, 26), scale_point(48, 30)], fill=color, width=fold_width)
    draw.line([scale_point(16, 36), scale_point(32, 32), scale_point(48, 36)], fill=color, width=fold_width)
    draw.line([scale_point(16, 42), scale_point(32, 38), scale_point(48, 42)], fill=color, width=fold_width)


def draw_activity_icon(draw, center_x, y, size=48, color="#333333"):
    """Draws the custom bicycle icon using Pillow with standardized stroke width."""
    offset_x = center_x - size / 2
    offset_y = y
    stroke_width = 2 # Standardized stroke width

    def p(px, py):
        return (px / 64 * size + offset_x, py / 64 * size + offset_y)

    # Wheels
    r = 8 / 64 * size
    draw.ellipse([(p(18-8, 44-8)), (p(18+8, 44+8))], outline=color, width=stroke_width)
    draw.ellipse([(p(46-8, 44-8)), (p(46+8, 44+8))], outline=color, width=stroke_width)
    
    # Frame
    draw.polygon([p(18, 44), p(30, 32), p(40, 44)], outline=color, width=stroke_width)
    
    # Seat and handle
    draw.line([p(30, 32), p(30, 24)], fill=color, width=stroke_width)
    draw.line([p(28, 24), p(34, 24)], fill=color, width=stroke_width)
    draw.line([p(40, 44), p(44, 30), p(52, 28)], fill=color, width=stroke_width)


def draw_indoors_icon(draw, center_x, y, size=48, color="#333333"):
    """Draws the house icon using Pillow."""
    s = size / 24 # Scale factor from 24x24 viewBox
    w = 2 # Reference stroke width
    offset_x = center_x - size / 2
    offset_y = y
    
    # Redefined for cleaner drawing
    house_outline = [
        (3*s + offset_x, 9*s + offset_y),
        (12*s + offset_x, 2*s + offset_y),
        (21*s + offset_x, 9*s + offset_y),
        (21*s + offset_x, 22*s + offset_y),
        (3*s + offset_x, 22*s + offset_y),
        (3*s + offset_x, 9*s + offset_y)
    ]
    draw.line(house_outline, fill=color, width=w)

    door = [
        (9*s + offset_x, 22*s + offset_y),
        (9*s + offset_x, 12*s + offset_y),
        (15*s + offset_x, 12*s + offset_y),
        (15*s + offset_x, 22*s + offset_y)
    ]
    draw.line(door, fill=color, width=w)


def generate_report_card(latest_pm25, level, color_hex, emoji, advice_details, date_str, lang, t):
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
    
    def create_font(font_bytes, size):
        font_bytes.seek(0)
        return ImageFont.truetype(font_bytes, size)

    font_header = create_font(font_bold_bytes, 36)
    font_date = create_font(font_reg_bytes, 24)
    font_pm_value = create_font(font_bold_bytes, 150)
    font_unit = create_font(font_reg_bytes, 30)
    font_level = create_font(font_bold_bytes, 40)
    font_advice_header = create_font(font_bold_bytes, 24)
    font_advice = create_font(font_reg_bytes, 20)
    font_footer = create_font(font_light_bytes, 16)
    
    width, height = 800, 1000
    base_color = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    img = Image.new('RGB', (width, height), color=base_color)
    draw = ImageDraw.Draw(img)

    header_title = t[lang]['page_title']
    draw.text((width/2, 60), header_title, font=font_header, anchor="ms", fill="#FFFFFF")
    draw.text((width/2, 105), date_str, font=font_date, anchor="ms", fill=(255, 255, 255, 200))

    box_y_start = 150
    draw.rounded_rectangle([(20, box_y_start), (width - 20, height - 20)], radius=20, fill="#FFFFFF")
    
    pm_y_pos = box_y_start + 110
    draw.text((width/2, pm_y_pos), f"{latest_pm25:.1f}", font=font_pm_value, anchor="ms", fill="#111111")
    draw.text((width/2, pm_y_pos + 80), "μg/m³", font=font_unit, anchor="ms", fill="#555555")
    draw.text((width/2, pm_y_pos + 130), level, font=font_level, anchor="ms", fill="#111111")
    
    advice_y_start = pm_y_pos + 220
    draw.line([(60, advice_y_start-20), (width - 60, advice_y_start-20)], fill="#EEEEEE", width=2)
    
    # --- Advice with Icons ---
    advice_items = [
        ('mask', t[lang]['advice_cat_mask'], draw_mask_icon),
        ('activity', t[lang]['advice_cat_activity'], draw_activity_icon),
        ('indoors', t[lang]['advice_cat_indoors'], draw_indoors_icon)
    ]

    item_width = width / len(advice_items)
    for i, (key, title, icon_func) in enumerate(advice_items):
        center_x = (item_width * i) + (item_width / 2)
        
        icon_func(draw, center_x, advice_y_start) # Draw icon
        
        text_y = advice_y_start + 60
        draw.text((center_x, text_y), title, font=font_advice_header, anchor="ms", fill="#333333")
        draw.text((center_x, text_y + 30), advice_details[key], font=font_advice, anchor="ms", fill="#555555", align="center")

    risk_y_start = advice_y_start + 150
    draw.line([(60, risk_y_start), (width - 60, risk_y_start)], fill="#EEEEEE", width=2)
    risk_text = f"{t[lang]['risk_group']}: {advice_details['risk_group']}"
    draw.text((width/2, risk_y_start + 30), risk_text, font=font_advice, anchor="ms", fill="#333333")

    # --- AQI Bar ---
    bar_y = height - 150
    bar_height = 50
    colors_map = {
        '#0099FF': (t[lang]['aqi_level_1'], "0-15"),
        '#2ECC71': (t[lang]['aqi_level_2'], "15-25"),
        '#F1C40F': (t[lang]['aqi_level_3'], "25-37.5"),
        '#E67E22': (t[lang]['aqi_level_4_short'], "37.5-75"),
        '#E74C3C': (t[lang]['aqi_level_5_short'], ">75")
    }
    num_segments = len(colors_map)
    segment_width = (width - 80) / num_segments
    font_bar = create_font(font_reg_bytes, 16)
    
    for i, (bar_color, (bar_level, bar_range)) in enumerate(colors_map.items()):
        x0 = 40 + i * segment_width
        x1 = x0 + segment_width
        text_color = "black" if bar_color == "#F1C40F" else "white"
        draw.rectangle([(x0, bar_y), (x1, bar_y + bar_height)], fill=bar_color)
        draw.text((x0 + segment_width/2, bar_y + 15), bar_level, font=font_bar, anchor="ms", fill=text_color)
        draw.text((x0 + segment_width/2, bar_y + 35), bar_range, font=font_bar, anchor="ms", fill=text_color)

    footer_text = t[lang]['report_card_footer']
    draw.text((width - 40, height - 40), footer_text, font=font_footer, anchor="rs", fill="#AAAAAA")
    
    # --- Round corners ---
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=30, fill=255)
    img.putalpha(mask)

    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

