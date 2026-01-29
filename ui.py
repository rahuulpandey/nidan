# ui.py
# Main Streamlit UI. This file composes the app using the small services above.

import streamlit as st
import streamlit.components.v1 as components
from config import CSS_FILE
from utils import get_default_image_paths, encode_image, get_base64_image_raw, trim_image
from services.ai_service import chat_with_ai, recommend_doctor
from services.image_service import enhance_and_analyze_image
from services.speech_service import speak_text, listen_speech
from services.ai_service import analyze_medical_image_with_ai
from PIL import Image
import os
import html
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap 

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

# small explanation generator
def generate_explanation(user_query: str) -> str:
    q = user_query.lower()

    for category, keywords in SYMPTOM_CATEGORIES.items():
        if any(keyword in q for keyword in keywords):
            return EXPLANATION_TEMPLATES.get(category, EXPLANATION_TEMPLATES["default"])

    return EXPLANATION_TEMPLATES["default"]

#helper function for exporting as text
def export_chat_as_txt(chat_history):
    lines = []
    for i, chat in enumerate(chat_history, 1):
        lines.append(f"Conversation {i}")
        lines.append(f"User: {chat['user']}")
        lines.append(f"NIDAN.ai: {chat['ai']}")
        lines.append("-" * 40)
    return "\n".join(lines)


def clean_markdown(text):
    # Remove markdown symbols
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"###\s*", "", text)
    return text

#helper function for exporting as text

def export_chat_as_pdf(chat_history):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x_margin = 40
    y = height - 50
    max_width = 95

    def new_page():
        nonlocal y
        pdf.showPage()
        pdf.setFont("Helvetica", 11)
        y = height - 50

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(x_margin, y, "NIDAN.ai – Consultation History")
    y -= 30

    for i, chat in enumerate(chat_history, 1):

        # Conversation heading
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x_margin, y, f"Conversation {i}")
        y -= 18

        pdf.setFont("Helvetica", 11)

        sections = [
            ("User:", chat["user"]),
            ("NIDAN.ai:", chat["ai"])
        ]

        for label, content in sections:
            content = clean_markdown(content)

            # Label
            if y < 80:
                new_page()

            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(x_margin, y, label)
            y -= 14

            pdf.setFont("Helvetica", 11)

            paragraphs = content.split("\n")

            for para in paragraphs:
                wrapped_lines = textwrap.wrap(para, max_width)

                for line in wrapped_lines:
                    if y < 60:
                        new_page()

                    pdf.drawString(x_margin + 10, y, line)
                    y -= 14

                y -= 6  # space between paragraphs

        # Divider
        y -= 10
        pdf.setLineWidth(0.5)
        pdf.line(x_margin, y, width - x_margin, y)
        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

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
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


#input box and clear button
    col_input, col_clear = st.columns([12, 1])

    with col_input:
        st.session_state.user_query = st.text_input(
            "Enter your query",
            value=st.session_state.user_query,
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


# # live status indicator so the user sees the state change instantly.

#     if st.session_state.listening:
#         mic_status = "Listening…" if st.session_state.listening else "Mic idle"
#         mic_color = "#ff4b4b" if st.session_state.listening else "#6c757d"

#         st.markdown(
#             f"<div class='mic-status' style='color:{mic_color};'>🎙 {mic_status}</div>",
#             unsafe_allow_html=True
#         )

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
            spoken_text = text.strip()

            # Stop listening immediately
            st.session_state.listening = False
            st.session_state.speech_text = ""
            st.session_state.user_query = ""

            # ✅ Treat voice exactly like typed input
            ai_response = chat_with_ai(spoken_text)

            st.session_state.chat_history.append({
                "user": spoken_text,
                "ai": ai_response,
                "explanation": generate_explanation(spoken_text)
            })

            st.toast("Voice query submitted 🎙️", icon="🤖")
    else:
        st.warning("Could not hear clearly. Please try again.")


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
            # Safe access (very important)
            explanation_text = html.escape(chat.get("explanation", ""))

            chat_html += f"""
            <div style="margin-bottom: 18px;">

                <!-- User message -->
                <div style="
                    padding: 10px 12px;
                    margin-bottom: 6px;
                    border-left: 4px solid #4da3ff;
                    background: rgba(77,163,255,0.08);
                    font-weight: 600;
                    color: #e6f1ff;
                    border-radius: 6px;
                ">
                    <span style="color:#9ad1ff;">You:</span> {user_text}
                </div>

                <!-- Explainable AI panel (only if explanation exists) -->
                {""
                if not explanation_text
                else f'''
                <details style="
                    margin-bottom: 8px;
                    border-left: 4px solid #8bc34a;
                    background: rgba(139,195,74,0.08);
                    padding: 8px 12px;
                    border-radius: 6px;
                    color: #dcedc8;
                    font-size: 13px;
                ">
                    <summary style="
                        cursor: pointer;
                        font-weight: 600;
                        color: #b7e38a;
                        outline: none;
                        user-select: none;
                    ">
                        Why this response?
                    </summary>
                    <div style="margin-top: 6px;">
                        {explanation_text}
                    </div>
                </details>
                 </div>
                '''}

                <!-- AI response -->
                <details open style="
                        padding: 10px 12px;
                        margin-bottom: 14px;
                        border-left: 4px solid #f5c16c;
                        background: rgba(245,193,108,0.06);
                        color: #eaeaea;
                        border-radius: 6px;
                    ">
                        <summary style="
                            cursor: pointer;
                            font-weight: 600;
                            color: #f5c16c;
                            outline: none;
                            user-select: none;
                        ">
                            NIDAN.ai Response
                        </summary>
                        <div style="margin-top: 8px;">
                            {ai_text}
                        </div>
                </details>
            """


        chat_html += "</div>"

        components.html(chat_html, height=420, scrolling=True)

#add export buttons
    with st.sidebar:
        st.markdown("### 📤 Export Consultation")

        if st.session_state.chat_history:

            # File name input (without extension)
            file_name = st.text_input(
                "File name",
                value="nidan_consultation",
                help="Enter file name without extension"
            )

            # File type selector
            file_type = st.radio(
                "Export format",
                options=["TXT", "PDF"],
                horizontal=True
            )

            # Prepare file based on selection
            if file_type == "TXT":
                file_data = export_chat_as_txt(st.session_state.chat_history)
                mime_type = "text/plain"
                final_file_name = f"{file_name}.txt"

            else:  # PDF
                file_data = export_chat_as_pdf(st.session_state.chat_history)
                mime_type = "application/pdf"
                final_file_name = f"{file_name}.pdf"

            # Download button
            st.download_button(
                label="⬇️ Download File",
                data=file_data,
                file_name=final_file_name,
                mime=mime_type
            )

        else:
            st.info("No chat history to export.")




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

        show_intermediate = st.checkbox(
        "Show Enhanced Images",
        value=False
    )
        # 👇 pass modality to the service
        enhanced_img, edges_img, mean_intensity, edge_density, ai_feedback = enhance_and_analyze_image(image, modality)
        ai_vision_report = analyze_medical_image_with_ai(image, modality)
        trimmed_image = trim_image(image)


# this is the modified part
        if show_intermediate:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.image(image, caption="Original Image", width=200)
                with col2:
                    st.image(enhanced_img, caption=f"Enhanced Image ({modality})", width=200)
                with col3:
                    st.image(edges_img, caption="Edge Map (Canny Detection)", width=200)
                with col4:
                    st.image(trimmed_image, caption="Trimmed Image", width=200)
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.image(image, caption="Original Image", width=200)

# Image summary
            st.markdown("### 🔎 Image Analysis Summary")
            st.markdown(f"🔬 Mean Intensity: {mean_intensity:.2f}")
            st.markdown(f"🔍 Edge Density: {edge_density:.4f}")
            st.markdown(f"🧠 AI Analysis: {ai_feedback}")

        with st.expander("🧠 AI Visual Review (Educational)"):
            st.markdown(ai_vision_report)


        with st.expander("ℹ️ What do these metrics mean?"):
            st.markdown("""
            - **Mean Intensity** reflects overall brightness of the image.
            - **Edge Density** indicates the amount of structural detail.
            - These values are used only for visual enhancement, not diagnosis.
            """)


    else:
        st.info("Upload a medical image to see enhancement and analysis.")

    with st.expander("⚠️ Medical Disclaimer"):
        st.markdown("""
        This AI-generated analysis is **educational and non-diagnostic**.

        - This tool performs visual enhancement and basic image analysis .
        - It does NOT detect diseases
        - It does NOT replace a radiologist or doctor
        - Final interpretation must be done by a qualified healthcare professional
        """)


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
