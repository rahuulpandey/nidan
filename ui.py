# ui.py
# Main Streamlit UI. This file composes the app using the small services above.

import streamlit as st
import streamlit.components.v1 as components
from config import CSS_FILE
from utils import get_default_image_paths, encode_image, get_base64_image_raw, trim_image
from services.ai_service import chat_with_ai, recommend_doctor
from services.image_service import enhance_and_analyze_image
from services.speech_service import speak_text, listen_speech
from PIL import Image
import os
import html
import re

def load_css():
    if os.path.exists(CSS_FILE):
        with open(CSS_FILE) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def hero_and_slideshow():
    # Simple hero text
    heading = """
    <div class="header">
        <h1>NIDAN.AI</h1>
        <p><b>NIDAN.AI</b> is an intelligent health diagnosis assistant that helps users understand symptoms and receive health insights in real time.</p>
    </div>
    """
    st.markdown(heading, unsafe_allow_html=True)

SYMPTOM_CATEGORIES = {
    "emergency": [
        "chest pain", "breathing", "shortness of breath",
        "heart", "severe pain", "unconscious", "bleeding"
    ],

    "common_physical": [
        "fever", "cold", "cough", "headache",
        "stomach", "pain", "body ache", "nausea", "vomiting"
    ],

    "mental_health": [
        "anxiety", "stress", "panic", "depression",
        "sad", "low mood", "overthinking", "fear"
    ],

    "lifestyle": [
        "sleep", "diet", "exercise", "weight",
        "tired", "fatigue", "routine", "hydration"
    ],

    "skin": [
        "rash", "itching", "acne", "skin", "allergy",
        "redness", "burn", "irritation"
    ]
}

EXPLANATION_TEMPLATES = {
    "emergency": (
        "This response focuses on caution because the symptoms mentioned "
        "may indicate a potentially serious condition that requires prompt medical attention."
    ),

    "common_physical": (
        "This response is based on commonly reported physical symptoms that are often "
        "managed with general care and symptom monitoring."
    ),

    "mental_health": (
        "This response addresses mental or emotional well-being concerns and provides "
        "general supportive guidance rather than medical diagnosis."
    ),

    "lifestyle": (
        "This response focuses on lifestyle-related factors that can influence overall "
        "health and are often managed through routine and habit changes."
    ),

    "skin": (
        "This response is based on common skin-related concerns that are usually managed "
        "with basic care and observation."
    ),

    "default": (
        "This response provides general health-related information based on the concern described."
    )
}
 
# small explanation generator
def generate_explanation(user_query: str) -> str:
    q = user_query.lower()

    for category, keywords in SYMPTOM_CATEGORIES.items():
        if any(keyword in q for keyword in keywords):
            return EXPLANATION_TEMPLATES.get(category, EXPLANATION_TEMPLATES["default"])

    return EXPLANATION_TEMPLATES["default"]


def format_ai_text(text: str) -> str:
    text = html.escape(text)

    # Convert ### headings to h3
    text = re.sub(r"^### (.*)$", r"<h3 style='color:#f5c16c;'>\1</h3>", text, flags=re.MULTILINE)

    # Convert **bold** to <b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    # Convert bullet points
    text = re.sub(r"^\* (.*)$", r"• \1", text, flags=re.MULTILINE)

    # Line breaks
    text = text.replace("\n", "<br>")

    return text


def run_app():

    st.markdown("""
    <style>
    /* Style ALL secondary buttons as destructive */
    button[kind="primary"] {
        border: none !important;
        background: rgba(220, 53, 69, 0.15) !important; /* soft danger red */
        color: #ff6b6b !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.9rem !important;
    }

    /* Hover */
    button[kind="primary"]:hover {
        background: rgba(220, 53, 69, 0.28) !important;
        color: #ff4d4d !important;
    }

    /* Active */
    button[kind="primary"]:active {
        background: rgba(220, 53, 69, 0.35) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# Basic Streamlit page config (should be first call)
    st.set_page_config(page_title="NIDAN.ai", layout="wide")
    load_css()

    hero_and_slideshow()
    st.markdown("---")

# Chat interface
    st.markdown("""<div class="input-label"><h1>Your Health Query</h1></div>""", unsafe_allow_html=True)

    if "user_query" not in st.session_state:
        st.session_state.user_query = ""
    if "ai_response" not in st.session_state:
        st.session_state.ai_response = ""
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    if "listening" not in st.session_state:
        st.session_state.listening = False
    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


#input box and clear button
    col_input, col_clear = st.columns([12, 1])

    with col_input:
        st.session_state.user_query = st.text_input(
            "Enter your query",
            value=st.session_state.speech_text or st.session_state.user_query,
            placeholder="Describe your health concern...",
            label_visibility="collapsed"
        )

    with col_clear:
        clear_clicked = st.button(
            "🗑 Clear",
            key="clear_chat_icon",
            help="Clear chat history",
            type="primary",
            use_container_width=True
    )


  

# live status indicator so the user sees the state change instantly.

    if st.session_state.listening:
        mic_status = "Listening…" if st.session_state.listening else "Mic idle"
        mic_color = "#ff4b4b" if st.session_state.listening else "#6c757d"

        st.markdown(
            f"<div class='mic-status' style='color:{mic_color};'>🎙 {mic_status}</div>",
            unsafe_allow_html=True
        )

# mic buttons and function

    col1, col2 = st.columns([1, 1])

    with col1:
        mic_label = "⏹ Stop Listening" if st.session_state.listening else "🎙 Start Listening"
        if st.button(mic_label):
            st.session_state.listening = not st.session_state.listening
            if not st.session_state.listening:
                st.toast("Listening stopped", icon="⏹")

    with col2:
        if st.button("Send 🤖", disabled=st.session_state.listening):
            if st.session_state.user_query.strip():
                ai_response = chat_with_ai(st.session_state.user_query)
                st.session_state.chat_history.append({
                    "user": st.session_state.user_query,
                    "ai": ai_response,
                    "explanation": generate_explanation(st.session_state.user_query)
                })

                st.session_state.user_query = "" 
            else:
                st.warning("⚠️ Please provide a query to send.")
# listening 
    if st.session_state.listening:
        with st.spinner("Listening..."):
            text = listen_speech()

        if text:
            st.session_state.speech_text = text.strip()
            st.session_state.user_query = st.session_state.speech_text
            st.session_state.listening = False
            st.success(f"You said: {text}")



#clear button
    if clear_clicked:
        st.session_state.chat_history = []
        st.session_state.user_query = ""
        st.session_state.speech_text = ""
        st.session_state.listening = False
        st.toast("Chat cleared", icon="🧹")


            
# chat history 
    if st.session_state.chat_history:

        chat_html = """
        <div style="
            max-height: 360px;
            overflow-y: auto;
            padding: 14px;
            border: 1px solid #333;
            border-radius: 10px;
            background-color: rgba(255,255,255,0.03);
            color: #eaeaea;
            font-family: system-ui, sans-serif;
        ">
        """

        for chat in st.session_state.chat_history:
            user_text = html.escape(chat["user"]).replace("\n", "<br>")
            ai_text = format_ai_text(chat["ai"])
            explanation_text = html.escape(chat["explanation"])

            chat_html += f"""
            <div style="margin-bottom: 18px;">
                <div style="
                    padding: 10px 12px;
                    margin-bottom: 8px;
                    border-left: 4px solid #4da3ff;
                    background: rgba(77,163,255,0.08);
                    font-weight: 600;
                    color: #e6f1ff;
                    border-radius: 6px;
                    <b>Why this response?</b><br>
                    {explanation_text}
                ">
                    <span style="color:#9ad1ff;">You:</span> {user_text}
                </div>

                <div style="
                    padding: 10px 12px;
                    border-left: 4px solid #f5c16c;
                    background: rgba(245,193,108,0.06);
                    color: #eaeaea;
                    border-radius: 6px;
                ">
                    <span style="color:#f5c16c; font-weight:600;">NIDAN.ai:</span><br>
                    {ai_text}
                </div>
            </div>
            """

        chat_html += "</div>"

        components.html(chat_html, height=420, scrolling=True)


# this is the modified part
    st.markdown("---")
    st.markdown("<div class='chat_head'><h1>Medical Image Enhancer and Analyzer</h1></div>", unsafe_allow_html=True)

    # 👇 NEW: modality selection
    modality = st.selectbox(
        "Select the image type",
        ["X-ray", "CT", "MRI", "Other / Not sure"],
        index=0
    )

    uploaded_file = st.file_uploader("Upload a medical image (e.g., X-ray, MRI)", type=["png", "jpg", "jpeg"])

# this is the modified part
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        # 👇 pass modality to the service
        enhanced_img, edges_img, mean_intensity, edge_density, ai_feedback = enhance_and_analyze_image(image, modality)
        trimmed_image = trim_image(image)


# this is the modified part
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(image, caption="Original Image", width=200)
        with col2:
            st.image(enhanced_img, caption=f"Enhanced Image ({modality})", width=200)
        with col3:
            st.image(edges_img, caption="Edge Map (Canny Detection)", width=200)
        with col4:
            st.image(trimmed_image, caption="Trimmed Image", width=200)


            st.markdown(f"🔬 Mean Intensity: {mean_intensity:.2f}")
            st.markdown(f"🔍 Edge Density: {edge_density:.4f}")
            st.markdown(f"🧠 AI Analysis: {ai_feedback}")


    else:
        st.info("Upload a medical image to see enhancement and analysis.")



    st.markdown("---")
    st.markdown("<div class='chat_head'><h1>Doctor Recommendation</h1></div>", unsafe_allow_html=True)


#new import for doctor search

    symptom = st.text_input("Enter your symptom", key="symptom")
    location = st.text_input("Enter the Location", key="location")
    if st.button("Search", use_container_width=True, key="search_doctor"):
        if symptom.strip():
            doctor_recommendation = recommend_doctor(symptom, location)
            st.markdown(f"<div class='text-box'>{doctor_recommendation}</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a symptom before searching.")




    # Footer (kept simple)
    st.markdown("""
    <footer class="footer">
        <div class="footer-container">
            <div class="footer-left">
                <p><b>By Team Rahul</b></p>
            </div>
            <div class="footer-center">
                <ul class="social-links">
                    <li><a href="https://www.linkedin.com/in/rahul-pandey-207baa276/" target="_blank">LinkedIn</a></li>
                    <li><a href="https://github.com/rahuulpandey" target="_blank">GitHub</a></li>
                </ul>
            </div>
        </div>
    </footer>
    """, unsafe_allow_html=True)
