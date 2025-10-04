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
st.title("🧠 लक्षण आधारित रोग जाँच")
st.write("लक्षण चुनें और संभावित रोग/कैंसर जोखिम देखें। उम्र और लक्षण के आधार पर जोखिम स्कोर अनुमानित किया गया है।")

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
        heart_history = st.checkbox("हृदय समस्याएँ")
        location = st.text_input("📍 स्थान / शहर")

    st.subheader("🧍 लक्षण चुनें")

    # ---------- SYMPTOM LISTS ----------
    basic_symptoms = ["बुखार", "ठंड लगना", "थकान / कमजोरी", "सिरदर्द", "उल्टी / मिचली", "मांसपेशियों / जोड़ों में दर्द"]
    advanced_symptoms = ["दस्त", "पेट दर्द", "भूख न लगना", "दाने / चकत्ते", "खांसी", "आँखों के पीछे दर्द", "सूजे हुए ग्रंथियाँ", "पीली त्वचा / आँखें", "कमजोरी"]
    
    male_cancer_symptoms = ["स्तंभ / मोटाई में गांठ", "असामान्य स्तन स्त्राव", "पेल्विक दर्द / सूजन", "गुप्तांग / टेस्टिस में सूजन", 
                            "असामान्य रक्तस्राव / चोट", "लगातार दर्द", "मुँह के घाव / रक्तस्राव / सुन्नता", "लगातार खाँसी / आवाज बदलना",
                            "अनजानी वजन घटाना / बढ़ना", "सूजन या गांठ", "त्वचा परिवर्तन / पीलापन / नए तिल", "सिरदर्द / दौरे", "अत्यधिक थकान", "दृष्टि या सुनने की समस्याएँ"]

    female_cancer_symptoms = ["स्तन में गांठ / मोटाई", "असामान्य स्तन स्त्राव", "पेल्विक दर्द / सूजन", 
                              "असामान्य योनि रक्तस्राव", "गर्भाशय ग्रीवा के कैंसर के लक्षण (दर्द, स्त्राव)", 
                              "अनजानी रक्तस्राव / चोट", "लगातार दर्द", "मुँह के घाव / रक्तस्राव / सुन्नता", "लगातार खाँसी / आवाज बदलना",
                              "अनजानी वजन घटाना / बढ़ना", "सूजन या गांठ", "त्वचा परिवर्तन / पीलापन / नए तिल", "सिरदर्द / दौरे", "अत्यधिक थकान", "दृष्टि या सुनने की समस्याएँ"]

    heart_symptoms = ["सीने में दर्द / दबाव", "बांह / जबड़ा / पीठ / गर्दन / गले में दर्द", "सांस लेने में तकलीफ", 
                      "तेज़ / अनियमित हृदयगति", "पैर / टखने / पाँव में सूजन", "व्यायाम करने की क्षमता कम होना",
                      "घरघराहट / लगातार खाँसी", "पेट में सूजन", "तेज़ वजन बढ़ना", "उल्टी / भूख न लगना", 
                      "ध्यान में कमी / चक्कर आना", "ठंडी पसीना"]

    # ---------- COLLAPSIBLE MULTISELECT ----------
    with st.expander("मूल लक्षण"):
        selected_basic = st.multiselect("चुनें", basic_symptoms)
    with st.expander("उन्नत लक्षण"):
        selected_advanced = st.multiselect("चुनें", advanced_symptoms)
    with st.expander("कैंसर लक्षण"):
        if gender == "पुरुष":
            selected_cancer = st.multiselect("पुरुष कैंसर लक्षण", male_cancer_symptoms)
        else:
            selected_cancer = st.multiselect("महिला कैंसर लक्षण", female_cancer_symptoms)
    with st.expander("हृदय / कार्डियोवस्कुलर लक्षण"):
        selected_heart = st.multiselect("चुनें", heart_symptoms)

    submitted = st.form_submit_button("🔍 जाँच करें")

# ---------- DIAGNOSIS LOGIC ----------
def diagnose(basic, advanced, cancer, heart, age):
    possible = []
    organs = []
    risk_score = 0
    all_symptoms = basic + advanced + cancer + heart
    symptom_count = len(all_symptoms)

    # Viral / Bacterial / Fever
    if "बुखार" in basic:
        if any(s in advanced for s in ["दस्त", "दाने / चकत्ते", "आँखों के पीछे दर्द"]):
            if "दाने / चकत्ते" in advanced or "आँखों के पीछे दर्द" in advanced:
                possible.append("डेंगू / वायरल संक्रमण")
                organs.append("रक्त / प्रतिरक्षा प्रणाली")
            elif "दस्त" in advanced:
                possible.append("टाइफाइड / बैक्टीरियल संक्रमण")
                organs.append("पाचन तंत्र")
            else:
                possible.append("वायरल बुखार")
                organs.append("प्रतिरक्षा प्रणाली")

    # Malaria
    if "थकान / कमजोरी" in basic and "दस्त" in advanced and "पेट दर्द" in advanced:
        possible.append("मलेरिया")
        organs.append("रक्त / जिगर / जोड़")

    # Cancer
    if cancer:
        possible.append("संभावित कैंसर")
        organs.append("लक्षणों के अनुसार प्रभावित अंग")

    # Heart
    if heart:
        possible.append("हृदय / कार्डियोवस्कुलर जोखिम")
        organs.append("हृदय / परिसंचरण प्रणाली")

    # Risk Score
    risk_score = min(100, symptom_count * 5 + (age / 2))
    return possible, organs, risk_score

# ---------- SHOW RESULTS ----------
if submitted:
    if not name or not mobile:
        st.error("कृपया अपना नाम और मोबाइल नंबर दर्ज करें।")
    else:
        results, organs, risk = diagnose(selected_basic, selected_advanced, selected_cancer, selected_heart, age)
        if results:
            st.success(f"**संभावित रोग / कैंसर:**")
            for r, o in zip(results, organs):
                st.write(f"🔸 {r} → प्रभावित अंग / प्रणाली: {o}")
            st.info(f"**अनुमानित जोखिम स्कोर:** {risk:.1f}%")
        else:
            st.info("चयनित लक्षणों के आधार पर कोई गंभीर रोग संकेत नहीं मिला।")

        # ---------- SAVE DATA TO GOOGLE SHEET ----------
        data = [
            name, age, gender, mobile, bp, diabetes, heart_history, location,
            ", ".join(selected_basic + selected_advanced + selected_cancer + selected_heart),
            ", ".join(results), ", ".join(organs), f"{risk:.1f}%"
        ]
        sheet.append_row(data)
        st.success("✅ आपका डेटा सुरक्षित रूप से रिकॉर्ड किया गया।")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("⚠️ यह उपकरण केवल शैक्षिक / डेमो उद्देश्यों के लिए है। यह पेशेवर चिकित्सीय सलाह का विकल्प नहीं है।")
