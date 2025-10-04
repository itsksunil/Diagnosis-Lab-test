import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open("Symptom_Records").sheet1

st.title("🩺 Symptom-Based Disease Checker")

# User Info
name = st.text_input("Name")
age = st.number_input("Age", min_value=0, max_value=120)
gender = st.radio("Gender", ["Male", "Female", "Other"])
mobile = st.text_input("Mobile Number")

# Symptoms
symptoms_list = ["Persistent cough", "Blood in urine", "Voice changes", "Headaches"]
selected_symptoms = st.multiselect("Select symptoms", symptoms_list)

# Diagnosis logic (simple example)
def diagnose(symptoms):
    result = []
    if "Persistent cough" in symptoms:
        result.append("Lung Cancer")
    if "Blood in urine" in symptoms:
        result.append("Prostate Cancer")
    return result

if st.button("Submit"):
    diagnosis = diagnose(selected_symptoms)
    SHEET.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name, age, gender, mobile, "-", ", ".join(selected_symptoms),
        ", ".join(diagnosis)
    ])
    st.success(f"✅ Possible diagnosis: {', '.join(diagnosis) if diagnosis else 'No match found'}")
