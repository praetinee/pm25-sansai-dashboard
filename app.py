import streamlit as st
from data_loader import load_data
from ui_components import (
    display_realtime_pm,
    display_24hr_chart,
    display_monthly_calendar,
    display_historical_data,
    display_knowledge_tabs
)
from translations import TRANSLATIONS as t

# --- Page Configuration ---
# Use session state to set page config
if 'lang' not in st.session_state:
    st.session_state.lang = 'th'

st.set_page_config(
    page_title=t[st.session_state.lang]['page_title'],
    page_icon="💨",
    layout="wide"
)

# --- Language Selection ---
_, col1, col2 = st.columns([10, 1, 1])
if col1.button('🇹🇭 TH'):
    st.session_state.lang = 'th'
    st.rerun()
if col2.button('🇬🇧 EN'):
    st.session_state.lang = 'en'
    st.rerun()

lang = st.session_state.lang

# --- Data Loading ---
df = load_data()

if df is None or df.empty:
    st.warning("ไม่พบข้อมูล หรือข้อมูลที่โหลดมาไม่สมบูรณ์" if lang == 'th' else "No data found or failed to load.")
    st.stop()

# --- Header ---
st.title(t[lang]['header'])
st.markdown(f"{t[lang]['latest_data']} `{df['Datetime'][0].strftime('%d %B %Y, %H:%M:%S')}`")

st.divider()

# --- UI Components ---
display_realtime_pm(df, lang, t)
st.divider()
display_24hr_chart(df, lang, t)
st.divider()
display_monthly_calendar(df, lang, t)
st.divider()
display_historical_data(df, lang, t)
st.divider()
display_knowledge_tabs(lang, t)

