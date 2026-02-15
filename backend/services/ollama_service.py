import ollama
import json

# Configuration
OLLAMA_MODEL = "gemma3:4b"  # Or "mistral", "gemma", etc.

def refine_response(raw_response: str) -> dict:
    """
    Cleans up the LLM response to ensure it is valid JSON.
    Local models often add markdown code blocks like ```json ... ```
    """
    clean_response = raw_response.strip()
    
    # Remove markdown code blocks if present
    if "```json" in clean_response:
        clean_response = clean_response.split("```json")[1].split("```")[0]
    elif "```" in clean_response:
        clean_response = clean_response.split("```")[1]
        
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw Content: {raw_response}")
        
        raise ValueError("Model response is not valid JSON")

def ask_tutor(question: str):
    """
    Generates a detailed answer + a 5-question quiz in JSON format.
    """
    system_instructions = """
    You are an AI tutor. Answer the question in very detail - cover each possible point in the topic and generate a 5-question quiz.
    
    
    CRITICAL: Output ONLY valid JSON. Do not add introductions or conclusions.
    
    JSON Structure:
    {
        "question": "The user's question",
        "answer": "Your detailed explanation",
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
        response = ollama.chat(model=OLLAMA_MODEL, messages=[
            {'role': 'system', 'content': system_instructions},
            {'role': 'user', 'content': question},
        ])
        
        raw_text = response['message']['content']
        return refine_response(raw_text)

    except Exception as e:
        print(f"Ollama Error: {str(e)}")
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
        response = ollama.chat(model=OLLAMA_MODEL, messages=[
            {'role': 'system', 'content': system_instructions},
            {'role': 'user', 'content': question},
        ])
        
        return response['message']['content']

    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"
    

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
    
    Do not output anything other than the JSON.
    """

    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[
            {'role': 'system', 'content': system_instruction},
            {'role': 'user', 'content': f"Here is the student's recent performance:\n{history_text}"},
        ])
        return refine_response(response['message']['content'])
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
    You are a helpful AI tutor. Answer the user's question ONLY based on the provided Context .Study the context carefully and answer only if the information is present in the context, otherwise say "I couldn't find that in the document." and ask the user did they want to ask something else in which you list related topics based on context. Keep answer concise. 
    Keep answer concise.
    """
    
    prompt = f"Context:\n{context}\n\nQuestion:\n{question}"

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return "Error generating PDF answer."