import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import calendar
import pandas as pd
import math
from utils import get_aqi_level

def inject_custom_css():
    """Injects custom CSS to make the app responsive and theme-aware."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
            
            /* Global Font */
            html, body, [class*="st-"], .stApp, .stApp * {
                font-family: 'Sarabun', sans-serif !important;
            }

            /* --- Modern Dashboard Container --- */
            .modern-card-container {
                background: white;
                border-radius: 2.5rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                overflow: hidden;
                border: 1px solid #f1f5f9;
                margin-bottom: 20px;
                max-width: 450px; /* Limit width for mobile look on desktop */
                margin-left: auto;
                margin-right: auto;
            }

            .modern-header-section {
                padding: 2.5rem 1.5rem 2rem 1.5rem;
                text-align: center;
                position: relative;
                color: white;
            }
            
            .modern-content-section {
                padding: 1.5rem;
                background: #fff;
            }

            /* --- Circular Gauge --- */
            .gauge-wrapper {
                position: relative;
                width: 180px;
                height: 180px;
                margin: 0 auto;
            }
            .gauge-bg {
                fill: none;
                stroke: rgba(255,255,255,0.25);
                stroke-width: 12;
            }
            .gauge-progress {
                fill: none;
                stroke: white;
                stroke-width: 12;
                stroke-linecap: round;
                transform: rotate(-90deg);
                transform-origin: 50% 50%;
                transition: stroke-dashoffset 1s ease-out;
            }
            .gauge-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                color: white;
                line-height: 1;
            }
            .gauge-value {
                font-size: 3.5rem;
                font-weight: 700;
                letter-spacing: -2px;
            }
            .gauge-unit {
                font-size: 0.8rem;
                opacity: 0.9;
                margin-top: 4px;
                font-weight: 500;
            }

            /* --- Status Text --- */
            .status-label {
                font-size: 2rem;
                font-weight: 700;
                margin-top: 1rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .status-sublabel {
                font-size: 0.9rem;
                opacity: 0.95;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                margin-top: 0.25rem;
            }

            /* --- Tab Styling (Custom Radio) --- */
            /* Container for the radio group */
            div[role="radiogroup"] {
                display: flex;
                flex-direction: row;
                background: #f1f5f9;
                padding: 6px;
                border-radius: 1rem;
                gap: 0;
                margin-bottom: 1.5rem;
                border-bottom: none !important;
                width: 100%;
            }
            /* Each option label */
            div[role="radiogroup"] label {
                flex: 1;
                margin: 0;
                padding: 0;
                background: transparent;
                border: none;
                cursor: pointer;
            }
            /* The inner div text of the label */
            div[role="radiogroup"] label > div {
                width: 100%;
                text-align: center;
                padding: 10px 0;
                border-radius: 0.8rem;
                font-weight: 600;
                font-size: 0.9rem;
                border: none !important;
                color: #64748b;
                transition: all 0.2s ease;
            }
            /* Active State - The selected tab */
            div[role="radiogroup"] label input[type="radio"]:checked + div {
                background: white;
                color: #0f172a;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                opacity: 1 !important;
            }
            /* Hide default radio circle */
            div[data-testid="stRadio"] label > div:first-child { display: none; }

            /* --- Advice Main Card --- */
            .main-advice-card {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 1.25rem;
                padding: 1.25rem;
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                margin-bottom: 1.5rem;
                transition: transform 0.2s;
            }
            .main-advice-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            }
            .advice-icon-box {
                width: 48px;
                height: 48px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                flex-shrink: 0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .advice-content h4 {
                margin: 0;
                font-size: 1rem;
                font-weight: 700;
                color: #1e293b;
            }
            .advice-content p {
                margin: 4px 0 0 0;
                font-size: 0.9rem;
                color: #64748b;
                line-height: 1.5;
            }

            /* --- Action Grid --- */
            .action-grid-title {
                font-size: 0.75rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #94a3b8;
                margin-bottom: 0.75rem;
                padding-left: 4px;
            }
            .action-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.75rem;
            }
            .action-card {
                padding: 1rem 0.5rem;
                border-radius: 1rem;
                border: 1px solid;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 6px;
                background: #f8fafc;
                height: 100%;
            }
            .action-icon { opacity: 0.8; }
            .action-label { font-size: 0.65rem; opacity: 0.7; text-transform: uppercase; font-weight: 600; }
            .action-value { font-size: 0.8rem; font-weight: 700; white-space: nowrap; line-height: 1.2; }

            /* --- Previous CSS for other components --- */
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
                border-bottom: 5px solid transparent;
            }
            .calendar-day-header { align-self: flex-start; font-size: 0.9rem; font-weight: 500; opacity: 0.8; }
            .calendar-day-value { font-size: 1.5rem; font-weight: 700; line-height: 1; }
            .calendar-day-na { background-color: var(--secondary-background-color); color: var(--text-color); opacity: 0.5; box-shadow: none; }
            
            .infographic-card {
                background-color: var(--secondary-background-color);
                border-left: 5px solid #1e40af;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                margin-top: 1rem;
            }
            .infographic-card h4 { color: #1e40af; margin-bottom: 0.5rem; }
            .infographic-card ul { list-style-type: none; padding-left: 0; margin-bottom: 0; }
            .infographic-card li { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
            .infographic-card .icon { font-size: 1.2rem; }
        </style>
    """, unsafe_allow_html=True)

def display_realtime_pm(df, lang, t, date_str):
    latest_pm25 = df['PM2.5'][0]
    
    # Get AQI data
    level_text, color, emoji, advice = get_aqi_level(latest_pm25, lang, t)
    advice_details = advice['details']
    
    # --- 1. Determine Color Theme & Status ---
    # Color logic based on PM2.5 ranges (matching the Modern UI design)
    if latest_pm25 <= 15:
        # Excellent (Teal/Sky)
        theme_gradient = "linear-gradient(135deg, #2dd4bf 0%, #0ea5e9 100%)" # Teal to Sky
        theme_shadow = "rgba(14, 165, 233, 0.3)"
        text_color_class = "text-sky-700"
        bg_light_class = "#f0f9ff" # sky-50
        border_class = "#e0f2fe" # sky-100
        status_key = "safe"
    elif latest_pm25 <= 25:
        # Good (Green)
        theme_gradient = "linear-gradient(135deg, #34d399 0%, #10b981 100%)" # Emerald
        theme_shadow = "rgba(16, 185, 129, 0.3)"
        text_color_class = "text-emerald-700"
        bg_light_class = "#ecfdf5" # emerald-50
        border_class = "#d1fae5" # emerald-100
        status_key = "safe"
    elif latest_pm25 <= 37.5:
        # Moderate (Yellow)
        theme_gradient = "linear-gradient(135deg, #facc15 0%, #eab308 100%)" # Yellow
        theme_shadow = "rgba(234, 179, 8, 0.3)"
        text_color_class = "text-yellow-700"
        bg_light_class = "#fefce8" # yellow-50
        border_class = "#fef9c3" # yellow-100
        status_key = "warning"
    elif latest_pm25 <= 75:
        # Unhealthy (Orange)
        theme_gradient = "linear-gradient(135deg, #fb923c 0%, #ea580c 100%)" # Orange
        theme_shadow = "rgba(234, 88, 12, 0.3)"
        text_color_class = "text-orange-700"
        bg_light_class = "#fff7ed" # orange-50
        border_class = "#ffedd5" # orange-100
        status_key = "danger"
    else:
        # Hazardous (Red)
        theme_gradient = "linear-gradient(135deg, #f87171 0%, #dc2626 100%)" # Red
        theme_shadow = "rgba(220, 38, 38, 0.3)"
        text_color_class = "text-rose-700"
        bg_light_class = "#fff1f2" # rose-50
        border_class = "#ffe4e6" # rose-100
        status_key = "critical"

    # --- 2. Calculate Gauge ---
    # Max value for gauge visual is 120 (for scale)
    percent = min((latest_pm25 / 120) * 100, 100)
    radius = 40
    circumference = 2 * math.pi * radius
    stroke_dashoffset = circumference - (percent / 100) * circumference

    # --- 3. Render Top Section (HTML) ---
    # Note: We split this into top and bottom to inject the Streamlit radio button in between
    
    col_center, = st.columns([1]) # Use full width but contained by CSS max-width
    
    with col_center:
        st.markdown(f"""
        <div class="modern-card-container">
            <div class="modern-header-section" style="background: {theme_gradient};">
                <!-- Background decoration -->
                <div style="position: absolute; top: -50px; right: -50px; width: 150px; height: 150px; background: white; opacity: 0.1; border-radius: 50%; filter: blur(40px);"></div>
                <div style="position: absolute; bottom: 0; left: 0; width: 100px; height: 100px; background: black; opacity: 0.05; border-radius: 50%; filter: blur(30px);"></div>
                
                <!-- Date Pill -->
                <div style="background: rgba(255,255,255,0.2); backdrop-filter: blur(4px); padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 20px;">
                    <span style="font-size: 0.8rem; font-weight: 500; opacity: 0.95;">{date_str}</span>
                </div>

                <!-- Gauge -->
                <div class="gauge-wrapper">
                    <svg viewBox="0 0 100 100" class="gauge-svg" style="transform: rotate(0deg);">
                        <circle cx="50" cy="50" r="{radius}" class="gauge-bg"></circle>
                        <circle cx="50" cy="50" r="{radius}" class="gauge-progress" 
                                style="stroke-dasharray: {circumference}; stroke-dashoffset: {stroke_dashoffset};"></circle>
                    </svg>
                    <div class="gauge-text">
                        <div class="gauge-value">{latest_pm25:.0f}</div>
                        <div class="gauge-unit">μg/m³</div>
                    </div>
                </div>
            </div>
            
            <div class="modern-content-section">
        """, unsafe_allow_html=True)

        # --- 4. Interactive Tabs (Streamlit Widget) ---
        
        # Closing the header section from above:
        st.markdown("</div></div>", unsafe_allow_html=True) 

        # --- 5. Tabs Selection ---
        tab_options = [t[lang]['general_public'], t[lang]['risk_group']]
        selected_tab = st.radio("Target Group", tab_options, label_visibility="collapsed")
        
        is_general = (selected_tab == t[lang]['general_public'])
        
        # Prepare Advice Content based on tab
        if is_general:
            main_title = t[lang]['general_public']
            main_desc = advice['summary']
            main_icon = "User" # Placeholder logic
            # Action logic for General (Simulated mapping based on PM level)
            act_mask = advice_details['mask']
            act_activity = advice_details['activity']
            act_home = advice_details['indoors']
        else:
            main_title = t[lang]['risk_group']
            main_desc = advice_details['risk_group']
            main_icon = "Heart"
            # Action logic for Risk (Usually stricter, but sticking to logic provided in utils)
            act_mask = advice_details['mask']
            act_activity = advice_details['activity']
            act_home = advice_details['indoors']

        # Determine colors for Action Cards based on status_key
        if status_key == 'safe':
            act_bg, act_color, act_border = "#ecfdf5", "#047857", "#d1fae5" # Green-ish
        elif status_key == 'warning':
            act_bg, act_color, act_border = "#fefce8", "#a16207", "#fef9c3" # Yellow-ish
        elif status_key == 'danger':
            act_bg, act_color, act_border = "#fff7ed", "#c2410c", "#ffedd5" # Orange-ish
        else:
            act_bg, act_color, act_border = "#fff1f2", "#be123c", "#ffe4e6" # Red-ish

        # Icons (SVG Strings)
        icon_mask = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>"""
        icon_activity = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>"""
        icon_home = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>"""
        icon_user = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>"""
        icon_heart = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 1 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 1 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>"""

        main_icon_svg = icon_user if is_general else icon_heart

        # --- 6. Render Bottom Content ---
        st.markdown(f"""
        <div style="max-width: 450px; margin: 0 auto;">
            <!-- Main Advice Card -->
            <div class="main-advice-card" style="border-left: 4px solid {act_color};">
                <div class="advice-icon-box" style="background: {theme_gradient};">
                    {main_icon_svg}
                </div>
                <div class="advice-content">
                    <h4>{main_title}</h4>
                    <p>{main_desc}</p>
                </div>
            </div>

            <!-- Action Grid -->
            <div class="action-grid-title">{t[lang]['advice_header']}</div>
            <div class="action-grid">
                <!-- Mask -->
                <div class="action-card" style="background: {act_bg}; border-color: {act_border}; color: {act_color};">
                    <div class="action-icon">{icon_mask}</div>
                    <div class="action-label">{t[lang]['advice_cat_mask']}</div>
                    <div class="action-value">{act_mask}</div>
                </div>
                <!-- Activity -->
                <div class="action-card" style="background: {act_bg}; border-color: {act_border}; color: {act_color};">
                    <div class="action-icon">{icon_activity}</div>
                    <div class="action-label">{t[lang]['advice_cat_activity']}</div>
                    <div class="action-value">{act_activity}</div>
                </div>
                <!-- Indoors -->
                <div class="action-card" style="background: {act_bg}; border-color: {act_border}; color: {act_color};">
                    <div class="action-icon">{icon_home}</div>
                    <div class="action-label">{t[lang]['advice_cat_indoors']}</div>
                    <div class="action-value">{act_home}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Spacer

        # --- 7. Footer Actions ---
        b_col1, b_col2 = st.columns([1, 1])
        with b_col1:
            if st.button(f"🔄 {t[lang]['refresh_button']}", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with b_col2:
            from card_generator import generate_report_card
            # Note: generate_report_card logic stays the same, generating the image for download
            report_card_bytes = generate_report_card(latest_pm25, level_text, color, emoji, advice_details, date_str, lang, t)
            if report_card_bytes:
                st.download_button(
                    label=f"🖼️ {t[lang]['download_button']}",
                    data=report_card_bytes,
                    file_name=f"pm25_report_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                    mime="image/png",
                    use_container_width=True)

def display_external_assessment(lang, t):
    st.subheader(t[lang]['external_assessment_title'])

    st.markdown(f"""
    <style>
        .assessment-card {{
            background-color: #F0F8FF; /* Light blue background */
            border-left: 6px solid #1E90FF; /* DodgerBlue accent line */
            padding: 24px;
            border-radius: 10px;
            margin: 20px 0px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        .assessment-card p {{
            font-size: 1.05rem;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        a.assessment-button {{
            display: inline-block;
            width: 100%;
            background-color: #1E90FF;
            color: white;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            font-size: 1.1rem;
            text-decoration: none;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }}
        a.assessment-button:hover {{
            background-color: #1C86EE;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }}
    </style>

    <div class="assessment-card">
        <p>{t[lang]['external_assessment_intro']}</p>
        <a href="https://www.pollutionclinic.com/home/diagnose/?gc=lampoon" target="_blank" class="assessment-button">
            {t[lang]['assessment_button_text']}
        </a>
    </div>
    """, unsafe_allow_html=True)


def display_health_impact(df, lang, t):
    current_year = datetime.now().year
    if lang == 'th':
        start_str = f"1 {t['th']['month_names'][0]} {current_year + 543}"
        end_str = f"31 {t['th']['month_names'][11]} {current_year + 543}"
        date_range = f"{start_str} - {end_str}"
    else:
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)
        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    st.subheader(t[lang]['health_impact_title'].format(date_range=date_range))
    df_current_year = df[df['Datetime'].dt.year == current_year]
    if df_current_year.empty:
        st.info(t[lang]['no_data_for_year'])
        return
    daily_avg_df = df_current_year.groupby(df_current_year['Datetime'].dt.date)['PM2.5'].mean().reset_index()
    unhealthy_days = daily_avg_df[daily_avg_df['PM2.5'] > 37.5]
    num_unhealthy_days = len(unhealthy_days)
    total_pm_exposure = daily_avg_df['PM2.5'].sum()
    equivalent_cigarettes = total_pm_exposure / 22
    col1, col2 = st.columns(2)
    col1.metric(label=t[lang]['unhealthy_days_text'], value=f"{num_unhealthy_days} {t[lang]['days_unit']}")
    col2.metric(label=t[lang]['cigarette_equivalent_text'], value=f"{int(equivalent_cigarettes)} {t[lang]['cigarettes_unit']}")
    st.caption(t[lang]['health_impact_explanation'])

def display_24hr_chart(df, lang, t):
    st.subheader(t[lang]['hourly_trend_today'])
    latest_date = df['Datetime'].max().date()
    day_data = df[df['Datetime'].dt.date == latest_date].sort_values(by="Datetime", ascending=True)
    if day_data.empty:
        st.info(t[lang]['no_data_today'])
        return
    colors = [get_aqi_level(pm, lang, t)[1] for pm in day_data['PM2.5']]
    fig_24hr = go.Figure(go.Bar(
        x=day_data['Datetime'], y=day_data['PM2.5'], name='PM2.5',
        marker_color=colors, marker=dict(cornerradius=5),
        text=day_data['PM2.5'].apply(lambda x: f'{x:.1f}'), textposition='outside'))
    fig_24hr.update_layout(
        font=dict(family="Sarabun"),
        yaxis_title=t[lang]['pm25_unit'],
        plot_bgcolor='rgba(0,0,0,0)', template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor='var(--border-color, #e9e9e9)', showticklabels=True, tickformat='%H:%M', tickangle=-45),
        yaxis=dict(gridcolor='var(--border-color, #e9e9e9)'),
        showlegend=False, uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig_24hr, use_container_width=True)

def display_monthly_calendar(df, lang, t):
    st.subheader(t[lang]['monthly_calendar_header'])
    
    st.caption(t[lang]['date_picker_label'])
    
    all_years = sorted(df['Datetime'].dt.year.unique(), reverse=True)
    
    def format_year(y):
        return str(y + 543) if lang == 'th' else str(y)
    
    col1, col2 = st.columns(2)
    selected_year = col1.selectbox("ปี" if lang == 'th' else "Year", options=all_years, format_func=format_year, index=0)
    
    df_year = df[df['Datetime'].dt.year == selected_year]
    available_months_num = sorted(df_year['Datetime'].dt.month.unique())
    month_map = {m: t[lang]['month_names'][m-1] for m in available_months_num}
    default_month_index = len(available_months_num) - 1
    selected_month_num = col2.selectbox("เดือน" if lang == 'th' else "Month", options=available_months_num, format_func=lambda m: month_map[m], index=default_month_index)
    
    year, month = selected_year, selected_month_num

    df_calendar = df.copy()
    df_calendar['date'] = df_calendar['Datetime'].dt.date
    daily_avg_pm25 = df_calendar.groupby('date')['PM2.5'].mean().reset_index()
    daily_avg_pm25['date'] = pd.to_datetime(daily_avg_pm25['date'])
    month_data = daily_avg_pm25[(daily_avg_pm25['date'].dt.year == year) & (daily_avg_pm25['date'].dt.month == month)]
    cal = calendar.monthcalendar(year, month)
    
    days_header = t[lang]['days_header_short']
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
                    </div>""", unsafe_allow_html=True)
                else:
                    cols[i].markdown(f"""
                    <div class="calendar-day calendar-day-na">
                        <div class="calendar-day-header">{day}</div>
                    </div>""", unsafe_allow_html=True)

def display_historical_data(df, lang, t):
    st.subheader(t[lang]['historical_expander'])
    today = datetime.now().date()
    default_start = today - pd.DateOffset(days=6)
    
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
            avg_pm, max_pm, min_pm = filtered_df['PM2.5'].mean(), filtered_df['PM2.5'].max(), filtered_df['PM2.5'].min()
            
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric(t[lang]['metric_avg'], f"{avg_pm:.1f} μg/m³")
            mcol2.metric(t[lang]['metric_max'], f"{max_pm:.1f} μg/m³")
            mcol3.metric(t[lang]['metric_min'], f"{min_pm:.1f} μg/m³")
            
            colors_hist = [get_aqi_level(pm, lang, t)[1] for pm in daily_avg_df['Avg PM2.5']]
            if lang == 'th':
                start_date_str = f"{start_date.day} {t['th']['month_names'][start_date.month - 1]} {start_date.year + 543}"
                end_date_str = f"{end_date.day} {t['th']['month_names'][end_date.month - 1]} {end_date.year + 543}"
            else:
                start_date_str, end_date_str = start_date.strftime('%b %d, %Y'), end_date.strftime('%b %d, %Y')
            title_text = f"{t[lang]['daily_avg_chart_title']} ({start_date_str} - {end_date_str})"
            
            fig_hist = go.Figure(go.Bar(
                x=daily_avg_df['Date'], y=daily_avg_df['Avg PM2.5'], name=t[lang]['avg_pm25_unit'],
                marker_color=colors_hist, marker=dict(cornerradius=5)))
            fig_hist.update_layout(
                title_text=title_text, font=dict(family="Sarabun"),
                yaxis_title=t[lang]['avg_pm25_unit'],
                template="plotly_white", plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
