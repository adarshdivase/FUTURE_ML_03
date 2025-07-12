# app.py
import streamlit as st
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import uuid

# --- Page Configuration ---
st.set_page_config(page_title="SupportSage - AI Assistant", layout="centered")

st.markdown(
    """
    <style>
    .stButton>button {
        border-radius: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Bot Configuration ---
BOT_NAME = "SupportSage"
# --- THIS LINE HAS BEEN UPDATED TO THE CORRECT RELATIVE PATH ---
KNOWLEDGE_BASE_PATH = "chatbot_knowledge_base.csv"

# --- Data Loading & Caching ---
# Use st.cache_resource to load the model only once
@st.cache_resource
def load_knowledge_base():
    """Loads data, trains the vectorizer, and creates question vectors."""
    try:
        df = pd.read_csv(KNOWLEDGE_BASE_PATH)
        if "question" not in df.columns or "answer" not in df.columns:
            st.error("Error: CSV must have 'question' and 'answer' columns.")
            return None, None, None
        
        vectorizer = TfidfVectorizer(preprocessor=lambda x: re.sub(r'[^a-z0-9\s]', '', x.lower()))
        question_vectors = vectorizer.fit_transform(df['question'])
        
        return vectorizer, df, question_vectors
    except FileNotFoundError:
        st.error(f"Knowledge base file not found at '{KNOWLEDGE_BASE_PATH}'. Please check the path.")
        return None, None, None

vectorizer, df, question_vectors = load_knowledge_base()

# --- Chatbot Logic ---
def get_bot_response(user_message):
    """Finds the most similar question and returns its answer."""
    if vectorizer is None or df is None:
        return "I'm sorry, my knowledge base isn't loaded correctly. Please check the application logs."

    # Preprocess and vectorize user's message
    user_vector = vectorizer.transform([user_message])
    
    # Calculate similarities
    similarities = cosine_similarity(user_vector, question_vectors)
    
    # Find the best match
    most_similar_index = np.argmax(similarities)
    confidence = similarities[0, most_similar_index]
    
    CONFIDENCE_THRESHOLD = 0.3 # Adjust if needed
    
    if confidence > CONFIDENCE_THRESHOLD:
        response = df.iloc[most_similar_index]['answer']
    else:
        response = "I'm not sure how to answer that. Could you please rephrase?"
        
    return response

# --- Streamlit UI ---
st.title(f"🤖 {BOT_NAME} - Your AI Customer Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me about customer support..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_bot_response(prompt)
            st.markdown(response)
            
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
