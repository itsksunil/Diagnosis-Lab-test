import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime
import pandas as pd

# ---------- GOOGLE SHEETS CONNECTION ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_NAME = "symptom_records"
sheet = CLIENT.open(SHEET_NAME).sheet1

# ---------- APP TITLE ----------
st.set_page_config(page_title="Advanced Symptom-Based Disease Checker", page_icon="🏥", layout="wide")
st.title("🏥 Advanced Symptom-Based Disease Checker")
st.write("Select symptoms and see possible disease risks with detailed analysis.")

# ---------- USER DETAILS FORM ----------
with st.form("user_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Full Name")
        age = st.number_input("🎂 Age", min_value=0, max_value=120, step=1)
        gender = st.radio("⚧ Gender", ["Male", "Female", "Other"])
        mobile = st.text_input("📱 Mobile Number")
        weight = st.number_input("⚖ Weight (kg)", min_value=1, max_value=300)
        height = st.number_input("📏 Height (cm)", min_value=50, max_value=250)
        
    with col2:
        st.subheader("🩺 Medical History")
        bp = st.checkbox("High Blood Pressure")
        diabetes = st.checkbox("Diabetes")
        heart = st.checkbox("Heart Issues")
        thyroid = st.checkbox("Thyroid Issues")
        asthma = st.checkbox("Asthma/Respiratory Issues")
        kidney = st.checkbox("Kidney Disease")
        liver = st.checkbox("Liver Disease")
        cancer_history = st.checkbox("Family History of Cancer")
        location = st.text_input("📍 Location / City")

    st.subheader("🧍 Select Symptoms")

    # ---------- ENHANCED SYMPTOM LISTS ----------
    basic_symptoms = [
        "Fever", "Chills", "Fatigue", "Headache", "Nausea", "Vomiting", 
        "Muscle Pain", "Joint Pain", "Weakness", "Dizziness"
    ]
    
    respiratory_symptoms = [
        "Cough", "Shortness of Breath", "Chest Congestion", "Runny Nose", 
        "Sore Throat", "Sneezing", "Wheezing", "Loss of Smell", "Loss of Taste"
    ]
    
    digestive_symptoms = [
        "Diarrhea", "Abdominal Pain", "Loss of Appetite", "Bloating", 
        "Constipation", "Heartburn", "Blood in Stool", "Difficulty Swallowing",
        "Excessive Thirst", "Frequent Urination"
    ]
    
    neurological_symptoms = [
        "Confusion", "Memory Problems", "Numbness", "Tingling Sensation",
        "Vision Problems", "Hearing Problems", "Balance Issues", "Seizures",
        "Speech Difficulties", "Tremors"
    ]
    
    skin_symptoms = [
        "Rash", "Itching", "Yellow Skin/Eyes", "New Moles", "Skin Discoloration",
        "Hives", "Swelling", "Bruising Easily", "Hair Loss", "Night Sweats"
    ]
    
    heart_symptoms = [
        "Chest Pain/Pressure", "Pain Radiating to Arm/Jaw/Back", 
        "Shortness of Breath", "Rapid/Irregular Heartbeat", "Swelling in Legs/Ankles",
        "Reduced Exercise Ability", "Persistent Cough", "Abdominal Swelling",
        "Rapid Weight Gain", "Cold Sweats", "Palpitations"
    ]
    
    cancer_symptoms = [
        "Breast Lump/Thickening", "Unusual Nipple Discharge", "Pelvic Pain/Bloating",
        "Abdominal Pain/Bloating", "Prostate Issues", "Testicular Lumps/Swelling",
        "Unusual Bleeding/Bruising", "Persistent Pain", "Mouth Sores/Bleeding",
        "Persistent Cough/Hoarseness", "Unexplained Weight Loss", "Swelling/Lumps",
        "Skin Changes/Jaundice", "Persistent Headaches", "Extreme Fatigue",
        "Vision/Hearing Problems", "Difficulty Swallowing", "Changes in Bowel Habits"
    ]

    # User symptom selection
    selected_basic = st.multiselect("General Symptoms", basic_symptoms)
    selected_respiratory = st.multiselect("Respiratory Symptoms", respiratory_symptoms)
    selected_digestive = st.multiselect("Digestive Symptoms", digestive_symptoms)
    selected_neurological = st.multiselect("Neurological Symptoms", neurological_symptoms)
    selected_skin = st.multiselect("Skin & Appearance Symptoms", skin_symptoms)
    selected_cancer = st.multiselect("Cancer Symptoms", cancer_symptoms)
    selected_heart = st.multiselect("Heart & Circulatory Symptoms", heart_symptoms)

    # Additional information
    st.subheader("📋 Additional Information")
    col3, col4 = st.columns(2)
    with col3:
        symptom_duration = st.selectbox("How long have you had these symptoms?", 
                                      ["Less than 1 week", "1-2 weeks", "2-4 weeks", "1-3 months", "More than 3 months"])
        severity = st.select_slider("Symptom Severity", options=["Mild", "Moderate", "Severe"])
    with col4:
        smoking = st.checkbox("Smoker")
        alcohol = st.checkbox("Regular Alcohol Consumption")
        exercise = st.selectbox("Exercise Frequency", 
                              ["Never", "Occasionally", "1-2 times/week", "3-5 times/week", "Daily"])

    submitted = st.form_submit_button("🔍 Analyze Symptoms")

# ---------- BMI CALCULATION ----------
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

# ---------- ENHANCED DIAGNOSIS LOGIC ----------
def enhanced_diagnose(basic, respiratory, digestive, neurological, skin, cancer, heart, age, medical_history, lifestyle):
    conditions = []
    risk_factors = []
    recommendations = []
    risk_score = 0
    
    all_symptoms = basic + respiratory + digestive + neurological + skin + cancer + heart
    symptom_count = len(all_symptoms)
    
    # Risk factors from medical history and lifestyle
    if medical_history.get('bp'): risk_factors.append("Hypertension")
    if medical_history.get('diabetes'): risk_factors.append("Diabetes")
    if medical_history.get('heart'): risk_factors.append("Cardiac History")
    if medical_history.get('smoking'): risk_factors.append("Smoking")
    if medical_history.get('alcohol'): risk_factors.append("Alcohol Use")
    
    # INFECTIOUS DISEASES ANALYSIS
    if "Fever" in basic:
        if "Cough" in respiratory and "Shortness of Breath" in respiratory:
            conditions.append(("Respiratory Infection (COVID-19/Influenza/Pneumonia)", "Respiratory System", "High"))
        if "Diarrhea" in digestive and "Abdominal Pain" in digestive:
            conditions.append(("Gastrointestinal Infection", "Digestive System", "Medium"))
        if "Rash" in skin and "Joint Pain" in basic:
            conditions.append(("Viral Infection (Dengue/Chikungunya)", "Immune System", "High"))
        if "Yellow Skin/Eyes" in skin:
            conditions.append(("Hepatitis/Liver Infection", "Liver", "High"))
    
    # RESPIRATORY CONDITIONS
    respiratory_symptom_count = len(respiratory)
    if respiratory_symptom_count >= 2:
        if "Wheezing" in respiratory and "Shortness of Breath" in respiratory:
            conditions.append(("Asthma/Bronchitis", "Respiratory System", "Medium"))
        if "Chest Congestion" in respiratory and "Cough" in respiratory:
            conditions.append(("Bronchitis/Upper Respiratory Infection", "Respiratory System", "Medium"))
    
    # DIGESTIVE CONDITIONS
    digestive_symptom_count = len(digestive)
    if digestive_symptom_count >= 3:
        if "Blood in Stool" in digestive or "Difficulty Swallowing" in digestive:
            conditions.append(("Gastrointestinal Disorder (IBD/Ulcers)", "Digestive System", "High"))
        elif "Bloating" in digestive and "Abdominal Pain" in digestive:
            conditions.append(("Irritable Bowel Syndrome", "Digestive System", "Medium"))
    
    # NEUROLOGICAL CONDITIONS
    neurological_symptom_count = len(neurological)
    if neurological_symptom_count >= 2:
        if "Headache" in basic and "Vision Problems" in neurological:
            conditions.append(("Migraine/Neurological Disorder", "Nervous System", "Medium"))
        if "Numbness" in neurological and "Tingling Sensation" in neurological:
            conditions.append(("Neuropathy", "Nervous System", "Medium"))
    
    # CARDIOVASCULAR RISK ASSESSMENT
    heart_symptom_count = len(heart)
    if heart_symptom_count >= 2:
        conditions.append(("Cardiovascular Issue", "Heart/Circulatory System", "High"))
        if "Chest Pain/Pressure" in heart:
            recommendations.append("🚨 Seek immediate medical attention for chest pain")
    
    # CANCER RISK ASSESSMENT
    cancer_symptom_count = len(cancer)
    if cancer_symptom_count >= 2:
        risk_level = "High" if cancer_symptom_count >= 3 or medical_history.get('cancer_history') else "Medium"
        conditions.append(("Possible Cancer Indicators", "Multiple Systems", risk_level))
        recommendations.append("Consult with oncologist for further evaluation")
    
    # LIFESTYLE RISK ASSESSMENT
    if lifestyle.get('exercise') in ["Never", "Occasionally"] and medical_history.get('bp'):
        risk_factors.append("Sedentary Lifestyle")
        recommendations.append("Increase physical activity to 150 minutes per week")
    
    # Calculate comprehensive risk score
    base_score = min(symptom_count * 4, 40)  # Up to 40% from symptoms
    age_score = min(age * 0.5, 20)  # Up to 20% from age
    medical_score = len(risk_factors) * 5  # Up to 25% from medical history
    lifestyle_score = 0
    if lifestyle.get('smoking'): lifestyle_score += 10
    if lifestyle.get('alcohol'): lifestyle_score += 5
    if lifestyle.get('exercise') in ["Never", "Occasionally"]: lifestyle_score += 5
    
    risk_score = min(base_score + age_score + medical_score + lifestyle_score, 95)
    
    # Add general recommendations based on risk factors
    if risk_score > 50:
        recommendations.append("Schedule appointment with primary care physician")
    if symptom_count > 5:
        recommendations.append("Consider comprehensive medical evaluation")
    
    return conditions, risk_factors, recommendations, risk_score

# ---------- SHOW RESULTS ----------
if submitted:
    if not name or not mobile:
        st.error("❌ Please enter your Name and Mobile Number.")
    else:
        # Calculate BMI
        bmi_value, bmi_category = calculate_bmi(weight, height)
        
        # Prepare data for diagnosis
        medical_history = {
            'bp': bp, 'diabetes': diabetes, 'heart': heart, 'thyroid': thyroid,
            'asthma': asthma, 'kidney': kidney, 'liver': liver, 'cancer_history': cancer_history
        }
        
        lifestyle = {
            'smoking': smoking, 'alcohol': alcohol, 'exercise': exercise
        }
        
        # Perform diagnosis
        conditions, risk_factors, recommendations, risk_score = enhanced_diagnose(
            selected_basic, selected_respiratory, selected_digestive, 
            selected_neurological, selected_skin, selected_cancer, 
            selected_heart, age, medical_history, lifestyle
        )

        # Display results
        st.success("## 📊 Analysis Results")
        
        # BMI and basic info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BMI Score", f"{bmi_value:.1f}", bmi_category)
        with col2:
            st.metric("Overall Risk Score", f"{risk_score:.1f}%")
        with col3:
            st.metric("Symptoms Reported", len(selected_basic + selected_respiratory + selected_digestive + 
                                            selected_neurological + selected_skin + selected_cancer + selected_heart))
        
        # Conditions detected
        if conditions:
            st.warning("## 🚨 Possible Conditions Detected")
            for condition, system, risk_level in conditions:
                risk_color = "🔴" if risk_level == "High" else "🟡" if risk_level == "Medium" else "🟢"
                st.write(f"{risk_color} **{condition}**")
                st.write(f"   • Affected System: {system}")
                st.write(f"   • Risk Level: {risk_level}")
                st.write("")
        else:
            st.info("## ✅ No significant disease indicators detected")
        
        # Risk factors
        if risk_factors:
            st.error("## ⚠️ Identified Risk Factors")
            for factor in risk_factors:
                st.write(f"• {factor}")
        
        # Recommendations
        if recommendations:
            st.success("## 💡 Recommendations")
            for recommendation in recommendations:
                st.write(f"• {recommendation}")
        
        # General health tips
        st.info("## 🌟 General Health Tips")
        if bmi_category in ["Overweight", "Obese"]:
            st.write("• Consider weight management through balanced diet and exercise")
        if age > 50:
            st.write("• Regular health screenings recommended due to age")
        if not risk_factors and risk_score < 30:
            st.write("• Maintain current healthy lifestyle with regular checkups")

        # ---------- SAVE DATA TO GOOGLE SHEET ----------
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        all_symptoms = selected_basic + selected_respiratory + selected_digestive + selected_neurological + selected_skin + selected_cancer + selected_heart
        condition_list = [f"{cond} ({risk})" for cond, sys, risk in conditions]
        
        data = [
            entry_time, name, age, gender, mobile, bp, diabetes, heart, thyroid, 
            asthma, kidney, liver, cancer_history, location, weight, height,
            ", ".join(all_symptoms), symptom_duration, severity,
            smoking, alcohol, exercise, ", ".join(condition_list),
            ", ".join(risk_factors), f"{risk_score:.1f}%", f"{bmi_value:.1f}", bmi_category
        ]
        
        try:
            sheet.append_row(data)
            st.success("✅ Your response has been recorded securely.")
        except Exception as e:
            st.error(f"⚠️ Could not save to database: {str(e)}")

# ---------- SIDEBAR WITH ADDITIONAL FEATURES ----------
with st.sidebar:
    st.header("ℹ️ About This Tool")
    st.write("""
    This advanced symptom checker analyzes your symptoms against:
    - Infectious diseases
    - Respiratory conditions  
    - Digestive disorders
    - Neurological issues
    - Cardiovascular risks
    - Cancer indicators
    """)
    
    st.header("📈 Health Metrics")
    if submitted and 'bmi_value' in locals():
        st.metric("Your BMI", f"{bmi_value:.1f}")
        st.metric("Risk Score", f"{risk_score:.1f}%")
        
        # BMI chart
        bmi_data = pd.DataFrame({
            'Category': ['Underweight', 'Normal', 'Overweight', 'Obese'],
            'Range': ['<18.5', '18.5-24.9', '25-29.9', '30+']
        })
        st.dataframe(bmi_data, hide_index=True)
    
    st.header("🚨 Emergency Symptoms")
    st.write("""
    Seek immediate medical care for:
    - Chest pain/pressure
    - Difficulty breathing
    - Severe abdominal pain
    - Sudden weakness/numbness
    - Suicidal thoughts
    - Severe bleeding
    """)

# ---------- FOOTER ----------
st.markdown("---")
st.caption("""
⚠️ **Disclaimer**: This tool is for educational and informational purposes only. 
It does not provide medical advice, diagnosis, or treatment. Always consult 
with qualified healthcare professionals for medical concerns.
""")
