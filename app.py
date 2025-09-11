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
    page_title="รายงานค่าฝุ่น PM2.5",
    page_icon="💨",
    layout="wide"
)

# --- Data Loading ---
df = load_data()

if df is None or df.empty:
    st.warning("ไม่พบข้อมูล หรือข้อมูลที่โหลดมาไม่สมบูรณ์")
    st.stop()

# --- Header ---
st.title("💨 รายงานค่าฝุ่น PM2.5 ณ จุดตรวจวัด รพ.สันทราย")
st.markdown(f"ข้อมูลล่าสุดเมื่อ: `{df['Datetime'][0].strftime('%d %B %Y, %H:%M:%S')}`")

st.divider()

# --- UI Components ---
display_realtime_pm(df)
st.divider()
display_24hr_chart(df)
st.divider()
display_monthly_calendar(df)
st.divider()
display_historical_data(df)
st.divider()
display_knowledge_tabs()

