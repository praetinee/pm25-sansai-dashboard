import streamlit as st
import pandas as pd
import datetime
import calendar
import random

# --- 1. การตั้งค่าหน้าเพจและฟอนต์ ---
st.set_page_config(
    page_title="รายงานเฝ้าระวัง PM2.5 อำเภอสันทราย",
    layout="wide",
    initial_sidebar_state="expanded"
)

# เพิ่ม CSS เพื่อเปลี่ยนฟอนต์เป็น Sarabun ให้ครอบคลุมทุกองค์ประกอบ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    
    /* Apply Sarabun font to all text elements in the Streamlit app */
    html, body, [class*="css"], .stApp, p, div, span, h1, h2, h3, h4, h5, h6 {
        font-family: 'Sarabun', sans-serif !important;
    }
    
    /* Custom styling for the main metric */
    .stMetric > div[data-testid="stMetricValue"] {
        font-size: 3rem;
        font-weight: bold;
    }
    .stMetric > div[data-testid="stMetricLabel"] > div {
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. กำหนดเกณฑ์และสีตามมาตรฐาน CCDC ---
def get_color_and_status(pm25_value):
    """
    ตรวจสอบค่า PM2.5 และคืนค่าสีและสถานะ (พร้อม emoji)
    ตามเกณฑ์ของ CCDC (กรมควบคุมโรค)
    """
    if pm25_value <= 25:
        return 'green', '🟢 ดีมาก'
    elif pm25_value <= 37:
        return 'yellow', '🟡 ดี'
    elif pm25_value <= 50:
        return 'orange', '🟠 ปานกลาง'
    elif pm25_value <= 75:
        return 'red', '🔴 เริ่มมีผลกระทบต่อสุขภาพ'
    else:
        return 'purple', '🟣 มีผลกระทบต่อสุขภาพ'

# --- 3. สร้างข้อมูลจำลอง (ในสถานการณ์จริงจะดึงจากแหล่งข้อมูลจริง) ---
def generate_dummy_data():
    """
    สร้างข้อมูลจำลองสำหรับค่า PM2.5 รายชั่วโมงและรายวัน
    เพื่อใช้ในการแสดงผล
    """
    today_date = datetime.date.today()
    today_datetime = datetime.datetime.now()

    # ข้อมูล PM2.5 รายชั่วโมง (จำลอง)
    hourly_data = {
        'timestamp': [today_datetime.replace(hour=i, minute=0, second=0, microsecond=0) for i in range(24)],
        'pm25': [random.randint(15, 80) for _ in range(24)]
    }
    hourly_df = pd.DataFrame(hourly_data)
    hourly_df['color'] = hourly_df['pm25'].apply(lambda x: get_color_and_status(x)[0])

    # ข้อมูล PM2.5 เฉลี่ยรายวัน (จำลอง)
    current_year = today_date.year
    current_month = today_date.month
    num_days = calendar.monthrange(current_year, current_month)[1]
    daily_data = {
        'date': [datetime.date(current_year, current_month, d) for d in range(1, num_days + 1)],
        'pm25_avg': [random.randint(15, 80) for _ in range(num_days)]
    }
    daily_df = pd.DataFrame(daily_data)
    daily_df['color'] = daily_df['pm25_avg'].apply(lambda x: get_color_and_status(x)[0])

    return hourly_df, daily_df

hourly_data, daily_data = generate_dummy_data()

# --- 4. การออกแบบหน้าเพจด้วย Streamlit ---

# หัวข้อและอัปเดตล่าสุด
st.title("รายงานเฝ้าระวัง PM2.5 อำเภอสันทราย")
st.markdown(f"**อัปเดตล่าสุด: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
st.markdown("---")

# ค่า PM2.5 ปัจจุบัน (ใช้ st.markdown และ HTML/CSS แทน st.metric)
current_pm25 = hourly_data['pm25'].iloc[-1]
color, status = get_color_and_status(current_pm25)
st.markdown(f"""
<div style="text-align: left;">
    <div style="font-size: 1.2rem; color: #888;">สถานะ PM2.5 ปัจจุบัน</div>
    <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">{current_pm25} µg/m³</div>
    <div style="color: {color}; font-size: 1.2rem;">{status}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# กราฟแท่ง PM2.5 รายชั่วโมงและปฏิทินรายวัน
col1, col2 = st.columns(2)

with col1:
    st.subheader("ค่า PM2.5 รายชั่วโมง (วันนี้)")
    hourly_data['hour'] = hourly_data['timestamp'].dt.hour
    st.bar_chart(hourly_data.set_index('hour'), y='pm25', color='color')

with col2:
    st.subheader("ค่า PM2.5 เฉลี่ยรายวัน (ทั้งเดือน)")
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    daily_data['day'] = daily_data['date'].dt.day
    
    # สร้าง HTML สำหรับปฏิทินที่แสดงผลได้ถูกต้องใน Streamlit
    html_calendar = "<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; font-family: Sarabun, sans-serif; text-align: center;'>"
    day_headers = ["อา", "จ", "อ", "พ", "พฤ", "ศ", "ส"]
    for header in day_headers:
        html_calendar += f"<div style='font-weight: bold; padding: 10px;'>{header}</div>"

    # คำนวณวันแรกของเดือนให้ถูกต้อง
    first_day_of_month_weekday = daily_data['date'].iloc[0].weekday()
    # weekday() returns 0 for Monday, 6 for Sunday. We need to adjust it for Sunday=0
    first_day_of_month_index = (first_day_of_month_weekday + 1) % 7

    for _ in range(first_day_of_month_index):
        html_calendar += "<div></div>"

    for day in range(1, len(daily_data) + 1):
        color = daily_data[daily_data['day'] == day]['color'].iloc[0]
        pm25_avg = daily_data[daily_data['day'] == day]['pm25_avg'].iloc[0]
        html_calendar += f"""
        <div style='border: 1px solid #ccc; padding: 15px; border-radius: 5px; min-height: 80px; position: relative; background-color:{color};'>
            <div style='font-size: 1.5em; font-weight: bold; position: absolute; top: 5px; left: 5px;'>{day}</div>
            <div style='font-size: 1em; position: absolute; bottom: 5px; right: 5px;'>{pm25_avg}</div>
        </div>
        """
    html_calendar += "</div>"
    st.markdown(html_calendar, unsafe_allow_html=True)


st.markdown("---")

# คำแนะนำการปฏิบัติตัว (ใช้ expander เพื่อให้หน้าเพจดูเรียบร้อย)
with st.expander("คำแนะนำการปฏิบัติตัว 🩺"):
    st.write("สำหรับประชาชนทั่วไป:")
    def get_recommendations_general(pm25_value):
        if pm25_value <= 25:
            return "สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ"
        elif pm25_value <= 37:
            return "สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ"
        elif pm25_value <= 50:
            return "ควรเฝ้าระวังอาการ"
        elif pm25_value <= 75:
            return "ควรงดกิจกรรมกลางแจ้งที่ใช้แรงมาก"
        else:
            return "ควรงดกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกัน"
    st.markdown(f"**{get_recommendations_general(current_pm25)}**")

    st.write("สำหรับกลุ่มเปราะบาง (ผู้สูงอายุ, เด็ก, ผู้มีโรคประจำตัว, หญิงตั้งครรภ์):")
    def get_recommendations_vulnerable(pm25_value):
        if pm25_value <= 50:
            return "ควรเฝ้าระวังอาการ"
        elif pm25_value <= 75:
            return "ควรงดกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกัน"
        else:
            return "ควรงดกิจกรรมกลางแจ้งโดยเด็ดขาด และอยู่ในอาคารที่ปิดมิดชิด"
    st.markdown(f"**{get_recommendations_vulnerable(current_pm25)}**")

st.markdown("---")

# ข้อมูลผู้ป่วย (จำลอง)
st.subheader("เฝ้าระวังผู้ป่วยที่เกี่ยวข้องกับ PM2.5")
st.write("จำนวนผู้ป่วยที่เข้ารับการรักษาในรอบ 7 วันที่ผ่านมา:")
patient_data = {
    'วันที่': [f'วันที่ {i}' for i in range(1, 8)],
    'จำนวนผู้ป่วย': [random.randint(5, 30) for _ in range(7)]
}
patient_df = pd.DataFrame(patient_data)
st.bar_chart(patient_df.set_index('วันที่')['จำนวนผู้ป่วย'])
