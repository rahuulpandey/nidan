# app.py
# Entrypoint for the Streamlit app. Keeps the app bootstrap minimal.
import streamlit as st
from config import load_env
load_env()
from ui import run_app
from ui import run_app
from auth import login, signup


# from processor import (
#     pil_to_gray_np, enhance_xray, enhance_ct, enhance_mri,
#     enhance_generic, analyze_quality, to_pil
# )

# ---------- Session State Init ----------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

def auth_page():
    st.title("NIDAN.ai")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", key="switch_to_login"):
            st.session_state.auth_mode = "login"

    with col2:
        if st.button("Sign Up", key="switch_to_signup"):
            st.session_state.auth_mode = "signup"

    st.markdown("---")

    if st.session_state.auth_mode == "login":
        login()
    else:
        signup()


def main():
    if not st.session_state.authenticated:
        auth_page()
    else:
        run_app()

if __name__ == "__main__":
    main()
