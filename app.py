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

# Get the worksheet
try:
    sheet = CLIENT.open(SHEET_NAME).sheet1
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")

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
        tb_history = st.checkbox("Family History of TB")
        hiv_immune = st.checkbox("HIV/Weakened Immune System")
        location = st.text_input("📍 Location / City")

    st.subheader("🧍 Select Symptoms")

    # ---------- ENHANCED SYMPTOM LISTS ----------
    fever_symptoms = [
        "Fever", "Chills", "Sweating", "Increased body temperature", 
        "Intermittent fever", "High fever (104°F+)", "Mild fever (100-101°F)",
        "Night sweats", "Morning fever"
    ]
    
    basic_symptoms = [
        "Fatigue", "Headache", "Nausea", "Vomiting", 
        "Muscle pain", "Joint pain", "Weakness", "Dizziness",
        "Loss of appetite", "Body pain", "Weight loss", "Chest pain"
    ]
    
    respiratory_symptoms = [
        "Cough", "Shortness of breath", "Chest tightness", "Runny nose", 
        "Sore throat", "Sneezing", "Wheezing", "Loss of smell", "Loss of taste",
        "Persistent cough (3 weeks+)", "Cough with blood", "Chest pain",
        "Breathlessness", "Chest pain when breathing"
    ]
    
    tuberculosis_symptoms = [
        "Cough lasting more than 3 weeks", "Coughing up blood", "Chest pain",
        "Breathing difficulty", "Night sweats", "Intermittent fever",
        "Weight loss", "Loss of appetite", "Fatigue and weakness",
        "Chest pain when breathing or coughing"
    ]
    
    digestive_symptoms = [
        "Diarrhea", "Abdominal pain", "Bloating", "Constipation", "Heartburn", 
        "Blood in stool", "Difficulty swallowing", "Excessive thirst", 
        "Frequent urination", "Abdominal cramps"
    ]
    
    skin_symptoms = [
        "Rash", "Itching", "Yellow skin/eyes", "Skin discoloration",
        "Hives", "Swelling", "Easy bruising", "Night sweats",
        "Red spots on skin", "Eye pain", "Red eyes"
    ]
    
    neurological_symptoms = [
        "Confusion", "Memory problems", "Numbness", "Tingling sensation",
        "Vision problems", "Hearing problems", "Balance issues", "Seizures",
        "Speech difficulties", "Tremors", "Severe headache"
    ]
    
    heart_symptoms = [
        "Chest pain/pressure", "Pain radiating to arm/jaw/back/neck/throat", 
        "Shortness of breath", "Rapid/irregular heartbeat", "Swelling in legs/ankles/feet",
        "Reduced exercise ability", "Persistent cough", "Abdominal swelling",
        "Rapid weight gain", "Cold sweats", "Palpitations"
    ]
    
    cancer_symptoms = [
        "Breast lump/thickening", "Unusual nipple discharge", "Pelvic pain/bloating",
        "Abdominal pain/bloating", "Prostate issues", "Testicular lumps/swelling",
        "Unusual bleeding/bruising", "Persistent pain", "Mouth sores/bleeding/numbness",
        "Persistent cough/hoarseness", "Unexplained weight loss", "Swelling/lumps",
        "Skin changes/jaundice/new moles", "Persistent headaches", "Extreme fatigue",
        "Vision/hearing problems", "Difficulty swallowing", "Changes in bowel habits"
    ]

    # User symptom selection
    st.subheader("🌡️ Fever and Infection Symptoms")
    selected_fever = st.multiselect("Fever Symptoms", fever_symptoms)
    
    st.subheader("🔍 Other Symptoms")
    selected_basic = st.multiselect("General Symptoms", basic_symptoms)
    selected_respiratory = st.multiselect("Respiratory Symptoms", respiratory_symptoms)
    selected_tuberculosis = st.multiselect("Tuberculosis (TB) Symptoms", tuberculosis_symptoms)
    selected_digestive = st.multiselect("Digestive Symptoms", digestive_symptoms)
    selected_skin = st.multiselect("Skin and Appearance Symptoms", skin_symptoms)
    selected_neurological = st.multiselect("Neurological Symptoms", neurological_symptoms)
    selected_cancer = st.multiselect("Cancer Symptoms", cancer_symptoms)
    selected_heart = st.multiselect("Heart and Circulatory Symptoms", heart_symptoms)

    # Additional information
    st.subheader("📋 Additional Information")
    col3, col4 = st.columns(2)
    with col3:
        symptom_duration = st.selectbox("How long have you had these symptoms?", 
                                      ["Less than 1 week", "1-2 weeks", "2-4 weeks", "1-3 months", "More than 3 months"])
        severity = st.select_slider("Symptom Severity", options=["Mild", "Moderate", "Severe"])
        fever_pattern = st.selectbox("Fever Pattern", 
                                   ["Continuous fever", "Intermittent fever", "Low in morning/high in evening", "Night fever", "No specific pattern"])
    with col4:
        smoking = st.checkbox("Smoker")
        alcohol = st.checkbox("Regular Alcohol Consumption")
        exercise = st.selectbox("Exercise Frequency", 
                              ["Never", "Occasionally", "1-2 times/week", "3-5 times/week", "Daily"])
        recent_travel = st.checkbox("Recent travel history")
        tb_contact = st.checkbox("Been in contact with TB patient")

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
def enhanced_diagnose(fever, basic, respiratory, tuberculosis, digestive, skin, neurological, cancer, heart, age, medical_history, lifestyle, fever_pattern, recent_travel, tb_contact):
    conditions = []
    risk_factors = []
    recommendations = []
    risk_score = 0
    
    all_symptoms = fever + basic + respiratory + tuberculosis + digestive + skin + neurological + cancer + heart
    symptom_count = len(all_symptoms)
    
    # Risk factors from medical history and lifestyle
    if medical_history.get('bp'): risk_factors.append("High Blood Pressure")
    if medical_history.get('diabetes'): risk_factors.append("Diabetes")
    if medical_history.get('heart'): risk_factors.append("Heart Disease History")
    if medical_history.get('smoking'): risk_factors.append("Smoking")
    if medical_history.get('alcohol'): risk_factors.append("Alcohol Use")
    if medical_history.get('hiv_immune'): risk_factors.append("Weakened Immune System")
    if recent_travel: risk_factors.append("Recent Travel")
    if tb_contact: risk_factors.append("Contact with TB Patient")
    
    # -------------------------------
    # TUBERCULOSIS (TB) ANALYSIS
    # -------------------------------
    
    # Major TB symptoms
    tb_major_symptoms = ["Cough lasting more than 3 weeks", "Coughing up blood", "Night sweats", "Weight loss"]
    tb_minor_symptoms = ["Intermittent fever", "Loss of appetite", "Fatigue and weakness", "Chest pain", "Breathing difficulty"]
    
    tb_major_count = sum(1 for symptom in tb_major_symptoms if symptom in tuberculosis)
    tb_minor_count = sum(1 for symptom in tb_minor_symptoms if symptom in (tuberculosis + fever + basic + respiratory))
    
    # TB risk assessment
    tb_risk_score = 0
    
    # High risk for major symptoms
    if tb_major_count >= 2:
        tb_risk_score += 60
    elif tb_major_count == 1:
        tb_risk_score += 30
    
    # Moderate risk for minor symptoms
    tb_risk_score += tb_minor_count * 10
    
    # Risk factors
    if medical_history.get('tb_history'):
        tb_risk_score += 20
    if medical_history.get('hiv_immune'):
        tb_risk_score += 25
    if tb_contact:
        tb_risk_score += 15
    if smoking:
        tb_risk_score += 10
    
    # TB diagnosis
    if tb_risk_score >= 50:
        risk_level = "High" if tb_risk_score >= 70 else "Medium"
        conditions.append((f"Tuberculosis (TB) - Risk Score: {tb_risk_score}%", "Lungs and Respiratory System", risk_level))
        recommendations.append("🚨 Get immediate Chest X-ray and Sputum test")
        recommendations.append("Visit TB clinic for DOTS therapy")
        recommendations.append("Wear mask to prevent infection spread")
    
    # -------------------------------
    # FEVER AND INFECTION ANALYSIS
    # -------------------------------
    
    # Normal Fever
    if "Fever" in fever and len(fever) == 1 and len([s for s in basic if s in ["Headache", "Body pain", "Fatigue"]]) >= 2:
        conditions.append(("Normal Fever (Viral Fever)", "Immune System", "Low"))
        recommendations.append("Rest, stay hydrated, and take paracetamol")
    
    # Viral Fever
    viral_fever_symptoms = ["Fever", "Headache", "Body pain", "Fatigue", "Weakness"]
    viral_count = sum(1 for symptom in viral_fever_symptoms if symptom in (fever + basic))
    if viral_count >= 4:
        conditions.append(("Viral Fever", "Immune System", "Medium"))
        recommendations.append("Get plenty of rest and fluids")
    
    # Dengue - Mosquito-borne
    dengue_symptoms = ["High fever (104°F+)", "Severe headache", "Eye pain", "Joint pain", "Muscle pain", "Red spots on skin"]
    dengue_count = sum(1 for symptom in dengue_symptoms if symptom in (fever + basic + skin))
    if dengue_count >= 4:
        conditions.append(("Dengue Fever", "Blood and Immune System", "High"))
        risk_factors.append("Mosquito-borne infection")
        recommendations.append("🚨 Get immediate blood test and consult doctor")
        recommendations.append("Monitor platelet count")
    
    # Malaria - Mosquito-borne
    malaria_symptoms = ["Intermittent fever", "Chills", "Sweating", "Headache", "Nausea", "Fatigue"]
    malaria_count = sum(1 for symptom in malaria_symptoms if symptom in (fever + basic))
    if malaria_count >= 4 and fever_pattern in ["Intermittent fever", "Low in morning/high in evening"]:
        conditions.append(("Malaria", "Blood and Liver", "High"))
        risk_factors.append("Mosquito-borne infection")
        recommendations.append("🚨 Get malaria blood test")
        recommendations.append("Start anti-malarial medications")
    
    # Typhoid - Water/food borne
    typhoid_symptoms = ["High fever (104°F+)", "Headache", "Weakness", "Abdominal pain", "Diarrhea or constipation", "Loss of appetite"]
    typhoid_count = sum(1 for symptom in typhoid_symptoms if symptom in (fever + basic + digestive))
    if typhoid_count >= 4:
        conditions.append(("Typhoid Fever", "Digestive System and Blood", "High"))
        risk_factors.append("Contaminated food/water")
        recommendations.append("🚨 Get Widal test and start antibiotics")
        recommendations.append("Maintain proper hygiene")
    
    # Chikungunya - Mosquito-borne
    if "Joint pain" in basic and "Fever" in fever and "Red spots on skin" in skin:
        conditions.append(("Chikungunya", "Joints and Immune System", "Medium"))
        recommendations.append("Get physiotherapy for joint pain")
    
    # -------------------------------
    # OTHER CONDITIONS
    # -------------------------------
    
    # Respiratory infections
    respiratory_symptom_count = len(respiratory)
    if respiratory_symptom_count >= 2 and "Fever" in fever:
        if "Cough" in respiratory and "Shortness of breath" in respiratory:
            conditions.append(("Respiratory Infection (COVID-19/Influenza/Pneumonia)", "Respiratory System", "High"))
        if "Wheezing" in respiratory and "Shortness of breath" in respiratory:
            conditions.append(("Asthma/Bronchitis", "Respiratory System", "Medium"))
    
    # Digestive infections
    digestive_symptom_count = len(digestive)
    if digestive_symptom_count >= 3 and "Fever" in fever:
        if "Diarrhea" in digestive and "Abdominal pain" in digestive:
            conditions.append(("Gastroenteritis", "Digestive System", "Medium"))
        if "Blood in stool" in digestive:
            conditions.append(("Dysentery/Enteritis", "Digestive System", "High"))
    
    # Hepatitis
    if "Yellow skin/eyes" in skin and "Fever" in fever:
        conditions.append(("Hepatitis/Liver Infection", "Liver", "High"))
    
    # Cardiovascular risk assessment
    heart_symptom_count = len(heart)
    if heart_symptom_count >= 2:
        conditions.append(("Cardiovascular Issue", "Heart/Circulatory System", "High"))
        if "Chest pain/pressure" in heart:
            recommendations.append("🚨 Seek immediate medical attention for chest pain")
    
    # Cancer risk assessment
    cancer_symptom_count = len(cancer)
    if cancer_symptom_count >= 2:
        risk_level = "High" if cancer_symptom_count >= 3 or medical_history.get('cancer_history') else "Medium"
        conditions.append(("Possible Cancer Indicators", "Multiple Systems", risk_level))
        recommendations.append("Consult with oncologist for further evaluation")
    
    # Lifestyle risk assessment
    if lifestyle.get('exercise') in ["Never", "Occasionally"] and medical_history.get('bp'):
        risk_factors.append("Sedentary Lifestyle")
        recommendations.append("Increase physical activity to 150 minutes per week")
    
    # Calculate comprehensive risk score
    base_score = min(symptom_count * 4, 40)
    age_score = min(age * 0.5, 20)
    medical_score = len(risk_factors) * 5
    lifestyle_score = 0
    if lifestyle.get('smoking'): lifestyle_score += 10
    if lifestyle.get('alcohol'): lifestyle_score += 5
    if lifestyle.get('exercise') in ["Never", "Occasionally"]: lifestyle_score += 5
    
    # Additional scores for fever and TB
    fever_score = len(fever) * 3
    tb_score = min(tb_risk_score / 2, 20)  # Include TB risk in overall score
    risk_score = min(base_score + age_score + medical_score + lifestyle_score + fever_score + tb_score, 95)
    
    # General recommendations
    if "Fever" in fever:
        recommendations.append("Monitor temperature regularly")
        recommendations.append("Drink plenty of fluids")
    
    if tb_risk_score >= 30:
        recommendations.append("Visit health center for TB screening")
    
    if risk_score > 50:
        recommendations.append("Schedule appointment with primary care physician")
    if symptom_count > 5:
        recommendations.append("Consider comprehensive medical evaluation")
    
    return conditions, risk_factors, recommendations, risk_score, tb_risk_score

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
            'asthma': asthma, 'kidney': kidney, 'liver': liver, 'cancer_history': cancer_history,
            'tb_history': tb_history, 'hiv_immune': hiv_immune, 'smoking': smoking
        }
        
        lifestyle = {
            'smoking': smoking, 'alcohol': alcohol, 'exercise': exercise
        }
        
        # Perform diagnosis
        conditions, risk_factors, recommendations, risk_score, tb_risk_score = enhanced_diagnose(
            selected_fever, selected_basic, selected_respiratory, selected_tuberculosis,
            selected_digestive, selected_skin, selected_neurological, selected_cancer, 
            selected_heart, age, medical_history, lifestyle, fever_pattern, recent_travel, tb_contact
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
            total_symptoms = len(selected_fever + selected_basic + selected_respiratory + 
                               selected_tuberculosis + selected_digestive + selected_skin + 
                               selected_neurological + selected_cancer + selected_heart)
            st.metric("Symptoms Reported", total_symptoms)
        
        # TB Special Analysis
        if selected_tuberculosis:
            st.info("## 🦠 Tuberculosis (TB) Analysis")
            tb_symptoms_text = ", ".join(selected_tuberculosis)
            st.write(f"**Selected TB Symptoms:** {tb_symptoms_text}")
            st.write(f"**TB Risk Score:** {tb_risk_score}%")
            
            if tb_risk_score >= 70:
                st.error("🔴 **High TB Risk:** Get immediate TB testing")
            elif tb_risk_score >= 50:
                st.warning("🟡 **Medium TB Risk:** TB screening advised")
            elif tb_risk_score >= 30:
                st.info("🟢 **Low TB Risk:** Monitoring advised")
        
        # Fever Analysis
        if selected_fever:
            st.info("## 🌡️ Fever Analysis")
            fever_symptoms_text = ", ".join(selected_fever)
            st.write(f"**Selected Fever Symptoms:** {fever_symptoms_text}")
            st.write(f"**Fever Pattern:** {fever_pattern}")
            
            # Fever type summary
            if any("Dengue" in cond[0] for cond in conditions):
                st.warning("🔴 **Dengue Symptoms:** High fever, severe headache, eye pain, joint pain")
            if any("Malaria" in cond[0] for cond in conditions):
                st.warning("🔴 **Malaria Symptoms:** Intermittent fever, chills, sweating")
            if any("Typhoid" in cond[0] for cond in conditions):
                st.warning("🔴 **Typhoid Symptoms:** Persistent high fever, abdominal pain, weakness")
        
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
            st.info("## ✅ No significant disease indicators found")
        
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
        if "Fever" in selected_fever:
            st.write("• Get plenty of rest and stay hydrated")
            st.write("• Monitor temperature regularly")
            st.write("• Don't take antibiotics without doctor's advice")
        
        if selected_tuberculosis and tb_risk_score > 30:
            st.write("• Visit nearby health center for TB testing")
            st.write("• If TB is confirmed, complete full course of medication")
        
        if bmi_category in ["Overweight", "Obese"]:
            st.write("• Consider weight management through balanced diet and exercise")
        
        if age > 50:
            st.write("• Regular health screenings recommended due to age")

        # ---------- SAVE DATA TO GOOGLE SHEET ----------
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        all_symptoms = selected_fever + selected_basic + selected_respiratory + selected_tuberculosis + selected_digestive + selected_skin + selected_neurological + selected_cancer + selected_heart
        condition_list = [f"{cond} ({risk})" for cond, sys, risk in conditions]
        
        # Prepare data row in exact column order
        data = [
            entry_time, name, age, gender, mobile, bp, diabetes, heart, thyroid,
            asthma, kidney, liver, cancer_history, tb_history, hiv_immune, location, 
            weight, height, ", ".join(all_symptoms), symptom_duration, severity, fever_pattern,
            smoking, alcohol, exercise, recent_travel, tb_contact,
            ", ".join(condition_list), ", ".join(risk_factors), 
            f"{risk_score:.1f}%", f"{tb_risk_score}%", f"{bmi_value:.1f}", bmi_category
        ]
        
        try:
            sheet.append_row(data)
            st.success("✅ Your response has been recorded securely in our database.")
        except Exception as e:
            st.error(f"⚠️ Could not save to database: {str(e)}")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("ℹ️ About This Tool")
    st.write("""
    This advanced symptom checker specifically analyzes:
    - Tuberculosis (TB) risk assessment
    - Normal fever vs Viral fever
    - Dengue, Malaria, Typhoid
    - Respiratory infections
    - Digestive disorders
    - Cardiovascular risks
    """)
    
    st.header("🌡️ Fever Type Guide")
    fever_guide = {
        "Normal Fever": ["Mild fever", "Headache", "Body pain"],
        "Viral Fever": ["High fever", "Fatigue", "Weakness", "Loss of appetite"],
        "Dengue": ["High fever (104°F+)", "Eye pain", "Joint pain", "Skin rash"],
        "Malaria": ["Intermittent fever", "Fever with chills", "Sweating"],
        "Typhoid": ["Persistent high fever", "Abdominal pain", "Diarrhea/constipation", "Weakness"],
        "Tuberculosis": ["Persistent cough", "Night sweats", "Weight loss", "Fever"]
    }
    
    for fever_type, symptoms in fever_guide.items():
        with st.expander(f"{fever_type}"):
            for symptom in symptoms:
                st.write(f"• {symptom}")
    
    st.header("🦠 TB Symptoms Guide")
    st.write("""
    Major TB Symptoms:
    • Cough lasting >3 weeks
    • Coughing up blood
    • Night sweats
    • Unexplained weight loss
    
    Minor TB Symptoms:
    • Intermittent fever
    • Loss of appetite
    • Fatigue
    • Chest pain
    """)
    
    st.header("🚨 Emergency Symptoms")
    st.write("""
    Seek immediate medical care for:
    - Fever above 104°F
    - Difficulty breathing
    - Severe abdominal pain
    - Persistent vomiting
    - Confusion or dizziness
    - Fever with skin rash
    - Coughing up blood
    - Chest pain with breathing
    """)

# ---------- FOOTER ----------
st.markdown("---")
st.caption("""
⚠️ **Disclaimer**: This tool is for educational and informational purposes only. 
It does not provide medical advice, diagnosis, or treatment. For fever or serious symptoms, 
always consult with qualified healthcare professionals.
""")
