import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import calendar
import pandas as pd
from utils import get_aqi_level
from card_generator import generate_report_card

# Updated Minimalist Icons v4
ICON_MASK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="advice-icon"><path d="M20 14.5a5.5 5.5 0 0 0-11 0"/><path d="M4 14.5a5.5 5.5 0 0 1 11 0"/><path d="M2.5 12.5 4 14.5l1.5-2"/><path d="M21.5 12.5 20 14.5l-1.5-2"/><path d="M9 14.5V11a3 3 0 0 1 6 0v3.5"/></svg>"""
ICON_ACTIVITY_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="advice-icon"><path d="M15.5 13.5 19 10l-4-1-1 4.5 3.5 1Z"/><circle cx="13" cy="7" r="1"/><path d="M8.5 15.5 5 19l4 1 1-4.5-2.5-1Z"/><circle cx="11" cy="17" r="1"/></svg>"""
ICON_INDOORS_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="advice-icon"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>"""
ICON_RISK_GROUP_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="risk-icon"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""

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
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .advice-container {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                text-align: center;
                margin-bottom: 20px;
            }
            .advice-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
            }
            .advice-icon {
                margin-bottom: 10px;
                color: var(--text-color);
            }
            .advice-title {
                font-weight: 600;
                font-size: 1.1rem;
                margin-bottom: 5px;
            }
            .advice-body {
                font-size: 0.95rem;
                opacity: 0.9;
                min-height: 50px;
            }
            .risk-advice {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid var(--border-color, #dfe6e9);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                font-size: 1.05rem;
            }
            .risk-icon {
                 display: inline-block;
                 vertical-align: middle;
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
            .aqi-legend-segment { flex-grow: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.4); font-size: 0.9rem; line-height: 1.2; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def display_realtime_pm(df, lang, t, date_str):
    inject_custom_css()
    latest_pm25 = df['PM2.5'][0]
    level, color, _, advice_details = get_aqi_level(latest_pm25, lang, t)

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
        advice_html = f"""
        <div class="card">
            <div class="advice-container">
                <div class="advice-item">
                    {ICON_MASK_SVG}
                    <div class="advice-title">{t[lang]['advice_cat_mask']}</div>
                    <div class="advice-body">{advice_details['mask']}</div>
                </div>
                <div class="advice-item">
                    {ICON_ACTIVITY_SVG}
                    <div class="advice-title">{t[lang]['advice_cat_activity']}</div>
                    <div class="advice-body">{advice_details['activity']}</div>
                </div>
                <div class="advice-item">
                    {ICON_INDOORS_SVG}
                    <div class="advice-title">{t[lang]['advice_cat_indoors']}</div>
                    <div class="advice-body">{advice_details['indoors']}</div>
                </div>
            </div>
            <div class="risk-advice">
                {ICON_RISK_GROUP_SVG}
                <span><b>{t[lang]['advice_cat_risk_group']}:</b> {advice_details['risk_group']}</span>
            </div>
        </div>
        """
        st.markdown(advice_html, unsafe_allow_html=True)

    st.write("") 

    b_col1, b_col2, b_col3 = st.columns([2,2,8]) 
    with b_col1:
        if st.button(f"🔄 {t[lang]['refresh_button']}", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with b_col2:
        report_card_bytes = generate_report_card(latest_pm25, level, color, "", advice_details, date_str, lang, t)
        if report_card_bytes:
            st.download_button(
                label=f"🖼️ {t[lang]['download_button']}",
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
        if st.checkbox(symptom, key=f"symptom_{symptom}"):
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
        index=len(month_options)-1 
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

def display_knowledge_base(lang, t):
    st.subheader(t[lang]['knowledge_header'])
    
    cols = st.columns(4)
    if 'selected_topic' not in st.session_state or st.session_state.selected_topic not in [item['title'] for item in t[lang]['knowledge_content']]:
        st.session_state.selected_topic = t[lang]['knowledge_content'][0]['title']

    for i, item in enumerate(t[lang]['knowledge_content']):
        with cols[i % 4]:
            if st.button(item['title'], key=f"topic_{i}", use_container_width=True):
                st.session_state.selected_topic = item['title']
    
    st.markdown("---")
    
    for item in t[lang]['knowledge_content']:
        if item['title'] == st.session_state.selected_topic:
            st.markdown(item['body'])
            break

