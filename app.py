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
st.set_page_config(page_title="लक्षण-आधारित रोग जाँच", page_icon="🧪", layout="wide")
st.title("🧠 लक्षण-आधारित रोग जाँच")
st.write("लक्षण चुनें और संभावित रोग/हृदय या कैंसर जोखिम देखें। आयु और लक्षणों के आधार पर जोखिम स्कोर अनुमानित।")

# ---------- USER DETAILS FORM ----------
with st.form("user_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 पूरा नाम")
        age = st.number_input("🎂 उम्र", min_value=0, max_value=120, step=1)
        gender = st.radio("⚧ लिंग", ["पुरुष", "महिला"])
        mobile = st.text_input("📱 मोबाइल नंबर")
    with col2:
        st.subheader("🩺 मेडिकल इतिहास")
        bp = st.checkbox("उच्च रक्तचाप")
        diabetes = st.checkbox("डायबिटीज़")
        heart = st.checkbox("हृदय समस्या")
        location = st.text_input("📍 स्थान / शहर")

    st.subheader("🧍 लक्षण चुनें")

    # ---------- SYMPTOM LISTS ----------
    basic_symptoms = [
        "बुखार", "काँपना", "कमज़ोरी / थकान", "सिरदर्द", "मतली / उल्टी", "मांसपेशी / जोड़ों में दर्द"
    ]

    advanced_symptoms = [
        "दस्त", "पेट में दर्द", "भूख की कमी", "रैश", "खांसी",
        "आंख के पीछे दर्द", "सूजी हुई ग्रंथियाँ", "पीलापन (त्वचा/आँख)", "कमज़ोरी"
    ]

    heart_symptoms = [
        "सीने में दर्द / दबाव", "बांह / जबड़ा / पीठ / गर्दन / गला में दर्द",
        "साँस लेने में तकलीफ़", "तेज़ / अनियमित हृदय गति", "पैर / टखने / पैरों में सूजन",
        "व्यायाम करने की क्षमता में कमी", "घोंघा / लगातार खांसी", "पेट में सूजन",
        "तेज़ वजन बढ़ना", "मतली / भूख की कमी", "एकाग्रता की कमी", "चक्कर / बेहोशी", "ठंडी पसीने"
    ]

    # Male Cancer Symptoms
    male_cancer_symptoms = [
        "प्रोस्टेट समस्या (बार-बार पेशाब, कमजोर धारा, श्रोणि में दर्द)",
        "अंडकोष में गांठ / सूजन",
        "रक्त में असामान्यताएँ / चोट या खून का बहना",
        "दर्द जो नहीं जाता",
        "मुँह में घाव / रक्तस्राव / सुन्नता",
        "लगातार खांसी / स्वर बदलाव",
        "अनजानी वजन कमी / वृद्धि",
        "सांय / गांठें",
        "त्वचा में बदलाव / पीलापन / नई मोल",
        "सिरदर्द / दौरे",
        "अत्यधिक थकान / कमजोरी",
        "दृष्टि या सुनने की समस्याएं"
    ]

    # Female Cancer Symptoms
    female_cancer_symptoms = male_cancer_symptoms + [
        "स्तन में गांठ / मोटाई",
        "असामान्य स्तन स्त्राव",
        "श्रोणि में दर्द / सूजन",
        "असामान्य योनि रक्तस्राव",
        "अंडाशय या गर्भाशय से संबंधित दर्द / सूजन"
    ]

    # ---------- USER INPUT ----------
    selected_basic = st.multiselect("मूल लक्षण", basic_symptoms)
    selected_advanced = st.multiselect("उन्नत लक्षण", advanced_symptoms)
    if gender == "पुरुष":
        selected_cancer = st.multiselect("पुरुष कैंसर लक्षण", male_cancer_symptoms)
    else:
        selected_cancer = st.multiselect("महिला कैंसर लक्षण", female_cancer_symptoms)
    selected_heart = st.multiselect("हृदय / कार्डियोवस्कुलर लक्षण", heart_symptoms)

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
        if any(s in advanced for s in ["दस्त", "रैश", "आंख के पीछे दर्द"]):
            if "रैश" in advanced or "आंख के पीछे दर्द" in advanced:
                possible.append("डेंगू / वायरल संक्रमण")
                organs.append("रक्त / प्रतिरक्षा प्रणाली")
            elif "दस्त" in advanced:
                possible.append("टाइफाइड / बैक्टीरियल संक्रमण")
                organs.append("पाचन तंत्र")
            else:
                possible.append("वायरल बुखार")
                organs.append("प्रतिरक्षा प्रणाली")

    # ---------- Malaria ----------
    if "कमज़ोरी / थकान" in basic and "दस्त" in advanced and "पेट में दर्द" in advanced:
        possible.append("मलेरिया")
        organs.append("रक्त / जिगर / जोड़")

    # ---------- Cancer ----------
    if cancer:
        possible.append("संभावित कैंसर")
        organs.append("लक्षणों के आधार पर प्रभावित अंग")

    # ---------- Heart Issues ----------
    if heart:
        possible.append("हृदय / कार्डियोवस्कुलर जोखिम")
        organs.append("हृदय / परिसंचरण प्रणाली")

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
            st.success(f"**संभावित रोग / स्थिति:**")
            for r, o in zip(results, organs):
                st.write(f"🔸 {r} → संभावित अंग/प्रणाली: {o}")
            st.info(f"**अनुमानित जोखिम स्कोर:** {risk:.1f}%")
        else:
            st.info("चयनित लक्षणों के आधार पर कोई गंभीर रोग संकेत नहीं मिला।")

        # ---------- SAVE DATA TO GOOGLE SHEET ----------
        data = [
            name, age, gender, mobile, bp, diabetes, heart, location,
            ", ".join(selected_basic + selected_advanced + selected_cancer + selected_heart),
            ", ".join(results), ", ".join(organs), f"{risk:.1f}%"
        ]
        sheet.append_row(data)
        st.success("✅ आपकी प्रतिक्रिया सुरक्षित रूप से रिकॉर्ड कर दी गई है।")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚠️ यह उपकरण केवल शैक्षिक / डेमो प्रयोजनों के लिए है। यह पेशेवर चिकित्सा सलाह का विकल्प नहीं है।")
