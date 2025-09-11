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

def display_realtime_pm(df):
    """Displays the current PM2.5 value and advice with a modern UI."""
    # Inject CSS on first render of a component
    inject_custom_css()
    
    latest_pm25 = df['PM2.5'][0]
    level, color, emoji, advice = get_aqi_level(latest_pm25)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("ค่า PM2.5 ปัจจุบัน")
        st.markdown(
            f"""
            <div style="background-color: {color}; padding: 25px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); height: 100%;">
                <h1 style="font-size: 4.5rem; margin: 0; text-shadow: 2px 2px 4px #000000;">{latest_pm25:.1f}</h1>
                <p style="font-size: 1.5rem; margin: 0;">μg/m³</p>
                <h2 style="margin-top: 15px;">{level} {emoji}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("คำแนะนำในการปฏิบัติตัว")
        st.markdown(f"<div class='card'>{advice}</div>", unsafe_allow_html=True)
        
    with st.expander("ℹ️ ดูเกณฑ์ดัชนีคุณภาพอากาศ"):
        st.markdown("""
            <div class="legend-box"><div class="legend-color" style="background-color: #0099FF;"></div><b>ดีมาก:</b> 0 - 15.0 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #2ECC71;"></div><b>ดี:</b> 15.1 - 25.0 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #F1C40F;"></div><b>ปานกลาง:</b> 25.1 - 37.5 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #E67E22;"></div><b>เริ่มมีผลกระทบ:</b> 37.6 - 75.0 μg/m³</div>
            <div class="legend-box"><div class="legend-color" style="background-color: #E74C3C;"></div><b>มีผลกระทบ:</b> > 75.0 μg/m³</div>
        """, unsafe_allow_html=True)

def display_24hr_chart(df):
    """Displays the PM2.5 trend for the latest day (00:00-23:59) as a colored bar chart."""
    st.subheader("แนวโน้มค่า PM2.5 รายชั่วโมงของวันนี้")
    
    latest_date = df['Datetime'].max().date()
    day_data = df[df['Datetime'].dt.date == latest_date].sort_values(by="Datetime", ascending=True)

    if day_data.empty:
        st.info("ยังไม่มีข้อมูลสำหรับวันนี้")
        return

    colors = [get_aqi_level(pm)[1] for pm in day_data['PM2.5']]

    fig_24hr = go.Figure()
    fig_24hr.add_trace(go.Bar(
        x=day_data['Datetime'], 
        y=day_data['PM2.5'], 
        name='PM2.5',
        marker_color=colors,
        marker=dict(cornerradius=5), # Rounded corners
        text=day_data['PM2.5'].apply(lambda x: f'{x:.1f}'), # Text on bars
        textposition='outside' # Position of text
    ))
    fig_24hr.update_layout(
        xaxis_title=None, 
        yaxis_title="PM2.5 (μg/m³)", 
        plot_bgcolor='rgba(0,0,0,0)', 
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            gridcolor='var(--border-color, #e9e9e9)', 
            showticklabels=True,
            tickformat='%H:%M', # Format to show HH:MM
            tickangle=-45      # Angle the ticks to prevent overlap
        ),
        yaxis=dict(gridcolor='var(--border-color, #e9e9e9)'),
        showlegend=False,
        uniformtext_minsize=8, 
        uniformtext_mode='hide'
    )
    st.plotly_chart(fig_24hr, use_container_width=True)

def display_monthly_calendar(df):
    """Displays the monthly PM2.5 calendar heatmap with a new modern design."""
    st.subheader("ปฏิทินค่าฝุ่น PM2.5 รายวัน")
    df_calendar = df.copy()
    df_calendar['date'] = df_calendar['Datetime'].dt.date
    daily_avg_pm25 = df_calendar.groupby('date')['PM2.5'].mean().reset_index()
    daily_avg_pm25['date'] = pd.to_datetime(daily_avg_pm25['date'])

    latest_date = daily_avg_pm25['date'].max() if not daily_avg_pm25.empty else datetime.now()
    
    selected_date = st.date_input(
        "เลือกเดือนและปีที่ต้องการดู",
        value=latest_date,
        min_value=df['Datetime'].min().date(),
        max_value=datetime.now().date(),
        key="calendar_date_picker"
    )
    
    year, month = selected_date.year, selected_date.month
    month_data = daily_avg_pm25[
        (daily_avg_pm25['date'].dt.year == year) & (daily_avg_pm25['date'].dt.month == month)
    ]
    
    cal = calendar.monthcalendar(year, month)
    month_name = selected_date.strftime("%B")

    st.markdown(f"#### {month_name} {year}")
    
    days_header = ["จันทร์", "อังคาร", "พุธ", "พฤหัส", "ศุกร์", "เสาร์", "อาทิตย์"]
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
                    _, color, _, _ = get_aqi_level(pm_value)
                    # Use border-bottom as color accent
                    cols[i].markdown(f"""
                    <div class="calendar-day" style="border-bottom-color: {color};">
                        <div class="calendar-day-header">{day}</div>
                        <div class="calendar-day-value">{pm_value:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # N/A day style
                    cols[i].markdown(f"""
                    <div class="calendar-day calendar-day-na">
                        <div class="calendar-day-header">{day}</div>
                    </div>
                    """, unsafe_allow_html=True)


def display_historical_data(df):
    """Displays the historical data section within a collapsible expander with a modern look."""
    with st.expander("📊 ดูข้อมูลย้อนหลัง (คลิกเพื่อเลือกช่วงวัน)"):
        today = date.today()
        default_start = today - timedelta(days=7)
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("วันที่เริ่มต้น", value=default_start, min_value=df['Datetime'].min().date(), max_value=today, key="start_date_hist")
        with col_date2:
            end_date = st.date_input("สิ้นสุด", value=today, min_value=df['Datetime'].min().date(), max_value=today, key="end_date_hist")

        if start_date > end_date:
            st.error("วันที่เริ่มต้นต้องมาก่อนวันที่สิ้นสุด")
        else:
            mask = (df['Datetime'].dt.date >= start_date) & (df['Datetime'].dt.date <= end_date)
            filtered_df = df.loc[mask]

            if filtered_df.empty:
                st.warning("ไม่พบข้อมูลในช่วงวันที่ที่เลือก")
            else:
                # Calculate daily averages for the chart
                daily_avg_df = filtered_df.groupby(filtered_df['Datetime'].dt.date)['PM2.5'].mean().reset_index()
                daily_avg_df.rename(columns={'Datetime': 'Date', 'PM2.5': 'Avg PM2.5'}, inplace=True)

                # Calculate overall metrics for the selected range
                avg_pm = filtered_df['PM2.5'].mean()
                max_pm = filtered_df['PM2.5'].max()
                min_pm = filtered_df['PM2.5'].min()

                mcol1, mcol2, mcol3 = st.columns(3)
                mcol1.metric("ค่าเฉลี่ย", f"{avg_pm:.1f} μg/m³")
                mcol2.metric("ค่าสูงสุด", f"{max_pm:.1f} μg/m³")
                mcol3.metric("ค่าต่ำสุด", f"{min_pm:.1f} μg/m³")

                # Generate colors for each daily average bar
                colors_hist = [get_aqi_level(pm)[1] for pm in daily_avg_df['Avg PM2.5']]

                fig_hist = go.Figure()
                fig_hist.add_trace(go.Bar(
                    x=daily_avg_df['Date'], 
                    y=daily_avg_df['Avg PM2.5'], 
                    name='ค่าเฉลี่ย PM2.5',
                    marker_color=colors_hist,
                    marker=dict(cornerradius=5)
                ))
                fig_hist.update_layout(
                    title=f"ค่าเฉลี่ย PM2.5 รายวัน ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')})",
                    xaxis_title="วันที่", 
                    yaxis_title="ค่าเฉลี่ย PM2.5 (μg/m³)",
                    template="plotly_white",
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(fig_hist, use_container_width=True)

def display_knowledge_tabs():
    """Displays the knowledge base section in tabs with improved formatting."""
    st.subheader("💡 เกร็ดความรู้เกี่ยวกับ PM2.5")

    tab1, tab2, tab3, tab4 = st.tabs(["PM2.5 คืออะไร?", "ความเข้าใจผิด", "DIY ป้องกันฝุ่น", "การเลือกหน้ากาก"])

    with tab1:
        st.markdown("""
        **PM2.5 (Particulate Matter 2.5)** คือฝุ่นละอองขนาดเล็กที่มีเส้นผ่านศูนย์กลางไม่เกิน 2.5 ไมครอน ซึ่งเล็กกว่าเส้นผมของมนุษย์ประมาณ 25 เท่า ทำให้สามารถเข้าสู่ทางเดินหายใจและกระแสเลือดได้ง่าย
        
        - 🔥 **แหล่งกำเนิด:** เกิดจากการเผาไหม้ เช่น การจราจร, โรงงาน, และการเผาในที่โล่ง
        - ❤️ **ผลกระทบ:** เป็นอันตรายต่อระบบทางเดินหายใจและหัวใจ อาจก่อให้เกิดการระคายเคืองและเป็นปัจจัยเสี่ยงของโรคร้ายแรง
        """)
    with tab2:
        st.markdown("""
        - ❌ **ความเชื่อ:** ฝนตกแล้วอากาศจะดีเสมอ
          - ✅ **ความจริง:** ฝนช่วยชะล้างฝุ่นได้ แต่หากแหล่งกำเนิดยังอยู่ ค่าฝุ่นก็สามารถกลับมาสูงได้อีก
        - ❌ **ความเชื่อ:** อยู่ในบ้านปลอดภัยเสมอ
          - ✅ **ความจริง:** ฝุ่น PM2.5 เล็ดลอดเข้ามาได้ ควรใช้เครื่องฟอกอากาศเพื่อประสิทธิภาพสูงสุด
        - ❌ **ความเชื่อ:** ใส่หน้ากากอนามัยก็พอ
          - ✅ **ความจริง:** หน้ากากอนามัยกัน PM2.5 ได้ไม่ดีพอ ควรใช้หน้ากาก N95 หรือเทียบเท่า
        """)
    with tab3:
        st.markdown("""
        - **🌬️ เครื่องฟอกอากาศ DIY:** ใช้พัดลมประกบกับแผ่นกรอง HEPA เป็นวิธีที่ประหยัดและได้ผลดีในห้องขนาดเล็ก
        - **🚪 การซีลประตูหน้าต่าง:** ใช้ซีลยางปิดช่องว่างตามขอบประตูหน้าต่างเพื่อป้องกันฝุ่นเข้าบ้าน
        - **💨 พัดลมดูดอากาศ:** เปิดเท่าที่จำเป็น เพราะเป็นการดึงอากาศภายนอกเข้ามา
        """)
    with tab4:
        st.markdown("""
        - **N95:** มาตรฐานสหรัฐอเมริกา กรองได้ 95% (ดีที่สุด)
        - **KN95:** มาตรฐานจีน ประสิทธิภาพใกล้เคียง N95
        - **KF94:** มาตรฐานเกาหลีใต้ กรองได้ 94% รูปทรงกระชับ
        - **หน้ากากอนามัย:** ไม่สามารถป้องกัน PM2.5 ได้อย่างมีประสิทธิภาพ
        
        > **สิ่งสำคัญ:** คือการเลือกหน้ากากที่ได้มาตรฐานและสวมให้กระชับกับใบหน้า
        """)

