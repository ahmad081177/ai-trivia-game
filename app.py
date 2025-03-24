import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="AI Trivia Game",
    page_icon="🎮",
    layout="centered"
)

# Import CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# Initialize Gemini API
def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Please set your GEMINI_API_KEY in the .env file")
        st.stop()
    genai.configure(api_key=api_key)
    return genai

# Get model configuration
def get_model_config():
    return os.getenv("GEMINI_MODEL", "gemini-pro"), float(os.getenv("TEMPERATURE", "0.7"))

# Session state initialization
def initialize_session_state():
    defaults = {
        "messages": [],
        "score": 0,
        "questions_asked": 0,
        "conversation_history": [],
        "current_topic": None,
        "awaiting_answer": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Get AI response
def get_ai_response(prompt):
    client = configure_gemini()
    model_name, temperature = get_model_config()
    
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
        model = client.GenerativeModel(
            model_name=model_name,
            generation_config={"temperature": temperature}
        )
        
        # Convert conversation history to Gemini-compatible format
        content = [system_prompt]
        for message in st.session_state.conversation_history:
            role = message["role"]
            msg_content = message["content"]
            content.append(f"{role}: {msg_content}")
        content.append(f"user: {prompt}")
        
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return "Sorry, I'm having trouble. Try again!"

# Process user message
def process_user_message(user_message):
    st.session_state.messages.append({"role": "user", "content": user_message})
    st.session_state.conversation_history.append({"role": "user", "content": user_message})
    
    with st.spinner("Quizzy is thinking..."):
        ai_response = get_ai_response(user_message)
    
    if st.session_state.awaiting_answer:
        if "CORRECT" in ai_response.upper():
            st.session_state.score += 1
            st.session_state.questions_asked += 1
        elif "INCORRECT" in ai_response.upper():
            st.session_state.questions_asked += 1
        st.session_state.awaiting_answer = False
    
    if "question" in ai_response.lower() or "שאלה" in ai_response or "سؤال" in ai_response:
        st.session_state.awaiting_answer = True
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})
    
    st.rerun()

# Start new game
def start_new_game():
    st.session_state.clear()
    initialize_session_state()
    welcome = "Hi! I'm Quizzy, your trivia host. Pick a topic (history, science, movies, etc.) to start!"
    st.session_state.messages = [{"role": "assistant", "content": welcome}]
    st.session_state.conversation_history = [{"role": "assistant", "content": welcome}]
    # Ensure UI updates after resetting
    st.rerun()

# Main app
def main():
    initialize_session_state()
    
    st.markdown("<h1 class='game-title'>🎮 AI Trivia Game 🎲</h1>", unsafe_allow_html=True)
    
    # Score display and New Game button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        # Always show score, even if 0/0
        st.markdown(f"<div class='score-display'>Score: {st.session_state.score}/{st.session_state.questions_asked}</div>", unsafe_allow_html=True)
    with col3:
        if st.button("New Game", key="new_game"):
            start_new_game()
    
    if not st.session_state.messages:
        start_new_game()
    
    # Display chat history in a container
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            # if message["role"] == "user":
            #     icon = "👤"  # Person icon
            # else:  # assistant
            #     icon = "🤖"  # AI-bot icon
            # st.markdown(f"<div class='chat-message {message['role']}'>{icon} {message['content']}</div>", unsafe_allow_html=True)

            #Icon i done thru css
            st.markdown(f"<div class='chat-message {message['role']}'>{message['content']}</div>", unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message here...", key="chat_input")
    if user_input:
        process_user_message(user_input)

if __name__ == "__main__":
    main()