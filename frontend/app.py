import streamlit as st
from auth import show_login
from dashboard import show_dashboard
from features.ask import show_ask
from features.quiz import show_quiz
from features.pdf_chat import show_pdf_chat
from features.summary import show_summary

# Page Config
st.set_page_config(page_title="AI Tutor", page_icon="🎓", layout="centered")

st.title("🎓 MentorMind ")
st.subheader("Your AI-Powered Learning Companion")

# Initialize Session State
if "token" not in st.session_state:
    st.session_state.token = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Routing Logic
if not st.session_state.token:
    show_login()
else:
    # Sidebar Navigation
    with st.sidebar:
        st.header(f"Welcome Back, {st.session_state.user['first_name']} 👋")
        st.write(f"Logged in as: **{st.session_state.user['email']}**")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # View Router
    page = st.session_state.page
    
    if page == "dashboard" or page == "quiz_list":
        show_dashboard()
    elif page == "ask":
        show_ask()
    elif page == "quiz":
        show_quiz()
    elif page == "pdf":
        show_pdf_chat()
    elif page == "summary":
        show_summary()