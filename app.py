import streamlit as st
from data_loader import load_data
from ui_components import (
    display_realtime_pm,
    display_24hr_chart,
    display_monthly_calendar,
    display_health_impact,
    display_symptom_checker,
    display_historical_data,
    display_knowledge_base
)
from translations import TRANSLATIONS as t

# --- Page Configuration ---
# Initialize session state for language if it doesn't exist
if 'lang' not in st.session_state:
    st.session_state.lang = 'th'

# Set page config based on the selected language
st.set_page_config(
    page_title=t[st.session_state.lang]['page_title'],
    page_icon="🍃",
    layout="wide"
)

# --- Language Selection ---
# Place buttons at the top right
_, col1, col2 = st.columns([10, 1, 1])
if col1.button('ไทย'):
    st.session_state.lang = 'th'
    st.rerun() # Rerun to apply language change immediately
if col2.button('English'):
    st.session_state.lang = 'en'
    st.rerun()

lang = st.session_state.lang

# --- Data Loading ---
df = load_data()

# Stop execution if data loading fails
if df is None or df.empty:
    st.warning("ไม่พบข้อมูล หรือข้อมูลที่โหลดมาไม่สมบูรณ์" if lang == 'th' else "No data found or failed to load.")
    st.stop()

# --- Header ---
st.title(t[lang]['header'])

# Format the latest date string based on the selected language
latest_dt = df['Datetime'][0]
if lang == 'th':
    thai_year = latest_dt.year + 543
    thai_month = t['th']['month_names'][latest_dt.month - 1]
    date_str = latest_dt.strftime(f"%d {thai_month} {thai_year}, %H:%M:%S")
else:
    date_str = latest_dt.strftime('%d %B %Y, %H:%M:%S')
st.markdown(f"{t[lang]['latest_data']} `{date_str}`")

st.divider()

# --- UI Components Display Order ---
display_realtime_pm(df, lang, t, date_str)
st.divider()
display_24hr_chart(df, lang, t)
st.divider()
display_monthly_calendar(df, lang, t)
st.divider()
display_symptom_checker(lang, t)
st.divider()
display_historical_data(df, lang, t)
st.divider()
display_knowledge_base(lang, t)
st.divider()
display_health_impact(df, lang, t)

