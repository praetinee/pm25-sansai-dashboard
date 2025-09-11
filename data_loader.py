import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Connection ---
@st.cache_resource(ttl=600)
def connect_to_gsheet():
    """Connects to Google Sheets using credentials from st.secrets."""
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ Google Sheets: {e}")
        st.info("โปรดตรวจสอบการตั้งค่าไฟล์ credentials ใน Streamlit Secrets")
        return None

# --- Data Loading and Caching ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data():
    """
    Loads data from a Google Sheet and returns a Pandas DataFrame.
    """
    client = connect_to_gsheet()
    if client is None:
        st.stop()

    try:
        SPREADSHEET_ID = "1-Une9oA0-ln6ApbhwaXFNpkniAvX7g1K9pNR800MJwQ"
        SHEET_NAME = "PM2.5 Log"
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        
        data = sheet.get_all_values()[1:]  # Skip header row
        
        expected_headers = ["Datetime", "PM2.5", "Date", "Time"]
        data_subset = [row[:4] for row in data]
        df = pd.DataFrame(data_subset, columns=expected_headers)

        # Data Cleaning and Preparation
        df['PM2.5'] = pd.to_numeric(df['PM2.5'], errors='coerce')
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        df.dropna(subset=['PM2.5', 'Datetime'], inplace=True)
        df = df.sort_values(by="Datetime", ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลจาก Google Sheet ได้: {e}")
        return None
