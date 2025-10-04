import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------- GOOGLE SHEETS CONNECTION ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_NAME = "symptom_records"
sheet = CLIENT.open(SHEET_NAME).sheet1

# ---------- APP CONFIG ----------
st.set_page_config(
    page_title="Disease Diagnosis Lab", page_icon="🧪", layout="wide", initial_sidebar_state="expanded"
)
st.title("🧠 Disease & Symptom Checker")
st.markdown(
    "Fill in your details and select symptoms to see possible disease risks.\n\n"
    "**⚠️ Note:** This tool is for educational/demo purposes only and does not replace professional medical advice."
)

# ---------- SIDEBAR FOR USER DETAILS ----------
st.sidebar.header("👤 Your Details")
name = st.sidebar.text_input("Full Name")
age = st.sidebar.number_input("Age", min_value=0, max_value=120, step=1)
gender = st.sidebar.radio("Gender", ["Male", "Female"])
mobile = st.sidebar.text_input("Mobile Number")
location = st.sidebar.text_input("Location / City")

st.sidebar.subheader("Medical History")
bp = st.sidebar.checkbox("High Blood Pressure")
diabetes = st.sidebar.checkbox("Diabetes")
heart = st.sidebar.checkbox("Heart Issues")

# ---------- SYMPTOM SELECTION ----------
st.header("🧍 Select Symptoms")

def multi_select_expander(title, options):
    with st.expander(title):
        return st.multiselect(f"Select {title}", options)

# Common Symptoms
common_symptoms = [
    "Fatigue / Extreme tiredness",
    "Unexplained weight loss or gain",
    "Loss of appetite / Nausea / Vomiting",
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
symptoms_selected = multi_select_expander("Common Symptoms", common_symptoms)

# Gender-specific Cancer Symptoms
if gender == "Male":
    male_symptoms = [
        "Prostate issues (frequent urination, weak stream, pelvic pain)",
        "Lung-related issues (persistent cough, chest pain)",
        "Testicular lumps or swelling",
        "Pancreatic issues (upper belly pain, jaundice)",
        "Blood cancer indicators (frequent infections, bruising)",
        "Brain tumor symptoms (seizures, severe headaches)"
    ]
    symptoms_selected += multi_select_expander("Male-specific Cancer Symptoms", male_symptoms)
else:
    female_symptoms = [
        "Breast lump or thickening",
        "Unusual nipple discharge",
        "Pelvic pain or bloating (ovarian)",
        "Abnormal vaginal bleeding",
        "Cervical cancer symptoms (pain, discharge)"
    ]
    symptoms_selected += multi_select_expander("Female-specific Cancer Symptoms", female_symptoms)

# Viral Disease Symptoms
malaria_symptoms = [
    "Fever", "Chills", "General discomfort", "Headache", "Nausea / Vomiting",
    "Diarrhea", "Abdominal pain", "Muscle / Joint pain", "Fatigue",
    "Rapid breathing", "Rapid heart rate", "Cough"
]
typhoid_symptoms = [
    "Headache", "Chills", "Loss of appetite", "Abdominal pain",
    "Rose spots rash", "Cough", "Muscle aches", "Nausea / Vomiting",
    "Diarrhea / Constipation"
]
dengue_symptoms = [
    "Headache", "Muscle / Bone / Joint pain", "Nausea", "Vomiting",
    "Pain behind the eyes", "Swollen glands", "Rash"
]
symptoms_selected += multi_select_expander("Malaria Symptoms", malaria_symptoms)
symptoms_selected += multi_select_expander("Typhoid Symptoms", typhoid_symptoms)
symptoms_selected += multi_select_expander("Dengue Symptoms", dengue_symptoms)

# Heart Symptoms
heart_symptoms = [
    "Shortness of breath", "Fatigue / Weakness", "Leg / Ankle / Foot swelling",
    "Rapid / Irregular heartbeat", "Reduced ability to exercise", "Wheezing",
    "Persistent cough or white/pink mucus with blood", "Swelling of belly",
    "Rapid weight gain from fluid buildup", "Nausea / Lack of appetite",
    "Difficulty concentrating", "Chest pain from heart attack",
    "Pain in neck / jaw / throat / upper belly / back"
]
symptoms_selected += multi_select_expander("Heart / Cardiovascular Symptoms", heart_symptoms)

# ---------- SUBMIT BUTTON ----------
submitted = st.button("🔍 Diagnose")

# ---------- DIAGNOSIS LOGIC ----------
def diagnose(symptoms, gender):
    possible = []
    organ_mapping = []
    severity = "Low"

    # Cancer Indicators
    if "Fatigue / Extreme tiredness" in symptoms and "Unusual bleeding or bruising" in symptoms:
        possible.append("Blood Cancer / Leukemia")
        organ_mapping.append("Blood / Bone Marrow")
        severity = "High"
    if "Pain that doesn't go away" in symptoms and "Skin changes / Jaundice / new moles" in symptoms:
        possible.append("Skin Cancer / Melanoma")
        organ_mapping.append("Skin")
        severity = "High"
    if "Cough or hoarseness that does not go away" in symptoms:
        possible.append("Lung Cancer")
        organ_mapping.append("Lungs")
        severity = "High"
    if "Change in bowel habits / blood in stool" in symptoms:
        possible.append("Colorectal Cancer")
        organ_mapping.append("Intestines / Colon")
        severity = "High"
    if "Bladder changes / pain / blood in urine" in symptoms:
        possible.append("Bladder Cancer")
        organ_mapping.append("Bladder")
        severity = "High"

    if gender == "Male":
        if "Prostate issues (frequent urination, weak stream, pelvic pain)" in symptoms:
            possible.append("Prostate Cancer")
            organ_mapping.append("Prostate")
            severity = "High"
        if "Testicular lumps or swelling" in symptoms:
            possible.append("Testicular Cancer")
            organ_mapping.append("Testicles")
            severity = "High"
    else:
        if "Breast lump or thickening" in symptoms or "Unusual nipple discharge" in symptoms:
            possible.append("Breast Cancer")
            organ_mapping.append("Breast")
            severity = "High"
        if "Pelvic pain or bloating (ovarian)" in symptoms or "Abnormal vaginal bleeding" in symptoms:
            possible.append("Ovarian / Cervical Cancer")
            organ_mapping.append("Ovaries / Cervix")
            severity = "High"

    # Viral Diseases
    if any(s in symptoms for s in malaria_symptoms):
        possible.append("Malaria")
        organ_mapping.append("Blood / Liver / Spleen")
        severity = "Medium"
    if any(s in symptoms for s in typhoid_symptoms):
        possible.append("Typhoid")
        organ_mapping.append("Digestive System / Liver")
        severity = "Medium"
    if any(s in symptoms for s in dengue_symptoms):
        possible.append("Dengue")
        organ_mapping.append("Blood / Immune System / Skin")
        severity = "Medium"

    # Heart Issue
    if any(s in symptoms for s in heart_symptoms):
        possible.append("Heart Issue / Cardiovascular Risk")
        organ_mapping.append("Heart / Circulatory System")
        severity = "High"

    return list(set(possible)), list(set(organ_mapping)), severity

# ---------- SHOW RESULTS ----------
if submitted:
    if not name or not mobile:
        st.error("Please enter your Name and Mobile Number.")
    elif not symptoms_selected:
        st.warning("Please select at least one symptom.")
    else:
        results, organs, severity = diagnose(symptoms_selected, gender)

        # Color coding severity
        if severity == "High":
            color = "red"
        elif severity == "Medium":
            color = "orange"
        else:
            color = "green"

        # Display summary
        st.markdown(f"<h3 style='color:{color}'>⚠️ Severity: {severity}</h3>", unsafe_allow_html=True)
        if results:
            for r, o in zip(results, organs):
                st.markdown(f"**🔸 {r} → Possible Organ/System:** {o}")
        else:
            st.info("No significant disease indicators detected.")

        # Quick action buttons
        st.markdown("### ⏱ Quick Actions")
        st.markdown(
            "[📞 Call Emergency Number](tel:+911)")  # Replace with local emergency number
        st.markdown("[📋 Contact Doctor / Clinic](mailto:doctor@example.com)")  # Replace with actual

        # Save to Google Sheet
        data = [
            name, age, gender, mobile, bp, diabetes, heart, location,
            ", ".join(symptoms_selected), ", ".join(results), ", ".join(organs), severity
        ]
        sheet.append_row(data)
        st.success("✅ Your response has been recorded securely.")
