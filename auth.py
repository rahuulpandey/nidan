# NOTE: In-memory storage, will be replaced with SQLite

import streamlit as st
import hashlib
import re

# ---------- Password Security ----------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ---------- In-memory user store (temporary) ----------
# Later we will replace this with SQLite
USERS = {}


# ---------- Signup ----------

def signup():
    st.subheader("📝 Create Account")
    
    # email validation
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        st.error("Please enter a valid email address")
        return
    
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up" ,key="signup_submit"):
        if not email or not password:
            st.error("All fields are required")
            return

        if password != confirm:
            st.error("Passwords do not match")
            return
        
        if len(password) < 6 or not any(char.isdigit() for char in password):
            st.error("Password must be at least 6 characters and contain a number")
            return

        if email in USERS:
            st.error("User already exists")
            return

        USERS[email] = hash_password(password)
        st.success("Account created successfully. Please log in.")


# ---------- Login ----------

def login():
    st.subheader("🔐 Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_submit"):
        hashed = hash_password(password)

        if email in USERS and USERS[email] == hashed:
            st.session_state.authenticated = True
            st.session_state.user = email
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Invalid email or password")
