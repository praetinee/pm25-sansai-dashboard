import streamlit as st
import streamlit.components.v1 as components
from data_loader import load_data
from ui_components import (
    display_realtime_pm,
    display_24hr_chart,
    display_monthly_calendar,
    display_health_impact,
    display_external_assessment,
    display_historical_data,
    inject_custom_css,
)
from translations import TRANSLATIONS as MAIN_T

# --- Translations ---
t = MAIN_T

# --- Page Configuration ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'th'

st.set_page_config(
    page_title=t[st.session_state.lang]['page_title'],
    page_icon="🍃",
    layout="wide"
)

# --- ANTI-SLEEP / KEEP ALIVE MECHANISM ---
# ใส่ไว้ที่นี่ (app.py) เพื่อให้ทำงานตลอดเวลาที่เปิดแอป
keep_alive_script = """
<script>
    // 1. ส่งสัญญาณ Ping ไปที่ Server ทุกๆ 5 นาที (300,000 ms)
    // เพื่อหลอกให้ Server คิดว่ามีการใช้งานอยู่ตลอดเวลา ไม่ตัด Connection
    setInterval(function(){
        var xhr = new XMLHttpRequest();
        // ยิงไปที่ endpoint health check ของ Streamlit เอง
        xhr.open("GET", "/_stcore/health", true);
        xhr.send();
    }, 300000);
    
    // 2. ถ้าเผลอหลุดไปแล้ว (Connection closed) ให้รีเฟรชหน้าจอให้อัตโนมัติ
    window.addEventListener('error', function(e) {
        if (e.message && (e.message.includes('Connection') || e.message.includes('disconnected'))) {
            window.location.reload();
        }
    });
</script>
"""
# ความสูง 0 เพื่อซ่อน component นี้ไม่ให้เห็นบนหน้าจอ
components.html(keep_alive_script, height=0, width=0)

# --- Inject CSS globally ---
inject_custom_css()

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

st.write("") # Spacer

# --- Main Display ---
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
