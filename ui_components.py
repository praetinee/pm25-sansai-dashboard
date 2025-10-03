import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import calendar
import pandas as pd
from utils import get_aqi_level

def inject_custom_css():
    """Injects custom CSS to make the app responsive and theme-aware."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
            
            /* Apply Sarabun font to all elements within the Streamlit app */
            html, body, [class*="st-"], .stApp, .stApp * {
                font-family: 'Sarabun', sans-serif !important;
            }

            .card {
                padding: 20px;
                border-radius: 15px;
                background-color: var(--secondary-background-color);
                border: 1px solid var(--border-color, #dfe6e9);
                height: 100%;
            }
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
                border-bottom: 5px solid transparent;
            }
            .calendar-day:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 12px rgba(0,0,0,0.1);
            }
            .calendar-day-header { align-self: flex-start; font-size: 0.9rem; font-weight: 500; opacity: 0.8; }
            .calendar-day-value { font-size: 1.5rem; font-weight: 700; line-height: 1; }
            .calendar-day-na { background-color: var(--secondary-background-color); color: var(--text-color); opacity: 0.5; box-shadow: none; }
            .aqi-legend-bar { display: flex; height: 50px; width: 100%; border-radius: 10px; overflow: hidden; margin-top: 10px; }
            .aqi-legend-segment {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 500;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
                font-size: 0.9rem;
                line-height: 1.2;
                text-align: center;
            }
            .advice-container {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                text-align: center;
            }
            .advice-item {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .advice-icon svg {
                width: 48px;
                height: 48px;
                margin-bottom: 8px;
            }
            .advice-title {
                font-weight: 600;
                margin-bottom: 4px;
            }
            .advice-text {
                font-size: 0.9rem;
            }
            .risk-group-advice {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
            }

            /* Styles for Infographic Cards in Quiz */
            .infographic-card {
                background-color: var(--secondary-background-color);
                border-left: 5px solid #1e40af;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                margin-top: 1rem;
            }
            .infographic-card h4 {
                 color: #1e40af;
                 margin-bottom: 0.5rem;
            }
            .infographic-card ul {
                list-style-type: none;
                padding-left: 0;
                margin-bottom: 0;
            }
            .infographic-card li {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 0.5rem;
            }
            .infographic-card .icon {
                font-size: 1.2rem;
            }
            
            /* --- NEW: Modern Underline Tab Style --- */
            div[role="radiogroup"] {
                display: flex;
                flex-direction: row;
                border-bottom: 1px solid var(--border-color, #dfe6e9);
                margin-bottom: 1.5rem;
                gap: 8px; /* Space between tabs */
                width: 100%;
            }
            div[role="radiogroup"] label input[type="radio"] {
                display: none; /* Hide the actual radio button */
            }
            div[role="radiogroup"] label {
                cursor: pointer;
            }

            /* The visible part of the tab */
            div[role="radiogroup"] label > div {
                padding: 12px 16px; /* Adjust padding */
                transition: border-color 0.2s, color 0.2s;
                color: var(--text-color);
                opacity: 0.7;
                font-weight: 500;
                border-bottom: 3px solid transparent; /* Prepare space for the active indicator */
                margin-bottom: -1px; /* Align with the main border */
            }

            /* Hover style for inactive tabs */
            div[role="radiogroup"] label:hover > div {
                opacity: 1.0;
                border-bottom: 3px solid var(--border-color, #dfe6e9);
            }

            /* Active tab style */
            div[role="radiogroup"] label input[type="radio"]:checked + div {
                color: var(--primary-color, #1e40af);
                border-bottom: 3px solid var(--primary-color, #1e40af); /* Active indicator line */
                opacity: 1.0;
                font-weight: 700;
            }
        </style>
    """, unsafe_allow_html=True)

def display_realtime_pm(df, lang, t, date_str):
    # inject_custom_css() is now called globally in app.py
    latest_pm25 = df['PM2.5'][0]
    level, color, emoji, advice = get_aqi_level(latest_pm25, lang, t)
    advice_details = advice['details'] # Get structured advice

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(t[lang]['current_pm25'])
        st.markdown(f"""
            <div style="background-color: {color}; padding: 25px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); height: 100%;">
                <h1 style="font-family: 'Sarabun', sans-serif; font-size: 4.5rem; margin: 0; text-shadow: 2px 2px 4px #000000;">{latest_pm25:.1f}</h1>
                <p style="font-family: 'Sarabun', sans-serif; font-size: 1.5rem; margin: 0;">μg/m³</p>
                <h2 style="font-family: 'Sarabun', sans-serif; margin-top: 15px;">{level}</h2>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.subheader(t[lang]['aqi_guideline_header'])
        st.markdown(f"""
            <div class="aqi-legend-bar">
                <div class="aqi-legend-segment" style="background-color: #0099FF; color: white;">{t[lang]['aqi_level_1']}<br>0-15</div>
                <div class="aqi-legend-segment" style="background-color: #2ECC71; color: white;">{t[lang]['aqi_level_2']}<br>15-25</div>
                <div class="aqi-legend-segment" style="background-color: #F1C40F; color: black;">{t[lang]['aqi_level_3']}<br>25-37.5</div>
                <div class="aqi-legend-segment" style="background-color: #E67E22; color: white;">{t[lang]['aqi_level_4_short']}<br>37.5-75</div>
                <div class="aqi-legend-segment" style="background-color: #E74C3C; color: white;">{t[lang]['aqi_level_5_short']}<br>>75</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader(t[lang]['advice_header'])
        
        # --- Standardized SVG Icons ---
        mask_svg = """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 9 Q12 4 20 9 Q21 14 20 18 Q12 22 4 18 Q3 14 4 9 Z" />
            <path d="M4 11 Q0 13 4 16" />
            <path d="M20 11 Q24 13 20 16" />
            <path d="M6 11 Q12 9.5 18 11" />
            <path d="M6 14 Q12 12.5 18 14" />
            <path d="M6 17 Q12 15.5 18 17" />
        </svg>
        """
        
        activity_svg = """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="6.75" cy="16.5" r="3" />
            <circle cx="17.25" cy="16.5" r="3" />
            <path d="M6.75 16.5 L11.25 12 L15 16.5 Z" />
            <path d="M11.25 12 L11.25 9" />
            <path d="M10.5 9 L12.75 9" />
            <path d="M15 16.5 L16.5 11.25 L19.5 10.5" />
        </svg>
        """
        indoors_svg = """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
        """
        
        st.markdown(f"""
        <div class="card">
            <div class="advice-container">
                <div class="advice-item">
                    <div class="advice-icon">{mask_svg}</div>
                    <div class="advice-title">{t[lang]['advice_cat_mask']}</div>
                    <div class="advice-text">{advice_details['mask']}</div>
                </div>
                <div class="advice-item">
                    <div class="advice-icon">{activity_svg}</div>
                    <div class="advice-title">{t[lang]['advice_cat_activity']}</div>
                    <div class="advice-text">{advice_details['activity']}</div>
                </div>
                <div class="advice-item">
                    <div class="advice-icon">{indoors_svg}</div>
                    <div class="advice-title">{t[lang]['advice_cat_indoors']}</div>
                    <div class="advice-text">{advice_details['indoors']}</div>
                </div>
            </div>
            <div class="risk-group-advice">
                <strong>{t[lang]['risk_group']}:</strong> {advice_details['risk_group']}
            </div>
        </div>
        """, unsafe_allow_html=True)


    st.write("") # Add a small space

    # --- Action Buttons ---
    b_col1, b_col2, b_col3 = st.columns([2,2,8]) # Adjust column ratios
    with b_col1:
        if st.button(f"🔄 {t[lang]['refresh_button']}", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with b_col2:
        from card_generator import generate_report_card
        report_card_bytes = generate_report_card(latest_pm25, level, color, "", advice_details, date_str, lang, t)
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
    
    unique_months = df['Datetime'].dt.to_period('M').unique()
    month_options = sorted([period for period in unique_months], reverse=False)
    
    def format_month(period):
        if lang == 'th':
            return f"{t['th']['month_names'][period.month-1]} {period.year + 543}"
        return period.strftime('%B %Y')

    selected_month_str = st.selectbox(
        t[lang]['date_picker_label'],
        options=month_options,
        format_func=format_month,
        index=len(month_options)-1 # Default to the latest month
    )
    
    year, month = selected_month_str.year, selected_month_str.month
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

