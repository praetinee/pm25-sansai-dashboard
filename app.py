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
from knowledge_base_ui import display_knowledge_base
from translations import TRANSLATIONS as t

# --- Page Configuration ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'th'
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "ค่า PM2.5 ปัจจุบัน"

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
    st.session_state.lang = 'en'
    st.rerun()

lang = st.session_state.lang

# --- Data Loading ---
df = load_data()

if df is None or df.empty:
    st.warning(t[lang]['no_data_for_year'])
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
tab_titles = ["ค่า PM2.5 ปัจจุบัน", "เกร็ดความรู้"]
active_tab = st.session_state.active_tab

# Get the index of the active tab to set it
try:
    active_tab_index = tab_titles.index(st.session_state.active_tab)
except ValueError:
    active_tab_index = 0

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
    display_knowledge_base(lang, t)

# Removed the redundant st.rerun() logic here.
# The app should automatically update based on session state changes.
