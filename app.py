import streamlit as st
import pandas as pd
import datetime
import calendar
import random
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
    html, body, [class*="css"], .stApp, p, div, span, h1, h2, h3, h4, h5, h6, label {
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
    /* Hide Streamlit's default menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 2. กำหนดเกณฑ์และสีตามมาตรฐาน CCDC และคำแนะนำ ---
def get_color_and_status(pm25_value):
    """
    ตรวจสอบค่า PM2.5 และคืนค่าสีและสถานะ (พร้อม emoji)
    ตามเกณฑ์ของ CCDC (กรมควบคุมโรค)
    """
    if pm25_value <= 25:
        return 'green', '#5CB85C', '🟢 ดีมาก'
    elif pm25_value <= 37:
        return 'yellow', '#F0AD4E', '🟡 ดี'
    elif pm25_value <= 50:
        return 'orange', '#F89825', '🟠 ปานกลาง'
    elif pm25_value <= 75:
        return 'red', '#D9534F', '🔴 เริ่มมีผลกระทบต่อสุขภาพ'
    else:
        return 'purple', '#8A2BE2', '🟣 มีผลกระทบต่อสุขภาพ'

def get_recommendations_general(pm25_value):
    """
    คืนค่าคำแนะนำสำหรับประชาชนทั่วไปตามค่า PM2.5
    """
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

def get_recommendations_vulnerable(pm25_value):
    """
    คืนค่าคำแนะนำสำหรับกลุ่มเปราะบางตามค่า PM2.5
    """
    if pm25_value <= 50:
        return "ควรเฝ้าระวังอาการ"
    elif pm25_value <= 75:
        return "ควรงดกิจกรรมกลางแจ้ง และสวมหน้ากากป้องกัน"
    else:
        return "ควรงดกิจกรรมกลางแจ้งโดยเด็ดขาด และอยู่ในอาคารที่ปิดมิดชิด"


# --- 3. ดึงข้อมูลจาก Google Sheets ---
# เพื่อให้โค้ดนี้ทำงานได้ คุณต้องสร้างไฟล์ `credentials.json`
# และแชร์ Google Sheet กับอีเมลของ service account ในไฟล์นั้น
def fetch_data_from_google_sheets():
    """
    เชื่อมต่อและดึงข้อมูล PM2.5 จาก Google Sheets
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # เปิด Google Sheet ด้วย URL หรือชื่อไฟล์
    # URL: https://docs.google.com/spreadsheets/d/1-Une9oA0-ln6ApbhwaXFNpkniAvX7g1K9pNR800MJwQ/edit?gid=1935007940#gid=1935007940
    sheet_id = "1-Une9oA0-ln6ApbhwaXFNpkniAvX7g1K9pNR800MJwQ"
    sheet = client.open_by_key(sheet_id).worksheet("PM2.5 Log")

    # ดึงข้อมูลทั้งหมดจากชีต
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # จัดการข้อมูล: แปลงวันที่และค่า PM2.5 เป็นประเภทที่เหมาะสม
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    df['pm25'] = pd.to_numeric(df['pm25'], errors='coerce')
    df.dropna(subset=['pm25'], inplace=True)
    
    # กรองข้อมูลเฉพาะวันนี้
    today_date = datetime.date.today()
    hourly_df = df[df['timestamp'].dt.date == today_date].copy()
    hourly_df['status_color'] = hourly_df['pm25'].apply(lambda x: get_color_and_status(x)[1])
    
    # คำนวณค่าเฉลี่ยรายวัน
    daily_df = df.set_index('timestamp').resample('D').mean().reset_index()
    daily_df['status_color'] = daily_df['pm25'].apply(lambda x: get_color_and_status(x)[1])
    daily_df.rename(columns={'timestamp': 'date', 'pm25': 'pm25_avg'}, inplace=True)

    return hourly_df, daily_df

# ใช้ Streamlit cache เพื่อไม่ให้ต้องดึงข้อมูลใหม่ทุกครั้งที่หน้ารีเฟรช
@st.cache_data
def get_data_cached():
    try:
        return fetch_data_from_google_sheets()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก Google Sheets: {e}")
        # ในกรณีที่ดึงข้อมูลไม่ได้ ให้ใช้ข้อมูลจำลองแทน
        today_date = datetime.date.today()
        today_datetime = datetime.datetime.now()
        hourly_data = {
            'timestamp': [today_datetime.replace(hour=i, minute=0, second=0, microsecond=0) for i in range(24)],
            'pm25': [random.randint(15, 80) for _ in range(24)]
        }
        hourly_df = pd.DataFrame(hourly_data)
        hourly_df['status_color'] = hourly_df['pm25'].apply(lambda x: get_color_and_status(x)[1])

        current_year = today_date.year
        current_month = today_date.month
        num_days = calendar.monthrange(current_year, current_month)[1]
        daily_data = {
            'date': [datetime.date(current_year, current_month, d) for d in range(1, num_days + 1)],
            'pm25_avg': [random.randint(15, 80) for _ in range(num_days)]
        }
        daily_df = pd.DataFrame(daily_data)
        daily_df['status_color'] = daily_df['pm25_avg'].apply(lambda x: get_color_and_status(x)[1])
        return hourly_df, daily_df

hourly_data, daily_data = get_data_cached()


# --- 4. การออกแบบหน้าเพจด้วย Streamlit ---

# หัวข้อและอัปเดตล่าสุด
st.title("รายงานเฝ้าระวัง PM2.5 อำเภอสันทราย")
st.markdown(f"**อัปเดตล่าสุด: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
st.markdown("---")

# ค่า PM2.5 ปัจจุบันและสถานะ
if not hourly_data.empty:
    current_pm25 = hourly_data['pm25'].iloc[-1]
else:
    current_pm25 = 0 # Default value if no data
_, color_hex, status = get_color_and_status(current_pm25)

st.header("สถานะ PM2.5 ปัจจุบัน")

col_metric, col_status_text = st.columns([1, 2])

with col_metric:
    st.markdown(f"""
        <div style="
            background-color: {color_hex};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            ">
            <div style="font-size: 1.5rem; font-weight: bold;">ค่า PM2.5</div>
            <div style="font-size: 4rem; font-weight: bold;">{current_pm25}</div>
            <div style="font-size: 1rem;">µg/m³</div>
        </div>
    """, unsafe_allow_html=True)
with col_status_text:
    st.markdown(f"""
        <div style="padding: 20px;">
            <div style="font-size: 2rem; font-weight: bold; color: {color_hex};">{status}</div>
            <div style="font-size: 1.2rem;">
                คุณภาพอากาศในอำเภอสันทรายขณะนี้อยู่ในระดับ **{status}**
            </div>
            <div style="font-size: 1.2rem; margin-top: 10px;">
                คำแนะนำ: **{get_recommendations_general(current_pm25)}**
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# กราฟ PM2.5 รายชั่วโมงและข้อมูลสรุป
st.subheader("แนวโน้ม PM2.5 วันนี้")
col_chart, col_summary = st.columns([2, 1])

with col_chart:
    if not hourly_data.empty:
        hourly_data['hour'] = hourly_data['timestamp'].dt.hour
        fig = px.bar(
            hourly_data, 
            x='hour', 
            y='pm25', 
            color='status_color',
            color_discrete_map={
                '#5CB85C': '#5CB85C',
                '#F0AD4E': '#F0AD4E',
                '#F89825': '#F89825',
                '#D9534F': '#D9534F',
                '#8A2BE2': '#8A2BE2'
            },
            labels={'pm25': 'ค่า PM2.5 (µg/m³)', 'hour': 'ชั่วโมง'},
            title="ค่า PM2.5 รายชั่วโมง (วันนี้)",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ไม่พบข้อมูลรายชั่วโมงสำหรับวันนี้")

with col_summary:
    st.markdown("##### ข้อมูลสรุปวันนี้")
    if not hourly_data.empty:
        st.metric(label="ค่าเฉลี่ย PM2.5", value=f"{hourly_data['pm25'].mean():.2f} µg/m³")
        st.metric(label="ค่าสูงสุด", value=f"{hourly_data['pm25'].max()} µg/m³")
        st.metric(label="ค่าต่ำสุด", value=f"{hourly_data['pm25'].min()} µg/m³")
    else:
        st.info("ไม่สามารถคำนวณข้อมูลสรุปได้")
    
st.markdown("---")

# ปฏิทินรายเดือนที่ปรับปรุงแล้ว
st.subheader("ค่า PM2.5 เฉลี่ยรายวัน (ทั้งเดือน)")
if not daily_data.empty:
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    daily_data['day'] = daily_data['date'].dt.day
    daily_data['weekday'] = daily_data['date'].dt.day_name()
    daily_data['month'] = daily_data['date'].dt.month

    # Get today's date to handle future days
    today_date = datetime.date.today()

    # Create the calendar HTML
    month_name = daily_data['date'].iloc[0].strftime('%B %Y')
    html_calendar = f"""
        <div style="font-family: Sarabun, sans-serif;">
            <h4 style="text-align: center; margin-bottom: 10px;">เดือน {daily_data['date'].iloc[0].strftime('%B %Y').replace('January', 'มกราคม').replace('February', 'กุมภาพันธ์').replace('March', 'มีนาคม').replace('April', 'เมษายน').replace('May', 'พฤษภาคม').replace('June', 'มิถุนายน').replace('July', 'กรกฎาคม').replace('August', 'สิงหาคม').replace('September', 'กันยายน').replace('October', 'ตุลาคม').replace('November', 'พฤศจิกายน').replace('December', 'ธันวาคม')}</h4>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; text-align: center; font-family: Sarabun, sans-serif;">
    """

    day_headers = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_headers_short = ["จ", "อ", "พ", "พฤ", "ศ", "ส", "อา"]

    for header in day_headers_short:
        html_calendar += f"<div style='font-weight: bold; padding: 10px; background-color: #f0f2f6; border-radius: 5px;'>{header}</div>"

    # Calculate the starting day of the month
    first_day_of_month_weekday = daily_data['date'].iloc[0].weekday()
    for _ in range(first_day_of_month_weekday):
        html_calendar += "<div></div>"

    for _, row in daily_data.iterrows():
        day = row['day']
        pm25_avg = row['pm25_avg']
        color = row['status_color']
        
        current_day_date = row['date'].date()
        
        if current_day_date > today_date:
            # For future dates, make it grey and transparent
            html_calendar += f"""
            <div style='
                border: 1px solid #ccc; 
                padding: 10px; 
                border-radius: 5px; 
                min-height: 80px; 
                position: relative; 
                background-color: #f0f2f6; 
                opacity: 0.5;
                color: #999;
            '>
                <div style='font-size: 1.5em; font-weight: bold; text-align: left;'>{day}</div>
                <div style='font-size: 1em; position: absolute; bottom: 5px; right: 5px; visibility:hidden;'>-</div>
            </div>
            """
        else:
            # For past and current dates, show the data
            html_calendar += f"""
            <div style='
                border: 1px solid #ccc; 
                padding: 10px; 
                border-radius: 5px; 
                min-height: 80px; 
                position: relative; 
                background-color: {color};
                color: white;
                box-shadow: 0 2px 4px 0 rgba(0,0,0,0.1);
            '>
                <div style='font-size: 1.5em; font-weight: bold; text-align: left;'>{day}</div>
                <div style='font-size: 1em; position: absolute; bottom: 5px; right: 5px;'>{pm25_avg:.0f}</div>
            </div>
            """

    html_calendar += "</div></div>"
    st.markdown(html_calendar, unsafe_allow_html=True)
else:
    st.warning("ไม่พบข้อมูลรายวันสำหรับเดือนนี้")

st.markdown("---")

# คำแนะนำการปฏิบัติตัว
with st.expander("คำแนะนำการปฏิบัติตัว 🩺", expanded=True):
    st.markdown("สำหรับประชาชนทั่วไป:")
    st.markdown(f"**{get_recommendations_general(current_pm25)}**")

    st.markdown("สำหรับกลุ่มเปราะบาง (ผู้สูงอายุ, เด็ก, ผู้มีโรคประจำตัว, หญิงตั้งครรภ์):")
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
fig_patient = px.bar(
    patient_df,
    x='วันที่',
    y='จำนวนผู้ป่วย',
    labels={'จำนวนผู้ป่วย': 'จำนวนผู้ป่วย', 'วันที่': 'วันที่'},
    title="จำนวนผู้ป่วยที่เกี่ยวข้องกับ PM2.5",
    template="plotly_white"
)
st.plotly_chart(fig_patient, use_container_width=True)
