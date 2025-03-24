import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini API
def __configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (None,"Please set your GEMINI_API_KEY in the .env file")
    genai.configure(api_key=api_key)
    return (genai,None)

# Get model configuration
def __get_model_config():
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), float(os.getenv("TEMPERATURE", "0.7"))

# Create the Gemini LLM Model
def create_llm_model():
    client, error = __configure_gemini()
    if client:
        model_name, temperature = __get_model_config()
        model = client.GenerativeModel(
            model_name=model_name,
            generation_config={"temperature": temperature}
        )
        return model, None
    else:
        return None, error


# Get AI response
def get_ai_response(prompt, conversation_history):
    system_prompt = """
    You are Quizzy, an AI trivia game host. Create a fun, interactive trivia experience.
    Guidelines:
    - Match the user's language (English, Hebrew, Arabic, etc.).
    - Keep a friendly, encouraging tone.
    - Gameplay:
      1. If no topic is set, suggest topics or ask for one.
      2. Once a topic is chosen, ask a trivia question.
      3. When answering:
         - Say if they're correct (use "CORRECT" or "INCORRECT" clearly)
         - Give feedback and extra info
         - Ask if they want another question
      4. Be flexible with topic changes or game resets.
    """
    
    try:
        model, error = create_llm_model()
        if not model or error:
            return (None, error)
        # Convert conversation history to Gemini-compatible format
        content = [system_prompt]
        for message in conversation_history:
            role = message["role"]
            msg_content = message["content"]
            content.append(f"{role}: {msg_content}")
        content.append(f"user: {prompt}")
        
        response = model.generate_content(content)
        return (response.text,None)
    except Exception as e:
        return (None, f"""Sorry, I'm having trouble. Try again!
        More details: {str(e)}""")