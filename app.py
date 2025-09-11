import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# =================================================================================
# Page Configuration (ตั้งค่าหน้าเว็บ)
# =================================================================================
st.set_page_config(
    page_title="รายงานคุณภาพอากาศ อ.สันทราย",
    page_icon="🌬️",
    layout="wide",
)

# =================================================================================
# Custom CSS for styling (ปรับแต่งหน้าตาเว็บให้สวยงาม)
# =================================================================================
st.markdown("""
    <style>
    /* Global Font */
    html, body, [class*="st-"] {
        font-family: 'IBM Plex Sans Thai', sans-serif;
    }
    /* Main Card Style */
    .main-metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid #EAEAEA;
    }
    /* Headings */
    h1, h2, h3 {
        color: #2c3e50;
    }
    /* Hide Streamlit default elements */
    .st-emotion-cache-18ni7ap, .st-emotion-cache-h4xjwg {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# =================================================================================
# Data Loading and Processing Function
# =================================================================================
@st.cache_data(ttl=600) # Refresh data every 10 minutes
def load_data_from_gsheet():
    """
    Connects to Google Sheets using gspread and st.secrets,
    fetches the data, and returns a cleaned pandas DataFrame.
    """
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet("PM2.5 Log")
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # Validate DataFrame structure
    if df.empty or "Datetime" not in df.columns or "PM2.5" not in df.columns:
        # This error is for internal validation, user-facing errors are handled below
        return pd.DataFrame() 

    # Data Cleaning and Preparation
    df = df[["Datetime", "PM2.5"]].copy()
    df.dropna(inplace=True)
    df.rename(columns={'Datetime': 'timestamp', 'PM2.5': 'pm25'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['pm25'] = pd.to_numeric(df['pm25'])
    df.sort_values('timestamp', inplace=True)
    return df

# =================================================================================
# Helper Functions (ฟังก์ชันช่วยคำนวณ)
# =================================================================================
def get_aqi_category(pm25):
    """Converts PM2.5 value to AQI category, color, and health advice."""
    if pm25 <= 25:
        return "ดีมาก", "#3498db", "คุณภาพอากาศดีมาก สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif pm25 <= 37:
        return "ดี", "#2ecc71", "คุณภาพอากาศดี สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif pm25 <= 50:
        return "ปานกลาง", "#f1c40f", "ประชาชนทั่วไป: ทำกิจกรรมกลางแจ้งได้ปกติ / ผู้มีความเสี่ยง: ควรลดระยะเวลาทำกิจกรรมกลางแจ้ง"
    elif pm25 <= 90:
        return "เริ่มมีผลกระทบต่อสุขภาพ", "#f39c12", "ประชาชนทั่วไป: ควรลดระยะเวลาทำกิจกรรมกลางแจ้ง / ผู้มีความเสี่ยง: ควรงดกิจกรรมกลางแจ้ง"
    else:
        return "มีผลกระทบต่อสุขภาพ", "#e74c3c", "ทุกคนควรงดกิจกรรมกลางแจ้ง และใช้อุปกรณ์ป้องกันตนเองหากจำเป็น"

# =================================================================================
# Main Application Logic with Robust Error Handling
# =================================================================================
try:
    df = load_data_from_gsheet()
    if df.empty:
        st.warning("ไม่พบข้อมูลที่สามารถแสดงผลได้ใน Google Sheet หรือคอลัมน์ 'Datetime', 'PM2.5' อาจไม่ถูกต้อง")
        st.stop()
except gspread.exceptions.SpreadsheetNotFound:
    project_id = st.secrets.get("gcp_service_account", {}).get("project_id", "your-project-id")
    client_email = st.secrets.get("gcp_service_account", {}).get("client_email", "[ไม่พบอีเมลใน Secrets]")
    sheet_url = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", "#")
    st.error(
        f"""
        **ยังคงเชื่อมต่อ Google Sheet ไม่ได้**
        ปัญหานี้เหลือเพียง 3 สาเหตุหลักที่เกี่ยวข้องกับการตั้งค่าของคุณเท่านั้นครับ ขอให้คุณใจเย็นๆ และตรวจสอบอีกครั้งอย่างละเอียดถี่ถ้วนที่สุดครับ

        **Checklist "ตรวจสอบสามครั้ง" (สาเหตุ 99% อยู่ในนี้):**

        **1. การแชร์ชีทผิดพลาด (สาเหตุอันดับ 1):**
        - **อีเมลถูกต้องหรือไม่?** ตรวจสอบว่าอีเมลที่แชร์ให้ใน Google Sheet คืออีเมลนี้ **เป๊ะๆ**: `{client_email}`
        - **สิทธิ์ถูกต้องหรือไม่?** ตรวจสอบว่าสิทธิ์ที่ให้คือ **"Editor"**
        - **คุณเป็นเจ้าของชีทหรือไม่?** หากไม่ใช่ ให้ลองสร้างชีทใหม่ที่คุณเป็นเจ้าของเพื่อทดสอบ

        **2. ข้อมูล Secrets ผิดพลาด (สาเหตุอันดับ 2):**
        - **URL ถูกต้องหรือไม่?** ตรวจสอบว่า URL ใน Secrets ไม่มีตัวอักษรขาดหรือเกิน
        - **คัดลอก `private_key` มาครบหรือไม่?** ลองคัดลอก-วางใหม่อีกครั้ง และตรวจสอบ `-----BEGIN...` และ `-----END...`

        **3. API ยังไม่พร้อมใช้งาน:**
        - **ไปที่ลิงก์นี้:** `https://console.cloud.google.com/apis/library/sheets.googleapis.com?project={project_id}`
        - ลอง **"ปิด" (Disable) API** แล้วรอสักครู่ จากนั้น **"เปิด" (Enable) ใหม่อีกครั้ง**
        """
    )
    st.stop()
except gspread.exceptions.WorksheetNotFound:
    st.error("**ไม่พบ Worksheet 'PM2.5 Log'!** กรุณาตรวจสอบว่าใน Google Sheet ของคุณมีชีทที่ชื่อว่า `PM2.5 Log` จริงๆ (ตัวพิมพ์ใหญ่-เล็กต้องตรงกัน)")
    st.stop()
except Exception as e:
    st.error(f"**เกิดข้อผิดพลาดที่ไม่คาดคิด:**\n\n`{e}`\n\nกรุณาตรวจสอบการตั้งค่า Secrets และโครงสร้างไฟล์ Google Sheet ของคุณอีกครั้ง")
    st.stop()

# =================================================================================
# UI Rendering (ส่วนแสดงผลของแอป)
# =================================================================================
st.title("🌬️ รายงานคุณภาพอากาศ อ.สันทราย จ.เชียงใหม่")
latest_timestamp = df['timestamp'].iloc[-1].strftime("%d %B %Y, %H:%M น.")
st.markdown(f"ข้อมูลล่าสุดเมื่อ: **{latest_timestamp}**")
st.divider()

# --- Real-time AQI Display ---
latest_pm25 = df['pm25'].iloc[-1]
category, color, advice = get_aqi_category(latest_pm25)
col1, col2 = st.columns([1, 2])

with col1:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>ค่า PM2.5 ปัจจุบัน</h3>", unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=latest_pm25,
            number={'font': {'size': 60, 'color': color}},
            title={'text': "μg/m³", 'font': {'size': 24}},
            gauge={'axis': {'range': [0, 150]}, 'bar': {'color': color},
                   'steps': [{'range': [0, 25], 'color': '#3498db'}, {'range': [25, 37], 'color': '#2ecc71'},
                             {'range': [37, 50], 'color': '#f1c40f'}, {'range': [50, 90], 'color': '#f39c12'},
                             {'range': [90, 150], 'color': '#e74c3c'}]}
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown(f"""
            <h3 style='margin:0; color: #2c3e50;'>คุณภาพอากาศ: 
                <span style='background-color:{color}; color:white; padding: 5px 10px; border-radius: 5px;'>{category}</span>
            </h3><br>
            <h4>คำแนะนำในการปฏิบัติตัว:</h4>
            <p style='font-size: 1.1em;'>{advice}</p>
        """, unsafe_allow_html=True)
        st.info("ℹ️ ค่ามาตรฐาน PM2.5 ของประเทศไทยใน 24 ชั่วโมง คือ 37.5 µg/m³ (ประกาศ กพ. 2566)")

st.divider()

# --- Tabs for different views ---
tab1, tab2, tab3 = st.tabs(["📊 กราฟแนวโน้ม 24 ชั่วโมง", "🗓️ ปฏิทินคุณภาพอากาศ", "🌍 แผนที่และข้อมูล"])

with tab1:
    st.subheader("กราฟแนวโน้มคุณภาพอากาศใน 24 ชั่วโมงล่าสุด")
    df_24h = df[df['timestamp'] >= (datetime.now() - timedelta(hours=24))]
    if not df_24h.empty:
        fig_24h = px.line(df_24h, x='timestamp', y='pm25', template="plotly_white",
                          labels={'timestamp': 'เวลา', 'pm25': 'ค่า PM2.5 (μg/m³)'})
        fig_24h.add_hline(y=37.5, line_dash="dot", annotation_text="ค่ามาตรฐาน", line_color="orange")
        fig_24h.update_traces(line_color='#2c3e50', line_width=3)
        st.plotly_chart(fig_24h, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลเพียงพอสำหรับ 24 ชั่วโมงล่าสุด")

with tab2:
    st.subheader("ปฏิทินคุณภาพอากาศ (ค่าเฉลี่ยรายวัน)")
    df_daily = df.set_index('timestamp').resample('D')['pm25'].mean().round(0).reset_index()
    df_daily = df_daily[df_daily['timestamp'] >= (datetime.now() - timedelta(days=35))]
    if not df_daily.empty:
        start_date = df_daily['timestamp'].min() - timedelta(days=df_daily['timestamp'].min().weekday())
        dates = pd.date_range(start=start_date, periods=42) # 6 weeks
        
        calendar_data = pd.DataFrame({'date': dates})
        calendar_data = pd.merge(calendar_data, df_daily, left_on='date', right_on='timestamp', how='left')
        calendar_data['day_of_week'] = calendar_data['date'].dt.day_name()
        calendar_data['week_of_month'] = calendar_data['date'].dt.isocalendar().week
        calendar_data['day_num'] = calendar_data['date'].dt.day
        calendar_data['color'] = calendar_data['pm25'].apply(lambda x: get_aqi_category(x)[1] if pd.notna(x) else 'rgba(0,0,0,0.05)')

        st.markdown("<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; text-align: center;'>", unsafe_allow_html=True)
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in weekdays:
            st.markdown(f"<div style='font-weight: bold;'>{day}</div>", unsafe_allow_html=True)
        
        for _, row in calendar_data.iterrows():
            pm_val = f"{int(row['pm25'])}" if pd.notna(row['pm25']) else ""
            font_color = 'white' if pd.notna(row['pm25']) and row['pm25'] > 50 else 'black'
            st.markdown(f"""
                <div style='background-color: {row['color']}; border-radius: 5px; padding: 10px; color: {font_color};'>
                    <div style='font-size: 0.8em;'>{row['day_num']}</div>
                    <div style='font-size: 1.1em; font-weight: bold;'>{pm_val}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("ไม่มีข้อมูลเพียงพอสำหรับสร้างปฏิทิน")

with tab3:
    st.subheader("ตำแหน่งที่ตั้งและข้อมูลดิบ")
    col_map, col_data = st.columns(2)
    with col_map:
        sansai_coords = pd.DataFrame({'lat': [18.8655], 'lon': [99.0435]})
        st.map(sansai_coords, zoom=11)
    with col_data:
        st.write("ข้อมูลล่าสุด 10 รายการ:")
        st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)

st.divider()
st.caption("พัฒนาโดย คู่หูเขียนโค้ด (Coding Copilot) | ข้อมูลคุณภาพอากาศอ้างอิงตามเกณฑ์ของกรมควบคุมมลพิษ ประเทศไทย")

