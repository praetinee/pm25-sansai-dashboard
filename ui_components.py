import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
import pandas as pd
from utils import get_aqi_level
from card_generator import generate_report_card

def inject_custom_css():
    """Injects custom CSS to make the app responsive and theme-aware."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
            html, body, [class*="st-"], .stApp, h1, h2, h3, h4, h5, h6 {
                font-family: 'Sarabun', sans-serif !important;
            }
            .st-expander-header p {
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
            .calendar-day-header {
                align-self: flex-start;
                font-size: 0.9rem;
                font-weight: 500;
                opacity: 0.8;
            }
            .calendar-day-value {
                font-size: 1.5rem;
                font-weight: 700;
                line-height: 1;
            }
            .calendar-day-na {
                 background-color: var(--secondary-background-color);
                 color: var(--text-color);
                 opacity: 0.5;
                 box-shadow: none;
            }
            .aqi-legend-bar {
                display: flex;
                height: 50px;
                width: 100%;
                border-radius: 10px;
                overflow: hidden;
                margin-top: 10px;
            }
            .aqi-legend-segment {
                flex-grow: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 500;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
            }
        </style>
    """, unsafe_allow_html=True)

def display_realtime_pm(df, lang, t, date_str):
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
            """, unsafe_allow_html=True)
    with col2:
        st.subheader(t[lang]['advice_header'])
        st.markdown(f"<div class='card'>{advice}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
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

    st.write("")
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
                use_container_width=True)

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
    current_year = datetime.now().year
    if lang == 'th':
        start_str = f"1 {t['th']['month_names'][0]} {current_year + 543}"
        end_str = f"31 {t['th']['month_names'][11]} {current_year + 543}"
        date_range = f"{start_str} - {end_str}"
    else:
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)
        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    st.subheader(t[lang]['health_impact_title'].format(date_range=date_range))
    df_current_year = df[df['Datetime'].dt.year == current_year]
    if df_current_year.empty:
        st.info("ไม่มีข้อมูลสำหรับปีนี้" if lang == 'th' else "No data available for the current year.")
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
    fig_24hr = go.Figure()
    fig_24hr.add_trace(go.Bar(
        x=day_data['Datetime'], y=day_data['PM2.5'], name='PM2.5',
        marker_color=colors, marker=dict(cornerradius=5),
        text=day_data['PM2.5'].apply(lambda x: f'{x:.1f}'), textposition='outside'))
    fig_24hr.update_layout(
        font=dict(family="Sarabun, sans-serif"),
        title_font=dict(family="Sarabun, sans-serif"),
        xaxis_title=None, y_axis_title=t[lang]['pm25_unit'],
        plot_bgcolor='rgba(0,0,0,0)', template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor='var(--border-color, #e9e9e9)', showticklabels=True, tickformat='%H:%M', tickangle=-45, title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
        yaxis=dict(gridcolor='var(--border-color, #e9e9e9)', title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
        showlegend=False, uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig_24hr, use_container_width=True)

def display_monthly_calendar(df, lang, t):
    st.subheader(t[lang]['monthly_calendar_header'])
    
    unique_months = df['Datetime'].dt.to_period('M').unique()
    month_options = sorted([period.strftime('%B %Y') if lang == 'en' else f"{t['th']['month_names'][period.month-1]} {period.year + 543}" for period in unique_months], reverse=True)
    selected_month_str = st.selectbox(t[lang]['date_picker_label'], options=month_options)

    if lang == 'th':
        month_name, year_str = selected_month_str.split()
        month = t['th']['month_names'].index(month_name) + 1
        year = int(year_str) - 543
    else:
        dt_object = datetime.strptime(selected_month_str, '%B %Y')
        year, month = dt_object.year, dt_object.month

    df_calendar = df.copy()
    df_calendar['date'] = df_calendar['Datetime'].dt.date
    daily_avg_pm25 = df_calendar.groupby('date')['PM2.5'].mean().reset_index()
    daily_avg_pm25['date'] = pd.to_datetime(daily_avg_pm25['date'])

    month_data = daily_avg_pm25[(daily_avg_pm25['date'].dt.year == year) & (daily_avg_pm25['date'].dt.month == month)]
    cal = calendar.monthcalendar(year, month)
    
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
                    </div>""", unsafe_allow_html=True)
                else:
                    cols[i].markdown(f"""
                    <div class="calendar-day calendar-day-na">
                        <div class="calendar-day-header">{day}</div>
                    </div>""", unsafe_allow_html=True)

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
                x=daily_avg_df['Date'], y=daily_avg_df['Avg PM2.5'], name=t[lang]['avg_pm25_unit'],
                marker_color=colors_hist, marker=dict(cornerradius=5)))
            fig_hist.update_layout(
                title_text=title_text, font=dict(family="Sarabun, sans-serif"),
                title_font=dict(family="Sarabun, sans-serif"),
                xaxis_title="วันที่" if lang == 'th' else "Date", 
                yaxis_title=t[lang]['avg_pm25_unit'],
                xaxis=dict(title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
                yaxis=dict(title_font=dict(family="Sarabun, sans-serif"), tickfont=dict(family="Sarabun, sans-serif")),
                template="plotly_white", plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)

def display_knowledge_base(lang, t):
    st.subheader(t[lang]['knowledge_header'])
    content = t[lang]['knowledge_content']
    for item in content:
        with st.expander(item['title']):
            st.markdown(item['body'])

