import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime
import pandas as pd

# ---------- गूगल शीट कनेक्शन ----------
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET_NAME = "symptom_records"

# वर्कशीट प्राप्त करें
try:
    sheet = CLIENT.open(SHEET_NAME).sheet1
except Exception as e:
    st.error(f"गूगल शीट से कनेक्ट होने में त्रुटि: {e}")

# ---------- ऐप टाइटल ----------
st.set_page_config(page_title="उन्नत लक्षण-आधारित बीमारी जांचकर्ता", page_icon="🏥", layout="wide")
st.title("🏥 उन्नत लक्षण-आधारित बीमारी जांचकर्ता")
st.write("लक्षण चुनें और संभावित बीमारी के जोखिमों को विस्तृत विश्लेषण के साथ देखें।")

# ---------- उपयोगकर्ता विवरण फॉर्म ----------
with st.form("user_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 पूरा नाम")
        age = st.number_input("🎂 उम्र", min_value=0, max_value=120, step=1)
        gender = st.radio("⚧ लिंग", ["पुरुष", "महिला", "अन्य"])
        mobile = st.text_input("📱 मोबाइल नंबर")
        weight = st.number_input("⚖ वजन (किलोग्राम)", min_value=1, max_value=300)
        height = st.number_input("📏 लंबाई (सेंटीमीटर)", min_value=50, max_value=250)
        
    with col2:
        st.subheader("🩺 चिकित्सा इतिहास")
        bp = st.checkbox("उच्च रक्तचाप")
        diabetes = st.checkbox("मधुमेह")
        heart = st.checkbox("हृदय संबंधी समस्याएं")
        thyroid = st.checkbox("थायराइड समस्याएं")
        asthma = st.checkbox("अस्थमा/श्वसन संबंधी समस्याएं")
        kidney = st.checkbox("किडनी रोग")
        liver = st.checkbox("लिवर रोग")
        cancer_history = st.checkbox("कैंसर का पारिवारिक इतिहास")
        location = st.text_input("📍 स्थान / शहर")

    st.subheader("🧍 लक्षण चुनें")

    # ---------- उन्नत लक्षण सूची ----------
    basic_symptoms = [
        "बुखार", "ठंड लगना", "थकान", "सिरदर्द", "मतली", "उल्टी", 
        "मांसपेशियों में दर्द", "जोड़ों में दर्द", "कमजोरी", "चक्कर आना"
    ]
    
    respiratory_symptoms = [
        "खांसी", "सांस लेने में तकलीफ", "छाती में जकड़न", "बहती नाक", 
        "गले में खराश", "छींक आना", "घरघराहट", "गंध न आना", "स्वाद न आना"
    ]
    
    digestive_symptoms = [
        "दस्त", "पेट दर्द", "भूख न लगना", "पेट फूलना", 
        "कब्ज", "सीने में जलन", "मल में खून", "निगलने में कठिनाई",
        "अत्यधिक प्यास लगना", "बार-बार पेशाब आना"
    ]
    
    neurological_symptoms = [
        "भ्रम", "याददाश्त की समस्या", "सुन्नता", "झुनझुनी सनसनी",
        "दृष्टि संबंधी समस्याएं", "सुनने में समस्या", "संतुलन की समस्या", "दौरे",
        "बोलने में कठिनाई", "कंपन"
    ]
    
    skin_symptoms = [
        "चकत्ते", "खुजली", "पीली त्वचा/आंखें", "नए तिल", "त्वचा का रंग बदलना",
        "पित्ती", "सूजन", "आसानी से चोट लगना", "बाल झड़ना", "रात को पसीना आना"
    ]
    
    heart_symptoms = [
        "सीने में दर्द/दबाव", "बांह/जबड़े/पीठ/गर्दन/गले में दर्द फैलना", 
        "सांस लेने में तकलीफ", "तेज/अनियमित धड़कन", "पैर/टखनों/पैरों में सूजन",
        "व्यायाम करने की क्षमता कम होना", "लगातार खांसी", "पेट में सूजन",
        "तेजी से वजन बढ़ना", "ठंडे पसीने आना", "धड़कन तेज होना"
    ]
    
    cancer_symptoms = [
        "स्तन में गांठ/मोटापन", "असामान्य निप्पल डिस्चार्ज", "श्रोणि में दर्द/सूजन",
        "पेट दर्द/सूजन", "प्रोस्टेट समस्याएं", "अंडकोष में गांठ/सूजन",
        "असामान्य रक्तस्राव/चोट", "लगातार दर्द", "मुंह के छाले/रक्तस्राव/सुन्नता",
        "लगातार खांसी/आवाज बैठना", "बिना कारण वजन कम होना", "सूजन/गांठ",
        "त्वचा में बदलाव/पीलिया/नए तिल", "लगातार सिरदर्द", "अत्यधिक थकान",
        "दृष्टि/श्रवण संबंधी समस्याएं", "निगलने में कठिनाई", "मल त्याग की आदतों में बदलाव"
    ]

    # उपयोगकर्ता लक्षण चयन
    selected_basic = st.multiselect("सामान्य लक्षण", basic_symptoms)
    selected_respiratory = st.multiselect("श्वसन संबंधी लक्षण", respiratory_symptoms)
    selected_digestive = st.multiselect("पाचन संबंधी लक्षण", digestive_symptoms)
    selected_neurological = st.multiselect("न्यूरोलॉजिकल लक्षण", neurological_symptoms)
    selected_skin = st.multiselect("त्वचा और रूप संबंधी लक्षण", skin_symptoms)
    selected_cancer = st.multiselect("कैंसर के लक्षण", cancer_symptoms)
    selected_heart = st.multiselect("हृदय और संचार संबंधी लक्षण", heart_symptoms)

    # अतिरिक्त जानकारी
    st.subheader("📋 अतिरिक्त जानकारी")
    col3, col4 = st.columns(2)
    with col3:
        symptom_duration = st.selectbox("आपको ये लक्षण कितने समय से हैं?", 
                                      ["1 सप्ताह से कम", "1-2 सप्ताह", "2-4 सप्ताह", "1-3 महीने", "3 महीने से अधिक"])
        severity = st.select_slider("लक्षणों की गंभीरता", options=["हल्के", "मध्यम", "गंभीर"])
    with col4:
        smoking = st.checkbox("धूम्रपान करने वाला")
        alcohol = st.checkbox("नियमित शराब का सेवन")
        exercise = st.selectbox("व्यायाम की आवृत्ति", 
                              ["कभी नहीं", "कभी-कभी", "सप्ताह में 1-2 बार", "सप्ताह में 3-5 बार", "रोज"])

    submitted = st.form_submit_button("🔍 लक्षणों का विश्लेषण करें")

# ---------- बीएमआई गणना ----------
def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    if bmi < 18.5:
        category = "कम वजन"
    elif 18.5 <= bmi < 25:
        category = "सामान्य"
    elif 25 <= bmi < 30:
        category = "अधिक वजन"
    else:
        category = "मोटापा"
    return bmi, category

# ---------- उन्नत निदान लॉजिक ----------
def enhanced_diagnose(basic, respiratory, digestive, neurological, skin, cancer, heart, age, medical_history, lifestyle):
    conditions = []
    risk_factors = []
    recommendations = []
    risk_score = 0
    
    all_symptoms = basic + respiratory + digestive + neurological + skin + cancer + heart
    symptom_count = len(all_symptoms)
    
    # चिकित्सा इतिहास और जीवनशैली से जोखिम कारक
    if medical_history.get('bp'): risk_factors.append("उच्च रक्तचाप")
    if medical_history.get('diabetes'): risk_factors.append("मधुमेह")
    if medical_history.get('heart'): risk_factors.append("हृदय रोग इतिहास")
    if medical_history.get('smoking'): risk_factors.append("धूम्रपान")
    if medical_history.get('alcohol'): risk_factors.append("शराब का सेवन")
    
    # संक्रामक रोग विश्लेषण
    if "बुखार" in basic:
        if "खांसी" in respiratory and "सांस लेने में तकलीफ" in respiratory:
            conditions.append(("श्वसन संक्रमण (COVID-19/इन्फ्लुएंजा/निमोनिया)", "श्वसन प्रणाली", "उच्च"))
        if "दस्त" in digestive and "पेट दर्द" in digestive:
            conditions.append(("गैस्ट्रोइंटेस्टाइनल संक्रमण", "पाचन तंत्र", "मध्यम"))
        if "चकत्ते" in skin and "जोड़ों में दर्द" in basic:
            conditions.append(("वायरल संक्रमण (डेंगू/चिकनगुनिया)", "प्रतिरक्षा प्रणाली", "उच्च"))
        if "पीली त्वचा/आंखें" in skin:
            conditions.append(("हेपेटाइटिस/लिवर संक्रमण", "लिवर", "उच्च"))
    
    # श्वसन स्थितियां
    respiratory_symptom_count = len(respiratory)
    if respiratory_symptom_count >= 2:
        if "घरघराहट" in respiratory and "सांस लेने में तकलीफ" in respiratory:
            conditions.append(("अस्थमा/ब्रोंकाइटिस", "श्वसन प्रणाली", "मध्यम"))
        if "छाती में जकड़न" in respiratory and "खांसी" in respiratory:
            conditions.append(("ब्रोंकाइटिस/ऊपरी श्वसन संक्रमण", "श्वसन प्रणाली", "मध्यम"))
    
    # पाचन स्थितियां
    digestive_symptom_count = len(digestive)
    if digestive_symptom_count >= 3:
        if "मल में खून" in digestive or "निगलने में कठिनाई" in digestive:
            conditions.append(("गैस्ट्रोइंटेस्टाइनल विकार (IBD/अल्सर)", "पाचन तंत्र", "उच्च"))
        elif "पेट फूलना" in digestive and "पेट दर्द" in digestive:
            conditions.append(("चिड़चिड़ा आंत्र सिंड्रोम", "पाचन तंत्र", "मध्यम"))
    
    # न्यूरोलॉजिकल स्थितियां
    neurological_symptom_count = len(neurological)
    if neurological_symptom_count >= 2:
        if "सिरदर्द" in basic and "दृष्टि संबंधी समस्याएं" in neurological:
            conditions.append(("माइग्रेन/न्यूरोलॉजिकल विकार", "तंत्रिका तंत्र", "मध्यम"))
        if "सुन्नता" in neurological and "झुनझुनी सनसनी" in neurological:
            conditions.append(("न्यूरोपैथी", "तंत्रिका तंत्र", "मध्यम"))
    
    # हृदय संबंधी जोखिम मूल्यांकन
    heart_symptom_count = len(heart)
    if heart_symptom_count >= 2:
        conditions.append(("हृदय संबंधी समस्या", "हृदय/संचार प्रणाली", "उच्च"))
        if "सीने में दर्द/दबाव" in heart:
            recommendations.append("🚨 सीने में दर्द के लिए तुरंत चिकित्सकीय सहायता लें")
    
    # कैंसर जोखिम मूल्यांकन
    cancer_symptom_count = len(cancer)
    if cancer_symptom_count >= 2:
        risk_level = "उच्च" if cancer_symptom_count >= 3 or medical_history.get('cancer_history') else "मध्यम"
        conditions.append(("संभावित कैंसर संकेतक", "कई प्रणालियां", risk_level))
        recommendations.append("आगे मूल्यांकन के लिए ऑन्कोलॉजिस्ट से परामर्श करें")
    
    # जीवनशैली जोखिम मूल्यांकन
    if lifestyle.get('exercise') in ["कभी नहीं", "कभी-कभी"] and medical_history.get('bp'):
        risk_factors.append("निष्क्रिय जीवनशैली")
        recommendations.append("शारीरिक गतिविधि को सप्ताह में 150 मिनट तक बढ़ाएं")
    
    # व्यापक जोखिम स्कोर की गणना
    base_score = min(symptom_count * 4, 40)  # लक्षणों से 40% तक
    age_score = min(age * 0.5, 20)  # उम्र से 20% तक
    medical_score = len(risk_factors) * 5  # चिकित्सा इतिहास से 25% तक
    lifestyle_score = 0
    if lifestyle.get('smoking'): lifestyle_score += 10
    if lifestyle.get('alcohol'): lifestyle_score += 5
    if lifestyle.get('exercise') in ["कभी नहीं", "कभी-कभी"]: lifestyle_score += 5
    
    risk_score = min(base_score + age_score + medical_score + lifestyle_score, 95)
    
    # जोखिम कारकों के आधार पर सामान्य सिफारिशें जोड़ें
    if risk_score > 50:
        recommendations.append("प्राथमिक देखभाल चिकित्सक के साथ अपॉइंटमेंट शेड्यूल करें")
    if symptom_count > 5:
        recommendations.append("व्यापक चिकित्सा मूल्यांकन पर विचार करें")
    
    return conditions, risk_factors, recommendations, risk_score

# ---------- परिणाम दिखाएं ----------
if submitted:
    if not name or not mobile:
        st.error("❌ कृपया अपना नाम और मोबाइल नंबर दर्ज करें।")
    else:
        # बीएमआई की गणना करें
        bmi_value, bmi_category = calculate_bmi(weight, height)
        
        # निदान के लिए डेटा तैयार करें
        medical_history = {
            'bp': bp, 'diabetes': diabetes, 'heart': heart, 'thyroid': thyroid,
            'asthma': asthma, 'kidney': kidney, 'liver': liver, 'cancer_history': cancer_history
        }
        
        lifestyle = {
            'smoking': smoking, 'alcohol': alcohol, 'exercise': exercise
        }
        
        # निदान करें
        conditions, risk_factors, recommendations, risk_score = enhanced_diagnose(
            selected_basic, selected_respiratory, selected_digestive, 
            selected_neurological, selected_skin, selected_cancer, 
            selected_heart, age, medical_history, lifestyle
        )

        # परिणाम प्रदर्शित करें
        st.success("## 📊 विश्लेषण परिणाम")
        
        # बीएमआई और बुनियादी जानकारी
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("बीएमआई स्कोर", f"{bmi_value:.1f}", bmi_category)
        with col2:
            st.metric("कुल जोखिम स्कोर", f"{risk_score:.1f}%")
        with col3:
            st.metric("लक्षणों की सूचना", len(selected_basic + selected_respiratory + selected_digestive + 
                                            selected_neurological + selected_skin + selected_cancer + selected_heart))
        
        # पाए गए रोग
        if conditions:
            st.warning("## 🚨 संभावित स्थितियां पाई गईं")
            for condition, system, risk_level in conditions:
                risk_color = "🔴" if risk_level == "उच्च" else "🟡" if risk_level == "मध्यम" else "🟢"
                st.write(f"{risk_color} **{condition}**")
                st.write(f"   • प्रभावित प्रणाली: {system}")
                st.write(f"   • जोखिम स्तर: {risk_level}")
                st.write("")
        else:
            st.info("## ✅ कोई महत्वपूर्ण बीमारी संकेतक नहीं मिले")
        
        # जोखिम कारक
        if risk_factors:
            st.error("## ⚠️ पहचाने गए जोखिम कारक")
            for factor in risk_factors:
                st.write(f"• {factor}")
        
        # सिफारिशें
        if recommendations:
            st.success("## 💡 सिफारिशें")
            for recommendation in recommendations:
                st.write(f"• {recommendation}")
        
        # सामान्य स्वास्थ्य सुझाव
        st.info("## 🌟 सामान्य स्वास्थ्य सुझाव")
        if bmi_category in ["अधिक वजन", "मोटापा"]:
            st.write("• संतुलित आहार और व्यायाम के माध्यम से वजन प्रबंधन पर विचार करें")
        if age > 50:
            st.write("• उम्र के कारण नियमित स्वास्थ्य जांच की सिफारिश की जाती है")
        if not risk_factors and risk_score < 30:
            st.write("• नियमित जांच-पड़ताल के साथ वर्तमान स्वस्थ जीवनशैली बनाए रखें")

        # ---------- गूगल शीट में डेटा सेव करें ----------
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        all_symptoms = selected_basic + selected_respiratory + selected_digestive + selected_neurological + selected_skin + selected_cancer + selected_heart
        condition_list = [f"{cond} ({risk})" for cond, sys, risk in conditions]
        
        # सटीक कॉलम क्रम में डेटा पंक्ति तैयार करें
        data = [
            entry_time,                    # 1. टाइमस्टैम्प
            name,                          # 2. पूरा नाम
            age,                           # 3. उम्र
            gender,                        # 4. लिंग
            mobile,                        # 5. मोबाइल नंबर
            bp,                            # 6. उच्च रक्तचाप
            diabetes,                      # 7. मधुमेह
            heart,                         # 8. हृदय संबंधी समस्याएं
            thyroid,                       # 9. थायराइड समस्याएं
            asthma,                        # 10. अस्थमा/श्वसन संबंधी समस्याएं
            kidney,                        # 11. किडनी रोग
            liver,                         # 12. लिवर रोग
            cancer_history,                # 13. कैंसर का पारिवारिक इतिहास
            location,                      # 14. स्थान/शहर
            weight,                        # 15. वजन (किलोग्राम)
            height,                        # 16. लंबाई (सेंटीमीटर)
            ", ".join(all_symptoms),       # 17. सभी लक्षण
            symptom_duration,              # 18. लक्षणों की अवधि
            severity,                      # 19. लक्षणों की गंभीरता
            smoking,                       # 20. धूम्रपान
            alcohol,                       # 21. शराब का सेवन
            exercise,                      # 22. व्यायाम की आवृत्ति
            ", ".join(condition_list),     # 23. पाई गई स्थितियां
            ", ".join(risk_factors),       # 24. जोखिम कारक
            f"{risk_score:.1f}%",          # 25. जोखिम स्कोर
            f"{bmi_value:.1f}",            # 26. बीएमआई मूल्य
            bmi_category                   # 27. बीएमआई श्रेणी
        ]
        
        try:
            sheet.append_row(data)
            st.success("✅ आपकी प्रतिक्रिया सुरक्षित रूप से हमारे डेटाबेस में दर्ज कर दी गई है।")
        except Exception as e:
            st.error(f"⚠️ डेटाबेस में सेव नहीं किया जा सका: {str(e)}")

# ---------- अतिरिक्त सुविधाओं वाला साइडबार ----------
with st.sidebar:
    st.header("ℹ️ इस टूल के बारे में")
    st.write("""
    यह उन्नत लक्षण जांचकर्ता आपके लक्षणों का विश्लेषण करता है:
    - संक्रामक रोग
    - श्वसन स्थितियां
    - पाचन विकार
    - न्यूरोलॉजिकल समस्याएं
    - हृदय संबंधी जोखिम
    - कैंसर संकेतक
    """)
    
    st.header("📈 स्वास्थ्य मेट्रिक्स")
    if submitted and 'bmi_value' in locals():
        st.metric("आपका बीएमआई", f"{bmi_value:.1f}")
        st.metric("जोखिम स्कोर", f"{risk_score:.1f}%")
        
        # बीएमआई चार्ट
        bmi_data = pd.DataFrame({
            'श्रेणी': ['कम वजन', 'सामान्य', 'अधिक वजन', 'मोटापा'],
            'सीमा': ['<18.5', '18.5-24.9', '25-29.9', '30+']
        })
        st.dataframe(bmi_data, hide_index=True)
    
    st.header("🚨 आपातकालीन लक्षण")
    st.write("""
    तत्काल चिकित्सकीय देखभाल लें:
    - सीने में दर्द/दबाव
    - सांस लेने में कठिनाई
    - गंभीर पेट दर्द
    - अचानक कमजोरी/सुन्नता
    - आत्महत्या के विचार
    - गंभीर रक्तस्राव
    """)

# ---------- फुटर ----------
st.markdown("---")
st.caption("""
⚠️ **अस्वीकरण**: यह टूल केवल शैक्षिक और सूचनात्मक उद्देश्यों के लिए है। 
यह चिकित्सकीय सलाह, निदान या उपचार प्रदान नहीं करता है। चिकित्सकीय चिंताओं के लिए 
हमेशा योग्य स्वास्थ्य देखभाल पेशेवरों से परामर्श लें।
""")
