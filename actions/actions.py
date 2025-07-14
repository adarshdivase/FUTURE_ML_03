
import json
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get('text')
        
        # Try to find similar questions in the dataset
        similar_response = self.find_similar_response(user_message)
        
        if similar_response:
            dispatcher.utter_message(text=similar_response)
        else:
            # Enhanced fallback responses
            fallback_responses = [
                "I'm not sure I understand that completely. Could you rephrase your question?",
                "That's an interesting question! I might not have the exact answer, but let me know if you'd like to explore something else.",
                "I'm still learning about that topic. Is there something specific you'd like to know?",
                "I don't have information about that right now. Could you ask me something else?",
                "That's outside my current knowledge. What else would you like to discuss?"
            ]
            import random
            dispatcher.utter_message(text=random.choice(fallback_responses))
        
        return []

    def find_similar_response(self, user_message: str, threshold: float = 0.3) -> str:
        """Find similar questions in the dataset and return the corresponding answer."""
        try:
            # Load the Q&A database
            csv_file = "Conversation.csv"
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                questions = df['question'].dropna().tolist()
                answers = df['answer'].dropna().tolist()
                
                if len(questions) == 0:
                    return None
                
                # Use TF-IDF to find similar questions
                vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
                all_questions = [user_message] + questions
                tfidf_matrix = vectorizer.fit_transform(all_questions)
                
                # Calculate similarity between user message and all questions
                similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                
                # Find the most similar question
                best_match_idx = similarities.argmax()
                best_similarity = similarities[best_match_idx]
                
                if best_similarity > threshold:
                    return answers[best_match_idx]
            
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
