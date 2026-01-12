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

    # # Slideshow using local images encoded as base64
    # image_paths = get_default_image_paths()
    # encoded_images = [encode_image(path) for path in image_paths if os.path.exists(path)]
    # html = f"""
    # <div class="slideshow-container">
    #     {''.join([f'<img class="mySlides" src="{img}">' for img in encoded_images])}
    # </div>
    # <script>
    # let slideIndex = 0;
    # function showSlides() {{
    #   let slides = document.getElementsByClassName("mySlides");
    #   for (let i = 0; i < slides.length; i++) {{
    #     slides[i].style.display = "none";
    #   }}
    #   slideIndex++;
    #   if (slideIndex > slides.length) {{ slideIndex = 1; }}
    #   if (slides.length>0) slides[slideIndex - 1].style.display = "block";
    #   setTimeout(showSlides, 2000);
    # }}
    # showSlides();
    # </script>
    # """
    # components.html(html, height=420)

def run_app():
    # Basic Streamlit page config (should be first call)
    st.set_page_config(page_title="NIDAN.ai", layout="wide")
    load_css()

    hero_and_slideshow()
    st.markdown("---")

    # Chat interface
    st.markdown("""<div class="chat_head"><h1>Interactive AI Health Advisor</h1></div>""", unsafe_allow_html=True)

    if "user_query" not in st.session_state:
        st.session_state.user_query = ""
    if "ai_response" not in st.session_state:
        st.session_state.ai_response = ""
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    st.session_state.user_query = st.text_input(
        "Enter your query: (Ability to answer up to 40+ languages)",
        value=st.session_state.get("user_query", ""),
        key="user_query_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Speak 🎙️", key="listen"):
            text = listen_speech()
            st.session_state.user_query = text.strip()
            st.success(f"You said: {text}")
    with col2:
        if st.button("Send 🤖", key="send"):
            if st.session_state.user_query.strip():
                ai_response = chat_with_ai(st.session_state.user_query)
                st.session_state.ai_response = ai_response
                st.session_state.query_history.append(st.session_state.user_query)
                st.success(ai_response)
            else:
                st.warning("⚠️ Please provide a query to send.")

    # Show history if present
    if st.session_state.query_history:
        st.markdown(f"<h3 class='history-head'>Search History <span class='counter'>({len(st.session_state.query_history)})</span></h3>", unsafe_allow_html=True)
        for i, q in enumerate(reversed(st.session_state.query_history), 1):
            st.markdown(f"<p class='query-item'>{i}. {q}</p>", unsafe_allow_html=True)



    # this is original and under this is the modified portion
        
    # st.markdown("---")
    # st.markdown("<div class='chat_head'><h1>Medical Image Enhancer and Analyzer</h1></div>", unsafe_allow_html=True)

    # uploaded_file = st.file_uploader("Upload a medical image (e.g., X-ray, MRI)", type=["png", "jpg", "jpeg"])




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

# this is original
    # if uploaded_file is not None:
    #     image = Image.open(uploaded_file)

    #     grayscale_img, edges_img, mean_intensity, edge_density, ai_feedback = enhance_and_analyze_image(image)
    #     trimmed_image = trim_image(image)


# this is the modified part
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        # 👇 pass modality to the service
        enhanced_img, edges_img, mean_intensity, edge_density, ai_feedback = enhance_and_analyze_image(image, modality)
        trimmed_image = trim_image(image)



# this is original
        # col1, col2, col3, col4 = st.columns(4)
        # with col1:
        #     st.image(image, caption="Original Image", width=200)
        # with col2:
        #     st.image(grayscale_img, caption="Grayscale Image", width=200)
        # with col3:
        #     st.image(edges_img, caption="Edge Map (Canny Detection)", width=200)
        # with col4:
        #     st.image(trimmed_image, caption="Trimmed Image", width=200)


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

    # symptom = st.text_input("Enter your symptom", key="symptom")
    # location = st.text_input("Enter the Location", key="location")
    # if st.button("Search", use_container_width=True, key="search_doctor"):
    #     if symptom.strip():
    #         doctor_recommendation = recommend_doctor(symptom, location)
    #         st.markdown(f"<div class='text-box'>{doctor_recommendation}</div>", unsafe_allow_html=True)
    #     else:
    #         st.warning("⚠️ Please enter a symptom before searching.")



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
