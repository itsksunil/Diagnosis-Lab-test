import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="🧠 रोग लक्षण चेकर", page_icon="🧪", layout="wide")

# ---------- GOOGLE SHEETS CONNECTION ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_NAME = "symptom_records"
sheet = CLIENT.open(SHEET_NAME).sheet1

# ---------- APP TITLE ----------
st.title("🧠 लक्षण आधारित रोग चेकर")
st.write("नीचे दिए गए लक्षण चुनें और संभावित रोगों एवं जोखिम स्कोर को देखें। (उम्र और लक्षणों के आधार पर अनुमान)")

# ---------- USER DETAILS ----------
with st.form("user_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 नाम")
        age = st.number_input("🎂 उम्र", min_value=0, max_value=120, step=1)
        gender = st.radio("⚧ लिंग", ["पुरुष", "महिला"])
        mobile = st.text_input("📱 मोबाइल नंबर")
    with col2:
        st.subheader("🩺 स्वास्थ्य इतिहास")
        bp = st.checkbox("उच्च रक्तचाप")
        diabetes = st.checkbox("मधुमेह")
        heart_history = st.checkbox("हृदय की समस्या")
        location = st.text_input("📍 शहर / स्थान")

    st.subheader("🧍 लक्षण चुनें")

    # ---------- BASIC SYMPTOMS ----------
    basic_symptoms = [
        "बुखार", "कंपकंपी", "थकान", "सिर दर्द", "मतली / उल्टी", "मांसपेशियों / जोड़ों में दर्द"
    ]
    selected_basic = st.multiselect("🟡 बेसिक लक्षण (वायरल/बुखार)", basic_symptoms)

    # ---------- ADVANCED SYMPTOMS ----------
    advanced_symptoms = [
        "दस्त", "पेट दर्द", "भूख न लगना", "चकत्ते", "खांसी", 
        "आंखों के पीछे दर्द", "गांठ या ग्रंथियां सूजना", "त्वचा / आंख पीली", "कमज़ोरी"
    ]
    selected_advanced = st.multiselect("🟠 एडवांस लक्षण (मलेरिया / डेंगू / बैक्टीरियल)", advanced_symptoms)

    # ---------- HEART SYMPTOMS ----------
    heart_symptoms = [
        "सीने में दर्द / दबाव", "दर्द हाथ/जबड़े/पीठ/गले की ओर", 
        "सांस फूलना", "तेज़ / अनियमित दिल की धड़कन", "पैरों/टखनों में सूजन",
        "शारीरिक क्षमता में कमी", "घरघराहट / लगातार खांसी", "पेट में सूजन",
        "तेज़ वजन बढ़ना", "भूख में कमी / मतली", "ध्यान केंद्रित करने में कठिनाई", 
        "चक्कर / बेहोशी", "ठंडा पसीना आना"
    ]
    selected_heart = st.multiselect("🔴 हृदय / कार्डियक लक्षण", heart_symptoms)

    # ---------- CANCER SYMPTOMS (Always Active) ----------
    male_cancer_symptoms = [
        "प्रोस्टेट की समस्या", "वृषण में गांठ / सूजन",
        "मुंह में छाले / खून / सुन्नपन", "लगातार खांसी / आवाज़ में बदलाव",
        "वज़न में अचानक कमी / बढ़ोतरी", "त्वचा में बदलाव / पीलिया / नए तिल",
        "सिर दर्द / दौरे", "थकान / कमजोरी", "दृष्टि या सुनने में समस्या"
    ]

    female_cancer_symptoms = [
        "स्तन में गांठ / मोटापन", "निप्पल से असामान्य स्राव", "पेल्विक दर्द / पेट फूलना",
        "असामान्य योनि रक्तस्राव", "पेट दर्द / सूजन",
        "मुंह में छाले / खून / सुन्नपन", "लगातार खांसी / आवाज़ में बदलाव",
        "वज़न में अचानक कमी / बढ़ोतरी", "त्वचा में बदलाव / पीलिया / नए तिल",
        "सिर दर्द / दौरे", "थकान / कमजोरी", "दृष्टि या सुनने में समस्या"
    ]

    st.subheader("🧬 कैंसर लक्षण (पुरुष / महिला)")
    selected_male_cancer = st.multiselect("पुरुष संबंधित कैंसर लक्षण", male_cancer_symptoms)
    selected_female_cancer = st.multiselect("महिला संबंधित कैंसर लक्षण", female_cancer_symptoms)
    selected_cancer = selected_male_cancer + selected_female_cancer

    submitted = st.form_submit_button("🔍 जांच करें")

# ---------- DIAGNOSIS LOGIC ----------
def diagnose(basic, advanced, cancer, heart, age):
    possible = []
    organs = []
    risk_score = 0

    all_symptoms = basic + advanced + cancer + heart
    symptom_count = len(all_symptoms)

    # Viral / Bacterial / Dengue
    if "बुखार" in basic:
        if any(s in advanced for s in ["दस्त", "चकत्ते", "आंखों के पीछे दर्द"]):
            if "चकत्ते" in advanced or "आंखों के पीछे दर्द" in advanced:
                possible.append("डेंगू / वायरल संक्रमण")
                organs.append("रक्त / प्रतिरक्षा प्रणाली")
            elif "दस्त" in advanced:
                possible.append("टाइफाइड / बैक्टीरियल संक्रमण")
                organs.append("पाचन तंत्र")
            else:
                possible.append("वायरल बुखार")
                organs.append("प्रतिरक्षा प्रणाली")

    # Malaria
    if "थकान" in basic and "दस्त" in advanced and "पेट दर्द" in advanced:
        possible.append("मलेरिया")
        organs.append("रक्त / यकृत / जोड़")

    # Cancer
    if cancer:
        possible.append("संभावित कैंसर संकेत")
        organs.append("लक्षणों के अनुसार प्रभावित अंग")

    # Heart
    if heart:
        possible.append("हृदय / कार्डियोवैस्कुलर जोखिम")
        organs.append("हृदय / परिसंचरण तंत्र")

    risk_score = min(100, symptom_count * 5 + (age / 2))
    return possible, organs, risk_score

# ---------- SHOW RESULTS ----------
if submitted:
    if not name or not mobile:
        st.error("कृपया नाम और मोबाइल नंबर भरें।")
    else:
        results, organs, risk = diagnose(selected_basic, selected_advanced, selected_cancer, selected_heart, age)
        if results:
            st.success("🧭 **संभावित रोग:**")
            for r, o in zip(results, organs):
                st.write(f"🔸 {r} → प्रभावित अंग: {o}")
            st.info(f"📊 **अनुमानित जोखिम स्कोर:** {risk:.1f}%")
        else:
            st.info("❇️ चयनित लक्षणों के आधार पर कोई गंभीर रोग संकेत नहीं मिले।")

        # Save to Google Sheet
        data = [
            name, age, gender, mobile, bp, diabetes, heart_history, location,
            ", ".join(selected_basic + selected_advanced + selected_cancer + selected_heart),
            ", ".join(results), ", ".join(organs), f"{risk:.1f}%"
        ]
        sheet.append_row(data)
        st.success("✅ आपका डेटा सुरक्षित रूप से रिकॉर्ड कर लिया गया है।")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚠️ यह टूल केवल शैक्षणिक / डेमो उद्देश्य के लिए है। चिकित्सकीय सलाह के लिए डॉक्टर से संपर्क करें।")
