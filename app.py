import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
# --- BEGIN: การเปลี่ยนแปลงที่ 1 ---
# เราจะใช้ gspread และเครื่องมือจัดการ credentials แทน
import gspread
from google.oauth2.service_account import Credentials
# --- END: การเปลี่ยนแปลงที่ 1 ---

# =================================================================================
# Page Configuration (ตั้งค่าหน้าเว็บ)
# =================================================================================
st.set_page_config(
    page_title="รายงานคุณภาพอากาศ อ.สันทราย",
    page_icon="🌬️",
    layout="wide"
)

# =================================================================================
# Custom CSS for styling (ปรับแต่งหน้าตาเว็บให้สวยงาม)
# =================================================================================
st.markdown("""
    <style>
    /* เปลี่ยน font */
    html, body, [class*="st-"] {
        font-family: 'IBM Plex Sans Thai', sans-serif;
    }
    /* การ์ดแสดงผลหลัก */
    .main-metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid #EAEAEA;
    }
    /* หัวข้อ */
    h1, h2, h3 {
        color: #2c3e50;
    }
    /* ซ่อน header และ footer ของ Streamlit */
    .st-emotion-cache-18ni7ap, .st-emotion-cache-h4xjwg {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)


# =================================================================================
# Data Loading and Processing (ส่วนจัดการข้อมูล)
# =================================================================================

# --- BEGIN: การเปลี่ยนแปลงที่ 2 ---
# แก้ไขฟังก์ชันโหลดข้อมูลทั้งหมดให้ใช้ gspread
@st.cache_data(ttl=600) # โหลดข้อมูลใหม่ทุก 10 นาที
def load_data_from_gsheet():
    """โหลดข้อมูลจาก Google Sheet โดยใช้ gspread โดยตรง"""
    # กำหนดขอบเขตการเข้าถึง
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    # สร้าง credentials จาก st.secrets ซึ่งเราจะตั้งค่าในขั้นตอนต่อไป
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    
    # URL ของ Google Sheet ของคุณ
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # เปิด Spreadsheet และ Worksheet
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet("PM2.5 Log")
    
    # ดึงข้อมูลทั้งหมดมาเป็น DataFrame
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # ตรวจสอบว่า DataFrame มีข้อมูลหรือไม่ และมีคอลัมน์ที่คาดหวังหรือไม่
    if df.empty or not all(col in df.columns for col in ["Datetime", "PM2.5"]):
        st.error("ไม่พบข้อมูลหรือชื่อคอลัมน์ 'Datetime', 'PM2.5' ใน Google Sheet")
        st.stop()
    
    # ขั้นตอนการจัดการข้อมูลเหมือนเดิม
    df = df[["Datetime", "PM2.5"]].copy() # เลือกเฉพาะคอลัมน์ที่ต้องการ
    df.dropna(inplace=True) 
    df.columns = ['timestamp', 'pm25'] # สมมติว่าชื่อคอลัมน์ในชีทคือ Datetime และ PM2.5
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['pm25'] = pd.to_numeric(df['pm25'])
    df = df.sort_values('timestamp')
    return df
# --- END: การเปลี่ยนแปลงที่ 2 ---

# --- BEGIN: การเปลี่ยนแปลงที่ 3 ---
# เรียกใช้ฟังก์ชันโหลดข้อมูลจาก Google Sheet พร้อมจัดการ Error
try:
    df = load_data_from_gsheet()
except gspread.exceptions.SpreadsheetNotFound:
    # --- BEGIN: ปรับปรุงส่วนแจ้งเตือน ---
    client_email = st.secrets.get("gcp_service_account", {}).get("client_email", "[ไม่พบอีเมลใน Secrets]")
    sheet_url = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", "#")
    st.error(
        f"""
        **ไม่พบ Google Sheet หรือไม่ได้รับอนุญาตให้เข้าถึง**

        ดูเหมือนว่า "หุ่นยนต์" ของเรายังไม่สามารถเข้าไปอ่านข้อมูลใน Google Sheet ได้ครับ ปัญหานี้มักเกิดจากการตั้งค่าการแชร์ยังไม่สมบูรณ์

        **ขั้นตอนการแก้ไข (สำคัญที่สุด):**
        1.  **คัดลอกอีเมลของ "หุ่นยนต์":**
            `{client_email}`
        2.  **ไปที่ Google Sheet ของคุณ:** [คลิกที่นี่เพื่อเปิดชีท]({sheet_url})
        3.  คลิกที่ปุ่ม **"Share"** (แชร์) สีเขียวที่มุมขวาบน
        4.  ในช่องสำหรับเพิ่มรายชื่อ ให้ **วางอีเมลที่คัดลอกมา** และตั้งค่าสิทธิ์ให้เป็น **"Editor"** จากนั้นกดส่ง
        5.  เมื่อให้สิทธิ์เรียบร้อยแล้ว กลับมาที่หน้านี้แล้วกด **Reboot** ที่เมนู 'Manage app' มุมขวาล่างของจอครับ
        """
    )
    # --- END: ปรับปรุงส่วนแจ้งเตือน ---
    st.stop()
except gspread.exceptions.WorksheetNotFound:
    st.error(
        "**ไม่พบ Worksheet 'PM2.5 Log'!** "
        "กรุณาตรวจสอบว่าใน Google Sheet ของคุณมีชีทที่ชื่อว่า `PM2.5 Log` จริงๆ (ตัวพิมพ์ใหญ่-เล็กต้องตรงกัน)"
    )
    st.stop()
except KeyError as e:
    if "gcp_service_account" in str(e) or "connections" in str(e):
         st.error(
            "**การตั้งค่า Secrets ไม่ถูกต้อง!** "
            "ดูเหมือนว่าโครงสร้างของ Secrets ใน Streamlit Cloud ของคุณจะไม่ตรงกับที่โค้ดต้องการ "
            "กรุณาตรวจสอบให้แน่ใจว่าคุณได้คัดลอกรูปแบบ `secrets.toml` ไปวางอย่างถูกต้อง"
         )
    else:
        st.error(f"**ไม่พบคอลัมน์ที่ต้องการใน Google Sheet!** กรุณาตรวจสอบว่ามีคอลัมน์ 'Datetime' และ 'PM2.5' อยู่ในชีท 'PM2.5 Log' ของคุณ")
    st.stop()
except Exception as e:
    st.error(f"""
        **เกิดข้อผิดพลาดที่ไม่คาดคิด**

        กรุณาตรวจสอบการตั้งค่าทั้งหมดอีกครั้ง

        **รายละเอียดทางเทคนิค:**
        ```
        {e}
        ```
    """)
    st.stop()

# --- ตรวจสอบว่า DataFrame มีข้อมูลหรือไม่หลังจากการประมวลผล ---
if df.empty:
    st.warning("ไม่พบข้อมูลที่สามารถแสดงผลได้ใน Google Sheet")
    st.stop()
# --- END: การเปลี่ยนแปลงที่ 3 ---


# =================================================================================
# Helper Functions (ฟังก์ชันช่วยคำนวณ)
# =================================================================================

def get_aqi_category(pm25):
    """แปลงค่า PM2.5 เป็นระดับ AQI, สี, และคำแนะนำ (อ้างอิงกรมควบคุมมลพิษ)"""
    if pm25 <= 25:
        return "ดีมาก", "#3498db", "คุณภาพอากาศดีมาก สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ" # ฟ้า
    elif pm25 <= 37:
        return "ดี", "#2ecc71", "คุณภาพอากาศดี สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ" # เขียว
    elif pm25 <= 50:
        return "ปานกลาง", "#f1c40f", "ประชาชนทั่วไป: ทำกิจกรรมกลางแจ้งได้ปกติ / ผู้มีความเสี่ยง: ควรลดระยะเวลาทำกิจกรรมกลางแจ้ง" # เหลือง
    elif pm25 <= 90:
        return "เริ่มมีผลกระทบต่อสุขภาพ", "#f39c12", "ประชาชนทั่วไป: ควรลดระยะเวลาทำกิจกรรมกลางแจ้ง / ผู้มีความเสี่ยง: ควรงดกิจกรรมกลางแจ้ง" # ส้ม
    else:
        return "มีผลกระทบต่อสุขภาพ", "#e74c3c", "ทุกคนควรงดกิจกรรมกลางแจ้ง และใช้อุปกรณ์ป้องกันตนเองหากจำเป็น" # แดง

# =================================================================================
# Main Application UI (ส่วนแสดงผลของแอป)
# =================================================================================

# --- Header ---
st.title("🌬️ รายงานคุณภาพอากาศ อ.สันทราย จ.เชียงใหม่")
latest_timestamp = df['timestamp'].iloc[-1].strftime("%d %B %Y, %H:%M น.")
st.markdown(f"ข้อมูลล่าสุดเมื่อ: **{latest_timestamp}**")

st.divider()

# --- Real-time AQI Display (ส่วนแสดงผลเรียลไทม์) ---
latest_pm25 = df['pm25'].iloc[-1]
category, color, advice = get_aqi_category(latest_pm25)

col1, col2 = st.columns([1, 2])

with col1:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>ค่า PM2.5 ปัจจุบัน</h3>", unsafe_allow_html=True)
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = latest_pm25,
            number = {'font': {'size': 60, 'color': color}},
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "μg/m³", 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [0, 150], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#ccc",
                'steps': [
                    {'range': [0, 25], 'color': '#3498db'},
                    {'range': [25, 37], 'color': '#2ecc71'},
                    {'range': [37, 50], 'color': '#f1c40f'},
                    {'range': [50, 90], 'color': '#f39c12'},
                    {'range': [90, 150], 'color': '#e74c3c'}],
            }))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown(f"""
        <div style='padding: 10px; border-radius: 10px;'>
            <h3 style='margin:0; color: #2c3e50;'>คุณภาพอากาศ: 
                <span style='background-color:{color}; color:white; padding: 5px 10px; border-radius: 5px;'>{category}</span>
            </h3>
            <br>
            <h4>คำแนะนำในการปฏิบัติตัว:</h4>
            <p style='font-size: 1.1em;'>{advice}</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("ℹ️ ค่ามาตรฐาน PM2.5 ของประเทศไทยใน 24 ชั่วโมง คือ 37.5 µg/m³ (ประกาศ กพ. 2566)", icon="ℹ️")


st.divider()

# --- Tabs for different views (แท็บแสดงข้อมูลในมุมมองต่างๆ) ---
tab1, tab2, tab3 = st.tabs(["📊 กราฟแนวโน้ม 24 ชั่วโมง", "🗓️ ปฏิทินคุณภาพอากาศ", "🌍 แผนที่และข้อมูล"])

with tab1:
    st.subheader("กราฟแนวโน้มคุณภาพอากาศใน 24 ชั่วโมงล่าสุด")
    
    # Filter data for the last 24 hours
    df_24h = df[df['timestamp'] >= (datetime.now() - timedelta(hours=24))]

    if not df_24h.empty:
        fig_24h = px.line(df_24h, x='timestamp', y='pm25', 
                        labels={'timestamp': 'เวลา', 'pm25': 'ค่า PM2.5 (μg/m³)'},
                        template="plotly_white")
        
        # Add threshold line (เส้นค่ามาตรฐาน)
        fig_24h.add_hline(y=37.5, line_dash="dot",
                        annotation_text="ค่ามาตรฐาน",
                        annotation_position="bottom right",
                        line_color="orange")
        
        fig_24h.update_traces(line_color='#2c3e50', line_width=3)
        fig_24h.update_layout(
            xaxis_title="",
            yaxis_title="ค่า PM2.5 (μg/m³)",
            font=dict(family="IBM Plex Sans Thai, sans-serif")
        )
        st.plotly_chart(fig_24h, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลเพียงพอสำหรับ 24 ชั่วโมงล่าสุด")


with tab2:
    st.subheader("ปฏิทินคุณภาพอากาศ (ค่าเฉลี่ยรายวัน)")

    # Resample to daily average
    df_daily = df.set_index('timestamp').resample('D')['pm25'].mean().round(0).reset_index()
    df_daily = df_daily[df_daily['timestamp'] >= (datetime.now() - timedelta(days=35))] # แสดงผลประมาณ 1 เดือน

    if not df_daily.empty:
        # Create calendar data
        start_date = df_daily['timestamp'].min()
        # Adjust start date to be a Monday
        start_date -= timedelta(days=start_date.weekday())
        
        dates = pd.date_range(start=start_date, periods=42) # 6 weeks
        
        calendar_data = pd.DataFrame({'date': dates})
        calendar_data['day_of_week'] = calendar_data['date'].dt.day_name()
        calendar_data['week_of_month'] = calendar_data['date'].dt.isocalendar().week
        calendar_data['day_num'] = calendar_data['date'].dt.day
        
        # Map PM2.5 values
        calendar_data = pd.merge(calendar_data, df_daily, left_on='date', right_on='timestamp', how='left')
        
        # Create text and color info
        calendar_data['text'] = calendar_data['day_num'].astype(str) + '<br><b>' + calendar_data['pm25'].fillna('').astype(str) + '</b>'
        calendar_data['color'] = calendar_data['pm25'].apply(lambda x: get_aqi_category(x)[1] if pd.notna(x) else 'rgba(0,0,0,0)')

        # Pivot for heatmap
        weekdays_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        calendar_data['day_of_week'] = pd.Categorical(calendar_data['day_of_week'], categories=weekdays_order, ordered=True)
        calendar_pivot = calendar_data.pivot_table(values='pm25', index='day_of_week', columns='week_of_month')

        # Create heatmap figure
        fig_cal = go.Figure(data=go.Heatmap(
            z=calendar_pivot.values,
            x=calendar_pivot.columns,
            y=calendar_pivot.index,
            xgap=3, ygap=3,
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']], # Transparent background
            showscale=False
        ))

        # Add day numbers and PM2.5 values as annotations
        annotations = []
        for _, row in calendar_data.iterrows():
            if pd.notna(row['pm25']):
                annotations.append(go.layout.Annotation(
                    x=row['week_of_month'], y=row['day_of_week'],
                    text=f"<b>{row['day_num']}</b><br>{int(row['pm25'])}",
                    showarrow=False,
                    font=dict(color='white' if row['pm25'] > 50 else 'black', size=10),
                ))

        # Add shapes for colored backgrounds
        shapes = []
        for _, row in calendar_data.iterrows():
            if pd.notna(row['pm25']):
                shapes.append(go.layout.Shape(
                    type="rect",
                    x0=row['week_of_month'] - 0.5, x1=row['week_of_month'] + 0.5,
                    y0=row['day_of_week'], y1=row['day_of_week'],
                    line=dict(width=0),
                    fillcolor=row['color'],
                    layer='below'
                ))

        fig_cal.update_layout(
            shapes=shapes,
            annotations=annotations,
            xaxis_title="สัปดาห์",
            yaxis_title="",
            template="plotly_white",
            xaxis=dict(tickmode='array', tickvals=list(calendar_pivot.columns), ticktext=[f'W{w}' for w in calendar_pivot.columns]),
            yaxis=dict(showgrid=False, autorange="reversed"),
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig_cal, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลเพียงพอสำหรับสร้างปฏิทิน")


with tab3:
    st.subheader("ตำแหน่งที่ตั้งและข้อมูลดิบ")
    
    col_map, col_data = st.columns(2)
    with col_map:
        # พิกัดของอำเภอสันทราย (โดยประมาณ)
        sansai_coords = pd.DataFrame({'lat': [18.8655], 'lon': [99.0435]})
        st.map(sansai_coords, zoom=11)
    
    with col_data:
        st.write("ข้อมูลล่าสุด 10 รายการ:")
        st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)

st.divider()
st.caption("พัฒนาโดย คู่หูเขียนโค้ด (Coding Copilot) | ข้อมูลคุณภาพอากาศอ้างอิงตามเกณฑ์ของกรมควบคุมมลพิษ ประเทศไทย")

