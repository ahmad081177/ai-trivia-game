import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from llm_utils import get_ai_response
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


# Process user message
def process_user_message(user_message):
    st.session_state.messages.append({"role": "user", "content": user_message})
    st.session_state.conversation_history.append({"role": "user", "content": user_message})
    
    with st.spinner("Quizzy is thinking..."):
        ai_response, error = get_ai_response(user_message, st.session_state.conversation_history)
    
    if error:
        st.error(error)
        return error
    
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