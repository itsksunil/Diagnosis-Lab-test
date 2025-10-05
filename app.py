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
    fever_symptoms = [
        "बुखार", "ठंड लगना", "पसीना आना", "शरीर का तापमान बढ़ना", 
        "बुखार आना-जाना", "तेज बुखार (104°F+)", "हल्का बुखार (100-101°F)"
    ]
    
    basic_symptoms = [
        "थकान", "सिरदर्द", "मतली", "उल्टी", 
        "मांसपेशियों में दर्द", "जोड़ों में दर्द", "कमजोरी", "चक्कर आना",
        "भूख न लगना", "शरीर में दर्द"
    ]
    
    respiratory_symptoms = [
        "खांसी", "सांस लेने में तकलीफ", "छाती में जकड़न", "बहती नाक", 
        "गले में खराश", "छींक आना", "घरघराहट", "गंध न आना", "स्वाद न आना"
    ]
    
    digestive_symptoms = [
        "दस्त", "पेट दर्द", "पेट फूलना", "कब्ज", "सीने में जलन", 
        "मल में खून", "निगलने में कठिनाई", "अत्यधिक प्यास लगना", 
        "बार-बार पेशाब आना", "पेट में ऐंठन"
    ]
    
    skin_symptoms = [
        "चकत्ते", "खुजली", "पीली त्वचा/आंखें", "त्वचा का रंग बदलना",
        "पित्ती", "सूजन", "आसानी से चोट लगना", "रात को पसीना आना",
        "त्वचा पर लाल धब्बे", "आंखों में दर्द", "आंखों का लाल होना"
    ]
    
    neurological_symptoms = [
        "भ्रम", "याददाश्त की समस्या", "सुन्नता", "झुनझुनी सनसनी",
        "दृष्टि संबंधी समस्याएं", "सुनने में समस्या", "संतुलन की समस्या", "दौरे",
        "बोलने में कठिनाई", "कंपन", "तेज सिरदर्द"
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
    st.subheader("🌡️ बुखार और संक्रमण संबंधी लक्षण")
    selected_fever = st.multiselect("बुखार के लक्षण", fever_symptoms)
    
    st.subheader("🔍 अन्य लक्षण")
    selected_basic = st.multiselect("सामान्य लक्षण", basic_symptoms)
    selected_respiratory = st.multiselect("श्वसन संबंधी लक्षण", respiratory_symptoms)
    selected_digestive = st.multiselect("पाचन संबंधी लक्षण", digestive_symptoms)
    selected_skin = st.multiselect("त्वचा और रूप संबंधी लक्षण", skin_symptoms)
    selected_neurological = st.multiselect("न्यूरोलॉजिकल लक्षण", neurological_symptoms)
    selected_cancer = st.multiselect("कैंसर के लक्षण", cancer_symptoms)
    selected_heart = st.multiselect("हृदय और संचार संबंधी लक्षण", heart_symptoms)

    # अतिरिक्त जानकारी
    st.subheader("📋 अतिरिक्त जानकारी")
    col3, col4 = st.columns(2)
    with col3:
        symptom_duration = st.selectbox("आपको ये लक्षण कितने समय से हैं?", 
                                      ["1 सप्ताह से कम", "1-2 सप्ताह", "2-4 सप्ताह", "1-3 महीने", "3 महीने से अधिक"])
        severity = st.select_slider("लक्षणों की गंभीरता", options=["हल्के", "मध्यम", "गंभीर"])
        fever_pattern = st.selectbox("बुखार का पैटर्न", 
                                   ["लगातार बुखार", "बुखार आना-जाना", "सुबह कम/शाम को ज्यादा", "कोई विशेष पैटर्न नहीं"])
    with col4:
        smoking = st.checkbox("धूम्रपान करने वाला")
        alcohol = st.checkbox("नियमित शराब का सेवन")
        exercise = st.selectbox("व्यायाम की आवृत्ति", 
                              ["कभी नहीं", "कभी-कभी", "सप्ताह में 1-2 बार", "सप्ताह में 3-5 बार", "रोज"])
        recent_travel = st.checkbox("हाल ही में यात्रा की है")

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
def enhanced_diagnose(fever, basic, respiratory, digestive, skin, neurological, cancer, heart, age, medical_history, lifestyle, fever_pattern, recent_travel):
    conditions = []
    risk_factors = []
    recommendations = []
    risk_score = 0
    
    all_symptoms = fever + basic + respiratory + digestive + skin + neurological + cancer + heart
    symptom_count = len(all_symptoms)
    
    # चिकित्सा इतिहास और जीवनशैली से जोखिम कारक
    if medical_history.get('bp'): risk_factors.append("उच्च रक्तचाप")
    if medical_history.get('diabetes'): risk_factors.append("मधुमेह")
    if medical_history.get('heart'): risk_factors.append("हृदय रोग इतिहास")
    if medical_history.get('smoking'): risk_factors.append("धूम्रपान")
    if medical_history.get('alcohol'): risk_factors.append("शराब का सेवन")
    if recent_travel: risk_factors.append("हाल की यात्रा")
    
    # -------------------------------
    # बुखार और संक्रमण विश्लेषण
    # -------------------------------
    
    # सामान्य बुखार (Normal Fever)
    if "बुखार" in fever and len(fever) == 1 and len([s for s in basic if s in ["सिरदर्द", "शरीर में दर्द", "थकान"]]) >= 2:
        conditions.append(("सामान्य बुखार (वायरल फीवर)", "प्रतिरक्षा प्रणाली", "कम"))
        recommendations.append("आराम करें, हाइड्रेटेड रहें, और पैरासिटामोल लें")
    
    # वायरल फीवर (Viral Fever)
    viral_fever_symptoms = ["बुखार", "सिरदर्द", "शरीर में दर्द", "थकान", "कमजोरी"]
    viral_count = sum(1 for symptom in viral_fever_symptoms if symptom in (fever + basic))
    if viral_count >= 4:
        conditions.append(("वायरल फीवर", "प्रतिरक्षा प्रणाली", "मध्यम"))
        recommendations.append("भरपूर आराम करें और तरल पदार्थ लें")
    
    # डेंगू (Dengue) - मच्छर जनित
    dengue_symptoms = ["तेज बुखार (104°F+)", "तेज सिरदर्द", "आंखों में दर्द", "जोड़ों में दर्द", "मांसपेशियों में दर्द", "त्वचा पर लाल धब्बे"]
    dengue_count = sum(1 for symptom in dengue_symptoms if symptom in (fever + basic + skin))
    if dengue_count >= 4:
        conditions.append(("डेंगू बुखार", "रक्त और प्रतिरक्षा प्रणाली", "उच्च"))
        risk_factors.append("मच्छर जनित संक्रमण")
        recommendations.append("🚨 तुरंत रक्त जांच कराएं और डॉक्टर से संपर्क करें")
        recommendations.append("प्लेटलेट काउंट की निगरानी करें")
    
    # मलेरिया (Malaria) - मच्छर जनित
    malaria_symptoms = ["बुखार आना-जाना", "ठंड लगना", "पसीना आना", "सिरदर्द", "मतली", "थकान"]
    malaria_count = sum(1 for symptom in malaria_symptoms if symptom in (fever + basic))
    if malaria_count >= 4 and fever_pattern in ["बुखार आना-जाना", "सुबह कम/शाम को ज्यादा"]:
        conditions.append(("मलेरिया", "रक्त और लिवर", "उच्च"))
        risk_factors.append("मच्छर जनित संक्रमण")
        recommendations.append("🚨 मलेरिया ब्लड टेस्ट कराएं")
        recommendations.append("एंटी-मलेरियल दवाएं शुरू करें")
    
    # टाइफाइड (Typhoid) - जल/भोजन जनित
    typhoid_symptoms = ["तेज बुखार (104°F+)", "सिरदर्द", "कमजोरी", "पेट दर्द", "दस्त या कब्ज", "भूख न लगना"]
    typhoid_count = sum(1 for symptom in typhoid_symptoms if symptom in (fever + basic + digestive))
    if typhoid_count >= 4:
        conditions.append(("टाइफाइड बुखार", "पाचन तंत्र और रक्त", "उच्च"))
        risk_factors.append("दूषित भोजन/पानी")
        recommendations.append("🚨 विडाल टेस्ट कराएं और एंटीबायोटिक्स शुरू करें")
        recommendations.append("हाइजीन का विशेष ध्यान रखें")
    
    # चिकनगुनिया (Chikungunya) - मच्छर जनित
    if "जोड़ों में दर्द" in basic and "बुखार" in fever and "त्वचा पर लाल धब्बे" in skin:
        conditions.append(("चिकनगुनिया", "जोड़ और प्रतिरक्षा प्रणाली", "मध्यम"))
        recommendations.append("जोड़ों के दर्द के लिए फिजियोथेरेपी लें")
    
    # -------------------------------
    # अन्य स्थितियां
    # -------------------------------
    
    # श्वसन संक्रमण
    respiratory_symptom_count = len(respiratory)
    if respiratory_symptom_count >= 2 and "बुखार" in fever:
        if "खांसी" in respiratory and "सांस लेने में तकलीफ" in respiratory:
            conditions.append(("श्वसन संक्रमण (COVID-19/इन्फ्लुएंजा/निमोनिया)", "श्वसन प्रणाली", "उच्च"))
        if "घरघराहट" in respiratory and "सांस लेने में तकलीफ" in respiratory:
            conditions.append(("अस्थमा/ब्रोंकाइटिस", "श्वसन प्रणाली", "मध्यम"))
    
    # पाचन संक्रमण
    digestive_symptom_count = len(digestive)
    if digestive_symptom_count >= 3 and "बुखार" in fever:
        if "दस्त" in digestive and "पेट दर्द" in digestive:
            conditions.append(("गैस्ट्रोएंटेराइटिस", "पाचन तंत्र", "मध्यम"))
        if "मल में खून" in digestive:
            conditions.append(("पेचिश/आंत्रशोथ", "पाचन तंत्र", "उच्च"))
    
    # हेपेटाइटिस
    if "पीली त्वचा/आंखें" in skin and "बुखार" in fever:
        conditions.append(("हेपेटाइटिस/लिवर संक्रमण", "लिवर", "उच्च"))
    
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
    base_score = min(symptom_count * 4, 40)
    age_score = min(age * 0.5, 20)
    medical_score = len(risk_factors) * 5
    lifestyle_score = 0
    if lifestyle.get('smoking'): lifestyle_score += 10
    if lifestyle.get('alcohol'): lifestyle_score += 5
    if lifestyle.get('exercise') in ["कभी नहीं", "कभी-कभी"]: lifestyle_score += 5
    
    # बुखार के लिए अतिरिक्त स्कोर
    fever_score = len(fever) * 3
    risk_score = min(base_score + age_score + medical_score + lifestyle_score + fever_score, 95)
    
    # सामान्य सिफारिशें
    if "बुखार" in fever:
        recommendations.append("तापमान की नियमित निगरानी करें")
        recommendations.append("पर्याप्त मात्रा में तरल पदार्थ पिएं")
    
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
            selected_fever, selected_basic, selected_respiratory, selected_digestive, 
            selected_skin, selected_neurological, selected_cancer, 
            selected_heart, age, medical_history, lifestyle, fever_pattern, recent_travel
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
            total_symptoms = len(selected_fever + selected_basic + selected_respiratory + 
                               selected_digestive + selected_skin + selected_neurological + 
                               selected_cancer + selected_heart)
            st.metric("लक्षणों की सूचना", total_symptoms)
        
        # बुखार विश्लेषण
        if selected_fever:
            st.info("## 🌡️ बुखार विश्लेषण")
            fever_symptoms_text = ", ".join(selected_fever)
            st.write(f"**चयनित बुखार लक्षण:** {fever_symptoms_text}")
            st.write(f"**बुखार पैटर्न:** {fever_pattern}")
            
            # बुखार प्रकार का सारांश
            if any("डेंगू" in cond[0] for cond in conditions):
                st.warning("🔴 **डेंगू के लक्षण:** उच्च बुखार, सिरदर्द, आंखों में दर्द, जोड़ों में दर्द")
            if any("मलेरिया" in cond[0] for cond in conditions):
                st.warning("🔴 **मलेरिया के लक्षण:** बुखार आना-जाना, ठंड लगना, पसीना आना")
            if any("टाइफाइड" in cond[0] for cond in conditions):
                st.warning("🔴 **टाइफाइड के लक्षण:** लगातार उच्च बुखार, पेट दर्द, कमजोरी")
        
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
        if "बुखार" in selected_fever:
            st.write("• भरपूर आराम करें और हाइड्रेटेड रहें")
            st.write("• तापमान की नियमित जांच करें")
            st.write("• डॉक्टर की सलाह के बिना एंटीबायोटिक्स न लें")
        
        if bmi_category in ["अधिक वजन", "मोटापा"]:
            st.write("• संतुलित आहार और व्यायाम के माध्यम से वजन प्रबंधन पर विचार करें")
        
        if age > 50:
            st.write("• उम्र के कारण नियमित स्वास्थ्य जांच की सिफारिश की जाती है")

        # ---------- गूगल शीट में डेटा सेव करें ----------
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        all_symptoms = selected_fever + selected_basic + selected_respiratory + selected_digestive + selected_skin + selected_neurological + selected_cancer + selected_heart
        condition_list = [f"{cond} ({risk})" for cond, sys, risk in conditions]
        
        # सटीक कॉलम क्रम में डेटा पंक्ति तैयार करें
        data = [
            entry_time, name, age, gender, mobile, bp, diabetes, heart, thyroid,
            asthma, kidney, liver, cancer_history, location, weight, height,
            ", ".join(all_symptoms), symptom_duration, severity, fever_pattern,
            smoking, alcohol, exercise, recent_travel,
            ", ".join(condition_list), ", ".join(risk_factors), 
            f"{risk_score:.1f}%", f"{bmi_value:.1f}", bmi_category
        ]
        
        try:
            sheet.append_row(data)
            st.success("✅ आपकी प्रतिक्रिया सुरक्षित रूप से हमारे डेटाबेस में दर्ज कर दी गई है।")
        except Exception as e:
            st.error(f"⚠️ डेटाबेस में सेव नहीं किया जा सका: {str(e)}")

# ---------- साइडबार ----------
with st.sidebar:
    st.header("ℹ️ इस टूल के बारे में")
    st.write("""
    यह उन्नत लक्षण जांचकर्ता विशेष रूप से विश्लेषण करता है:
    - सामान्य बुखार vs वायरल फीवर
    - डेंगू, मलेरिया, टाइफाइड
    - श्वसन संक्रमण
    - पाचन विकार
    - हृदय संबंधी जोखिम
    """)
    
    st.header("🌡️ बुखार प्रकार गाइड")
    fever_guide = {
        "सामान्य बुखार": ["हल्का बुखार", "सिरदर्द", "शरीर दर्द"],
        "वायरल फीवर": ["तेज बुखार", "थकान", "कमजोरी", "भूख न लगना"],
        "डेंगू": ["तेज बुखार (104°F+)", "आंखों में दर्द", "जोड़ों में दर्द", "त्वचा पर रैश"],
        "मलेरिया": ["बुखार आना-जाना", "ठंड लगकर बुखार आना", "पसीना आना"],
        "टाइफाइड": ["लगातार उच्च बुखार", "पेट दर्द", "दस्त/कब्ज", "कमजोरी"]
    }
    
    for fever_type, symptoms in fever_guide.items():
        with st.expander(f"{fever_type}"):
            for symptom in symptoms:
                st.write(f"• {symptom}")
    
    st.header("🚨 आपातकालीन लक्षण")
    st.write("""
    तत्काल चिकित्सकीय देखभाल लें:
    - 104°F से अधिक बुखार
    - सांस लेने में कठिनाई
    - गंभीर पेट दर्द
    - लगातार उल्टी
    - भ्रम या चक्कर आना
    - त्वचा पर रैश के साथ बुखार
    """)

# ---------- फुटर ----------
st.markdown("---")
st.caption("""
⚠️ **अस्वीकरण**: यह टूल केवल शैक्षिक और सूचनात्मक उद्देश्यों के लिए है। 
यह चिकित्सकीय सलाह, निदान या उपचार प्रदान नहीं करता है। बुखार या गंभीर लक्षणों के 
मामले में हमेशा योग्य स्वास्थ्य देखभाल पेशेवरों से परामर्श लें।
""")
