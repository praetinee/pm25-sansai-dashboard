import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
from utils import get_aqi_level

def display_realtime_pm(df):
    """Displays the current PM2.5 value and advice with a modern UI."""
    latest_pm25 = df['PM2.5'][0]
    level, color_gradient, emoji, advice = get_aqi_level(latest_pm25)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("ค่า PM2.5 ปัจจุบัน")
        st.markdown(
            f"""
            <div style="background-image: {color_gradient}; padding: 25px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);">
                <h1 style="font-size: 4.5rem; margin: 0; text-shadow: 2px 2px 4px #000000;">{latest_pm25:.1f}</h1>
                <p style="font-size: 1.5rem; margin: 0;">μg/m³</p>
                <h2 style="margin-top: 15px;">{level} {emoji}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("คำแนะนำในการปฏิบัติตัว")
        st.markdown(f"<div style='padding: 20px; border-radius: 15px; background-color: #f0f2f6; border: 1px solid #dfe6e9;'>{advice}</div>", unsafe_allow_html=True)
        with st.expander("ℹ️ ดูเกณฑ์ดัชนีคุณภาพอากาศ"):
            st.markdown("""
                <style>
                    .legend-box {{ display: flex; align-items: center; font-size: 1.1rem; margin-bottom: 8px; }}
                    .legend-color {{ height: 20px; width: 20px; border-radius: 5px; margin-right: 10px; }}
                </style>
                <div class="legend-box"><div class="legend-color" style="background-image: linear-gradient(to right, #4facfe, #00f2fe);"></div><b>ดีมาก:</b> 0 - 15.0 μg/m³</div>
                <div class="legend-box"><div class="legend-color" style="background-image: linear-gradient(to right, #6a11cb, #2575fc);"></div><b>ดี:</b> 15.1 - 25.0 μg/m³</div>
                <div class="legend-box"><div class="legend-color" style="background-image: linear-gradient(to right, #f7971e, #ffd200);"></div><b>ปานกลาง:</b> 25.1 - 37.5 μg/m³</div>
                <div class="legend-box"><div class="legend-color" style="background-image: linear-gradient(to right, #ff416c, #ff4b2b);"></div><b>เริ่มมีผลกระทบ:</b> 37.6 - 75.0 μg/m³</div>
                <div class="legend-box"><div class="legend-color" style="background-image: linear-gradient(to right, #c31432, #240b36);"></div><b>มีผลกระทบ:</b> > 75.0 μg/m³</div>
            """, unsafe_allow_html=True)

def display_24hr_chart(df):
    """Displays the 24-hour PM2.5 trend chart with a modern look."""
    st.subheader("แนวโน้มค่า PM2.5 ใน 24 ชั่วโมงล่าสุด")
    last_24_hours_data = df[df['Datetime'] >= (df['Datetime'].max() - timedelta(hours=24))].sort_values(by="Datetime", ascending=True)

    fig_24hr = go.Figure()
    fig_24hr.add_trace(go.Scatter(
        x=last_24_hours_data['Datetime'], 
        y=last_24_hours_data['PM2.5'], 
        mode='lines+markers', 
        name='PM2.5', 
        line=dict(color='#2575fc', width=3), 
        marker=dict(size=6, symbol='circle-open')
    ))
    fig_24hr.update_layout(
        xaxis_title="เวลา", 
        yaxis_title="PM2.5 (μg/m³)", 
        plot_bgcolor='rgba(0,0,0,0)', 
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor='#e9e9e9'),
        yaxis=dict(gridcolor='#e9e9e9')
    )
    st.plotly_chart(fig_24hr, use_container_width=True)

def display_monthly_calendar(df):
    """Displays the monthly PM2.5 calendar heatmap."""
    st.warning("ฟังก์ชันปฏิทินกำลังอยู่ในระหว่างการพัฒนา")
    pass

def display_historical_data(df):
    """Displays the historical data section within a collapsible expander with a modern look."""
    with st.expander("📊 ดูข้อมูลย้อนหลัง (คลิกเพื่อเลือกช่วงวัน)"):
        today = date.today()
        default_start = today - timedelta(days=7)
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("วันที่เริ่มต้น", value=default_start, min_value=df['Datetime'].min().date(), max_value=today, key="start_date_hist")
        with col_date2:
            end_date = st.date_input("วันที่สิ้นสุด", value=today, min_value=df['Datetime'].min().date(), max_value=today, key="end_date_hist")

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
                fig_hist.add_trace(go.Scatter(x=filtered_df['Datetime'], y=filtered_df['PM2.5'], mode='lines', name='PM2.5', line=dict(color='#2575fc')))
                fig_hist.update_layout(
                    title=f"ข้อมูล PM2.5 ตั้งแต่ {start_date.strftime('%d/%m/%Y')} ถึง {end_date.strftime('%d/%m/%Y')}",
                    xaxis_title="วันที่", 
                    yaxis_title="PM2.5 (μg/m³)",
                    template="plotly_white"
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

