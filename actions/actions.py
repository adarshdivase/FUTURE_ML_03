
import json
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import re
import random

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get('text', '').lower().strip()
        
        # Check if it's a greeting that might have been missed
        if self.is_greeting(user_message):
            dispatcher.utter_message(text="Hello! How can I help you today?")
            return []
        
        # Check if it's a goodbye
        if self.is_goodbye(user_message):
            dispatcher.utter_message(text="Goodbye! Have a great day!")
            return []
        
        # Try to find similar questions in the dataset
        similar_response = self.find_similar_response(user_message)
        
        if similar_response:
            dispatcher.utter_message(text=similar_response)
        else:
            # Enhanced fallback responses
            fallback_responses = [
                "I'm not sure I understand that completely. Could you rephrase your question?",
                "That's an interesting question! I don't have the exact answer right now.",
                "I'm still learning about that topic. Is there something else I can help with?",
                "I don't have information about that right now. Could you ask me something else?",
            ]
            dispatcher.utter_message(text=random.choice(fallback_responses))
        
        return []

    def is_greeting(self, text):
        greeting_patterns = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'what\'s up', 'how are you', 'howdy', 'greetings', 'sup', 'yo'
        ]
        return any(pattern in text for pattern in greeting_patterns)

    def is_goodbye(self, text):
        goodbye_patterns = [
            'bye', 'goodbye', 'see you', 'take care', 'farewell', 'later',
            'catch you later', 'have a good day', 'good night'
        ]
        return any(pattern in text for pattern in goodbye_patterns)

    def find_similar_response(self, user_message: str, threshold: float = 0.3) -> str:
        try:
            csv_file = "Conversation.csv"
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                questions = df['question'].dropna().tolist()
                answers = df['answer'].dropna().tolist()
                
                if not questions:
                    return None
                
                # Filter out greetings and goodbyes
                filtered_questions = []
                filtered_answers = []
                for q, a in zip(questions, answers):
                    if not (self.is_greeting(q.lower()) or self.is_goodbye(q.lower())):
                        filtered_questions.append(q)
                        filtered_answers.append(a)
                
                if not filtered_questions:
                    return None
                
                vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
                all_text = [user_message] + filtered_questions
                tfidf_matrix = vectorizer.fit_transform(all_text)
                
                similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                
                best_match_idx = similarities.argmax()
                if similarities[best_match_idx] > threshold:
                    return filtered_answers[best_match_idx]
            
        except Exception as e:
            print(f"Error in similarity matching: {e}")
        
        return None

class ActionProvideHelp(Action):
    def name(self) -> Text:
        return "action_provide_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        help_message = """
I'm here to help! Here are some things you can try:
- Ask me questions about topics I've been trained on
- Use clear, specific language
- Try rephrasing if I don't understand
- Ask "What can you do?" to learn more about my capabilities
        """
        dispatcher.utter_message(text=help_message)
        return []
