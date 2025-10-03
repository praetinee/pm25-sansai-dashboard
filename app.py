import streamlit as st
from data_loader import load_data
from ui_components import (
    display_realtime_pm,
    display_24hr_chart,
    display_monthly_calendar,
    display_health_impact,
    display_external_assessment,
    display_historical_data,
)
from knowledge_base_ui import display_knowledge_quiz # Updated import
from translations import TRANSLATIONS as t

# --- Page Configuration ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'th'

st.set_page_config(
    page_title=t[st.session_state.lang]['page_title'],
    page_icon="🍃",
    layout="wide"
)

# --- Language Selection ---
_, col1, col2 = st.columns([10, 1, 1])
if col1.button('ไทย'):
    st.session_state.lang = 'th'
    st.rerun()
if col2.button('English'):
    # Note: English translations for the quiz are not yet available.
    # It will show Thai content for now.
    st.session_state.lang = 'th' 
    st.rerun()

lang = st.session_state.lang

# --- Data Loading ---
df = load_data()

if df is None or df.empty:
    st.warning("ไม่สามารถโหลดข้อมูลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    st.stop()

# --- Header ---
st.title(t[lang]['header'])

latest_dt = df['Datetime'][0]
if lang == 'th':
    thai_year = latest_dt.year + 543
    thai_month = t['th']['month_names'][latest_dt.month - 1]
    date_str = latest_dt.strftime(f"%d {thai_month} {thai_year}, %H:%M:%S")
else:
    date_str = latest_dt.strftime('%d %B %Y, %H:%M:%S')
st.markdown(f"{t[lang]['latest_data']} `{date_str}`")

st.divider()

# --- Tabbed UI ---
# Updated tab titles using the new translation key
tab_titles = [t[lang]['main_tab_title'], t[lang]['quiz_header']] 

tabs = st.tabs(tab_titles)

with tabs[0]:
    display_realtime_pm(df, lang, t, date_str)
    st.divider()
    display_24hr_chart(df, lang, t)
    st.divider()
    display_monthly_calendar(df, lang, t)
    st.divider()
    display_historical_data(df, lang, t)
    st.divider()
    display_health_impact(df, lang, t)
    st.divider()
    display_external_assessment(lang, t)

with tabs[1]:
    # Updated function call to the new quiz UI
    display_knowledge_quiz(lang, t)

