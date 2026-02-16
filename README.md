# 🎓 AI Tutor Platform

A comprehensive, AI-powered learning platform built with **FastAPI** (Backend) and **Streamlit** (Frontend). This application allows students to ask questions via text or voice, generates personalized quizzes, tracks learning history, and lets users chat with PDF documents using RAG (Retrieval-Augmented Generation).

## 🚀 Features

*   **💬 AI Tutor Chat:** Ask deep-dive questions and get detailed explanations powered by **Groq / Llama 3**.
*   **📝 Automated Quizzes:** Every explanation automatically generates a 5-question quiz to test understanding.
*   **🎙️ Voice Assistant:** Ask questions via microphone and receive spoken audio responses (using **Groq Whisper** for STT and **gTTS** for TTS).
*   **📄 Chat with PDF (RAG):** Upload study materials (PDFs), embed them into **Pinecone**, and ask context-aware questions.
*   **📊 AI Analytics:** Get a personalized summary of your performance, including strong/weak topics and study advice.
*   **🔐 Authentication:** Secure JWT-based Login and Signup system.

---

## 🛠️ Tech Stack

### Frontend
*   **Streamlit:** UI Framework.
*   **Streamlit Mic Recorder:** For capturing browser audio.
*   **Requests:** For API communication.

### Backend
*   **FastAPI:** High-performance web framework.
*   **SQLAlchemy:** Database ORM (SQLite).
*   **Groq API:** Ultra-fast LLM inference (Llama 3 & Whisper).
*   **Pinecone:** Vector Database for RAG.
*   **SentenceTransformers:** Local embeddings (`all-MiniLM-L6-v2`).
*   **gTTS:** Text-to-Speech generation.

---

## ⚙️ Prerequisites

1.  **Python 3.10+** installed.
2.  **API Keys:**
    *   **Groq API Key** (for LLM & Whisper): [Get it here](https://console.groq.com/)
    *   **Pinecone API Key** (for RAG): [Get it here](https://app.pinecone.io/)
    *   *Optional:* Google Gemini or Ollama keys if you switched services.

---

## 📥 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-tutor.git
cd ai-tutor
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///./tutor.db

# Security
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256

# AI Services
GROQ_API_KEY=gsk_...
PINECONE_API_KEY=pcsk_...
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*(See the `requirements.txt` section below if you haven't created it yet)*

---

## 🏃‍♂️ Running the Application

You need to run the Backend and Frontend in **two separate terminals**.

### Terminal 1: Start Backend (FastAPI)
This handles the database, AI logic, and API routes.

```bash
cd backend
uvicorn main:app --reload --port 8000
```
*You should see: `Uvicorn running on http://127.0.0.1:8000`*

### Terminal 2: Start Frontend (Streamlit)
This launches the user interface.

```bash
cd frontend_streamlit
streamlit run app.py
```
*The app will open automatically in your browser at `http://localhost:8501`*

---

## 📂 Project Structure

```text
ai-tutor/
├── backend/
│   ├── main.py              # Entry point
│   ├── database.py          # DB connection
│   ├── models/              # SQLAlchemy Tables
│   ├── routes/              # API Endpoints (auth, tutor, pdf)
│   ├── services/            # AI Logic (Groq, Pinecone, TTS)
│   └── core/                # Security & Hashing
│
├── frontend_streamlit/
│   ├── app.py               # Main Entry (Routing)
│   ├── auth.py              # Login Screens
│   ├── dashboard.py         # Main Menu
│   ├── utils.py             # API Helper
│   └── features/            # Feature Components
│       ├── ask.py           # Voice/Text Chat
│       ├── quiz.py          # Quiz Interface
│       ├── pdf_chat.py      # RAG Interface
│       └── summary.py       # Analytics View
│
├── requirements.txt         # Dependencies
└── .env                     # API Keys
```

---

## 🧩 Key Functionalities Explained

### 1. RAG (Retrieval Augmented Generation)
When you upload a PDF:
1.  **Backend** reads the PDF using `pypdf`.
2.  Text is chunked and embedded using `SentenceTransformers`.
3.  Vectors are upserted to a **Pinecone Index** (`dimension=384`).
4.  When you chat, the query is embedded, relevant chunks are retrieved from Pinecone, and sent to Groq Llama 3 for the final answer.

### 2. Voice Mode
1.  **Frontend** records audio using `streamlit-mic-recorder`.
2.  Raw bytes are sent to `FastAPI`.
3.  **Groq Whisper** (`distil-whisper-large-v3`) transcribes audio to text instantly.
4.  **Groq Llama 3** generates a text answer.
5.  **gTTS** converts text to MP3 audio.
6.  **Frontend** plays the MP3 automatically.

---

## 🐛 Troubleshooting

*   **"Pinecone Index Not Found":**
    Ensure you created an index named `ai-tutor` with **Dimensions: 384** and **Metric: Cosine** in your Pinecone console.
*   **Database Errors:**
    If you change models, delete `tutor.db` and restart the backend to recreate tables.
*   **Audio Issues:**
    Ensure your browser has permission to access the microphone.

