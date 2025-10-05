import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="🧠 Symptom-Based Disease Checker", page_icon="🧪", layout="wide")

# ---------- GOOGLE SHEETS CONNECTION ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_NAME = "symptom_records"
sheet = CLIENT.open(SHEET_NAME).sheet1

# ---------- TITLE ----------
st.title("🧠 Symptom-Based Disease Checker")
st.write("Select symptoms to check possible diseases and calculate risk score based on age, BMI, and medical history.")

# ---------- USER FORM ----------
with st.form("user_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Full Name")
        age = st.number_input("🎂 Age", min_value=0, max_value=120, step=1)
        gender = st.radio("⚧ Gender", ["Male", "Female"])
        mobile = st.text_input("📱 Mobile Number")
        location = st.text_input("📍 Location / City")
        weight = st.number_input("⚖️ Weight (kg)", min_value=0.0, step=0.1)
        height = st.number_input("📏 Height (cm)", min_value=0.0, step=0.1)
    with col2:
        st.subheader("🩺 Medical History")
        bp = st.checkbox("High Blood Pressure")
        diabetes = st.checkbox("Diabetes")
        heart_history = st.checkbox("Heart Issues")
        thyroid = st.checkbox("Thyroid Disorder")

    st.subheader("🧍 Select Symptoms")

    # ---------- SYMPTOM LISTS ----------
    basic_symptoms = [
        "Fever", "Chills", "Headache", "Fatigue", "Nausea", "Vomiting", "Cough", "Loss of appetite",
        "Muscle aches", "Sore throat", "Runny nose", "Body pain", "Sneezing", "Mild abdominal discomfort",
        "Night sweats", "Mild dizziness", "Irritability", "Loss of smell", "Loss of taste", "Malaise"
    ]

    advanced_symptoms = [
        "Abdominal pain", "Diarrhea", "Joint pain", "Pain behind the eyes",
        "Swollen glands", "Rapid breathing", "Rapid heart rate", "Rose spots rash",
        "Constipation", "Swelling in legs", "Chest pain", "Jaundice", "Severe dehydration",
        "Severe headache", "Extreme tiredness", "Persistent high-grade fever", "Shivering",
        "Nosebleeds", "Bleeding gums", "Dark-colored urine", "Pale skin", "Persistent vomiting",
        "Enlarged spleen", "Confusion or delirium", "Seizures", "Light sensitivity", "Neck stiffness"
    ]

    heart_symptoms = [
        "Shortness of breath", "Swelling in ankles", "Irregular heartbeat",
        "Chest pain or pressure", "Pain in jaw/neck/back", "Sudden dizziness",
        "Extreme fatigue", "Wheezing", "Swelling in abdomen", "Rapid or irregular pulse",
        "Fainting spells", "Cold sweats", "Bluish lips or fingers", "Palpitations",
        "Reduced ability to exercise", "Difficulty breathing when lying flat",
        "Unexplained coughing with pink mucus", "Sudden severe shortness of breath at night"
    ]

    cancer_symptoms_male = [
        "Unexplained weight loss", "Persistent fatigue", "Lump or swelling", "Persistent cough",
        "Difficulty swallowing", "Blood in urine", "Rectal bleeding", "Changes in bowel habits",
        "Prolonged pain in bones", "Chronic headaches", "Hoarseness or voice change",
        "Non-healing ulcers", "Unexplained bleeding", "Skin changes or moles changing",
        "Difficulty urinating", "Persistent back pain", "Swelling of testicles",
        "Chronic indigestion or heartburn", "Unexplained night sweats", "Unexplained fever"
    ]

    cancer_symptoms_female = [
        "Breast lump or thickening", "Changes in breast shape", "Nipple discharge",
        "Unusual vaginal bleeding", "Pelvic pain", "Persistent bloating", "Pain during intercourse",
        "Changes in menstrual cycle", "Unexplained weight loss", "Chronic fatigue",
        "Skin changes on breast", "Retraction of nipple", "Bloody nipple discharge",
        "Unusual vaginal discharge", "Lump in pelvic area", "Difficulty urinating",
        "Lower back pain", "Persistent abdominal bloating", "Painful urination",
        "Unexpected post-menopausal bleeding", "Persistent cough", "Voice changes",
        "Non-healing mouth ulcers", "Swollen lymph nodes in armpit or groin"
    ]

    neurological_symptoms = [
        "Severe headache", "Sudden weakness on one side", "Difficulty speaking",
        "Loss of balance", "Seizures", "Sudden confusion", "Double vision",
        "Facial drooping", "Numbness or tingling", "Loss of consciousness"
    ]

    respiratory_symptoms = [
        "Shortness of breath", "Cough with phlegm", "Chest tightness", "Wheezing",
        "Coughing blood", "Rapid shallow breathing", "Painful breathing",
        "Persistent dry cough", "Loss of smell", "Bluish skin or lips"
    ]

    # ---------- USER SELECTION ----------
    selected_basic = st.multiselect("Basic Symptoms", basic_symptoms)
    selected_advanced = st.multiselect("Advanced Symptoms", advanced_symptoms)
    selected_heart = st.multiselect("Heart Symptoms", heart_symptoms)
    selected_cancer_male = st.multiselect("Male Cancer Symptoms", cancer_symptoms_male)
    selected_cancer_female = st.multiselect("Female Cancer Symptoms", cancer_symptoms_female)
    selected_neuro = st.multiselect("Neurological Symptoms", neurological_symptoms)
    selected_respiratory = st.multiselect("Respiratory Symptoms", respiratory_symptoms)

    submitted = st.form_submit_button("🔍 Diagnose")

# ---------- BMI CALCULATION ----------
def calculate_bmi(weight, height_cm):
    if weight > 0 and height_cm > 0:
        h_m = height_cm / 100
        bmi = weight / (h_m ** 2)
        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 25:
            category = "Normal"
        elif 25 <= bmi < 30:
            category = "Overweight"
        else:
            category = "Obesity"
        return round(bmi, 1), category
    return None, None

# ---------- DIAGNOSIS FUNCTION ----------
def diagnose(symptoms, age, bmi_category):
    results = []
    organs = []

    # Viral / Typhoid / Dengue
    if "Fever" in symptoms:
        if "Rash" in symptoms or "Pain behind the eyes" in symptoms:
            results.append("Dengue / Viral Infection")
            organs.append("Blood / Immune System")
        elif "Diarrhea" in symptoms:
            results.append("Typhoid / Bacterial Infection")
            organs.append("Digestive System")
        else:
            results.append("Viral Fever")
            organs.append("Immune System")

    # Malaria
    if "Fever" in symptoms and "Chills" in symptoms and "Abdominal pain" in symptoms:
        results.append("Malaria")
        organs.append("Blood / Liver / Digestive System")

    # Heart
    if any(s in heart_symptoms for s in symptoms):
        results.append("Heart / Cardiovascular Risk")
        organs.append("Heart / Circulatory System")

    # Cancer
    if any(s in cancer_symptoms_male + cancer_symptoms_female for s in symptoms):
        results.append("Possible Cancer Risk")
        organs.append("Affected Organs based on Symptoms")

    # Respiratory / Neurological
    if any(s in respiratory_symptoms for s in symptoms):
        results.append("Respiratory Illness (e.g., Pneumonia, TB, COVID)")
        organs.append("Lungs / Airways")
    if any(s in neurological_symptoms for s in symptoms):
        results.append("Neurological Condition Risk (e.g., Stroke, Meningitis)")
        organs.append("Nervous System")

    # Risk Score
    risk_score = len(symptoms) * 4 + (age / 2)
    if bmi_category in ["Overweight", "Obesity"]:
        risk_score += 10
    risk_score = min(100, risk_score)

    return results, organs, risk_score

# ---------- RESULT SECTION ----------
if submitted:
    if not name or not mobile:
        st.error("Please fill in Name and Mobile Number.")
    else:
        all_symptoms = (
            selected_basic + selected_advanced + selected_heart +
            selected_cancer_male + selected_cancer_female +
            selected_neuro + selected_respiratory
        )

        bmi, bmi_category = calculate_bmi(weight, height)
        results, organs, risk = diagnose(all_symptoms, age, bmi_category)

        if bmi:
            st.info(f"**BMI:** {bmi} ({bmi_category})")

        if results:
            st.success("✅ **Possible Conditions Detected:**")
            for r, o in zip(results, organs):
                st.write(f"🔸 {r} → **Organ/System:** {o}")
            st.warning(f"**Estimated Risk Score:** {risk:.1f}%")
        else:
            st.info("No significant disease indicators found.")

        # ---------- SAVE TO GOOGLE SHEET ----------
        data = [
            name, age, gender, mobile, location, weight, height, bmi, bmi_category,
            bp, diabetes, heart_history, thyroid,
            ", ".join(all_symptoms),
            ", ".join(results), ", ".join(organs), f"{risk:.1f}%"
        ]
        sheet.append_row(data)
        st.success("📊 Your response has been recorded securely.")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚠️ This tool is for educational/demo purposes only. It does not replace professional medical advice.")
