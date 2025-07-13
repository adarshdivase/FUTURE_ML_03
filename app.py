import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# --- CONFIGURATION ---

# Backend URL options for HuggingFace Spaces
RASA_INTERNAL_URL = "http://localhost:7860"
RASA_PUBLIC_URL = "https://adarshdivase-rasabackend.hf.space"  # Standard HF Spaces format
RASA_ALTERNATIVE_URL = "https://huggingface.co/spaces/adarshdivase/Rasabackend"  # Alternative format (might not work for API)

# Initialize session state variables if they don't exist
if 'rasa_server_url' not in st.session_state:
    st.session_state.rasa_server_url = RASA_PUBLIC_URL  # Default to public URL for HF Spaces

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
        
        # Add more detailed logging for debugging
        st.write(f"🔍 Debug: Sending to {st.session_state.rasa_webhook_url}")
        st.write(f"🔍 Debug: Payload: {payload}")
        
        response = requests.post(
            st.session_state.rasa_webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        st.write(f"🔍 Debug: Response status: {response.status_code}")
        st.write(f"🔍 Debug: Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            st.write(f"🔍 Debug: Response content: {result}")
            return result
        else:
            st.error(f"Error: Status code {response.status_code} from Rasa server.")
            st.error(f"Response: {response.text}")
            return [{"text": "Sorry, I'm having trouble connecting. Please check the connection."}]
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: Could not connect to Rasa at {st.session_state.rasa_webhook_url}")
        st.error(f"Details: {str(e)}")
        return [{"text": "Sorry, I'm currently unavailable. Please try again later."}]


def check_rasa_server():
    """Check if Rasa server is running"""
    try:
        # Try multiple endpoints to check server status
        endpoints_to_try = [
            f"{st.session_state.rasa_server_url}/",
            f"{st.session_state.rasa_server_url}/status",
            f"{st.session_state.rasa_server_url}/webhooks/rest/webhook"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                st.write(f"🔍 Debug: Checking endpoint: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                st.write(f"🔍 Debug: Endpoint {endpoint} returned status: {response.status_code}")
                if response.status_code in [200, 404, 405]:  # 404/405 might be expected for some endpoints
                    return True
            except Exception as e:
                st.write(f"🔍 Debug: Endpoint {endpoint} failed: {str(e)}")
                continue
        return False
    except Exception as e:
        st.write(f"🔍 Debug: Server check failed: {str(e)}")
        return False

# --- STREAMLIT UI ---

st.set_page_config(page_title="Rasa Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Rasa Chatbot")
st.markdown("---")

# Add debug toggle
debug_mode = st.checkbox("Enable Debug Mode", value=False)

# Main layout
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### Chat with your Rasa assistant")
with col2:
    if check_rasa_server():
        st.success("🟢 Server Online")
    else:
        st.error("🔴 Server Offline")

# Display current connection info
st.info(f"🔗 Connected to: {st.session_state.rasa_server_url}")

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
            if debug_mode:
                st.write("🔍 Debug mode enabled - showing detailed logs")
            rasa_responses = send_message_to_rasa(prompt, st.session_state.user_id)

        if not rasa_responses:
             rasa_responses = [{"text": "No response received from server."}]

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
    
    new_url = st.text_input("Rasa Server URL", value=st.session_state.rasa_server_url)
    if st.button("Update Server URL"):
        st.session_state.rasa_server_url = new_url
        st.session_state.rasa_webhook_url = f"{new_url}/webhooks/rest/webhook"
        st.rerun()

    st.subheader("Quick Server Options")
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        if st.button("🌐 HF Spaces"):
            st.session_state.rasa_server_url = RASA_PUBLIC_URL
            st.session_state.rasa_webhook_url = f"{RASA_PUBLIC_URL}/webhooks/rest/webhook"
            st.rerun()
    with s_col2:
        if st.button("🔄 Alt HF"):
            st.session_state.rasa_server_url = RASA_ALTERNATIVE_URL
            st.session_state.rasa_webhook_url = f"{RASA_ALTERNATIVE_URL}/webhooks/rest/webhook"
            st.rerun()
    with s_col3:
        if st.button("🏠 Local"):
            st.session_state.rasa_server_url = RASA_INTERNAL_URL
            st.session_state.rasa_webhook_url = f"{RASA_INTERNAL_URL}/webhooks/rest/webhook"
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

    # Test webhook endpoint specifically
    if st.button("🧪 Test Webhook"):
        with st.spinner("Testing webhook..."):
            try:
                test_payload = {"sender": "test", "message": "hello"}
                st.write(f"🔍 Testing webhook at: {st.session_state.rasa_webhook_url}")
                st.write(f"🔍 Test payload: {test_payload}")
                
                response = requests.post(
                    st.session_state.rasa_webhook_url,
                    json=test_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                st.write(f"🔍 Response status: {response.status_code}")
                st.write(f"🔍 Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    st.success("✅ Webhook working!")
                    st.json(response.json())
                else:
                    st.error(f"❌ Webhook failed: {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Webhook test failed: {str(e)}")

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
