import streamlit as st
from utils import api_call

def show_summary():
    if st.button("← Back"):
        st.session_state.page = "dashboard"
        st.rerun()
        
    st.title("📊 Performance Analysis")
    
    with st.spinner("Analyzing your history..."):
        data = api_call("/user/summary")
        
    if not data or not data.get("has_data"):
        st.warning("No quiz history found. Go take some quizzes!")
        return

    analysis = data["analysis"]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Score", f"{analysis['average_score']}%")
    
    # Layout
    c1, c2 = st.columns(2)
    with c1:
        st.success("✅ Strong Topics")
        for t in analysis['strong_topics']:
            st.write(f"- {t}")
            
    with c2:
        st.error("⚠️ Needs Improvement")
        for t in analysis['weak_topics']:
            st.write(f"- {t}")
            
    st.info(f"**💡 AI Advice:** {analysis['advice']}")