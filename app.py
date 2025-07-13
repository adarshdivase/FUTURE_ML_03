import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# --- CONFIGURATION ---

# When running inside the same container on Hugging Face,
# Streamlit must connect to Rasa using the internal 'localhost' address.
# The logs show Rasa is running on port 7860, so we connect to that.
RASA_INTERNAL_URL = "http://localhost:7860"
RASA_PUBLIC_URL = "https://adarshdivase-rasabackend.hf.space"

# Initialize session state variables if they don't exist
if 'rasa_server_url' not in st.session_state:
    st.session_state.rasa_server_url = RASA_INTERNAL_URL # Default to internal URL

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# The webhook URL is derived from the server URL
st.session_state.rasa_webhook_url = f"{st.session_state.rasa_server_url}/webhooks/rest/webhook"

# Your GitHub Repository Link
GITHUB_REPO_LINK = "https://github.com/adarshdivase/FUTURE_ML_05"


# --- HELPER FUNCTIONS ---

def send_message_to_rasa(message, user_id):
    """Send message to Rasa server and get response"""
    try:
        payload = {
            "sender": user_id,
            "message": message
        }
        response = requests.post(
            st.session_state.rasa_webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: Status code {response.status_code} from Rasa server.")
            st.error(f"Rasa server response: {response.text}")
            return [{"text": "Sorry, I'm having trouble connecting. Please check the logs."}]
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: Could not connect to Rasa at {st.session_state.rasa_webhook_url}. Details: {e}")
        return [{"text": "Sorry, I'm currently unavailable. Please try again later."}]


def check_rasa_server():
    """Check if Rasa server is running"""
    try:
        # Check the /status endpoint which is standard for Rasa
        response = requests.get(f"{st.session_state.rasa_server_url}/status", timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# --- STREAMLIT UI ---

st.set_page_config(page_title="Rasa Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Rasa Chatbot")
st.markdown("---")

# Main layout
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### Chat with your Rasa assistant")
with col2:
    if check_rasa_server():
        st.success("🟢 Server Online")
    else:
        st.error("🔴 Server Offline")

# Chat container
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("timestamp"):
                st.caption(message["timestamp"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})

    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(timestamp)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            rasa_responses = send_message_to_rasa(prompt, st.session_state.user_id)

        if not rasa_responses:
             rasa_responses = []

        for response in rasa_responses:
            response_timestamp = datetime.now().strftime("%H:%M:%S")
            if 'text' in response:
                st.markdown(response['text'])
                st.caption(response_timestamp)
                st.session_state.messages.append({"role": "assistant", "content": response['text'], "timestamp": response_timestamp})
            if 'image' in response:
                st.image(response['image'])
            if 'buttons' in response:
                st.markdown("**Quick replies:**")
                for button in response['buttons']:
                    if st.button(button['title'], key=f"btn_{button['payload']}_{uuid.uuid4()}"):
                        st.session_state.messages.append({"role": "user", "content": button['payload'], "timestamp": datetime.now().strftime("%H:%M:%S")})
                        st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    st.subheader("Server Configuration")
    st.info("🔗 Connected to Hugging Face Spaces backend")

    new_url = st.text_input("Rasa Server URL", value=st.session_state.rasa_server_url)
    if st.button("Update Server URL"):
        st.session_state.rasa_server_url = new_url
        st.rerun()

    st.subheader("Quick Server Options")
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        if st.button("🌐 HF Spaces"):
            st.session_state.rasa_server_url = RASA_PUBLIC_URL # Use public for external testing
            st.rerun()
    with s_col2:
        if st.button("🏠 Local"):
            st.session_state.rasa_server_url = "http://localhost:7860" # Match the actual running port
            st.rerun()

    st.subheader("Chat Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    if st.button("New Session"):
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.subheader("Debug Info")
    st.text(f"User ID: {st.session_state.user_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")
    st.text(f"Webhook URL: {st.session_state.rasa_webhook_url}")

    if st.button("🔄 Test Connection"):
        with st.spinner("Testing..."):
            if check_rasa_server():
                st.success("✅ Connection successful!")
            else:
                st.error("❌ Connection failed!")

    if st.button("Export Chat"):
        chat_data = {"user_id": st.session_state.user_id, "messages": st.session_state.messages}
        st.download_button(
            label="Download Chat JSON",
            data=json.dumps(chat_data, indent=2),
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# --- FOOTER ---
st.markdown("---")
st.markdown(f"Built with Streamlit and Rasa | [GitHub]({GITHUB_REPO_LINK}) | [Backend]({RASA_PUBLIC_URL})")
