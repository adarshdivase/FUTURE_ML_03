import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# --- CONFIGURATION ---

# Use the actual Hugging Face Space URL for your Rasa backend
RASA_SERVER_URL = "https://adarshdivase-Rasabackend.hf.space"
RASA_WEBHOOK_URL = f"{RASA_SERVER_URL}/webhooks/rest/webhook"

# GitHub repository link
GITHUB_REPO_LINK = "https://github.com/adarshdivase/FUTURE_ML_05"

# Initialize session state variables if they don't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())


# --- HELPER FUNCTIONS ---

def send_message_to_rasa(message, user_id):
    """Send message to Rasa server and get response"""
    try:
        payload = {
            "sender": user_id,
            "message": message
        }
        
        # Add headers for better compatibility
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Use the Hugging Face Space URL
        response = requests.post(
            RASA_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: Status code {response.status_code} from Rasa server.")
            st.error(f"Rasa server response: {response.text}")
            return [{"text": "Sorry, I'm having trouble connecting. Please check the logs."}]
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. The server might be busy.")
        return [{"text": "Sorry, the request timed out. Please try again."}]
    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Could not connect to Rasa at {RASA_WEBHOOK_URL}")
        return [{"text": "Sorry, I'm currently unavailable. Please try again later."}]
    except requests.exceptions.RequestException as e:
        st.error(f"Request Error: {e}")
        return [{"text": "Sorry, I'm having trouble connecting. Please try again later."}]


def check_rasa_server():
    """Check if Rasa server is running"""
    try:
        # First try the /status endpoint
        response = requests.get(f"{RASA_SERVER_URL}/status", timeout=10)
        if response.status_code == 200:
            return True
        
        # If status endpoint fails, try the main endpoint
        response = requests.get(RASA_SERVER_URL, timeout=10)
        return response.status_code == 200
        
    except requests.exceptions.RequestException:
        return False


def test_webhook():
    """Test the webhook endpoint specifically"""
    try:
        test_payload = {
            "sender": "test_user",
            "message": "hello"
        }
        
        response = requests.post(
            RASA_WEBHOOK_URL,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        return response.status_code == 200, response.status_code, response.text
        
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)


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
             rasa_responses = [{"text": "Sorry, I didn't receive a response. Please try again."}]

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

    st.subheader("Chat Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    if st.button("New Session"):
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.subheader("Connection Status")
    st.info(f"Backend: {RASA_SERVER_URL}")
    st.info(f"Webhook: {RASA_WEBHOOK_URL}")

    if st.button("🔄 Test Server"):
        with st.spinner("Testing server..."):
            if check_rasa_server():
                st.success("✅ Server is running!")
            else:
                st.error("❌ Server is not responding!")

    if st.button("🔧 Test Webhook"):
        with st.spinner("Testing webhook..."):
            success, status_code, response_text = test_webhook()
            if success:
                st.success(f"✅ Webhook working! Status: {status_code}")
                try:
                    response_json = json.loads(response_text)
                    st.json(response_json)
                except:
                    st.text(response_text)
            else:
                st.error(f"❌ Webhook failed! Status: {status_code}")
                st.error(f"Response: {response_text}")

    st.subheader("Debug Info")
    st.text(f"User ID: {st.session_state.user_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")

    if st.button("Export Chat"):
        chat_data = {
            "user_id": st.session_state.user_id, 
            "messages": st.session_state.messages,
            "timestamp": datetime.now().isoformat()
        }
        st.download_button(
            label="Download Chat JSON",
            data=json.dumps(chat_data, indent=2),
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# --- FOOTER ---
st.markdown("---")
st.markdown(f"Built with Streamlit and Rasa | [GitHub]({GITHUB_REPO_LINK}) | [Backend]({RASA_SERVER_URL})")

# --- QUICK START GUIDE ---
with st.expander("🚀 Quick Start Guide"):
    st.markdown("""
    **How to use this chatbot:**
    1. Type your message in the chat input below
    2. Press Enter to send
    3. Wait for the assistant's response
    
    **Troubleshooting:**
    - If you see connection errors, use the "Test Server" and "Test Webhook" buttons
    - Check that the backend server is running at the URL above
    - Clear chat history if responses seem stuck
    
    **Features:**
    - Persistent chat history during session
    - Export chat conversations
    - Debug tools for connection testing
    """)

# --- ADVANCED DEBUG (Collapsible) ---
with st.expander("🔍 Advanced Debug"):
    st.write("**Current Configuration:**")
    config_info = {
        "Rasa Server URL": RASA_SERVER_URL,
        "Webhook URL": RASA_WEBHOOK_URL,
        "User ID": st.session_state.user_id,
        "Total Messages": len(st.session_state.messages),
        "Session State Keys": list(st.session_state.keys())
    }
    st.json(config_info)
    
    if st.button("🔍 Full Connection Test"):
        st.write("**Testing full connection flow...**")
        
        # Test 1: Basic server connectivity
        st.write("1. Testing server connectivity...")
        try:
            response = requests.get(RASA_SERVER_URL, timeout=5)
            st.success(f"✅ Server accessible: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Server connection failed: {e}")
        
        # Test 2: Status endpoint
        st.write("2. Testing status endpoint...")
        try:
            response = requests.get(f"{RASA_SERVER_URL}/status", timeout=5)
            if response.status_code == 200:
                st.success("✅ Status endpoint working")
                st.json(response.json())
            else:
                st.error(f"❌ Status endpoint failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Status endpoint error: {e}")
        
        # Test 3: Webhook endpoint
        st.write("3. Testing webhook endpoint...")
        try:
            test_payload = {"sender": "debug_user", "message": "test connection"}
            response = requests.post(
                RASA_WEBHOOK_URL, 
                json=test_payload, 
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                st.success("✅ Webhook responding correctly")
                st.json(response.json())
            else:
                st.error(f"❌ Webhook failed: {response.status_code}")
                st.error(f"Response: {response.text}")
        except Exception as e:
            st.error(f"❌ Webhook error: {e}")
