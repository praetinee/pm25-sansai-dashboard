import streamlit as st
from data_loader import load_data
from ui_components import (
    display_realtime_pm,
    display_24hr_chart,
    display_monthly_calendar,
    display_health_impact,
    display_symptom_checker,
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

# --- Custom CSS for Radio Tabs ---
st.markdown("""
<style>
    /* Hide the default radio buttons circle */
    div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    /* Style the labels to look like tabs */
    div[role="radiogroup"] > label {
        display: inline-block;
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        margin: 0 5px;
        font-size: 1rem;
        font-family: 'Sarabun', sans-serif;
        color: #808495; /* Inactive tab color */
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    /* Style for the selected tab */
    div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
        background-color: #f0f2f5; /* Light background for selected */
        color: #1e40af !important; /* Active tab color */
        border-bottom: 3px solid #1e40af !important; /* Active tab underline */
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Tabbed UI (Re-implemented with st.radio) ---
tab_titles = ["ค่า PM2.5 ปัจจุบัน", "เกร็ดความรู้"]

# The radio button's state is controlled by st.session_state.active_tab
selected_tab = st.radio(
    " ", 
    tab_titles,
    key='tabs_radio',
    horizontal=True,
    label_visibility='collapsed',
    index=tab_titles.index(st.session_state.active_tab) # Set default from state
)
# Ensure our session state is always in sync with the user's selection
st.session_state.active_tab = selected_tab 

# Render content based on the selected tab
if selected_tab == "ค่า PM2.5 ปัจจุบัน":
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
    display_symptom_checker(lang, t)

elif selected_tab == "เกร็ดความรู้":
    display_knowledge_base(lang, t)
