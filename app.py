import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json

# ---------- GOOGLE SHEETS CONNECTION ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load service account from Streamlit Secrets
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)

# Replace with your Google Sheet name
SHEET_NAME = "symptom_records"
sheet = CLIENT.open(SHEET_NAME).sheet1

# ---------- APP TITLE ----------
st.set_page_config(page_title="Disease Diagnosis Lab", page_icon="🧪", layout="centered")
st.title("🧠 Disease & Cancer Symptom Checker")
st.write("Fill in your details and symptoms to see possible disease or cancer risks.")

# ---------- USER DETAILS FORM ----------
with st.form("user_form"):
    name = st.text_input("👤 Full Name")
    age = st.number_input("🎂 Age", min_value=0, max_value=120, step=1)
    gender = st.radio("⚧ Gender", ["Male", "Female"])
    mobile = st.text_input("📱 Mobile Number")
    st.subheader("🩺 Medical History")
    bp = st.checkbox("High Blood Pressure")
    diabetes = st.checkbox("Diabetes")
    heart = st.checkbox("Heart Issues")

    st.subheader("🧍 Symptoms")
    common_symptoms = [
        "Fatigue / Extreme tiredness",
        "Unexplained weight loss or gain",
        "Eating problems (loss of appetite, nausea, vomiting)",
        "Swelling or lumps in body",
        "Pain that doesn't go away",
        "Skin changes / Jaundice / new moles",
        "Cough or hoarseness that does not go away",
        "Unusual bleeding or bruising",
        "Change in bowel habits / blood in stool",
        "Bladder changes / pain / blood in urine",
        "Fever or night sweats",
        "Headaches",
        "Vision or hearing problems",
        "Mouth changes (sores, bleeding, numbness)"
    ]

    male_symptoms = [
        "Prostate issues (frequent urination, weak stream, pelvic pain)",
        "Lung-related issues (persistent cough, chest pain)",
        "Testicular lumps or swelling",
        "Pancreatic issues (upper belly pain, jaundice)",
        "Blood cancer indicators (frequent infections, bruising)",
        "Brain tumor symptoms (seizures, severe headaches)"
    ]

    female_symptoms = [
        "Breast lump or thickening",
        "Unusual nipple discharge",
        "Pelvic pain or bloating (ovarian)",
        "Abnormal vaginal bleeding",
        "Cervical cancer symptoms (pain, discharge)",
    ]

    # Gender-based symptom filtering
    symptoms_selected = st.multiselect("Select Symptoms", common_symptoms)
    if gender == "Male":
        symptoms_selected += st.multiselect("Male-specific Symptoms", male_symptoms)
    else:
        symptoms_selected += st.multiselect("Female-specific Symptoms", female_symptoms)

    submitted = st.form_submit_button("🔍 Diagnose")

# ---------- DIAGNOSIS LOGIC ----------
def diagnose(symptoms, gender):
    """Very basic rules for demonstration."""
    possible = []

    # Common indicators
    if "Fatigue / Extreme tiredness" in symptoms and "Unusual bleeding or bruising" in symptoms:
        possible.append("Blood Cancer / Leukemia")
    if "Pain that doesn't go away" in symptoms and "Skin changes / Jaundice / new moles" in symptoms:
        possible.append("Skin Cancer / Melanoma")
    if "Cough or hoarseness that does not go away" in symptoms:
        possible.append("Lung Cancer")
    if "Change in bowel habits / blood in stool" in symptoms:
        possible.append("Colorectal Cancer")
    if "Bladder changes / pain / blood in urine" in symptoms:
        possible.append("Bladder Cancer")

    if gender == "Male":
        if "Prostate issues (frequent urination, weak stream, pelvic pain)" in symptoms:
            possible.append("Prostate Cancer")
        if "Testicular lumps or swelling" in symptoms:
            possible.append("Testicular Cancer")
    else:
        if "Breast lump or thickening" in symptoms or "Unusual nipple discharge" in symptoms:
            possible.append("Breast Cancer")
        if "Pelvic pain or bloating (ovarian)" in symptoms or "Abnormal vaginal bleeding" in symptoms:
            possible.append("Ovarian / Cervical Cancer")

    return list(set(possible))

# ---------- SHOW RESULTS ----------
if submitted:
    if not name or not mobile:
        st.error("Please enter your Name and Mobile Number.")
    else:
        results = diagnose(symptoms_selected, gender)
        if results:
            st.success(f"**Possible Conditions / Cancers Detected:**")
            for r in results:
                st.write(f"🔸 {r}")
        else:
            st.info("No significant cancer indicators found based on selected symptoms.")

        # ---------- SAVE DATA TO GOOGLE SHEET ----------
        data = [name, age, gender, mobile, bp, diabetes, heart, ", ".join(symptoms_selected), ", ".join(results)]
        sheet.append_row(data)
        st.success("✅ Your response has been recorded securely.")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚠️ This tool is for educational/demo purposes only. It does not replace professional medical advice.")

