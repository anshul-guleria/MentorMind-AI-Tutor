import streamlit as st
from utils import api_call

def show_dashboard():
    
    # Action Grid
    c1, c2= st.columns(2)
    
    with c1:
        if st.button("💬 Ask Question", use_container_width=True):
            st.session_state.page = "ask"
            st.rerun()
    with c2:
        if st.button("📝 Start Quiz", use_container_width=True):
            st.session_state.page = "quiz_list"
            st.rerun()
    with c1:
        if st.button("📄 Ask PDF", use_container_width=True):
            st.session_state.page = "pdf"
            st.rerun()
    with c2:
        if st.button("📊 Summary", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()

    st.divider()
    
    is_quiz_mode = st.session_state.get("page") == "quiz_list"
    
    st.subheader("Select Topic for Quiz" if is_quiz_mode else "Learning History")
    if is_quiz_mode:
        if st.button("Cancel Quiz Selection"):
            st.session_state.page = "dashboard"
            st.rerun()

    topics_data = api_call("/user/topics")
    if topics_data and topics_data['topics']:
        for t in topics_data['topics']:
            with st.expander(f"{t['topic']}"):
                if is_quiz_mode:
                    if st.button("Start Quiz", key=f"start_{t['response_id']}"):
                        st.session_state.current_quiz_id = t['response_id']
                        st.session_state.page = "quiz"
                        st.rerun()
                else:
                    # View Details logic
                    if st.button("View Details", key=f"view_{t['response_id']}"):
                         detail = api_call(f"/response/{t['response_id']}")
                         st.markdown(f"**Q:** {detail['question']}")
                         st.markdown(f"**A:** {detail['answer']}")
    else:
        st.info("No history found.")