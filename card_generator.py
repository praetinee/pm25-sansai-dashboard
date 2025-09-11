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
    """Draws the custom mask icon using Pillow."""
    # Scale coordinates from 64x64 viewBox to the target size
    def scale(p):
        return (p[0] * size / 64, p[1] * size / 64)

    # Center the icon
    offset_x = center_x - size / 2
    offset_y = y

    # Define points for the quadratic Bezier curves
    p = {
        'main': [(12, 24), (32, 10), (52, 24), (54, 36), (52, 44), (32, 58), (12, 44), (10, 36), (12, 24)],
        'ear_l': [(12, 28), (2, 32), (12, 40)],
        'ear_r': [(52, 28), (62, 32), (52, 40)],
        'fold1': [(16, 30), (32, 26), (48, 30)],
        'fold2': [(16, 36), (32, 32), (48, 36)],
        'fold3': [(16, 42), (32, 38), (48, 42)]
    }

    # Apply scaling and offset to all points
    for key in p:
        p[key] = [(pt[0] / 64 * size + offset_x, pt[1] / 64 * size + offset_y) for pt in p[key]]
    
    # Custom path drawing logic for curves
    # This is a simplification; true Bezier requires more complex rendering
    # We will use lines to connect points of the curves
    draw.line(p['main'][0:3], fill=color, width=3)
    draw.line(p['main'][2:5], fill=color, width=3)
    draw.line(p['main'][4:7], fill=color, width=3)
    draw.line(p['main'][6:9], fill=color, width=3)
    
    draw.line(p['ear_l'], fill=color, width=3)
    draw.line(p['ear_r'], fill=color, width=3)

    draw.line(p['fold1'], fill=color, width=2)
    draw.line(p['fold2'], fill=color, width=2)
    draw.line(p['fold3'], fill=color, width=2)


def draw_activity_icon(draw, center_x, y, size=48, color="#333333"):
    """Draws the cyclist icon using Pillow."""
    s = size / 24 # Scale factor
    w = 2
    # Circle centers
    c1_x, c1_y = center_x - (18.5-12) * s, y + (17.5-4) * s
    c2_x, c2_y = center_x - (5.5-12) * s, y + (17.5-4) * s
    head_x, head_y = center_x + (15-12) * s, y + (6.5-4) * s
    
    # Radii
    r1 = 3.5 * s
    r_head = 2 * s

    # Draw wheels
    draw.ellipse([(c1_x-r1, c1_y-r1), (c1_x+r1, c1_y+r1)], outline=color, width=w)
    draw.ellipse([(c2_x-r1, c2_y-r1), (c2_x+r1, c2_y+r1)], outline=color, width=w)
    
    # Draw frame and person
    p = {
        'frame_person': [
            (center_x + (12-12)*s, y + (17.5-4)*s), # Midpoint between wheels
            (center_x - (5.5-12)*s, y + (17.5-4)*s),# Back wheel center
            (center_x - (5.5-12-1.5)*s, y + (17.5-4-5)*s), # Seat post
            (center_x + (12-12-4)*s, y + (17.5-4-7.5)*s), # Top tube
            (center_x + (12-12+2)*s, y + (17.5-4-10.5)*s), # Head
            (center_x + (15-12)*s, y + (6.5-4)*s),
            (center_x + (12-12+1.5)*s, y + (17.5-4-5)*s), # Handlebar
            (center_x + (18.5-12)*s, y + (17.5-4)*s) # Front wheel center
        ]
    }
    draw.line(p['frame_person'], fill=color, width=w)
    
    # Draw head
    draw.ellipse([(head_x-r_head, head_y-r_head), (head_x+r_head, head_y+r_head)], outline=color, width=w)


def draw_indoors_icon(draw, center_x, y, size=48, color="#333333"):
    """Draws the house icon using Pillow."""
    s = size / 24 # Scale factor
    w = 2
    
    points = [
        (center_x + (3-12)*s, y + (9-2)*s),
        (center_x + (12-12)*s, y + (2-2)*s),
        (center_x + (21-12)*s, y + (9-2)*s),
        (center_x + (21-12)*s, y + (20-2)*s),
        (center_x + (17-12)*s, y + (20-2)*s),
        (center_x + (17-12)*s, y + (12-2)*s),
        (center_x + (7-12)*s, y + (12-2)*s),
        (center_x + (7-12)*s, y + (20-2)*s),
        (center_x + (3-12)*s, y + (20-2)*s),
        (center_x + (3-12)*s, y + (9-2)*s),
    ]
    draw.line(points, fill=color, width=w)


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

