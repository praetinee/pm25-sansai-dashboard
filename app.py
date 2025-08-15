import streamlit as st
import pandas as pd
import datetime
import calendar

# --- 1. การกำหนดค่าและฟังก์ชันช่วยต่างๆ ---
# เกณฑ์ค่า PM2.5 และสีตามมาตรฐาน CCDC
def get_color_and_status(pm25_value):
    if pm25_value <= 25:
        return 'green', 'ดีมาก'
    elif pm25_value <= 37:
        return 'yellow', 'ดี'
    elif pm25_value <= 50:
        return 'orange', 'ปานกลาง'
    elif pm25_value <= 75:
        return 'red', 'เริ่มมีผลกระทบต่อสุขภาพ'
    else:
        return 'purple', 'มีผลกระทบต่อสุขภาพ'

# คำแนะนำตามค่า PM2.5
def get_recommendations(pm25_value, is_vulnerable):
    if pm25_value <= 25:
        return "อากาศดีมาก สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif pm25_value <= 37:
        return "อากาศดี สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif pm25_value <= 50:
        return "อากาศปานกลาง กลุ่มเปราะบางควรเฝ้าระวังอาการ"
    elif pm25_value <= 75:
        if is_vulnerable:
            return "อากาศเริ่มมีผลกระทบต่อสุขภาพ กลุ่มเปราะบางควรงดกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกัน"
        else:
            return "อากาศเริ่มมีผลกระทบต่อสุขภาพ ควรงดกิจกรรมกลางแจ้งที่ใช้แรงมาก"
    else:
        if is_vulnerable:
            return "อากาศมีผลกระทบต่อสุขภาพ ควรงดกิจกรรมกลางแจ้งโดยเด็ดขาด และอยู่ในอาคารที่ปิดมิดชิด"
        else:
            return "อากาศมีผลกระทบต่อสุขภาพ ควรงดกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกัน"

# --- 2. การจำลองข้อมูล (ในสถานการณ์จริงจะดึงจาก API) ---
def load_and_generate_data():
    # ข้อมูล PM2.5 รายชั่วโมงของวันนี้
    today = datetime.date.today()
    hourly_data = {
        'timestamp': [today + datetime.timedelta(hours=i) for i in range(24)],
        'pm25': [20, 22, 25, 30, 35, 40, 45, 50, 55, 60, 58, 50, 45, 40, 35, 30, 25, 20, 18, 15, 12, 10, 8, 7]
    }
    hourly_df = pd.DataFrame(hourly_data)
    hourly_df['color'] = hourly_df['pm25'].apply(lambda x: get_color_and_status(x)[0])

    # ข้อมูล PM2.5 เฉลี่ยรายวันของเดือนนี้
    current_year = today.year
    current_month = today.month
    num_days = calendar.monthrange(current_year, current_month)[1]
    daily_data = {
        'date': [datetime.date(current_year, current_month, d) for d in range(1, num_days + 1)],
        'pm25_avg': [20, 25, 30, 35, 40, 45, 50, 55, 60, 55, 50, 45, 40, 35, 30, 25, 20, 18, 15, 12, 10, 8, 7, 20, 25, 30, 35, 40, 45, 50]
    }
    daily_df = pd.DataFrame(daily_data)
    daily_df['color'] = daily_df['pm25_avg'].apply(lambda x: get_color_and_status(x)[0])

    return hourly_df, daily_df

hourly_data, daily_data = load_and_generate_data()

# --- 3. การออกแบบหน้าเพจด้วย Streamlit ---
st.set_page_config(
    page_title="รายงานเฝ้าระวัง PM2.5 อำเภอสันทราย",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ส่วนหัวของหน้าเพจ
st.title("รายงานเฝ้าระวัง PM2.5 อำเภอสันทราย")
st.markdown(f"**อัปเดตล่าสุด: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
st.markdown("---")

# ค่า PM2.5 ปัจจุบัน (จำลองจากค่าสุดท้ายในข้อมูลรายชั่วโมง)
current_pm25 = hourly_data['pm25'].iloc[-1]
color, status = get_color_and_status(current_pm25)

st.markdown(f"### ค่า PM2.5 ปัจจุบัน: <span style='color:{color};'>**{current_pm25} µg/m³**</span> (สถานะ: **{status}**)", unsafe_allow_html=True)
st.markdown("---")

# แบ่งหน้าจอออกเป็น 2 คอลัมน์สำหรับกราฟและปฏิทิน
col1, col2 = st.columns(2)

with col1:
    st.subheader("ค่า PM2.5 รายชั่วโมง (วันนี้)")
    # สร้างกราฟแท่ง
    hourly_data['hour'] = hourly_data['timestamp'].dt.hour
    st.bar_chart(hourly_data.set_index('hour')['pm25'], color=hourly_data['color'])

with col2:
    st.subheader("ค่า PM2.5 เฉลี่ยรายวัน (ทั้งเดือน)")
    # สร้างปฏิทินจำลอง
    daily_data['day'] = daily_data['date'].dt.day
    # สร้างตาราง HTML เพื่อให้เหมือนปฏิทิน
    html_calendar = """
    <style>
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
            font-family: sans-serif;
            text-align: center;
        }
        .day-header {
            font-weight: bold;
            padding: 10px;
        }
        .day-box {
            border: 1px solid #ccc;
            padding: 15px;
            border-radius: 5px;
            min-height: 80px;
            position: relative;
        }
        .day-number {
            font-size: 1.5em;
            font-weight: bold;
            position: absolute;
            top: 5px;
            left: 5px;
        }
        .day-value {
            font-size: 1em;
            position: absolute;
            bottom: 5px;
            right: 5px;
        }
    </style>
    <div class="calendar-grid">
        <div class="day-header">อา</div><div class="day-header">จ</div><div class="day-header">อ</div><div class="day-header">พ</div><div class="day-header">พฤ</div><div class="day-header">ศ</div><div class="day-header">ส</div>
    """
    for day in range(1, len(daily_data) + 1):
        color = daily_data[daily_data['day'] == day]['color'].iloc[0]
        pm25_avg = daily_data[daily_data['day'] == day]['pm25_avg'].iloc[0]
        html_calendar += f"""
        <div class="day-box" style="background-color:{color};">
            <div class="day-number">{day}</div>
            <div class="day-value">{pm25_avg}</div>
        </div>
        """
    html_calendar += "</div>"
    st.markdown(html_calendar, unsafe_allow_html=True)


st.markdown("---")

# ส่วนคำแนะนำ
st.subheader("คำแนะนำการปฏิบัติตัว")
st.write(f"สำหรับประชาชนทั่วไป: **{get_recommendations(current_pm25, False)}**")
st.write(f"สำหรับกลุ่มเปราะบาง (ผู้สูงอายุ, เด็ก, ผู้มีโรคประจำตัว, หญิงตั้งครรภ์): **{get_recommendations(current_pm25, True)}**")

st.markdown("---")

# ส่วนข้อมูลผู้ป่วย (จำลอง)
st.subheader("เฝ้าระวังผู้ป่วยที่เกี่ยวข้องกับ PM2.5")
st.write("ข้อมูลจำนวนผู้ป่วยที่เข้ารับการรักษาในรอบ 7 วันที่ผ่านมา:")
patient_data = {
    'วันที่': [f'วันที่ {i}' for i in range(1, 8)],
    'จำนวนผู้ป่วย': [10, 12, 15, 20, 25, 22, 18]
}
patient_df = pd.DataFrame(patient_data)
st.bar_chart(patient_df.set_index('วันที่')['จำนวนผู้ป่วย'])

st.markdown("---")
