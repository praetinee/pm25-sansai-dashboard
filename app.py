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
from translations import TRANSLATIONS as MAIN_T
from quiz_translations import TRANSLATIONS as QUIZ_T

# --- Deep merge translation dictionaries ---
def merge_dicts(d1, d2):
    for k, v in d2.items():
        if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
            d1[k] = merge_dicts(d1[k], v)
        else:
            d1[k] = v
    return d1

t = merge_dicts(MAIN_T, QUIZ_T)


# --- Page Configuration ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'th'

# Initialize active_tab with a language-independent key if it doesn't exist
if 'active_tab_key' not in st.session_state:
    st.session_state.active_tab_key = 'main' # 'main' or 'quiz'

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

# --- Tabbed UI using Radio Button Hack ---
tab_keys = ['main', 'quiz']
tab_titles = [t[lang]['main_tab_title'], t[lang]['quiz_header']]

# Get the index of the currently active tab
active_tab_index = tab_keys.index(st.session_state.active_tab_key)

selected_tab_title = st.radio(
    "Main navigation",
    options=tab_titles,
    index=active_tab_index,
    horizontal=True,
    label_visibility="collapsed"
)

# Update session state with the key of the selected tab
st.session_state.active_tab_key = tab_keys[tab_titles.index(selected_tab_title)]

# --- Display content based on selected tab ---
if st.session_state.active_tab_key == 'main':
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

elif st.session_state.active_tab_key == 'quiz':
    display_knowledge_base(lang, t)

