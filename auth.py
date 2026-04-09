# # NOTE: In-memory storage, will be replaced with SQLite

# import streamlit as st
# import hashlib
# import re

# #Password Security using hashlib library
# def hash_password(password: str) -> str:
#     return hashlib.sha256(password.encode()).hexdigest()

# #In-memory user store (temporary)
# USERS = {}

# # Signup 
# def signup():
#     st.subheader("📝 Create Account")

#     email = st.text_input("Email", key="signup_email")
#     password = st.text_input("Password", type="password", key="signup_password")
#     confirm = st.text_input("Confirm Password", type="password")

#     if st.button("Sign Up", key="signup_submit"):

#         if not email or not password:
#             st.error("All fields are required")
#             return

#         # ✅ Email validation AFTER email is defined
#         email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
#         if not re.match(email_pattern, email):
#             st.error("Please enter a valid email address")
#             return

#         if password != confirm:
#             st.error("Passwords do not match")
#             return

#         if len(password) < 6 or not any(char.isdigit() for char in password):
#             st.error("Password must be at least 6 characters and contain a number")
#             return

#         if email in USERS:
#             st.error("User already exists")
#             return

#         USERS[email] = hash_password(password)
#         st.success("Account created successfully. Please log in.")

# #Login
# def login():
#     st.subheader("🔐 Login")

#     email = st.text_input("Email", key="login_email")
#     password = st.text_input("Password", type="password", key="login_password")

#     if st.button("Login", key="login_submit"):
#         hashed = hash_password(password)

#         if email in USERS and USERS[email] == hashed:
#             st.session_state.authenticated = True
#             st.session_state.user = email
#             st.success("Logged in successfully")
#             st.rerun()
#         else:
#             st.error("Invalid email or password")


# auth.py
# User authentication with persistent SQLite storage

# auth.py
# User authentication with persistent SQLite storage + improved UI

import streamlit as st
import hashlib
import re
import sqlite3
import os

st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const inputs = window.parent.document.querySelectorAll('input');
    inputs.forEach(input => {
        input.setAttribute('autocomplete', 'off');
    });
});
</script>
""", unsafe_allow_html=True)

# ---------- Database Setup ----------

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "nidan.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

# ---------- Password Hashing ----------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- User Operations ----------

def user_exists(email: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def create_user(email: str, password: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(email: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == hash_password(password)

# ---------- Streamlit UI ----------

def signup():
    st.markdown("### 👤 Create your account")
    st.markdown("<br>", unsafe_allow_html=True)

    email    = st.text_input("📧 Email address", placeholder="you@example.com", key="signup_email",autocomplete="email")
    password = st.text_input("🔑 Password", type="password",
                              placeholder="Min 6 chars + 1 number", key="signup_password",autocomplete="password")
    confirm  = st.text_input("🔑 Confirm Password", type="password",
                              placeholder="Repeat your password", key="signup_confirm")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Create Account ✨", use_container_width=True, type="primary"):
        if not email or not password:
            st.error("⚠️ All fields are required.")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            st.error("⚠️ Please enter a valid email address.")
            return
        if password != confirm:
            st.error("⚠️ Passwords do not match.")
            return
        if len(password) < 6 or not any(c.isdigit() for c in password):
            st.error("⚠️ Password must be at least 6 chars and contain a number.")
            return
        if create_user(email, password):
            st.success("✅ Account created! Switch to Login to get started.")
            st.balloons()
        else:
            st.error("⚠️ An account with this email already exists.")

    st.markdown("""
        <div style="color:#666; font-size:0.8rem; margin-top:0.5rem;">
            🔒 Passwords are securely hashed and never stored in plain text.
        </div>
    """, unsafe_allow_html=True)


def login():
    st.markdown("### 👋 Welcome back!")
    st.markdown("<br>", unsafe_allow_html=True)

    email    = st.text_input("📧 Email address", placeholder="you@example.com", key="login_email",autocomplete="email")
    password = st.text_input("🔑 Password", type="password",
                              placeholder="Enter your password", key="login_password",autocomplete="password")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Login →", use_container_width=True, type="primary"):
        if not email or not password:
            st.error("⚠️ Please enter your email and password.")
            return
        if verify_user(email, password):
            st.session_state.authenticated = True
            st.session_state.user = email
            st.success("✅ Logged in!")
            st.rerun()
        else:
            st.error("❌ Invalid email or password. Please try again.")

    st.markdown("""
        <div style="color:#666; font-size:0.8rem; margin-top:0.5rem; text-align:center;">
            Don't have an account? Switch to Sign Up above.
        </div>
    """, unsafe_allow_html=True)


# Auto-init DB on import
from database import init_db