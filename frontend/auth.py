import streamlit as st
from utils import api_call

def show_login():
    st.title("Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary"):
            data = api_call("/api/auth/login", "POST", {"email": email, "password": password})
            if data:
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.success("Login successful!")
                st.rerun()

    with tab2:
        c1, c2 = st.columns(2)
        f_name = c1.text_input("First Name")
        l_name = c2.text_input("Last Name")
        phone = st.text_input("Phone")
        s_email = st.text_input("Email", key="signup_email")
        s_pass = st.text_input("Password", type="password", key="signup_pass")
        v_pass = st.text_input("Verify Password", type="password")
        role = st.selectbox("Role", ["Student", "Tutor"])
        
        if st.button("Create Account"):
            if s_pass != v_pass:
                st.error("Passwords do not match")
                return
            
            payload = {
                "email": s_email, "password": s_pass, "verify_password": v_pass,
                "first_name": f_name, "last_name": l_name, "phone_number": phone,
                "student": role == "Student", "tutor": role == "Tutor"
            }
            res = api_call("/api/auth/register", "POST", payload)
            if res:
                st.success("Account created! Please login.")