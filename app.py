import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# ---------- GOOGLE SHEETS CONNECTION ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_NAME = "symptom_records"
sheet = CLIENT.open(SHEET_NAME).sheet1

# ---------- APP TITLE ----------
st.set_page_config(page_title="Symptom-Based Disease Checker", page_icon="🧪", layout="wide")
st.title("🧠 Symptom-Based Disease Checker with Body Mapping")

# ---------- USER DETAILS ----------
with st.form("user_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Full Name")
        age = st.number_input("🎂 Age", min_value=0, max_value=120, step=1)
        gender = st.radio("⚧ Gender", ["Male", "Female"])
        mobile = st.text_input("📱 Mobile Number")
        weight = st.number_input("⚖ Weight (kg)", min_value=1, max_value=300)
        height = st.number_input("📏 Height (cm)", min_value=50, max_value=250)
    with col2:
        st.subheader("🩺 Medical History")
        bp = st.checkbox("High Blood Pressure")
        diabetes = st.checkbox("Diabetes")
        heart = st.checkbox("Heart Issues")
        thyroid = st.checkbox("Thyroid Issues")
        location = st.text_input("📍 Location / City")

    st.subheader("🧍 Select Symptoms")
    basic_symptoms = ["Fever", "Chills", "Fatigue", "Headache", "Nausea / Vomiting", "Muscle / Joint Pain"]
    advanced_symptoms = ["Diarrhea", "Abdominal Pain", "Loss of Appetite", "Rash", "Cough",
                         "Pain behind eyes", "Swollen glands", "Yellow skin / Eyes", "Weakness"]
    heart_symptoms = ["Chest pain / Pressure", "Pain radiating to arm/jaw/back/neck/throat",
                      "Shortness of breath", "Rapid / Irregular heartbeat", "Swelling in legs/ankles/feet",
                      "Reduced exercise ability", "Wheezing / Persistent cough", "Swelling of belly",
                      "Rapid weight gain", "Nausea / Lack of appetite", "Difficulty concentrating",
                      "Dizziness / Fainting", "Cold sweats"]
    cancer_symptoms = ["Breast lump / Thickening", "Unusual nipple discharge", "Pelvic pain / Bloating",
                       "Abdominal pain / Bloating", "Prostate issues", "Testicular lumps / swelling",
                       "Unusual bleeding / bruising", "Pain that doesn't go away", "Mouth sores / bleeding / numbness",
                       "Persistent cough / Hoarseness", "Unexplained weight loss / gain", "Swelling or lumps",
                       "Skin changes / Jaundice / new moles", "Headaches / Seizures", "Fatigue / Extreme tiredness",
                       "Vision or hearing problems"]

    selected_basic = st.multiselect("Basic Symptoms", basic_symptoms)
    selected_advanced = st.multiselect("Advanced Symptoms", advanced_symptoms)
    selected_cancer = st.multiselect("Cancer Symptoms", cancer_symptoms)
    selected_heart = st.multiselect("Heart / Cardiovascular Symptoms", heart_symptoms)
    submitted = st.form_submit_button("🔍 Diagnose")

# ---------- BMI Calculation ----------
def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category

# ---------- Diagnosis Logic ----------
def diagnose(basic, advanced, cancer, heart, age):
    possible = []
    organs = []
    risk_score = 0
    all_symptoms = basic + advanced + cancer + heart
    symptom_count = len(all_symptoms)

    # Viral / Fever / Bacterial
    if "Fever" in basic:
        if any(s in advanced for s in ["Diarrhea", "Rash", "Pain behind eyes"]):
            if "Rash" in advanced or "Pain behind eyes" in advanced:
                possible.append("Dengue / Viral Infection")
                organs.append("Blood / Immune System")
            elif "Diarrhea" in advanced:
                possible.append("Typhoid / Bacterial Infection")
                organs.append("Digestive System")
            else:
                possible.append("Viral Fever")
                organs.append("Immune System")

    if "Fatigue" in basic and "Diarrhea" in advanced and "Abdominal Pain" in advanced:
        possible.append("Malaria")
        organs.append("Blood / Liver / Joints")

    if cancer:
        possible.append("Possible Cancer Detected")
        organs.append("Affected Organs")

    if heart:
        possible.append("Heart / Cardiovascular Risk")
        organs.append("Heart / Circulatory System")

    risk_score = min(100, symptom_count * 5 + (age / 2))
    return possible, organs, risk_score

# ---------- Symptom → Body Part Mapping ----------
symptom_body_map = {
    "Headache": (200, 50), "Vision or hearing problems": (200, 60),
    "Chest pain / Pressure": (200, 250), "Shortness of breath": (200, 260),
    "Breast lump / Thickening": (180, 180), "Unusual nipple discharge": (220, 180),
    "Abdominal pain / Bloating": (200, 300), "Pelvic pain / Bloating": (200, 350),
    "Leg swelling": (200, 450), "Fatigue": (200, 200),
}

# ---------- Show Results ----------
if submitted:
    if not name or not mobile:
        st.error("Please enter your Name and Mobile Number.")
    else:
        bmi_value, bmi_category = calculate_bmi(weight, height)
        results, organs, risk = diagnose(selected_basic, selected_advanced, selected_cancer, selected_heart, age)

        st.success(f"**BMI:** {bmi_value:.1f} → Category: {bmi_category}")
        if results:
            st.success(f"**Possible Conditions Detected:**")
            for r, o in zip(results, organs):
                st.write(f"🔸 {r} → Possible organ/system: {o}")
            st.info(f"**Estimated Risk Score:** {risk:.1f}%")
        else:
            st.info("No significant disease indicators found based on selected symptoms.")

        # ---------- Display Human Body ----------
        st.subheader("🧍 Symptom Mapping on Human Body")
        body_img = Image.new("RGB", (400, 600), "white")  # Replace with body image if available
        draw = ImageDraw.Draw(body_img)
        for s in selected_basic + selected_advanced + selected_cancer + selected_heart:
            if s in symptom_body_map:
                x, y = symptom_body_map[s]
                draw.ellipse((x-10, y-10, x+10, y+10), fill="red")
                draw.text((x+15, y-5), s, fill="black")
        st.image(body_img, use_column_width=True)

        # ---------- Save to Google Sheet ----------
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [
            entry_time, name, age, gender, mobile, bp, diabetes, heart, thyroid, location,
            ", ".join(selected_basic + selected_advanced + selected_cancer + selected_heart),
            ", ".join(results), ", ".join(organs), f"{risk:.1f}%", f"{bmi_value:.1f}", bmi_category
        ]
        sheet.append_row(data)
        st.success("✅ Your response has been recorded securely.")
