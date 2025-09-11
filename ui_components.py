import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
import pandas as pd
from utils import get_aqi_level

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

def display_realtime_pm(df, lang, t):
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
        font=dict(family="Sarabun"),
        xaxis_title=None, 
        yaxis_title=t[lang]['pm25_unit'], 
        plot_bgcolor='rgba(0,0,0,0)', 
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor='var(--border-color, #e9e9e9)', showticklabels=True, tickformat='%H:%M', tickangle=-45),
        yaxis=dict(gridcolor='var(--border-color, #e9e9e9)'),
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
    with st.expander(t[lang]['historical_expander']):
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
                    font=dict(family="Sarabun"),
                    title=title_text,
                    xaxis_title="วันที่" if lang == 'th' else "Date", 
                    yaxis_title=t[lang]['avg_pm25_unit'],
                    template="plotly_white",
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(fig_hist, use_container_width=True)

def display_knowledge_tabs(lang, t):
    st.subheader(t[lang]['knowledge_header'])

    tabs = st.tabs(t[lang]['tabs'])
    
    with tabs[0]:
        st.markdown("""
        **PM2.5 (Particulate Matter 2.5)** คือฝุ่นละอองขนาดเล็กที่มีเส้นผ่านศูนย์กลางไม่เกิน 2.5 ไมครอน ซึ่งเล็กกว่าเส้นผมของมนุษย์ประมาณ 25 เท่า ทำให้สามารถเข้าสู่ทางเดินหายใจและกระแสเลือดได้ง่าย
        
        - 🔥 **แหล่งกำเนิด:** เกิดจากการเผาไหม้ เช่น การจราจร, โรงงาน, และการเผาในที่โล่ง
        - ❤️ **ผลกระทบ:** เป็นอันตรายต่อระบบทางเดินหายใจและหัวใจ อาจก่อให้เกิดการระคายเคืองและเป็นปัจจัยเสี่ยงของโรคร้ายแรง
        """ if lang == 'th' else """
        **PM2.5 (Particulate Matter 2.5)** refers to fine inhalable particles, with diameters that are generally 2.5 micrometers and smaller. That's about 25 times smaller than a human hair.
        
        - 🔥 **Sources:** Combustion from traffic, industrial factories, and open burning.
        - ❤️ **Health Effects:** Harmful to the respiratory and cardiovascular systems, causing irritation and increasing the risk of serious diseases.
        """)
    with tabs[1]:
        st.markdown("""
        - ❌ **ความเชื่อ:** ฝนตกแล้วอากาศจะดีเสมอ
          - ✅ **ความจริง:** ฝนช่วยชะล้างฝุ่นได้ แต่หากแหล่งกำเนิดยังอยู่ ค่าฝุ่นก็สามารถกลับมาสูงได้อีก
        - ❌ **ความเชื่อ:** อยู่ในบ้านปลอดภัยเสมอ
          - ✅ **ความจริง:** ฝุ่น PM2.5 เล็ดลอดเข้ามาได้ ควรใช้เครื่องฟอกอากาศเพื่อประสิทธิภาพสูงสุด
        - ❌ **ความเชื่อ:** ใส่หน้ากากอนามัยก็พอ
          - ✅ **ความจริง:** หน้ากากอนามัยกัน PM2.5 ได้ไม่ดีพอ ควรใช้หน้ากาก N95 หรือเทียบเท่า
        """ if lang == 'th' else """
        - ❌ **Myth:** Rain always clears the air.
          - ✅ **Fact:** Rain can wash away dust, but if the source of pollution remains, PM2.5 levels can rise again quickly.
        - ❌ **Myth:** It's always safe indoors.
          - ✅ **Fact:** PM2.5 can seep into buildings. An air purifier with a HEPA filter is recommended for best results.
        - ❌ **Myth:** A simple surgical mask is enough.
          - ✅ **Fact:** Surgical masks are not effective against PM2.5. An N95-rated mask or equivalent is necessary.
        """)
    with tabs[2]:
        st.markdown("""
        - **🌬️ เครื่องฟอกอากาศ DIY:** ใช้พัดลมประกบกับแผ่นกรอง HEPA เป็นวิธีที่ประหยัดและได้ผลดีในห้องขนาดเล็ก
        - **🚪 การซีลประตูหน้าต่าง:** ใช้ซีลยางปิดช่องว่างตามขอบประตูหน้าต่างเพื่อป้องกันฝุ่นเข้าบ้าน
        - **💨 พัดลมดูดอากาศ:** เปิดเท่าที่จำเป็น เพราะเป็นการดึงอากาศภายนอกเข้ามา
        """ if lang == 'th' else """
        - **🌬️ DIY Air Purifier:** Attaching a HEPA filter to a standard box fan is a cost-effective way to reduce dust in a small room.
        - **🚪 Sealing Windows & Doors:** Use weatherstripping to seal gaps and prevent outside air from entering.
        - **💨 Exhaust Fans:** Use kitchen or bathroom exhaust fans only when necessary, as they pull outside air into your home.
        """)
    with tabs[3]:
        st.markdown("""
        - **N95:** US standard, filters 95% of 0.3-micron particles (Best option).
        - **KN95:** Chinese standard, similar performance to N95.
        - **KF94:** South Korean standard, filters 94%, offers a comfortable fit.
        - **Surgical Mask:** Not effective for protecting against PM2.5.
        
        > **สิ่งสำคัญ:** คือการเลือกหน้ากากที่ได้มาตรฐานและสวมให้กระชับกับใบหน้า
        """ if lang == 'th' else """
        - **N95:** US standard, filters 95% of 0.3-micron particles (Best option).
        - **KN95:** Chinese standard, similar performance to N95.
        - **KF94:** South Korean standard, filters 94%, offers a comfortable fit.
        - **Surgical Mask:** Not effective for protecting against PM2.5.
        
        > **Key takeaway:** Choose a certified mask and ensure it fits your face snugly for maximum effectiveness.
        """)

