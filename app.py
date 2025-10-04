import streamlit as st
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json

# ---------- GOOGLE SHEETS CONNECTION ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_NAME = "symptom_records"
sheet = CLIENT.open(SHEET_NAME).sheet1

# ---------- APP TITLE ----------
st.set_page_config(page_title="Disease Diagnosis Lab", page_icon="🧪", layout="centered")
st.title("🧠 Disease & Symptom Checker")
st.write("Fill in your details and symptoms to see possible disease risks.")

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
    location = st.text_input("📍 Location / City")

    st.subheader("🧍 Symptoms")
    # Common Symptoms
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

    # Male/Female Cancer Symptoms
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

    # Viral Disease Symptoms
    viral_symptoms = [
        "High fever",
        "Chills / Sweating",
        "Body pain / Joint pain",
        "Rash",
        "Nausea / Vomiting",
        "Headache",
        "Weakness / Fatigue",
    ]

    # Heart Attack Symptoms
    heart_symptoms = [
        "Chest pain / pressure / tightness",
        "Pain radiating to arm / jaw / back",
        "Shortness of breath",
        "Cold sweats",
        "Nausea / vomiting",
        "Dizziness / fainting",
    ]

    # Gender-based symptom filtering
    symptoms_selected = st.multiselect("Select Symptoms", common_symptoms)
    if gender == "Male":
        symptoms_selected += st.multiselect("Male-specific Symptoms", male_symptoms)
    else:
        symptoms_selected += st.multiselect("Female-specific Symptoms", female_symptoms)

    symptoms_selected += st.multiselect("Viral Disease Symptoms", viral_symptoms)
    symptoms_selected += st.multiselect("Heart Attack Symptoms", heart_symptoms)

    submitted = st.form_submit_button("🔍 Diagnose")

# ---------- DIAGNOSIS LOGIC ----------
def diagnose(symptoms, gender):
    """Basic rule-based diagnosis."""
    possible = []
    organ_mapping = []

    # Cancer Indicators
    if "Fatigue / Extreme tiredness" in symptoms and "Unusual bleeding or bruising" in symptoms:
        possible.append("Blood Cancer / Leukemia")
        organ_mapping.append("Blood / Bone Marrow")
    if "Pain that doesn't go away" in symptoms and "Skin changes / Jaundice / new moles" in symptoms:
        possible.append("Skin Cancer / Melanoma")
        organ_mapping.append("Skin")
    if "Cough or hoarseness that does not go away" in symptoms:
        possible.append("Lung Cancer")
        organ_mapping.append("Lungs")
    if "Change in bowel habits / blood in stool" in symptoms:
        possible.append("Colorectal Cancer")
        organ_mapping.append("Intestines / Colon")
    if "Bladder changes / pain / blood in urine" in symptoms:
        possible.append("Bladder Cancer")
        organ_mapping.append("Bladder")

    if gender == "Male":
        if "Prostate issues (frequent urination, weak stream, pelvic pain)" in symptoms:
            possible.append("Prostate Cancer")
            organ_mapping.append("Prostate")
        if "Testicular lumps or swelling" in symptoms:
            possible.append("Testicular Cancer")
            organ_mapping.append("Testicles")
    else:
        if "Breast lump or thickening" in symptoms or "Unusual nipple discharge" in symptoms:
            possible.append("Breast Cancer")
            organ_mapping.append("Breast")
        if "Pelvic pain or bloating (ovarian)" in symptoms or "Abnormal vaginal bleeding" in symptoms:
            possible.append("Ovarian / Cervical Cancer")
            organ_mapping.append("Ovaries / Cervix")

    # Viral Diseases
    if any(s in symptoms for s in ["High fever", "Chills / Sweating", "Body pain / Joint pain", "Rash"]):
        if "Rash" in symptoms:
            possible.append("Dengue")
            organ_mapping.append("Blood / Immune System")
        elif "Joint pain" in symptoms:
            possible.append("Chikungunya / Malaria")
            organ_mapping.append("Blood / Joints / Liver")
        else:
            possible.append("Viral Infection (Typhoid / Flu)")
            organ_mapping.append("Digestive / Immune System")

    # Heart Attack
    if any(s in symptoms for s in heart_symptoms):
        possible.append("Heart Attack / Cardiovascular Risk")
        organ_mapping.append("Heart / Circulatory System")

    return list(set(possible)), list(set(organ_mapping))

# ---------- SHOW RESULTS ----------
if submitted:
    if not name or not mobile:
        st.error("Please enter your Name and Mobile Number.")
    else:
        results, organs = diagnose(symptoms_selected, gender)
        if results:
            st.success(f"**Possible Conditions Detected:**")
            for r, o in zip(results, organs):
                st.write(f"🔸 {r} → Possible organ/system: {o}")
        else:
            st.info("No significant disease indicators found based on selected symptoms.")

        # ---------- SAVE DATA TO GOOGLE SHEET ----------
        data = [
            name, age, gender, mobile, bp, diabetes, heart, location,
            ", ".join(symptoms_selected), ", ".join(results), ", ".join(organs)
        ]
        sheet.append_row(data)
        st.success("✅ Your response has been recorded securely.")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚠️ This tool is for educational/demo purposes only. It does not replace professional medical advice.")
