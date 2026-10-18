import streamlit as st
import google.generativeai as genai
from twilio.rest import Client

# Page Configuration
st.set_page_config(page_title="MacroSnap - Nutrition Tracker", page_icon="🥗", layout="centered")

st.title("🥗 MacroSnap - AI Nutrition Tracker")
st.write("तुमच्या जेवणाचा फोटो किंवा वर्णन टाका आणि न्यूट्रिशन (Macros) ट्रॅक करा!")

# secrets.toml मधून API Keys लोड करणे
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    twilio_sid = st.secrets["TWILIO_ACCOUNT_SID"]
    twilio_token = st.secrets["TWILIO_AUTH_TOKEN"]
    twilio_from = st.secrets["TWILIO_WHATSAPP_FROM"]
    
    # Gemini AI Setup
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-3.8-flash')
except Exception as e:
    st.error(f"Secrets लोड करताना अडचण आली: {e}")
    st.stop()

# User Input - Text or Image
user_prompt = st.text_input("आज तुम्ही काय खाल्ले? (उदा. 2 Chapati, 1 Bowl Dal)")

if st.button("Analyze & Log Meal"):
    if user_prompt:
        with st.spinner("Gemini AI तुमचे जेवण विश्लेषित करत आहे..."):
            prompt = f"""
            You are a professional nutritionist. Analyze the following meal description: "{user_prompt}".
            Provide:
            1. Estimated Total Calories
            2. Protein, Carbs, Fats breakdown
            3. A short nutritional tip in Marathi.
            Keep the response concise and well-formatted.
            """
            
            try:
                response = model.generate_content(prompt)
                nutrition_data = response.text
                
                st.success("विश्लेषण पूर्ण झाले!")
                st.markdown("### 📊 Nutrition Analysis:")
                st.write(nutrition_data)

                # Send WhatsApp Alert via Twilio
                try:
                    twilio_client = Client(twilio_sid, twilio_token)
                    message = twilio_client.messages.create(
                        body=f"🥗 *MacroSnap Summary*:\n{nutrition_data[:300]}...",
                        from_=twilio_from,
                        to="whatsapp:+91YOUR_NUMBER_HERE" # येथे तुमचा नंबर टाकू शकता
                    )
                    st.info("📱 WhatsApp वर रिपोर्ट पाठवला आहे!")
                except Exception as twilio_err:
                    st.warning("WhatsApp मॅसेज पाठवता आला नाही, पण ॲपमध्ये माहिती सेव्ह झाली आहे.")
                    
            except Exception as gemini_err:
                st.error(f"Gemini API Error: {gemini_err}")
    else:
        st.warning("कृपया काहीतरी वर्णन टाईप करा!")