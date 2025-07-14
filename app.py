import streamlit as st
import requests
import json
import time
import uuid
from streamlit_lottie import st_lottie

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- RASA SERVER CONFIGURATION ---
RASA_SERVER_URL = "https://adarshdivase-Rasabackend.hf.space"
RASA_WEBHOOK_URL = f"{RASA_SERVER_URL}/webhooks/rest/webhook"

# --- LOTTIE ANIMATION LOADER ---
def load_lottieurl(url: str):
    """Loads a Lottie animation from a URL."""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- SESSION STATE INITIALIZATION ---
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- HELPER FUNCTIONS ---
def send_message_to_rasa(message, user_id):
    """Sends a message to the Rasa server and returns the response."""
    payload = {"sender": user_id, "message": message}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(RASA_WEBHOOK_URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return [{"text": "Sorry, I'm having trouble connecting to the server. Please try again later."}]

def stream_response(text):
    """Streams the response with a typing effect."""
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 AI Assistant")
    st.markdown("Controls and Information")
    lottie_sidebar = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_vfs41M.json")
    if lottie_sidebar:
        st_lottie(lottie_sidebar, height=150, key="sidebar_lottie")

    if st.button("Start New Chat"):
        st.session_state.messages = []
        st.session_state.user_id = str(uuid.uuid4())
        st.rerun()

    with st.expander("Connection Details", expanded=False):
        st.info(f"**Backend URL**\n{RASA_SERVER_URL}")
        st.info(f"**User ID**\n`{st.session_state.user_id[:8]}`")

# --- MAIN UI ---
st.title("AI Assistant for Future Interns")

# Initialize chat with a welcome message if empty
if not st.session_state.messages:
    st.session_state.messages.append(
        {"role": "assistant", "content": "Hello! How can I assist you with the internship program today?"}
    )

# Display chat messages from history
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask a question about the internship..."):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate and display bot response
    with st.chat_message("assistant", avatar="🤖"):
        # Show Lottie animation while waiting for response
        lottie_thinking = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_NTDA23.json")
        lottie_container = st.empty()
        if lottie_thinking:
            with lottie_container:
                st_lottie(lottie_thinking, height=100, speed=1.5, key="thinking")

        # Get response from Rasa
        rasa_responses = send_message_to_rasa(prompt, st.session_state.user_id)
        
        # Remove the Lottie animation
        lottie_container.empty()
        
        # Stream the response
        full_response_text = " ".join([res.get("text", "") for res in rasa_responses])
        if full_response_text:
            st.write_stream(stream_response(full_response_text))
            st.session_state.messages.append({"role": "assistant", "content": full_response_text})
        else:
            fallback_text = "Sorry, I encountered an issue. Please try again."
            st.write_stream(stream_response(fallback_text))
            st.session_state.messages.append({"role": "assistant", "content": fallback_text})
