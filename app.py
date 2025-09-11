import streamlit as st
from data_loader import load_data
from ui_components import (
    display_realtime_pm,
    display_24hr_chart,
    display_monthly_calendar,
    display_historical_data,
    display_knowledge_tabs
)

# --- Page Configuration ---
st.set_page_config(
    page_title="รายงานค่าฝุ่น PM2.5 อ.สันทราย",
    page_icon="💨",
    layout="wide"
)

# --- Load Data ---
df = load_data()

if df is None or df.empty:
    st.warning("ไม่พบข้อมูล หรือข้อมูลที่โหลดมาไม่สมบูรณ์")
    st.stop()

# --- Header ---
st.title("💨 รายงานค่าฝุ่น PM2.5 อำเภอสันทราย")
st.markdown(f"ข้อมูลล่าสุดเมื่อ: `{df['Datetime'][0].strftime('%d %B %Y, %H:%M:%S')}`")
st.divider()

# --- Main UI Components ---
display_realtime_pm(df)
st.divider()

display_24hr_chart(df)
st.divider()

# NOTE: The calendar display is commented out as it was not fully implemented in the original code.
# You can uncomment it if you complete the implementation in ui_components.py
# st.subheader("ปฏิทินค่าฝุ่น PM2.5 รายวัน")
# display_monthly_calendar(df)
# st.divider()

display_historical_data(df)
st.divider()

display_knowledge_tabs()

st.sidebar.success("เลือกเมนูเพื่อดูข้อมูล")

