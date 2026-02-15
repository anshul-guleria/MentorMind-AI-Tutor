import streamlit as st
from utils import api_call

def show_pdf_chat():
    if st.button("← Back"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.title("📄 Ask from PDF")

    # Sidebar: List & Upload
    with st.sidebar:
        st.header("My Documents")
        uploaded_file = st.file_uploader("Upload New PDF", type="pdf")
        
        if uploaded_file and st.button("Process PDF"):
            with st.spinner("Uploading & Embedding..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                res = api_call("/pdf/upload", "POST", files=files)
                if res:
                    st.success("PDF Processed!")
                    st.rerun() # Refresh list

        st.divider()
        st.write("Select a file to chat:")
        pdfs = api_call("/pdf/list")
        if pdfs:
            for pdf in pdfs:
                if st.button(f"📄 {pdf['filename']}", key=pdf['id']):
                    st.session_state.selected_pdf = pdf

    # Chat Area
    if "selected_pdf" in st.session_state:
        pdf = st.session_state.selected_pdf
        st.subheader(f"Chatting with: {pdf['filename']}")

        # Initialize chat history
        if "pdf_messages" not in st.session_state:
            st.session_state.pdf_messages = []

        # Display history
        for msg in st.session_state.pdf_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input
        if prompt := st.chat_input("Ask a question about this document..."):
            # Add user message
            st.session_state.pdf_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get AI Response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    res = api_call("/pdf/chat", "POST", {"pdf_id": pdf['id'], "question": prompt})
                    if res:
                        ai_msg = res["answer"]
                        st.markdown(ai_msg)
                        st.session_state.pdf_messages.append({"role": "assistant", "content": ai_msg})
    else:
        st.info("Please select or upload a PDF from the sidebar.")