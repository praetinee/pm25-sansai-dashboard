import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
import pandas as pd
from utils import get_aqi_level
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

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
    """Generates a beautiful, shareable report card image."""
    # --- Font Handling ---
    font_url_reg = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_url_bold = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    
    font_reg_bytes = get_font(font_url_reg)
    font_bold_bytes = get_font(font_url_bold)

    if not font_reg_bytes or not font_bold_bytes:
        return None

    font_main = ImageFont.truetype(font_reg_bytes, 32)
    font_pm_value = ImageFont.truetype(font_bold_bytes, 120)
    font_level = ImageFont.truetype(font_bold_bytes, 48)
    font_advice_header = ImageFont.truetype(font_bold_bytes, 28)
    font_advice = ImageFont.truetype(font_reg_bytes, 24)
    font_footer = ImageFont.truetype(font_reg_bytes, 18)

    # --- Card Creation ---
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # --- Background Gradient ---
    top_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    bottom_color = (255, 255, 255)
    for y in range(height):
        r = int(top_color[0] * (1 - y/height) + bottom_color[0] * (y/height))
        g = int(top_color[1] * (1 - y/height) + bottom_color[1] * (y/height))
        b = int(top_color[2] * (1 - y/height) + bottom_color[2] * (y/height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # --- Drawing Elements ---
    draw.text((40, 40), date_str, font=font_main, fill=(0,0,0, 200))

    draw.text((width/2, 160), f"{latest_pm25:.1f}", font=font_pm_value, anchor="ms", fill="#333333")
    draw.text((width/2, 230), f"μg/m³", font=font_main, anchor="ms", fill="#555555")
    draw.text((width/2, 280), f"{level} {emoji}", font=font_level, anchor="ms", fill="#333333")

    # --- Advice Section ---
    advice_text = advice.replace('<br>', '\n').replace('<strong>', '').replace('</strong>', '')
    advice_lines = advice_text.split('\n')
    y_text = 360
    
    draw.line([(40, y_text - 20), (width - 40, y_text - 20)], fill="#DDDDDD", width=1)
    
    for line in advice_lines:
        line = line.strip()
        if line:
            font_to_use = font_advice_header if t[lang]['general_public'] in line or t[lang]['risk_group'] in line else font_advice
            draw.text((40, y_text), line, font=font_to_use, fill="#333333")
            y_text += 35 if font_to_use == font_advice_header else 30
    
    # --- Footer ---
    footer_text = t[lang]['report_card_footer']
    draw.text((width - 40, height - 40), footer_text, font=font_footer, anchor="rs", fill="#555555")
    
    # --- Convert image to bytes ---
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def inject_custom_css():
    """Injects custom CSS to make the app responsive and theme-aware."""
    st.markdown("""
        <style>
            /* Import Google Font 'Sarabun' */
            @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');

            /* Apply font to the entire app, using !important to override defaults */
            html, body, [class*="st-"], .stApp, h1, h2, h3, h4, h5, h6 {
                font-family: 'Sarabun', sans-serif !important;
            }
            
            /* SUPER-SPECIFIC FIX for st.expander header font */
            .st-expander-header p {
                 font-family: 'Sarabun', sans-serif !important;
            }

            /* General Card Style */
            .card {
                padding: 20px;
                border-radius: 15px;
                background-color: var(--secondary-background-color);
                border: 1px solid var(--border-color, #dfe6e9);
                height: 100%;
            }

            /* NEW Calendar Styles */
            .calendar-day {
                background-color: var(--secondary-background-color);
                border-radius: 10px;
                padding: 10px;
                text-align: center;
                min-height: 90px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                border-bottom: 5px solid transparent; /* Default transparent border */
            }
            .calendar-day:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 12px rgba(0,0,0,0.1);
            }
            .calendar-day-header {
                align-self: flex-start; /* Day number to the top-left */
                font-size: 0.9rem;
                font-weight: 500;
                opacity: 0.8;
            }
            .calendar-day-value {
                font-size: 1.5rem; /* Bigger value */
                font-weight: 700;
                line-height: 1;
            }
            .calendar-day-na { /* Style for N/A days */
                 background-color: var(--secondary-background-color);
                 color: var(--text-color);
                 opacity: 0.5;
                 box-shadow: none;
            }
            
            /* Legend Box for AQI */
            .legend-box {
                display: flex;
                align-items: center;
                font-size: 1.1rem;
                margin-bottom: 8px;
            }
            .legend-color {
                height: 20px;
                width: 20px;
                border-radius: 5px;
                margin-right: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

def display_realtime_pm(df, lang, t, date_str):
    """Displays the current PM2.5 value and advice with a modern UI."""
    inject_custom_css()
    
    latest_pm25 = df['PM2.5'][0]
    level, color, emoji, advice = get_aqi_level(latest_pm25, lang, t)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader(t[lang]['current_pm25'])
        st.markdown(
            f"""
            <div style="background-color: {color}; padding: 25px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); height: 100%;">
                <h1 style="font-family: 'Sarabun', sans-serif; font-size: 4.5rem; margin: 0; text-shadow: 2px 2px 4px #000000;">{latest_pm25:.1f}</h1>
                <p style="font-family: 'Sarabun', sans-serif; font-size: 1.5rem; margin: 0;">μg/m³</p>
                <h2 style="font-family: 'Sarabun', sans-serif; margin-top: 15px;">{level} {emoji}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.subheader(t[lang]['advice_header'])
        st.markdown(f"<div class='card'>{advice}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""
            <div class="legend-box"><div class="legend-color" style="background-color: #0099FF;"></div><b>{t[lang]['aqi_level_1']}:</b> 0 - 15.0 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #2ECC71;"></div><b>{t[lang]['aqi_level_2']}:</b> 15.1 - 25.0 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #F1C40F;"></div><b>{t[lang]['aqi_level_3']}:</b> 25.1 - 37.5 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #E67E22;"></div><b>{t[lang]['aqi_level_4']}:</b> 37.6 - 75.0 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #E74C3C;"></div><b>{t[lang]['aqi_level_5']}:</b> > 75.0 μg/m³</div>
        """, unsafe_allow_html=True)

    # --- Action Buttons ---
    st.write("") # Spacer
    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
    with btn_col1:
        if st.button(t[lang]['refresh_button'], use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with btn_col2:
        report_card_bytes = generate_report_card(latest_pm25, level, color, emoji, advice, date_str, lang, t)
        if report_card_bytes:
            st.download_button(
                label=t[lang]['download_button'],
                data=report_card_bytes,
                file_name=f"pm25_report_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                mime="image/png",
                use_container_width=True
            )

def display_symptom_checker(lang, t):
    st.subheader(t[lang]['symptom_checker_title'])
    st.write(t[lang]['symptom_checker_intro'])

    symptoms = t[lang]['symptoms']
    checked_symptoms = 0
    
    for symptom in symptoms:
        if st.checkbox(symptom):
            checked_symptoms += 1

    st.write("---")

    if checked_symptoms == 0:
        st.success(f"✅ {t[lang]['symptom_results_0']}")
    elif 1 <= checked_symptoms <= 2:
        st.warning(f"⚠️ {t[lang]['symptom_results_1_2']}")
    else:
        st.error(f"🚨 {t[lang]['symptom_results_3_plus']}")
    
    st.caption(t[lang]['symptom_disclaimer'])


def display_health_impact(df, lang, t):
    """Calculates and displays health impact metrics for the current year."""
    
    current_year = datetime.now().year
    
    # Create date range string for the title
    if lang == 'th':
        start_str = f"1 {t['th']['month_names'][0]} {current_year + 543}"
        end_str = f"31 {t['th']['month_names'][11]} {current_year + 543}"
        date_range = f"{start_str} - {end_str}"
    else:
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)
        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

    st.subheader(t[lang]['health_impact_title'].format(date_range=date_range))

    # Filter data for the current year
    df_current_year = df[df['Datetime'].dt.year == current_year]

    if df_current_year.empty:
        st.info("ไม่มีข้อมูลสำหรับปีนี้" if lang == 'th' else "No data available for the current year.")
        return

    # Calculate daily averages for the current year
    daily_avg_df = df_current_year.groupby(df_current_year['Datetime'].dt.date)['PM2.5'].mean().reset_index()

    # Calculate number of unhealthy days
    unhealthy_days = daily_avg_df[daily_avg_df['PM2.5'] > 37.5]
    num_unhealthy_days = len(unhealthy_days)

    # Calculate cigarette equivalent from total exposure for the current year
    total_pm_exposure = daily_avg_df['PM2.5'].sum()
    equivalent_cigarettes = total_pm_exposure / 22

    col1, col2 = st.columns(2)
    col1.metric(
        label=t[lang]['unhealthy_days_text'],
        value=f"{num_unhealthy_days} {t[lang]['days_unit']}"
    )
    col2.metric(
        label=t[lang]['cigarette_equivalent_text'],
        value=f"{int(equivalent_cigarettes)} {t[lang]['cigarettes_unit']}"
    )
    st.caption(t[lang]['health_impact_explanation'])


def display_24hr_chart(df, lang, t):
    st.subheader(t[lang]['hourly_trend_today'])
    
    latest_date = df['Datetime'].max().date()
    day_data = df[df['Datetime'].dt.date == latest_date].sort_values(by="Datetime", ascending=True)

    if day_data.empty:
        st.info(t[lang]['no_data_today'])
        return

    colors = [get_aqi_level(pm, lang, t)[1] for pm in day_data['PM2.5']]

    fig_24hr = go.Figure()
    fig_24hr.add_trace(go.Bar(
        x=day_data['Datetime'], 
        y=day_data['PM2.5'], 
        name='PM2.5',
        marker_color=colors,
        marker=dict(cornerradius=5),
        text=day_data['PM2.5'].apply(lambda x: f'{x:.1f}'),
        textposition='outside'
    ))
    fig_24hr.update_layout(
        font=dict(family="Sarabun, sans-serif"),
        title_font=dict(family="Sarabun, sans-serif"),
        xaxis_title=None, 
        yaxis_title=t[lang]['pm25_unit'], 
        plot_bgcolor='rgba(0,0,0,0)', 
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor='var(--border-color, #e9e9e9)', showticklabels=True, tickformat='%H:%M', tickangle=-45, title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
        yaxis=dict(gridcolor='var(--border-color, #e9e9e9)', title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
        showlegend=False,
        uniformtext_minsize=8, 
        uniformtext_mode='hide'
    )
    st.plotly_chart(fig_24hr, use_container_width=True)

def display_monthly_calendar(df, lang, t):
    st.subheader(t[lang]['monthly_calendar_header'])
    df_calendar = df.copy()
    df_calendar['date'] = df_calendar['Datetime'].dt.date
    daily_avg_pm25 = df_calendar.groupby('date')['PM2.5'].mean().reset_index()
    daily_avg_pm25['date'] = pd.to_datetime(daily_avg_pm25['date'])

    latest_date = daily_avg_pm25['date'].max() if not daily_avg_pm25.empty else datetime.now()
    
    selected_date = st.date_input(
        t[lang]['date_picker_label'],
        value=latest_date,
        min_value=df['Datetime'].min().date(),
        max_value=datetime.now().date(),
        key="calendar_date_picker"
    )
    
    year, month = selected_date.year, selected_date.month
    month_data = daily_avg_pm25[(daily_avg_pm25['date'].dt.year == year) & (daily_avg_pm25['date'].dt.month == month)]
    
    cal = calendar.monthcalendar(year, month)
    
    month_name = t[lang]['month_names'][month-1]
    year_display = year + 543 if lang == 'th' else year

    st.markdown(f"#### {month_name} {year_display}")
    
    days_header = t[lang]['days_header']
    cols = st.columns(7)
    for i, day_name in enumerate(days_header):
        cols[i].markdown(f"<div style='text-align: center; font-weight: bold; opacity: 0.7;'>{day_name}</div>", unsafe_allow_html=True)

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown("")
            else:
                day_data = month_data[month_data['date'].dt.day == day]
                if not day_data.empty:
                    pm_value = day_data['PM2.5'].iloc[0]
                    _, color, _, _ = get_aqi_level(pm_value, lang, t)
                    cols[i].markdown(f"""
                    <div class="calendar-day" style="border-bottom-color: {color};">
                        <div class="calendar-day-header">{day}</div>
                        <div class="calendar-day-value">{pm_value:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    cols[i].markdown(f"""
                    <div class="calendar-day calendar-day-na">
                        <div class="calendar-day-header">{day}</div>
                    </div>
                    """, unsafe_allow_html=True)

def display_historical_data(df, lang, t):
    st.subheader(t[lang]['historical_expander'])
    today = date.today()
    default_start = today - timedelta(days=7)
    
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input(t[lang]['start_date'], value=default_start, min_value=df['Datetime'].min().date(), max_value=today, key="start_date_hist")
    with col_date2:
        end_date = st.date_input(t[lang]['end_date'], value=today, min_value=df['Datetime'].min().date(), max_value=today, key="end_date_hist")

    if start_date > end_date:
        st.error(t[lang]['date_error'])
    else:
        mask = (df['Datetime'].dt.date >= start_date) & (df['Datetime'].dt.date <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            st.warning(t[lang]['no_data_in_range'])
        else:
            daily_avg_df = filtered_df.groupby(filtered_df['Datetime'].dt.date)['PM2.5'].mean().reset_index()
            daily_avg_df.rename(columns={'Datetime': 'Date', 'PM2.5': 'Avg PM2.5'}, inplace=True)

            avg_pm = filtered_df['PM2.5'].mean()
            max_pm = filtered_df['PM2.5'].max()
            min_pm = filtered_df['PM2.5'].min()

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric(t[lang]['metric_avg'], f"{avg_pm:.1f} μg/m³")
            mcol2.metric(t[lang]['metric_max'], f"{max_pm:.1f} μg/m³")
            mcol3.metric(t[lang]['metric_min'], f"{min_pm:.1f} μg/m³")

            colors_hist = [get_aqi_level(pm, lang, t)[1] for pm in daily_avg_df['Avg PM2.5']]
            
            if lang == 'th':
                start_date_str = f"{start_date.day} {t['th']['month_names'][start_date.month - 1]} {start_date.year + 543}"
                end_date_str = f"{end_date.day} {t['th']['month_names'][end_date.month - 1]} {end_date.year + 543}"
                title_text = f"{t[lang]['daily_avg_chart_title']} ({start_date_str} - {end_date_str})"
            else:
                title_text = f"{t[lang]['daily_avg_chart_title']} ({start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')})"


            fig_hist = go.Figure()
            fig_hist.add_trace(go.Bar(
                x=daily_avg_df['Date'], 
                y=daily_avg_df['Avg PM2.5'], 
                name=t[lang]['avg_pm25_unit'],
                marker_color=colors_hist,
                marker=dict(cornerradius=5)
            ))
            fig_hist.update_layout(
                title_text=title_text,
                font=dict(family="Sarabun, sans-serif"),
                title_font=dict(family="Sarabun, sans-serif"),
                xaxis_title="วันที่" if lang == 'th' else "Date", 
                yaxis_title=t[lang]['avg_pm25_unit'],
                xaxis=dict(title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
                yaxis=dict(title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
                template="plotly_white",
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True)

def display_knowledge_tabs(lang, t):
    st.subheader(t[lang]['knowledge_header'])
    
    knowledge_items = t[lang]['tabs']
    content_th = [
        """
        #### PM2.5: ฆาตกรเงียบที่มองไม่เห็น
        **PM2.5** คือฝุ่นพิษขนาดจิ๋วที่เล็กกว่าเส้นผมของเราถึง 25 เท่า มันคือภัยร้ายที่เรามองไม่เห็นด้วยตาเปล่า แต่สามารถเดินทางผ่านการหายใจเข้าสู่ปอดและแทรกซึมเข้าสู่กระแสเลือดได้โดยตรง
        > มันไม่ใช่แค่ "ฝุ่น" แต่มันคือ **"พาหะของสารพิษ"** ที่พร้อมจะทำลายสุขภาพของเราจากภายใน
        """,
        """
        #### ทำไม PM2.5 ถึงเป็น "หายนะ" สำหรับอนาคตของเด็ก?
        ปอดและสมองของเด็กยังคงพัฒนาอย่างต่อเนื่อง การหายใจเอาอากาศพิษเข้าไปในช่วงวัยนี้ **เปรียบเสมือนการวางยาพิษต่อพัฒนาการของพวกเขา**
        - **ปอดถูกทำลาย:** ขัดขวางการเติบโตของปอด เพิ่มความเสี่ยงของโรคหอบหืดและภูมิแพ้ไปตลอดชีวิต
        - **สมองเสียหาย:** ส่งผลกระทบต่อพัฒนาการทางสมองและสติปัญญา ทำให้ศักยภาพของเด็กลดลง
        > การปกป้องเด็กจาก PM2.5 ไม่ใช่ทางเลือก แต่คือ **หน้าที่ในการปกป้องอนาคตของพวกเขา**
        """,
        """
        #### PM2.5: ตัวเร่งให้วาระสุดท้ายมาถึงเร็วขึ้น
        สำหรับผู้สูงอายุ ร่างกายที่เสื่อมถอยตามวัยนั้นเปราะบางอยู่แล้ว PM2.5 ทำหน้าที่เหมือน **"ตัวจุดชนวน"** ที่กระตุ้นให้โรคประจำตัวกำเริบอย่างรุนแรง
        - **หัวใจวายและหลอดเลือดสมอง:** เพิ่มความเสี่ยงเฉียบพลันอย่างมีนัยสำคัญ
        - **โรคปอดกำเริบ:** ทำให้ผู้ป่วยโรคถุงลมโป่งพองหรือหลอดลมอักเสบเรื้อรังมีอาการทรุดลงอย่างรวดเร็ว
        > ทุกวันที่ต้องหายใจในอากาศที่มีมลพิษ คือการบั่นทอนคุณภาพชีวิตและเร่งเวลาสู่ความเจ็บป่วยที่หนักหนาสาหัส
        """,
        """
        #### ภัยคุกคามต่อ "สองชีวิต" ในครรภ์มารดา
        เมื่อแม่หายใจเอา PM2.5 เข้าไป พิษร้ายไม่ได้หยุดอยู่แค่ที่แม่ แต่มันสามารถ **เดินทางผ่านรกไปสู่ทารกในครรภ์ได้**
        - **คลอดก่อนกำหนด:** เพิ่มความเสี่ยงที่ทารกจะลืมตาดูโลกก่อนเวลาอันควร
        - **น้ำหนักแรกเกิดต่ำ:** ส่งผลต่อสุขภาพและพัฒนาการในระยะยาวของเด็ก
        > การปกป้องหญิงตั้งครรภ์ คือการให้ **"ของขวัญชิ้นแรกที่ดีที่สุด"** แก่ชีวิตใหม่ที่กำลังจะเกิดขึ้น นั่นคือสุขภาพที่แข็งแรง
        """,
        """
        #### เปลี่ยนโรคประจำตัวให้กลายเป็น "ภาวะฉุกเฉิน"
        สำหรับผู้ที่มีโรคประจำตัว เช่น โรคหัวใจ, โรคหอบหืด, หรือภูมิแพ้ PM2.5 ไม่ใช่แค่สิ่งรบกวน แต่คือ **"ตัวกระตุ้นชั้นดี"** ที่สามารถเปลี่ยนวันที่ปกติให้กลายเป็นวิกฤตได้
        - **กระตุ้นอาการแพ้:** ทำให้อาการภูมิแพ้รุนแรงและควบคุมได้ยากขึ้น
        - **จุดชนวนหอบหืด:** เพิ่มความถี่และความรุนแรงของการจับหืด
        - **เพิ่มภาระให้หัวใจ:** ทำให้หัวใจทำงานหนักขึ้น เสี่ยงต่อภาวะหัวใจล้มเหลว
        > การป้องกัน PM2.5 คือ **การป้องกันภาวะแทรกซ้อนที่อาจเป็นอันตรายถึงชีวิต**
        """,
        """
        #### ลำดับชั้นของการป้องกัน PM2.5 ที่ได้ผลจริง
        1.  **สร้างห้องปลอดฝุ่น (Clean Room):** วิธีที่ดีที่สุดคือการสร้างพื้นที่ปลอดภัยในบ้าน โดยใช้เครื่องฟอกอากาศที่มีแผ่นกรอง HEPA ในห้องที่ปิดสนิท และอาจทำระบบ Positive Pressure เพื่อดันอากาศพิษออกไป
        2.  **เครื่องฟอกอากาศ:** เลือกเครื่องที่มีค่า **CADR (Clean Air Delivery Rate)** เหมาะสมกับขนาดห้อง และใช้แผ่นกรอง **HEPA** ที่สามารถดักจับฝุ่นจิ๋วได้
        3.  **หน้ากาก N95/KF94:** เมื่อต้องออกนอกอาคาร การสวมหน้ากากที่ได้มาตรฐานและกระชับกับใบหน้าเป็นสิ่งจำเป็น
        4.  **ปิดบ้านให้สนิท:** ลดการนำอากาศจากภายนอกเข้ามาในบ้าน
        5.  **ระบบปรับอากาศ:** แอร์ที่มีแผ่นกรองสามารถช่วยกรองฝุ่นได้ในระดับหนึ่ง
        6.  **สเปรย์ละอองน้ำ:** เป็นวิธีที่ได้ผลน้อยและแค่ชั่วคราว ไม่สามารถแก้ปัญหาที่ต้นเหตุได้
        """,
        """
        #### หน้ากากที่ดีที่สุด ไม่ใช่แค่ยี่ห้อ แต่คือ "ความฟิต"
        หน้ากาก N95 ราคาแพงอาจไร้ค่า ถ้าอากาศพิษยังเล็ดลอดผ่านช่องว่างข้างแก้มได้
        - **มาตรฐานต้องมี:** มองหาสัญลักษณ์ N95, KN95, หรือ KF94 ที่รับรองความสามารถในการกรอง
        - **ความกระชับสำคัญที่สุด:** หน้ากากต้องแนบสนิทกับใบหน้า ไม่มีช่องว่างให้อากาศรั่วไหล
        - **วาล์วหายใจออก:** ช่วยให้หายใจสะดวกขึ้น แต่ **ไม่ป้องกันการแพร่เชื้อ** จากตัวเราไปสู่ผู้อื่น
        > **จำไว้ว่า:** หน้ากากที่ดีที่สุดคือหน้ากากที่ได้มาตรฐาน และคุณสวมมันอย่าง "ถูกต้องและกระชับ" ทุกครั้งที่ออกนอกบ้าน
        """,
        """
        #### เลือกเครื่องฟอกอากาศให้ฉลาด เหมือนเลือก "ปอดที่สาม" ให้บ้าน
        อย่าดูแค่ดีไซน์หรือราคา แต่ให้ดูที่ "ประสิทธิภาพ" ในการฟอกอากาศ
        - **รู้จัก CADR (Clean Air Delivery Rate):** คือค่าที่บอกว่าเครื่องฟอกอากาศสามารถสร้างอากาศบริสุทธิ์ได้เร็วแค่ไหน (ยิ่งสูงยิ่งดี) **เลือก CADR ให้เหมาะสมกับขนาดห้องของคุณ**
        - **หัวใจคือแผ่นกรอง HEPA:** ตรวจสอบให้แน่ใจว่าเป็น **"True HEPA"** ซึ่งสามารถดักจับอนุภาคขนาดเล็กถึง 0.3 ไมครอนได้ 99.97%
        - **ไส้กรองเสริม:** ไส้กรอง Carbon ช่วยลดกลิ่นและสารเคมีระเหยได้
        > การลงทุนกับเครื่องฟอกอากาศที่ดี คือการลงทุนกับ **"ลมหายใจที่สะอาด"** ของทุกคนในครอบครัว
        """
    ]
    content_en = [
        """
        #### PM2.5: The Invisible Killer
        **PM2.5** are tiny toxic particles, 25 times smaller than a human hair. They are an invisible danger that can bypass your body's defenses, entering your lungs and bloodstream directly.
        > It's not just "dust"; it's a **carrier for toxins** ready to damage our health from the inside out.
        """,
        """
        #### Why is PM2.5 a "Catastrophe" for a Child's Future?
        A child's lungs and brain are still developing. Breathing toxic air during this critical period is **like poisoning their growth.**
        - **Damaged Lungs:** Hinders lung development, increasing lifelong risks of asthma and allergies.
        - **Brain Impairment:** Affects cognitive development and intelligence, limiting their full potential.
        > Protecting children from PM2.5 isn't an option; it's our **duty to safeguard their future.**
        """,
        """
        #### PM2.5: Accelerating the Inevitable
        For the elderly, an aging body is already vulnerable. PM2.5 acts as a **"trigger"** that severely aggravates chronic diseases.
        - **Heart Attacks and Strokes:** Significantly increases the acute risk.
        - **Exacerbated Lung Disease:** Rapidly worsens conditions for patients with emphysema or chronic bronchitis.
        > Every day spent breathing polluted air diminishes their quality of life and hastens severe illness.
        """,
        """
        #### A Threat to "Two Lives"
        When an expectant mother breathes in PM2.5, the toxins don't stop with her. They can **cross the placental barrier and affect the unborn child.**
        - **Premature Birth:** Increases the risk of the baby being born too early.
        - **Low Birth Weight:** Impacts the child's long-term health and development.
        > Protecting pregnant women is giving the **"best first gift"** to a new life: a healthy start.
        """,
        """
        #### Turning a Chronic Condition into an "Emergency"
        For individuals with conditions like heart disease, asthma, or allergies, PM2.5 is not just an irritant; it's a **potent trigger** that can turn a normal day into a crisis.
        - **Intensified Allergies:** Makes allergy symptoms more severe and difficult to control.
        - **Asthma Attacks:** Increases the frequency and severity of asthma attacks.
        - **Strained Heart:** Forces the heart to work harder, risking heart failure.
        > Protecting against PM2.5 is **preventing life-threatening complications.**
        """,
        """
        #### The Hierarchy of Effective PM2.5 Protection
        1.  **Create a Clean Room:** The best method is to establish a safe zone at home using an air purifier with a HEPA filter in a sealed room. A positive pressure system can also be used to push out polluted air.
        2.  **Air Purifiers:** Choose a unit with a **CADR (Clean Air Delivery Rate)** appropriate for your room size and a **HEPA** filter capable of trapping microscopic particles.
        3.  **N95/KF94 Masks:** Essential when outdoors. Ensure the mask is certified and fits snugly.
        4.  **Seal Your Home:** Minimize air infiltration from outside.
        5.  **Air Conditioning:** AC units with filters can provide some level of filtration.
        6.  **Water Misting:** A temporary and minimally effective solution that doesn't address the root cause.
        """,
        """
        #### The Best Mask Isn't a Brand, It's a "Fit"
        An expensive N95 mask is useless if polluted air can leak through gaps on the sides.
        - **Look for Standards:** Check for certifications like N95, KN95, or KF94.
        - **The Fit is Everything:** The mask must create a tight seal against your face with no gaps.
        - **Exhalation Valves:** Make breathing easier but **do not protect others from you** if you are sick.
        > **Remember:** The best mask is one that is certified AND that you wear "correctly and snugly" every time you go outside.
        """,
        """
        #### Choose an Air Purifier Wisely, Like Choosing a "Third Lung" for Your Home
        Don't just look at design or price; focus on performance.
        - **Know Your CADR (Clean Air Delivery Rate):** This value indicates how quickly the purifier cleans the air. A higher CADR is better. **Match the CADR to your room size.**
        - **The HEPA Filter is Key:** Ensure it's a **"True HEPA"** filter, which captures 99.97% of particles as small as 0.3 microns.
        - **Additional Filters:** An activated carbon filter can help remove odors and volatile organic compounds (VOCs).
        > Investing in a good air purifier is an investment in the **"clean breaths"** of your entire family.
        """
    ]

    content_to_display = content_th if lang == 'th' else content_en
    
    for i, title in enumerate(knowledge_items):
        with st.expander(title):
            st.markdown(content_to_display[i])

