import os
import io
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=api_key)

GROQ_MODEL = "llama-3.3-70b-versatile" 

def refine_response(raw_response: str) -> dict:
    """
    Cleans up the LLM response to ensure it is valid JSON.
    """
    clean_response = raw_response.strip()
    
    # Remove markdown code blocks if present (Groq sometimes adds them even in JSON mode)
    if "```json" in clean_response:
        clean_response = clean_response.split("```json")[1].split("```")[0]
    elif "```" in clean_response:
        clean_response = clean_response.split("```")[1]
        
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw Content: {raw_response}")
        return {
            "topic": "Error",
            "field": "General",
            "question": "Error parsing response",
            "answer": "The AI generated a response that could not be parsed. Please try again.",
            "quiz": {}
        }

def ask_tutor(question: str):
    """
    Generates a detailed answer + a 5-question quiz in JSON format.
    """
    system_instructions = """
    You are an AI tutor. Answer the question in very detail - cover each possible point in the topic and generate a 5-question quiz.
    
    CRITICAL: Output ONLY valid JSON.
    
    JSON Structure:
    {
        "question": "The user's question",
        "answer": "Your detailed explanation (markdown supported)",
        "topic": "The specific topic",
        "field": "The general field of study",
        "quiz": {
            "1": {
                "question": "Quiz Question 1",
                "options": {"1": "A", "2": "B", "3": "C", "4": "D"},
                "answer": "2", 
                "difficulty": "easy"
            },
            ... (repeat for 5 questions)
        }
    }
    """

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role': 'system', 'content': system_instructions},
                {'role': 'user', 'content': question},
            ],
            # Groq JSON mode ensures valid structure
            response_format={"type": "json_object"},
            temperature=0.3 # Lower temperature for more consistent JSON
        )
        
        raw_text = completion.choices[0].message.content
        return refine_response(raw_text)

    except Exception as e:
        print(f"Groq Error: {str(e)}")
        raise

def ask_quick_tutor(question: str):
    """
    Generates a short, plain-text answer for the voice feature.
    """
    system_instructions = """
    You are a helpful AI tutor. Provide a clear, concise answer in plain text.
    Keep it under 3-4 sentences. Do NOT use JSON.
    """

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role': 'system', 'content': system_instructions},
                {'role': 'user', 'content': question},
            ],
            temperature=0.5
        )
        
        return completion.choices[0].message.content

    except Exception as e:
        return f"Error communicating with Groq: {str(e)}"

def analyze_student_performance(history_text: str):
    """
    Analyzes quiz history and returns a JSON report.
    """
    system_instruction = """
    You are an AI Academic Advisor. Analyze the student's quiz history provided below.
    
    Generate a JSON report with the following structure:
    {
        "average_score": "Calculate an approximate percentage (0-100)",
        "strong_topics": ["List 2-3 topics where they answered mostly correctly"],
        "weak_topics": ["List 2-3 topics where they answered incorrectly"],
        "advice": "A paragraph (3-4 sentences) giving specific study advice based on their mistakes."
    }
    
    Output ONLY valid JSON.
    """

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': f"Here is the student's recent performance:\n{history_text}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return refine_response(completion.choices[0].message.content)
    except Exception as e:
        print(f"Analysis Error: {e}")
        return {
            "average_score": 0,
            "strong_topics": [],
            "weak_topics": [],
            "advice": "Could not generate analysis at this time."
        }

def ask_pdf_tutor(question: str, context: str):
    """
    RAG Answer generation based on PDF context.
    """
    system_instruction = """
    You are a helpful AI tutor. Answer the user's question ONLY based on the provided Context. 
    Study the context carefully and answer only if the information is present in the context, 
    otherwise say "I couldn't find that in the document." and suggest related topics based on context.
    Keep answer concise.
    """
    
    prompt = f"Context:\n{context}\n\nQuestion:\n{question}"

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error generating PDF answer: {str(e)}"
    



def transcribe_audio(audio_bytes: bytes):
    """
    Transcribes audio bytes using Groq's Whisper model.
    """
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm" 

        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="distil-whisper-large-v3-en", # Groq's fast whisper model
            response_format="text",
            language="en"
        )
        
        return transcription
    except Exception as e:
        print(f"Groq Transcription Error: {e}")
        return None