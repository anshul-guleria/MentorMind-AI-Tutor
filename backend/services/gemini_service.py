import os
from google import genai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

# Use Flash model for speed (good for real-time voice/quiz)
MODEL_NAME = "gemini-2.5-flash" 

def refine_response(raw_response: str) -> dict:
    """
    Cleans up the LLM response to ensure it is valid JSON.
    Gemini often adds markdown code blocks like ```json ... ```
    """
    clean_response = raw_response.strip()
    
    # Remove markdown code blocks if present
    if clean_response.startswith("```json"):
        clean_response = clean_response.replace("```json", "", 1)
    elif clean_response.startswith("```"):
        clean_response = clean_response.replace("```", "", 1)
    
    if clean_response.endswith("```"):
        clean_response = clean_response.rsplit("```", 1)[0]
        
    try:
        return json.loads(clean_response.strip())
    except json.JSONDecodeError:
        # Fallback structure to prevent frontend crash
        print(f"JSON Decode Error. Raw: {raw_response}")
        return {
            "topic": "Error",
            "field": "General",
            "question": "Error parsing response",
            "answer": raw_response,
            "quiz": {}
        }

def ask_tutor(question: str):
    """
    Generates a detailed answer + a 5-question quiz in JSON format.
    """
    system_instructions = """
    You are a helpful and precise AI tutor.
    1. Answer the question in detail.
    2. Generate a 5-question quiz based on the answer.

    CRITICAL: You must output ONLY valid JSON. Do not add any text before or after the JSON.
    
    The JSON structure must be exactly this:
    {
        "question": "The user's question",
        "answer": "Your detailed answer goes here.",
        "topic": "The specific topic",
        "field": "The general field of study",
        "quiz": {
            "1": {
                "question": "Question text",
                "options": {"1": "Option A", "2": "Option B", "3": "Option C", "4": "Option D"},
                "answer": "2", 
                "difficulty": "easy"
            },
            ... (repeat for questions 2, 3, 4, 5)
        }
    }
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": system_instructions}, {"text": question}]}
            ]
        )
        return refine_response(response.text)

    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        raise

def ask_quick_tutor(question: str):
    """
    Generates a short, plain-text answer for the voice feature.
    """
    system_instructions = """
    You are a helpful AI tutor. The user is asking via voice.
    Provide a clear, concise answer in plain text.
    Keep it under 3-4 sentences. Do NOT use JSON.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": system_instructions}, {"text": question}]}
            ]
        )
        return response.text

    except Exception as e:
        return f"I'm having trouble connecting to the AI service right now. Error: {str(e)}"

def analyze_student_performance(history_text: str):
    """
    Analyzes quiz history and returns a JSON report for the dashboard.
    """
    system_instruction = """
    You are an AI Academic Advisor. Analyze the student's quiz history provided below.
    
    Generate a JSON report with the following structure:
    {
        "average_score": "Calculate an approximate percentage (0-100) based on correct/wrong status",
        "strong_topics": ["List 2-3 topics where they answered mostly CORRECT"],
        "weak_topics": ["List 2-3 topics where they answered WRONG"],
        "advice": "A short paragraph (3-4 sentences) giving specific study advice."
    }
    
    Output ONLY valid JSON.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": system_instruction}, {"text": f"Student History:\n{history_text}"}]}
            ]
        )
        return refine_response(response.text)

    except Exception as e:
        print(f"Analysis Error: {e}")
        return {
            "average_score": 0,
            "strong_topics": [],
            "weak_topics": [],
            "advice": "Could not generate analysis at this time."
        }
    
def ask_pdf_tutor(question: str, context: str):
    system_instruction = """
    You are a helpful assistant. Answer the user's question ONLY based on the provided Context.
    If the answer is not in the context, say "I couldn't find that in the document."
    Keep answer concise.
    """
    
    prompt = f"Context:\n{context}\n\nQuestion:\n{question}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {"role": "user", "parts": [{"text": system_instruction}, {"text": prompt}]}
            ]
        )
        return response.text
    except Exception as e:
        return "Error generating PDF answer."