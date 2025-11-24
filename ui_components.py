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

            /* --- Modern Layout Containers --- */
            .main-container {
                max-width: 1000px; /* Increased width for 2-column layout */
                margin: 0 auto;
                padding: 10px;
            }

            /* --- Left Side: Status Card --- */
            .status-card {
                border-radius: 2rem;
                padding: 2.5rem 1.5rem;
                text-align: center;
                color: white;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                position: relative;
                overflow: hidden;
                height: 100%; /* Full height to match right side */
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 420px; /* Increased min-height to match double cards */
            }
            
            .date-pill {
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                padding: 6px 16px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 500;
                margin-bottom: 2rem;
            }

            /* --- Gauge Area --- */
            .gauge-container {
                position: relative;
                width: 200px;
                height: 200px;
                margin: 0 auto;
            }
            .gauge-svg {
                width: 100%;
                height: 100%;
                transform: rotate(-90deg);
            }
            .gauge-track {
                fill: none;
                stroke: rgba(255,255,255,0.2);
                stroke-width: 15;
            }
            .gauge-fill {
                fill: none;
                stroke: white;
                stroke-width: 15;
                stroke-linecap: round;
                transition: stroke-dashoffset 1s ease-out;
            }
            .gauge-content {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                color: white;
            }
            .gauge-number {
                font-size: 4.5rem;
                font-weight: 700;
                line-height: 1;
                letter-spacing: -2px;
            }
            .gauge-unit {
                font-size: 1rem;
                font-weight: 500;
                opacity: 0.9;
            }

            /* --- Right Side: Advice Card --- */
            .advice-section-card {
                background: var(--secondary-background-color);
                border-radius: 1.5rem;
                padding: 1.25rem;
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1rem;
                border: 2px solid transparent; /* Dynamic border color inline */
                transition: transform 0.2s;
            }
            .advice-section-card:hover {
                transform: translateX(5px);
            }
            .advice-icon-wrapper {
                min-width: 48px;
                height: 48px;
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.2rem;
            }
            .advice-text-content h4 {
                margin: 0 0 4px 0;
                font-size: 1rem;
                font-weight: 700;
            }
            .advice-text-content p {
                margin: 0;
                font-size: 0.9rem;
                opacity: 0.8;
                line-height: 1.4;
            }

            /* --- Right Side: Action Grid --- */
            .action-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
            }
            .action-item {
                background: transparent;
                border: 2px solid; /* Color set inline */
                border-radius: 1.2rem;
                padding: 1rem 0.5rem;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                transition: transform 0.2s;
                min-height: 110px;
            }
            .action-item:hover {
                transform: translateY(-3px);
            }
            .action-icon-svg {
                margin-bottom: 8px;
            }
            .action-label {
                font-size: 0.65rem;
                font-weight: 600;
                opacity: 0.7;
                margin-bottom: 4px;
            }
            .action-val {
                font-size: 0.85rem;
                font-weight: 700;
            }

            /* --- Calendar --- */
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
        </style>
    """, unsafe_allow_html=True)

def display_realtime_pm(df, lang, t, date_str):
    latest_pm25 = df['PM2.5'][0]
    level_text, color, emoji, advice = get_aqi_level(latest_pm25, lang, t)
    advice_details = advice['details']
    
    # --- Color & Theme Logic ---
    if latest_pm25 <= 15: # Excellent (Teal/Green)
        bg_color = "#10b981" # Emerald 500
        accent_color = "#10b981"
    elif latest_pm25 <= 25: # Good (Green)
        bg_color = "#10b981" 
        accent_color = "#10b981"
    elif latest_pm25 <= 37.5: # Moderate (Yellow)
        bg_color = "#fbbf24" # Amber 400
        accent_color = "#fbbf24"
    elif latest_pm25 <= 75: # Unhealthy (Orange)
        bg_color = "#f97316" # Orange 500
        accent_color = "#f97316"
    else: # Hazardous (Red)
        bg_color = "#ef4444" # Red 500
        accent_color = "#ef4444"

    # Gauge Calculation
    percent = min((latest_pm25 / 120) * 100, 100)
    radius = 80
    circumference = 2 * math.pi * radius
    stroke_dashoffset = circumference - (percent / 100) * circumference

    # --- Main Layout Container ---
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Create 2 Columns: Left (40%) and Right (60%)
    col_left, col_right = st.columns([4, 6], gap="large")

    # --- LEFT COLUMN: PM2.5 Value & Gauge ---
    with col_left:
        st.markdown(f"""
        <div class="status-card" style="background-color: {bg_color};">
            <div class="date-pill">{date_str}</div>
            <div class="gauge-container">
                <svg class="gauge-svg" viewBox="0 0 200 200">
                    <circle cx="100" cy="100" r="{radius}" class="gauge-track"></circle>
                    <circle cx="100" cy="100" r="{radius}" class="gauge-fill" 
                        style="stroke-dasharray: {circumference}; stroke-dashoffset: {stroke_dashoffset};"></circle>
                </svg>
                <div class="gauge-content">
                    <div class="gauge-number">{latest_pm25:.0f}</div>
                    <div class="gauge-unit">μg/m³</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- RIGHT COLUMN: Advice & Actions ---
    with col_right:
        # Define Content
        title_gen = t[lang]['general_public']
        desc_gen = advice['summary']
        icon_gen = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>"""

        title_risk = t[lang]['risk_group']
        desc_risk = advice_details['risk_group']
        icon_risk = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 1 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 1 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>"""

        act_mask = advice_details['mask']
        act_activity = advice_details['activity']
        act_home = advice_details['indoors']

        # Icons
        icon_mask = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>"""
        icon_activity_s = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>"""
        icon_home_s = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>"""

        # 3. Render Two Advice Cards Stacked + Action Grid
        st.markdown(f"""
        <div class="main-container">
            <!-- General Public Card -->
            <div class="advice-section-card" style="border-left: 4px solid {accent_color};">
                <div class="advice-icon-wrapper" style="background-color: {accent_color};">
                    {icon_gen}
                </div>
                <div class="advice-text-content">
                    <h4>{title_gen}</h4>
                    <p>{desc_gen}</p>
                </div>
            </div>

            <!-- Risk Group Card -->
            <div class="advice-section-card" style="border-left: 4px solid {accent_color};">
                <div class="advice-icon-wrapper" style="background-color: {accent_color};">
                    {icon_risk}
                </div>
                <div class="advice-text-content">
                    <h4>{title_risk}</h4>
                    <p>{desc_risk}</p>
                </div>
            </div>

            <!-- Action Grid Header -->
            <div style="font-size: 0.85rem; font-weight: 700; margin-bottom: 12px; opacity: 0.7; margin-top: 1.5rem;">{t[lang]['advice_header']}</div>
            
            <!-- Action Grid -->
            <div class="action-grid">
                <div class="action-item" style="border-color: {accent_color}; color: {accent_color};">
                    <div class="action-icon-svg">{icon_mask}</div>
                    <div class="action-label">{t[lang]['advice_cat_mask']}</div>
                    <div class="action-val">{act_mask}</div>
                </div>
                <div class="action-item" style="border-color: {accent_color}; color: {accent_color};">
                    <div class="action-icon-svg">{icon_activity_s}</div>
                    <div class="action-label">{t[lang]['advice_cat_activity']}</div>
                    <div class="action-val">{act_activity}</div>
                </div>
                <div class="action-item" style="border-color: {accent_color}; color: {accent_color};">
                    <div class="action-icon-svg">{icon_home_s}</div>
                    <div class="action-label">{t[lang]['advice_cat_indoors']}</div>
                    <div class="action-val">{act_home}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End Main Container
    st.write("") # Spacer

    # Footer Actions
    b_col1, b_col2 = st.columns([1, 1])
    with b_col1:
        if st.button(f"🔄 {t[lang]['refresh_button']}", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with b_col2:
        from card_generator import generate_report_card
        report_card_bytes = generate_report_card(latest_pm25, level_text, color, emoji, advice_details, date_str, lang, t)
        if report_card_bytes:
            st.download_button(
                label=f"🖼️ {t[lang]['download_button']}",
                data=report_card_bytes,
                file_name=f"pm25_report_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                mime="image/png",
                use_container_width=True)

# --- Re-export other functions ---
def display_external_assessment(lang, t):
    st.subheader(t[lang]['external_assessment_title'])
    st.markdown(f"""
    <style>
        .assessment-card {{
            background-color: #F0F8FF;
            border-left: 6px solid #1E90FF;
            padding: 24px;
            border-radius: 10px;
            margin: 20px 0px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        .assessment-card p {{ font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px; }}
        a.assessment-button {{
            display: inline-block; width: 100%; background-color: #1E90FF; color: white; padding: 16px;
            border-radius: 8px; text-align: center; font-weight: 600; font-size: 1.1rem; text-decoration: none;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }}
        a.assessment-button:hover {{ background-color: #1C86EE; transform: translateY(-2px); }}
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
    def format_year(y): return str(y + 543) if lang == 'th' else str(y)
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
                    cols[i].markdown(f"<div class='calendar-day' style='border-bottom-color: {color};'><div class='calendar-day-header'>{day}</div><div class='calendar-day-value'>{pm_value:.1f}</div></div>", unsafe_allow_html=True)
                else:
                    cols[i].markdown(f"<div class='calendar-day calendar-day-na'><div class='calendar-day-header'>{day}</div></div>", unsafe_allow_html=True)

def display_historical_data(df, lang, t):
    st.subheader(t[lang]['historical_expander'])
    today = datetime.now().date()
    default_start = today - pd.DateOffset(days=6)
    col_date1, col_date2 = st.columns(2)
    with col_date1: start_date = st.date_input(t[lang]['start_date'], value=default_start, min_value=df['Datetime'].min().date(), max_value=today, key="start_date_hist")
    with col_date2: end_date = st.date_input(t[lang]['end_date'], value=today, min_value=df['Datetime'].min().date(), max_value=today, key="end_date_hist")
    if start_date > end_date: st.error(t[lang]['date_error'])
    else:
        mask = (df['Datetime'].dt.date >= start_date) & (df['Datetime'].dt.date <= end_date)
        filtered_df = df.loc[mask]
        if filtered_df.empty: st.warning(t[lang]['no_data_in_range'])
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
            else: start_date_str, end_date_str = start_date.strftime('%b %d, %Y'), end_date.strftime('%b %d, %Y')
            title_text = f"{t[lang]['daily_avg_chart_title']} ({start_date_str} - {end_date_str})"
            fig_hist = go.Figure(go.Bar(x=daily_avg_df['Date'], y=daily_avg_df['Avg PM2.5'], name=t[lang]['avg_pm25_unit'], marker_color=colors_hist, marker=dict(cornerradius=5)))
            fig_hist.update_layout(title_text=title_text, font=dict(family="Sarabun"), yaxis_title=t[lang]['avg_pm25_unit'], template="plotly_white", plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
