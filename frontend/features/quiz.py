import streamlit as st
from utils import api_call

def show_quiz():
    if "current_quiz_id" not in st.session_state:
        st.session_state.page = "dashboard"
        st.rerun()

    if st.button("← Back"):
        st.session_state.page = "dashboard"
        st.rerun()

    response_id = st.session_state.current_quiz_id
    
    # Fetch Quiz Data (Lazy load)
    if "quiz_data" not in st.session_state or st.session_state.quiz_id_ref != response_id:
        with st.spinner("Loading Quiz..."):
            data = api_call(f"/quiz/{response_id}")
            if data:
                # Fetch details for each question
                questions = []
                for qid in data["question_ids"]:
                    q_detail = api_call(f"/question/{qid}")
                    questions.append(q_detail)
                
                st.session_state.quiz_data = data
                st.session_state.questions = questions
                st.session_state.quiz_id_ref = response_id
                st.session_state.answers = {}

    quiz = st.session_state.quiz_data
    questions = st.session_state.questions

    st.title(f"Quiz: {quiz['topic']}")

    with st.form("quiz_form"):
        for i, q in enumerate(questions):
            st.markdown(f"**{i+1}. {q['question_text']}**")
            options = {
                "1": q['option_1'],
                "2": q['option_2'],
                "3": q['option_3'],
                "4": q['option_4']
            }
            
            # Helper to display readable options
            choice = st.radio(
                f"Select answer for Q{i+1}",
                options.keys(),
                format_func=lambda x: options[x],
                key=q['id']
            )
            st.session_state.answers[q['id']] = choice
            st.markdown("---")

        submitted = st.form_submit_button("Submit Quiz")
        
        if submitted:
            payload = {
                "quiz_id": quiz['id'],
                "answers": [{"question_id": qid, "answer": ans} for qid, ans in st.session_state.answers.items()]
            }
            res = api_call("/quiz/submit", "POST", payload)
            if res:
                st.balloons()
                st.success(f"You scored: {res['score']} / {res['total']}")
                
                # Show breakdown
                for det in res['details']:
                    icon = "✅" if det['correct'] else "❌"
                    st.write(f"Question ID {det['question_id'][:8]}... : {icon}")