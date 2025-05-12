import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

# --- Configuration ---
UPLOAD_DIR = os.path.expanduser("~/Desktop/uploads")
LOG_FILE = os.path.join(UPLOAD_DIR, "upload_log.xlsx")
MANDATORY_FIELDS = ["Field1", "Field2"]

# --- Ensure Upload Folder Exists ---
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Simple Auth ---
def login(username, password):
    return username == "admin" and password == "pass123"

st.title("Excel Upload Portal (Local Testing)")

# --- Login Section ---
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if login(username, password):
        st.session_state['logged_in'] = True
    else:
        st.error("Invalid credentials")

# --- Upload Section ---
if st.session_state.get("logged_in"):
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    comment = st.text_area("Enter your comments")

    if st.button("Submit"):
        if uploaded_file:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            missing = [col for col in MANDATORY_FIELDS if col not in df.columns or df[col].isnull().any()]
            
            if missing:
                st.error(f"Missing or empty mandatory fields: {missing}")
            else:
                # Save the file locally
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = f"{timestamp}_{uploaded_file.name}"
                file_path = os.path.join(UPLOAD_DIR, safe_filename)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Log the metadata to Excel
                log_entry = {
                    "Timestamp": datetime.now(),
                    "Filename": safe_filename,
                    "Username": username,
                    "Comment": comment
                }

                if os.path.exists(LOG_FILE):
                    log_df = pd.read_excel(LOG_FILE, engine="openpyxl")
                    log_df = pd.concat([log_df, pd.DataFrame([log_entry])], ignore_index=True)
                else:
                    log_df = pd.DataFrame([log_entry])
                
                log_df.to_excel(LOG_FILE, index=False, engine="openpyxl")

                st.success(f"File uploaded and logged successfully: {safe_filename}")
        else:
            st.warning("Please upload a file before submitting.")