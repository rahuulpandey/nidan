# # app.py
# # Entrypoint for the Streamlit app. Keeps the app bootstrap minimal.
# import streamlit as st
# from config import load_env
# load_env()
# from ui import run_app
# from auth import login, signup


# # from processor import (
# #     pil_to_gray_np, enhance_xray, enhance_ct, enhance_mri,
# #     enhance_generic, analyze_quality, to_pil
# # )

# # ---------- Session State Init ----------

# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False

# if "user" not in st.session_state:
#     st.session_state.user = None

# if "auth_mode" not in st.session_state:
#     st.session_state.auth_mode = "login"

# def auth_page():
#     st.title("NIDAN.ai")

#     col1, col2 = st.columns(2)

#     with col1:
#         if st.button("Login", key="switch_to_login"):
#             st.session_state.auth_mode = "login"

#     with col2:
#         if st.button("Sign Up", key="switch_to_signup"):
#             st.session_state.auth_mode = "signup"

#     st.markdown("---")

#     if st.session_state.auth_mode == "login":
#         login()
#     else:
#         signup()


# def main():
#     if not st.session_state.authenticated:
#         auth_page()
#     else:
#         run_app()
    
# if __name__ == "__main__":
#     main()


# app.py
# Entrypoint for the Streamlit app.

import streamlit as st
from config import load_env

load_env()

from ui import run_app
from auth import login, signup, init_db

# Initialise DB
init_db()

# ---------- Session State Init ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


def auth_page():
    st.set_page_config(page_title="NIDAN.ai", layout="centered")

    # ── Hero ──────────────────────────────────────────────
    st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1rem 0;">
            <h1 style="font-size:3rem; color:#4da3ff; margin-bottom:0;">NIDAN.ai</h1>
            <p style="color:#aaa; font-size:1.05rem;">
                Your AI-powered medical report analysis assistant
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Tab switcher ──────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True,
                     type="primary" if st.session_state.auth_mode == "login" else "secondary"):
            st.session_state.auth_mode = "login"
    with col2:
        if st.button("📝 Sign Up", use_container_width=True,
                     type="primary" if st.session_state.auth_mode == "signup" else "secondary"):
            st.session_state.auth_mode = "signup"

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Card container ────────────────────────────────────
    with st.container(border=True):
        if st.session_state.auth_mode == "login":
            login()
        else:
            signup()

    # ── Footer note ───────────────────────────────────────
    st.markdown("""
        <div style="text-align:center; margin-top:2rem; color:#555; font-size:0.85rem;">
            NIDAN.ai · B.Tech Final Year Project · For educational purposes only
        </div>
    """, unsafe_allow_html=True)


def main():
    if not st.session_state.authenticated:
        auth_page()
    else:
        # ── Sidebar logout ────────────────────────────────
        with st.sidebar:
            st.markdown(f"""
                <div style="
                    background: rgba(77,163,255,0.1);
                    border: 1px solid #4da3ff33;
                    border-radius: 10px;
                    padding: 12px 16px;
                    margin-bottom: 1rem;
                ">
                    <p style="margin:0; color:#9ad1ff; font-size:0.85rem;">Logged in as</p>
                    <p style="margin:0; color:#fff; font-weight:600; font-size:0.95rem; 
                       word-break:break-all;">
                       {st.session_state.user}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Logout", use_container_width=True, type="primary"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.auth_mode = "login"
                st.rerun()

        run_app()


if __name__ == "__main__":
    main()