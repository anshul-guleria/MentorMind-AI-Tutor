import streamlit as st
from streamlit_mic_recorder import speech_to_text
from utils import api_call
import speech_recognition as sr
import base64
import io

def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    try:
        # Load audio data from bytes
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return f"API Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def show_ask():
    #Navigation
    if st.button("← Back to Dashboard"):
        if 'ask_response' in st.session_state:
            del st.session_state.ask_response
            
        if 'voice_response' in st.session_state:
            del st.session_state.voice_response
        st.session_state.page = "dashboard"
        st.rerun()

    st.title("AI Tutor")

    tab_chat, tab_voice = st.tabs(["💬 Chat & Quiz (Deep Dive)", "🎙️ Voice Assistant (Quick)"])

    #Chat & Quiz (Deep Dive)
    with tab_chat:
        st.markdown("### Deep Dive Learning")
        st.caption("Ask detailed questions. The AI will provide a comprehensive answer and generate a quiz.")

        # Input Form
        with st.form("chat_form"):
            text_input = st.text_area("Type your question:", height=100, placeholder="e.g. Explain Quantum Entanglement...")
            submitted = st.form_submit_button("Ask Tutor", type="primary")

        if submitted and text_input:
            with st.spinner("Analyzing and generating quiz..."):
                # Call /ask-tutor
                data = api_call("/ask-tutor", "POST", {"question": text_input})
                
                if data:
                    st.session_state.ask_response = data
                    st.rerun() 

        # Display Results
        if 'ask_response' in st.session_state and st.session_state.ask_response.get('type') != 'quick':
            data = st.session_state.ask_response
            
            st.divider()
            st.subheader(f"Topic: {data.get('topic', 'General')}")
            
            # Render Markdown Answer
            st.markdown(data['answer'])
            
            st.divider()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("📝 Take Generated Quiz", type="primary", use_container_width=True):
                    if data.get("response_id"):
                        st.session_state.current_quiz_id = data["response_id"]
                        st.session_state.page = "quiz"
                        st.rerun()
                    else:
                        st.error("No Quiz ID returned from backend.")
            
            with col2:
                if st.button("🔄 Ask Another Question"):
                    del st.session_state.ask_response
                    st.rerun()

    #Voice Assistant (Quick)
    with tab_voice:
        st.markdown("### 🎙️ Voice Assistant")
        st.caption("Tap microphone to speak. I will listen and respond.")

        # Audio Recorder Component
        audio = speech_to_text(
            start_prompt="Start Recording",
            stop_prompt="Stop & Transcribe",
            key='voice_recorder'
        )

        if audio:
            st.info("Transcribing audio...")
            
            text_query = audio

            print(f"Transcribed Text: {text_query}")
            
            if text_query:
                st.success(f"You said: '{text_query}'")
                
                # Send Text to Backend
                with st.spinner("Thinking..."):
                    data = api_call("/ask-quick", "POST", {"question": text_query})
                    
                    if data:
                        st.session_state.voice_response = data
                        # st.rerun()
            else:
                st.error("Could not understand audio. Please try again.")

        # Display AI Response (Text + Audio)
        if 'voice_response' in st.session_state:
            v_data = st.session_state.voice_response
            
            st.divider()
            st.subheader("AI Answer:")
            st.write(v_data['answer'])
            
            if v_data.get('audio'):
                try:
                    audio_bytes = base64.b64decode(v_data['audio'])
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                except Exception as e:
                    st.error(f"Playback Error: {e}")