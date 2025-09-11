import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# --- Page Configuration ---
st.set_page_config(
    page_title="รายงานค่าฝุ่น PM2.5 อ.สันทราย",
    page_icon="💨",
    layout="wide"
)

# --- Google Sheets Connection ---
# ใช้ st.secrets เพื่อการจัดการข้อมูล credentials ที่ปลอดภัย
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    
    # --- CONFIG ---
    SPREADSHEET_ID = "1-Une9oA0-ln6ApbhwaXFNpkniAvX7g1K9pNR800MJwQ"
    SHEET_NAME = "PM2.5 Log"

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ Google Sheets: {e}")
    st.info("โปรดตรวจสอบการตั้งค่าไฟล์ credentials ใน Streamlit Secrets")
    st.stop()


# --- Data Loading and Caching ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data():
    """
    โหลดข้อมูลจาก Google Sheet และแปลงเป็น Pandas DataFrame
    """
    try:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        
        # --- FIX: ใช้ get_all_values() เพื่อดึงข้อมูลทั้งหมด ---
        # ข้ามแถวแรก (header) ของชีตด้วย [1:]
        data = sheet.get_all_values()[1:] 
        
        # กำหนดชื่อคอลัมน์เองโดยตรงเพื่อป้องกันปัญหา header ซ้ำซ้อน
        # ตรวจสอบให้แน่ใจว่าจำนวนชื่อตรงกับจำนวนคอลัมน์ในชีตของคุณ
        expected_headers = ["Datetime", "PM2.5", "Date", "Time"]
        # เลือกข้อมูลมาแค่ 4 คอลัมน์แรกเท่านั้น
        data_subset = [row[:4] for row in data]
        df = pd.DataFrame(data_subset, columns=expected_headers)

        # Data Cleaning and Preparation
        df['PM2.5'] = pd.to_numeric(df['PM2.5'], errors='coerce')
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        df.dropna(subset=['PM2.5', 'Datetime'], inplace=True)
        df = df.sort_values(by="Datetime", ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลจาก Google Sheet ได้: {e}")
        return None

# --- Helper Functions for AQI ---
def get_aqi_level(pm25):
    """
    แปลงค่า PM2.5 เป็นระดับคุณภาพอากาศและสี
    ตามมาตรฐานของประเทศไทย
    """
    if pm25 <= 15:
        return "ดีมาก", "#0099FF", "😊", "ทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif 15 < pm25 <= 25:
        return "ดี", "#00CC00", "🙂", "ทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif 25 < pm25 <= 37.5:
        return "ปานกลาง", "#FFFF00", "😐", "ผู้ที่ต้องดูแลสุขภาพเป็นพิเศษ หากมีอาการผิดปกติ ควรลดระยะเวลาการทำกิจกรรมกลางแจ้ง"
    elif 37.5 < pm25 <= 75:
        return "เริ่มมีผลกระทบต่อสุขภาพ", "#FF9900", "😷", "ประชาชนทั่วไปควรเฝ้าระวังสุขภาพ ถ้ามีอาการผิดปกติควรรีบพบแพทย์ | ผู้ที่ต้องดูแลสุขภาพเป็นพิเศษ ควรลดระยะเวลาการทำกิจกรรมกลางแจ้ง"
    else: # pm25 > 75
        return "มีผลกระทบต่อสุขภาพ", "#FF0000", "🤢", "ทุกคนควรหลีกเลี่ยงกิจกรรมกลางแจ้ง และใช้อุปกรณ์ป้องกันตนเองหากมีความจำเป็น"

# --- Main App ---
df = load_data()

if df is None or df.empty:
    st.warning("ไม่พบข้อมูล หรือข้อมูลที่โหลดมาไม่สมบูรณ์")
    st.stop()

# --- Header ---
st.title("💨 รายงานค่าฝุ่น PM2.5 อำเภอสันทราย")
st.markdown(f"ข้อมูลล่าสุดเมื่อ: `{df['Datetime'][0].strftime('%d %B %Y, %H:%M:%S')}`")


# --- Real-time PM2.5 Display ---
latest_pm25 = df['PM2.5'][0]
level, color, emoji, advice = get_aqi_level(latest_pm25)

st.divider()

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
        # --- FIX: เปลี่ยนจากการแสดงรูปภาพ เป็นการแสดงข้อมูลจากโค้ดโดยตรง ---
        st.markdown("""
            <style>
                .legend-dot {
                    height: 15px;
                    width: 15px;
                    border-radius: 50%;
                    display: inline-block;
                    margin-right: 8px;
                    vertical-align: middle;
                }
                .legend-item {
                    font-size: 1.1rem;
                    margin-bottom: 8px;
                }
            </style>
            <div class="legend-item"><span class="legend-dot" style="background-color: #0099FF;"></span><b>ดีมาก:</b> 0 - 15.0 μg/m³</div>
            <div class="legend-item"><span class="legend-dot" style="background-color: #00CC00;"></span><b>ดี:</b> 15.1 - 25.0 μg/m³</div>
            <div class="legend-item" style="color: black;"><span class="legend-dot" style="background-color: #FFFF00;"></span><b>ปานกลาง:</b> 25.1 - 37.5 μg/m³</div>
            <div class="legend-item"><span class="legend-dot" style="background-color: #FF9900;"></span><b>เริ่มมีผลกระทบ:</b> 37.6 - 75.0 μg/m³</div>
            <div class="legend-item"><span class="legend-dot" style="background-color: #FF0000;"></span><b>มีผลกระทบ:</b> > 75.0 μg/m³</div>
        """, unsafe_allow_html=True)


st.divider()

# --- 24-Hour Trend Chart ---
st.subheader("แนวโน้มค่า PM2.5 ใน 24 ชั่วโมงล่าสุด")

# Filter data for the last 24 hours
now = datetime.now()
last_24_hours_data = df[df['Datetime'] >= (df['Datetime'].max() - timedelta(hours=24))]
last_24_hours_data = last_24_hours_data.sort_values(by="Datetime", ascending=True)

fig_24hr = go.Figure()

# Add line trace
fig_24hr.add_trace(go.Scatter(
    x=last_24_hours_data['Datetime'],
    y=last_24_hours_data['PM2.5'],
    mode='lines+markers',
    name='PM2.5',
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=5)
))

# Add colored background ranges for AQI levels
fig_24hr.add_hrect(y0=0, y1=15, line_width=0, fillcolor="#0099FF", opacity=0.1, annotation_text="ดีมาก", annotation_position="right")
fig_24hr.add_hrect(y0=15, y1=25, line_width=0, fillcolor="#00CC00", opacity=0.1, annotation_text="ดี", annotation_position="right")
fig_24hr.add_hrect(y0=25, y1=37.5, line_width=0, fillcolor="#FFFF00", opacity=0.1, annotation_text="ปานกลาง", annotation_position="right")
fig_24hr.add_hrect(y0=37.5, y1=75, line_width=0, fillcolor="#FF9900", opacity=0.1, annotation_text="เริ่มมีผลกระทบ", annotation_position="right")
fig_24hr.add_hrect(y0=75, y1=max(100, last_24_hours_data['PM2.5'].max() * 1.1), line_width=0, fillcolor="#FF0000", opacity=0.1, annotation_text="มีผลกระทบ", annotation_position="right")


fig_24hr.update_layout(
    xaxis_title="เวลา",
    yaxis_title="PM2.5 (μg/m³)",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    hovermode="x unified",
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(gridcolor='lightgrey'),
    yaxis=dict(gridcolor='lightgrey')
)
st.plotly_chart(fig_24hr, use_container_width=True)


# --- Monthly Calendar Heatmap ---
st.subheader("ปฏิทินค่าฝุ่น PM2.5 รายวัน")

# Prepare data for calendar
df_calendar = df.copy()
df_calendar['date'] = df_calendar['Datetime'].dt.date
# Calculate daily average
daily_avg_pm25 = df_calendar.groupby('date')['PM2.5'].mean().reset_index()
daily_avg_pm25['date'] = pd.to_datetime(daily_avg_pm25['date'])

# Get the most recent month's data
latest_date = daily_avg_pm25['date'].max()
start_of_month = latest_date.replace(day=1)
end_of_month = (start_of_month + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
month_data = daily_avg_pm25[(daily_avg_pm25['date'] >= start_of_month) & (daily_avg_pm25['date'] <= end_of_month)]

# Create calendar structure
month_calendar = calendar.Calendar()
cal = month_calendar.monthdatescalendar(start_of_month.year, start_of_month.month)

dates = []
values = []
for week in cal:
    for day in week:
        dates.append(day)
        if day.month == start_of_month.month:
            record = month_data[month_data['date'].dt.date == day]
            if not record.empty:
                values.append(record['PM2.5'].iloc[0])
            else:
                values.append(None) # No data for this day
        else:
            values.append(None) # Day not in current month


# Create the heatmap
x = [(d.strftime('%A')) for d in cal[0]] # Days of week
y = [f"Week {i+1}" for i in range(len(cal))]
z = [values[i:i+7] for i in range(0, len(values), 7)]

# Get color scale
colorscale = [
    [0.0, "#0099FF"],
    [0.15, "#00CC00"],
    [0.25, "#FFFF00"],
    [0.375, "#FF9900"],
    [0.75, "#FF0000"],
    [1.0, "#800000"]
]

custom_text = [[f"{z_val:.1f}" if z_val is not None else "" for z_val in row] for row in z]
day_numbers = [[d.day for d in week] for week in cal]

hover_text = []
for i, week in enumerate(cal):
    week_hover = []
    for j, day in enumerate(week):
        val = z[i][j]
        if val is not None:
            level, _, _, _ = get_aqi_level(val)
            week_hover.append(f"<b>{day.strftime('%d %b %Y')}</b><br>ค่าเฉลี่ย PM2.5: {val:.1f}<br>คุณภาพอากาศ: {level}")
        else:
            week_hover.append("")
    hover_text.append(week_hover)


fig_cal = go.Figure(data=go.Heatmap(
    z=z,
    x=x,
    y=y,
    colorscale=colorscale,
    zmin=0,
    zmax=100,
    text=day_numbers,
    texttemplate="%{text}",
    hovertext=hover_text,
    hoverinfo='text',
    xgap=3,
    ygap=3
))

fig_cal.update_layout(
    title=f"ค่าเฉลี่ย PM2.5 รายวัน เดือน {start_of_month.strftime('%B %Y')}",
    yaxis=dict(autorange='reversed'),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig_cal, use_container_width=True)

st.sidebar.success("เลือกเมนูเพื่อดูข้อมูล")

