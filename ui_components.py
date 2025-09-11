import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
from utils import get_aqi_level

def display_realtime_pm(df):
    """Displays the current PM2.5 value and advice."""
    latest_pm25 = df['PM2.5'][0]
    level, color, emoji, advice = get_aqi_level(latest_pm25)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("ค่า PM2.5 ปัจจุบัน")
        st.markdown(
            f"""
            <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h1 style="color: {'black' if color == '#FFFF00' else 'white'}; font-size: 4rem; margin: 0;">{latest_pm25:.1f}</h1>
                <p style="color: {'black' if color == '#FFFF00' else 'white'}; font-size: 1.5rem; margin: 0;">μg/m³</p>
                <h2 style="color: {'black' if color == '#FFFF00' else 'white'}; margin-top: 10px;">{level} {emoji}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("คำแนะนำในการปฏิบัติตัว")
        st.info(advice)
        with st.expander("ℹ️ ดูเกณฑ์ดัชนีคุณภาพอากาศ"):
            st.markdown("""
                <style>
                    .legend-dot {{ height: 15px; width: 15px; border-radius: 50%; display: inline-block; margin-right: 8px; vertical-align: middle; }}
                    .legend-item {{ font-size: 1.1rem; margin-bottom: 8px; }}
                </style>
                <div class="legend-item"><span class="legend-dot" style="background-color: #0099FF;"></span><b>ดีมาก:</b> 0 - 15.0 μg/m³</div>
                <div class="legend-item"><span class="legend-dot" style="background-color: #00CC00;"></span><b>ดี:</b> 15.1 - 25.0 μg/m³</div>
                <div class="legend-item" style="color: black;"><span class="legend-dot" style="background-color: #FFFF00;"></span><b>ปานกลาง:</b> 25.1 - 37.5 μg/m³</div>
                <div class="legend-item"><span class="legend-dot" style="background-color: #FF9900;"></span><b>เริ่มมีผลกระทบ:</b> 37.6 - 75.0 μg/m³</div>
                <div class="legend-item"><span class="legend-dot" style="background-color: #FF0000;"></span><b>มีผลกระทบ:</b> > 75.0 μg/m³</div>
            """, unsafe_allow_html=True)

def display_24hr_chart(df):
    """Displays the 24-hour PM2.5 trend chart."""
    st.subheader("แนวโน้มค่า PM2.5 ใน 24 ชั่วโมงล่าสุด")

    last_24_hours_data = df[df['Datetime'] >= (df['Datetime'].max() - timedelta(hours=24))]
    last_24_hours_data = last_24_hours_data.sort_values(by="Datetime", ascending=True)

    fig_24hr = go.Figure()
    fig_24hr.add_trace(go.Scatter(x=last_24_hours_data['Datetime'], y=last_24_hours_data['PM2.5'], mode='lines+markers', name='PM2.5', line=dict(color='#1f77b4', width=3), marker=dict(size=5)))
    fig_24hr.add_hrect(y0=0, y1=15, line_width=0, fillcolor="#0099FF", opacity=0.1, annotation_text="ดีมาก", annotation_position="right")
    fig_24hr.add_hrect(y0=15, y1=25, line_width=0, fillcolor="#00CC00", opacity=0.1, annotation_text="ดี", annotation_position="right")
    fig_24hr.add_hrect(y0=25, y1=37.5, line_width=0, fillcolor="#FFFF00", opacity=0.1, annotation_text="ปานกลาง", annotation_position="right")
    fig_24hr.add_hrect(y0=37.5, y1=75, line_width=0, fillcolor="#FF9900", opacity=0.1, annotation_text="เริ่มมีผลกระทบ", annotation_position="right")
    fig_24hr.add_hrect(y0=75, y1=max(100, last_24_hours_data['PM2.5'].max() * 1.1), line_width=0, fillcolor="#FF0000", opacity=0.1, annotation_text="มีผลกระทบ", annotation_position="right")
    fig_24hr.update_layout(xaxis_title="เวลา", yaxis_title="PM2.5 (μg/m³)", plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_24hr, use_container_width=True)

def display_monthly_calendar(df):
    """Displays the monthly PM2.5 calendar heatmap."""
    # This function is kept as a placeholder. The original code for the calendar
    # was incomplete and needs further development to function correctly.
    st.warning("ฟังก์ชันปฏิทินกำลังอยู่ในระหว่างการพัฒนา")
    # Placeholder for the complex calendar logic from the original file
    pass

def display_historical_data(df):
    """Displays the historical data section with a date selector."""
    st.subheader("📊 ดูข้อมูลย้อนหลัง")

    today = date.today()
    default_start = today - timedelta(days=7)
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("วันที่เริ่มต้น", value=default_start, min_value=df['Datetime'].min().date(), max_value=today)
    with col_date2:
        end_date = st.date_input("วันที่สิ้นสุด", value=today, min_value=df['Datetime'].min().date(), max_value=today)

    if start_date > end_date:
        st.error("วันที่เริ่มต้นต้องมาก่อนวันที่สิ้นสุด")
    else:
        mask = (df['Datetime'].dt.date >= start_date) & (df['Datetime'].dt.date <= end_date)
        filtered_df = df.loc[mask].sort_values(by="Datetime", ascending=True)

        if filtered_df.empty:
            st.warning("ไม่พบข้อมูลในช่วงวันที่ที่เลือก")
        else:
            avg_pm = filtered_df['PM2.5'].mean()
            max_pm = filtered_df['PM2.5'].max()
            min_pm = filtered_df['PM2.5'].min()

            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("ค่าเฉลี่ย", f"{avg_pm:.1f} μg/m³")
            mcol2.metric("ค่าสูงสุด", f"{max_pm:.1f} μg/m³")
            mcol3.metric("ค่าต่ำสุด", f"{min_pm:.1f} μg/m³")

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(x=filtered_df['Datetime'], y=filtered_df['PM2.5'], mode='lines', name='PM2.5'))
            fig_hist.update_layout(title=f"ข้อมูล PM2.5 ตั้งแต่ {start_date.strftime('%d/%m/%Y')} ถึง {end_date.strftime('%d/%m/%Y')}",
                                   xaxis_title="วันที่", yaxis_title="PM2.5 (μg/m³)")
            st.plotly_chart(fig_hist, use_container_width=True)

def display_knowledge_tabs():
    """Displays the knowledge base section in tabs."""
    st.subheader("💡 เกร็ดความรู้เกี่ยวกับ PM2.5")

    tab1, tab2, tab3, tab4 = st.tabs(["PM2.5 คืออะไร?", "ความเข้าใจผิด", "DIY ป้องกันฝุ่น", "การเลือกหน้ากาก"])

    with tab1:
        st.markdown("""
        **PM2.5 (Particulate Matter 2.5)** คือฝุ่นละอองขนาดเล็กที่มีเส้นผ่านศูนย์กลางไม่เกิน 2.5 ไมครอน เล็กกว่าเส้นผมของมนุษย์ประมาณ 25 เท่า ทำให้สามารถเดินทางผ่านขนจมูกเข้าสู่ทางเดินหายใจและแทรกซึมเข้าสู่กระแสเลือดได้ง่าย
        - **แหล่งกำเนิด:** เกิดจากการเผาไหม้ทั้งจากธรรมชาติ (ไฟป่า) และกิจกรรมของมนุษย์ (การจราจร, โรงงานอุตสาหกรรม, การเผาในที่โล่ง)
        - **ผลกระทบ:** เป็นอันตรายต่อสุขภาพโดยเฉพาะระบบทางเดินหายใจและหัวใจ อาจทำให้เกิดอาการแสบตา, แสบจมูก, ไอ, และเป็นปัจจัยเสี่ยงของโรคหอบหืด, ภูมิแพ้, และมะเร็งปอด
        """)
    with tab2:
        st.markdown("""
        - **ความเชื่อ:** ฝนตกแล้วอากาศจะดีเสมอ
          - **ความจริง:** ฝนสามารถช่วยชะล้างฝุ่นในอากาศได้จริง แต่หากแหล่งกำเนิดฝุ่นยังมีอยู่ต่อเนื่อง หลังจากฝนหยุดตกไม่นาน ค่าฝุ่นก็สามารถกลับมาสูงได้อีกครั้ง
        - **ความเชื่อ:** อยู่ในบ้านปลอดภัย ไม่ต้องป้องกัน
          - **ความจริง:** ฝุ่น PM2.5 สามารถเล็ดลอดเข้ามาในอาคารได้ การปิดประตูหน้าต่างช่วยลดได้เพียงส่วนหนึ่ง การใช้เครื่องฟอกอากาศที่มีแผ่นกรอง HEPA จะช่วยเพิ่มประสิทธิภาพในการกรองฝุ่นได้ดีที่สุด
        - **ความเชื่อ:** ใส่หน้ากากอนามัยธรรมดาก็พอ
          - **ความจริง:** หน้ากากอนามัยทั่วไปไม่สามารถกรองฝุ่น PM2.5 ได้ดีพอ ควรใช้หน้ากากที่ระบุมาตรฐาน N95 หรือเทียบเท่า ซึ่งออกแบบมาเพื่อกรองอนุภาคขนาดเล็กโดยเฉพาะ
        """)
    with tab3:
        st.markdown("""
        - **เครื่องฟอกอากาศ DIY:** ใช้พัดลมธรรมดาประกบกับแผ่นกรองอากาศ (เช่น HEPA filter) สามารถช่วยลดปริมาณฝุ่นในห้องขนาดเล็กได้ในราคาประหยัด
        - **การซีลประตูหน้าต่าง:** ใช้เทปหรือซีลยางปิดช่องว่างตามขอบประตูและหน้าต่าง เพื่อป้องกันไม่ให้อากาศภายนอกที่มีฝุ่นเล็ดลอดเข้ามาในบ้าน
        - **พัดลมดูดอากาศ:** หากใช้พัดลมดูดอากาศในห้องน้ำหรือห้องครัว ควรเปิดเท่าที่จำเป็น เพราะจะเป็นการดึงอากาศจากภายนอกเข้ามาในบ้าน
        """)
    with tab4:
        st.markdown("""
        - **N95:** เป็นมาตรฐานของสหรัฐอเมริกา สามารถกรองฝุ่นละอองขนาด 0.3 ไมครอนได้ 95%
        - **KN95:** เป็นมาตรฐานของจีน มีประสิทธิภาพใกล้เคียงกับ N95
        - **KF94:** เป็นมาตรฐานของเกาหลีใต้ สามารถกรองฝุ่นได้ 94% มีรูปทรงที่กระชับกับใบหน้า
        - **หน้ากากอนามัย (Surgical Mask):** ไม่สามารถป้องกัน PM2.5 ได้อย่างมีประสิทธิภาพ
        **ข้อควรจำ:** ควรเลือกหน้ากากที่ได้มาตรฐานและสวมใส่ให้กระชับกับใบหน้า
        """)
