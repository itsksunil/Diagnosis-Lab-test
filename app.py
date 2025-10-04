import streamlit as st
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
st.set_page_config(page_title="लक्षण आधारित रोग जाँच", page_icon="🧪", layout="wide")
st.title("लक्षण आधारित रोग जाँच")
st.write("अपने लक्षण चुनें और संभावित रोग जोखिम देखें। उम्र और लक्षण के आधार पर जोखिम स्कोर अनुमानित है।")

# ---------- USER DETAILS FORM ----------
with st.form("user_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 नाम")
        age = st.number_input("🎂 आयु", min_value=0, max_value=120, step=1)
        gender = st.radio("⚧ लिंग", ["पुरुष", "महिला"])
        mobile = st.text_input("📱 मोबाइल नंबर")
    with col2:
        st.subheader("🩺 चिकित्सीय इतिहास")
        bp = st.checkbox("उच्च रक्तचाप")
        diabetes = st.checkbox("डायबिटीज़")
        heart = st.checkbox("हृदय रोग")
        location = st.text_input("📍 स्थान / शहर")

    st.subheader("🧍 लक्षण चुनें")

    # ---------- SYMPTOM LISTS ----------
    # Basic Viral / Fever Symptoms
    basic_symptoms = [
        "बुखार", "सर्दी / ठंड लगना", "थकान / कमजोरी", "सरदर्द", "मिचली / उल्टी", "मांसपेशियों / जोड़ों में दर्द"
    ]

    # Advanced Symptoms (Viral / Bacterial / Malaria / Dengue / Jaundice)
    advanced_symptoms = [
        "दस्त", "पेट दर्द", "भूख कम होना", "चकत्तेदार दाने / दाने", "खांसी", 
        "आँख के पीछे दर्द", "सूजी हुई ग्रंथियाँ", "पीली त्वचा / आँखें", "कमज़ोरी"
    ]

    # Heart Symptoms
    heart_symptoms = [
        "सीने में दर्द / दबाव", "बाँह / जबड़ा / पीठ / गर्दन / गला में दर्द", 
        "साँस लेने में कठिनाई", "तेज़ / अनियमित हृदय गति", "पाँव / टखने / पैर में सूजन",
        "व्यायाम करने की क्षमता कम होना", "घबराहट / लगातार खाँसी", "पेट में सूजन",
        "तेज़ वजन बढ़ना", "उल्टी / भूख की कमी", "ध्यान केंद्रित करने में कठिनाई", 
        "चक्कर / बेहोशी", "ठंडी पसीना"
    ]

    # Male Cancer Symptoms
    male_cancer_symptoms = [
        "स्तन में गांठ / मोटाई", "असामान्य स्तन स्त्राव", "पेल्विक दर्द / सूजन",
        "पेट में दर्द / सूजन", "प्रोस्टेट समस्याएँ", "अंडकोष में गांठ / सूजन",
        "असामान्य रक्तस्राव / चोट", "दर्द जो चला नहीं जाता", "मुँह में घाव / रक्त / सुन्नपन",
        "लगातार खाँसी / आवाज में बदलाव", "अनचाहा वजन कम / ज्यादा होना", "सूजन या गांठ",
        "त्वचा में बदलाव / पीलापन / नए तिल", "सरदर्द / दौरे", "अत्यधिक थकान / कमजोरी",
        "दृष्टि या सुनने में समस्या"
    ]

    # Female Cancer Symptoms
    female_cancer_symptoms = [
        "स्तन में गांठ / मोटाई", "असामान्य स्तन स्त्राव", "पेल्विक दर्द / सूजन",
        "असामान्य योनि रक्तस्राव", "गर्भाशय ग्रीवा के कैंसर लक्षण", "पेट में दर्द / सूजन",
        "असामान्य रक्तस्राव / चोट", "दर्द जो चला नहीं जाता", "मुँह में घाव / रक्त / सुन्नपन",
        "लगातार खाँसी / आवाज में बदलाव", "अनचाहा वजन कम / ज्यादा होना", "सूजन या गांठ",
        "त्वचा में बदलाव / पीलापन / नए तिल", "सरदर्द / दौरे", "अत्यधिक थकान / कमजोरी",
        "दृष्टि या सुनने में समस्या"
    ]

    # ---------- USER INPUT ----------
    selected_basic = st.multiselect("बुनियादी लक्षण", basic_symptoms)
    selected_advanced = st.multiselect("उन्नत लक्षण", advanced_symptoms)
    
    st.subheader("🧬 कैंसर लक्षण")
    if gender == "पुरुष":
        selected_cancer = st.multiselect("पुरुष कैंसर लक्षण", male_cancer_symptoms)
    else:
        selected_cancer = st.multiselect("महिला कैंसर लक्षण", female_cancer_symptoms)
        
    selected_heart = st.multiselect("हृदय / कार्डियोवैस्कुलर लक्षण", heart_symptoms)

    submitted = st.form_submit_button("🔍 जाँच करें")

# ---------- DIAGNOSIS LOGIC ----------
def diagnose(basic, advanced, cancer, heart, age):
    possible = []
    organs = []
    risk_score = 0

    all_symptoms = basic + advanced + cancer + heart
    symptom_count = len(all_symptoms)

    # ---------- Viral / Fever / Bacterial ----------
    if "बुखार" in basic:
        if any(s in advanced for s in ["दस्त", "चकत्तेदार दाने / दाने", "आँख के पीछे दर्द"]):
            if "चकत्तेदार दाने / दाने" in advanced or "आँख के पीछे दर्द" in advanced:
                possible.append("डेंगू / वायरल संक्रमण")
                organs.append("रक्त / प्रतिरक्षा प्रणाली")
            elif "दस्त" in advanced:
                possible.append("टाइफाइड / बैक्टीरियल संक्रमण")
                organs.append("पाचन तंत्र")
            else:
                possible.append("वायरल बुखार")
                organs.append("प्रतिरक्षा प्रणाली")

    # ---------- Malaria ----------
    if "थकान / कमजोरी" in basic and "दस्त" in advanced and "पेट दर्द" in advanced:
        possible.append("मलेरिया")
        organs.append("रक्त / जिगर / जोड़ों")

    # ---------- Cancer ----------
    if cancer:
        possible.append("संभावित कैंसर")
        organs.append("लक्षण अनुसार प्रभावित अंग")

    # ---------- Heart Issues ----------
    if heart:
        possible.append("हृदय / कार्डियोवैस्कुलर जोखिम")
        organs.append("हृदय / परिसंचारी तंत्र")

    # ---------- Risk Score ----------
    risk_score = min(100, symptom_count * 5 + (age / 2))
    
    return possible, organs, risk_score

# ---------- SHOW RESULTS ----------
if submitted:
    if not name or not mobile:
        st.error("कृपया अपना नाम और मोबाइल नंबर दर्ज करें।")
    else:
        results, organs, risk = diagnose(selected_basic, selected_advanced, selected_cancer, selected_heart, age)
        if results:
            st.success(f"**संभावित स्थितियाँ:**")
            for r, o in zip(results, organs):
                st.write(f"🔸 {r} → संभावित अंग / प्रणाली: {o}")
            st.info(f"**अनुमानित जोखिम स्कोर:** {risk:.1f}%")
        else:
            st.info("चयनित लक्षणों के आधार पर कोई महत्वपूर्ण रोग संकेत नहीं मिला।")

        # ---------- SAVE DATA TO GOOGLE SHEET ----------
        data = [
            name, age, gender, mobile, bp, diabetes, heart, location,
            ", ".join(selected_basic + selected_advanced + selected_cancer + selected_heart),
            ", ".join(results), ", ".join(organs), f"{risk:.1f}%"
        ]
        sheet.append_row(data)
        st.success("✅ आपकी जानकारी सुरक्षित रूप से रिकॉर्ड कर दी गई है।")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚠️ यह टूल केवल शैक्षिक / डेमो उद्देश्यों के लिए है। यह पेशेवर चिकित्सा सलाह का विकल्प नहीं है।")

