import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Connection & Data Loading ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data():
    """
    Loads data from the specified Google Sheet and returns it as a Pandas DataFrame.
    Handles authentication using Streamlit Secrets.
    """
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(creds)
        
        SPREADSHEET_ID = "1-Une9oA0-ln6ApbhwaXFNpkniAvX7g1K9pNR800MJwQ"
        SHEET_NAME = "PM2.5 Log"
        
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(SHEET_NAME)
        
        # Fetch all values, skipping the header row
        data = sheet.get_all_values()[1:] 
        
        # Manually define headers to avoid duplicate/empty header issues
        expected_headers = ["Datetime", "PM2.5", "Date", "Time"]
        
        # Ensure we only take the first 4 columns to match headers
        data_subset = [row[:4] for row in data]
        
        df = pd.DataFrame(data_subset, columns=expected_headers)

        # --- Data Cleaning and Type Conversion ---
        # Convert 'PM2.5' to numeric, coercing errors to NaN (Not a Number)
        df['PM2.5'] = pd.to_numeric(df['PM2.5'], errors='coerce')
        # Convert 'Datetime' to datetime objects, coercing errors
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        
        # Drop rows where critical data ('PM2.5', 'Datetime') is missing
        df.dropna(subset=['PM2.5', 'Datetime'], inplace=True)
        
        # Sort by Datetime in descending order to get the latest data first
        df = df.sort_values(by="Datetime", ascending=False).reset_index(drop=True)
        
        return df
        
    except Exception as e:
        # Display an error message in the app if something goes wrong
        st.error(f"ไม่สามารถโหลดข้อมูลจาก Google Sheet ได้ (An error occurred while loading data from Google Sheets): {e}")
        return None

