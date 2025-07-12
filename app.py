import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Configuration
RASA_SERVER_URL = "http://localhost:5005"  # Change this to your Rasa server URL
RASA_WEBHOOK_URL = f"{RASA_SERVER_URL}/webhooks/rest/webhook"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

def send_message_to_rasa(message, user_id):
    """Send message to Rasa server and get response"""
    try:
        payload = {
            "sender": user_id,
            "message": message
        }
        
        response = requests.post(
            RASA_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            rasa_responses = response.json()
            return rasa_responses
        else:
            st.error(f"Error: Received status code {response.status_code}")
            return [{"text": "Sorry, I'm having trouble connecting to the server."}]
            
    except requests.exceptions.ConnectionError:
        st.error("Connection Error: Could not connect to Rasa server. Make sure it's running.")
        return [{"text": "Sorry, I'm currently unavailable. Please try again later."}]
    except requests.exceptions.Timeout:
        st.error("Timeout Error: Server took too long to respond.")
        return [{"text": "Sorry, I'm taking too long to respond. Please try again."}]
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return [{"text": "Sorry, something went wrong. Please try again."}]

def check_rasa_server():
    """Check if Rasa server is running"""
    try:
        response = requests.get(f"{RASA_SERVER_URL}/version", timeout=5)
        return response.status_code == 200
    except:
        return False

# Streamlit UI
st.set_page_config(page_title="Rasa Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Rasa Chatbot")
st.markdown("---")

# Check server status
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

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("timestamp"):
                st.caption(message["timestamp"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt,
        "timestamp": timestamp
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(timestamp)
    
    # Get response from Rasa
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            rasa_responses = send_message_to_rasa(prompt, st.session_state.user_id)
        
        # Display bot responses
        for response in rasa_responses:
            if 'text' in response:
                st.markdown(response['text'])
                response_timestamp = datetime.now().strftime("%H:%M:%S")
                st.caption(response_timestamp)
                
                # Add bot response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response['text'],
                    "timestamp": response_timestamp
                })
            
            # Handle other response types (images, buttons, etc.)
            if 'image' in response:
                st.image(response['image'])
            
            if 'buttons' in response:
                st.markdown("**Quick replies:**")
                for button in response['buttons']:
                    if st.button(button['title'], key=f"btn_{uuid.uuid4()}"):
                        # Simulate clicking the button
                        st.rerun()

# Sidebar with additional features
with st.sidebar:
    st.header("Settings")
    
    # Server configuration
    st.subheader("Server Configuration")
    new_url = st.text_input("Rasa Server URL", value=RASA_SERVER_URL)
    if st.button("Update Server URL"):
        RASA_SERVER_URL = new_url
        RASA_WEBHOOK_URL = f"{RASA_SERVER_URL}/webhooks/rest/webhook"
        st.rerun()
    
    # Chat controls
    st.subheader("Chat Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("New Session"):
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    # Debug info
    st.subheader("Debug Info")
    st.text(f"User ID: {st.session_state.user_id[:8]}...")
    st.text(f"Messages: {len(st.session_state.messages)}")
    
    # Export chat
    if st.button("Export Chat"):
        chat_data = {
            "user_id": st.session_state.user_id,
            "messages": st.session_state.messages,
            "export_time": datetime.now().isoformat()
        }
        st.download_button(
            label="Download Chat JSON",
            data=json.dumps(chat_data, indent=2),
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and Rasa | [GitHub](https://github.com/your-repo)")
