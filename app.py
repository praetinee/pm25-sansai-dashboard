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
from knowledge_base_ui import display_knowledge_quiz
from translations import TRANSLATIONS as t

# --- Page Configuration ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'th'
# --- Session State for Tabs ---
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = t[st.session_state.lang]['main_tab_title']


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

# --- Tabbed UI Simulation with st.radio ---
tab_titles = [t[lang]['main_tab_title'], t[lang]['quiz_header']]

# Update session state when radio button changes
def handle_tab_change():
    st.session_state.active_tab = st.session_state.tab_selection

# Find the index of the active tab for the radio button
try:
    active_tab_index = tab_titles.index(st.session_state.active_tab)
except ValueError:
    active_tab_index = 0

# Create the radio button that looks like tabs
st.radio(
    label="Navigation",
    options=tab_titles,
    index=active_tab_index,
    key="tab_selection",
    horizontal=True,
    on_change=handle_tab_change,
    label_visibility="collapsed"
)


# Display content based on the selected tab
if st.session_state.active_tab == tab_titles[0]:
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

elif st.session_state.active_tab == tab_titles[1]:
    display_knowledge_quiz(lang, t)

