import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================
# GOOGLE SHEET CONNECTION
# ==========================
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, SCOPE)
CLIENT = gspread.authorize(CREDS)

SHEET_NAME = "Medical_Symptom_Records"
SHEET = CLIENT.open(SHEET_NAME).sheet1

# ==========================
# HELPER FUNCTIONS
# ==========================
def calculate_bmi(weight, height_cm):
    if height_cm <= 0:
        return 0, "Invalid"
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    if bmi < 18.5:
        return round(bmi, 1), "Underweight"
    elif 18.5 <= bmi < 24.9:
        return round(bmi, 1), "Normal"
    elif 25 <= bmi < 29.9:
        return round(bmi, 1), "Overweight"
    else:
        return round(bmi, 1), "Obese"

def save_to_google_sheet(data):
    SHEET.append_row([
        data["timestamp"],
        data["name"],
        data["age"],
        data["gender"],
        data["height"],
        data["weight"],
        data["bmi"],
        data["bmi_category"],
        data["medical_history"],
        ", ".join(data["symptoms"]),
        ", ".join(data["conditions"]),
        data["risk_score"],
        data["feedback"]
    ])

def match_conditions(symptoms, gender):
    matched = []

    # Basic Viral Fever
    basic = {"Fever", "Headache", "Fatigue", "Chills", "Cough"}
    if basic.intersection(symptoms):
        matched.append("Viral Fever")

    # Malaria
    malaria = {"Fever", "Chills", "Headache", "Nausea", "Vomiting", "Diarrhea", "Abdominal pain", "Muscle pain", "Fatigue", "Rapid breathing", "Rapid heart rate", "Cough"}
    if malaria.intersection(symptoms):
        matched.append("Malaria")

    # Typhoid
    typhoid = {"Headache", "Chills", "Loss of appetite", "Abdominal pain", "Rose spots", "Cough", "Muscle aches", "Nausea", "Vomiting", "Diarrhea", "Constipation"}
    if typhoid.intersection(symptoms):
        matched.append("Typhoid Fever")

    # Dengue
    dengue = {"Headache", "Muscle pain", "Joint pain", "Nausea", "Vomiting", "Pain behind the eyes", "Swollen glands", "Rash"}
    if dengue.intersection(symptoms):
        matched.append("Dengue")

    # Heart Issues
    heart = {"Shortness of breath", "Fatigue", "Swelling in legs", "Rapid heartbeat", "Irregular heartbeat",
             "Reduced ability to exercise", "Wheezing", "Cough with pink mucus", "Swelling belly",
             "Rapid weight gain", "Nausea", "Difficulty concentrating", "Chest pain", "Pain in neck", "Pain in jaw",
             "Pain in throat", "Pain in back"}
    if heart.intersection(symptoms):
        matched.append("Heart Disease Risk")

    # Cancer Symptoms (Male & Female common)
    cancer_common = {"Unexplained weight loss", "Unusual bleeding", "Fatigue", "Persistent cough",
                     "Change in bowel habits", "Lump or swelling", "Loss of appetite", "Skin changes",
                     "Pain without cause", "Frequent infections", "Difficulty swallowing", "Persistent pain"}
    if cancer_common.intersection(symptoms):
        matched.append("Possible Cancer Symptoms (Common)")

    # Female-specific cancer symptoms
    if gender == "Female":
        female_cancer = {"Abnormal vaginal bleeding", "Pelvic pain", "Unusual vaginal discharge", "Breast lump",
                         "Change in breast shape", "Nipple discharge", "Pain during intercourse"}
        if female_cancer.intersection(symptoms):
            matched.append("Female Cancer Symptoms")

    return list(set(matched))


# ==========================
# UI LAYOUT
# ==========================
st.set_page_config(page_title="Medical Symptom Checker", layout="centered")
st.title("🧠 Medical Symptom & Health Checker")

# --------------------------
# USER INFO
# --------------------------
st.subheader("👤 User Information")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
with col2:
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

# Medical history (checkboxes)
medical_history = st.multiselect(
    "Medical History",
    ["Thyroid", "Diabetes", "Hypertension", "Heart Disease", "Cancer", "None"]
)

# BMI Section
st.subheader("📏 BMI Calculator")
col3, col4 = st.columns(2)
with col3:
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
with col4:
    height = st.number_input("Height (cm)", min_value=0.0, step=0.1)

bmi, bmi_category = calculate_bmi(weight, height)
st.write(f"**Your BMI:** {bmi} ({bmi_category})")

# --------------------------
# SYMPTOMS SELECTION
# --------------------------
st.subheader("🦠 Select Your Symptoms")
all_symptoms = sorted(list({
    "Fever", "Headache", "Fatigue", "Chills", "Cough",
    "Nausea", "Vomiting", "Diarrhea", "Abdominal pain", "Muscle pain", "Joint pain",
    "Loss of appetite", "Rose spots", "Pain behind the eyes", "Swollen glands", "Rash",
    "Shortness of breath", "Swelling in legs", "Rapid heartbeat", "Irregular heartbeat",
    "Reduced ability to exercise", "Wheezing", "Cough with pink mucus", "Swelling belly",
    "Rapid weight gain", "Difficulty concentrating", "Chest pain", "Pain in neck", "Pain in jaw",
    "Pain in throat", "Pain in back", "Unexplained weight loss", "Unusual bleeding", "Change in bowel habits",
    "Lump or swelling", "Skin changes", "Pain without cause", "Frequent infections", "Difficulty swallowing",
    "Persistent pain", "Abnormal vaginal bleeding", "Pelvic pain", "Unusual vaginal discharge", "Breast lump",
    "Change in breast shape", "Nipple discharge", "Pain during intercourse"
}))
selected_symptoms = st.multiselect("Choose symptoms", all_symptoms)

# --------------------------
# SUBMIT
# --------------------------
if st.button("📝 Submit"):
    if not name or not age or not gender:
        st.warning("Please fill all user information fields.")
    else:
        conditions = match_conditions(set(selected_symptoms), gender)

        # Simple Risk Scoring
        risk_score = "Low"
        if len(conditions) >= 3 or bmi_category in ["Overweight", "Obese"]:
            risk_score = "Medium"
        if "Cancer" in " ".join(conditions) or "Heart" in " ".join(conditions):
            risk_score = "High"

        feedback_text = f"Your risk level is **{risk_score}** based on selected symptoms and BMI."

        st.success("✅ Data submitted successfully!")
        st.write(f"**Matched Conditions:** {', '.join(conditions) if conditions else 'No match found'}")
        st.info(feedback_text)

        # ==========================
        # SAVE TO GOOGLE SHEET WITH DATE & TIME
        # ==========================
        entry_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "bmi_category": bmi_category,
            "medical_history": ", ".join(medical_history),
            "symptoms": selected_symptoms,
            "conditions": conditions,
            "risk_score": risk_score,
            "feedback": feedback_text
        }
        save_to_google_sheet(entry_data)
