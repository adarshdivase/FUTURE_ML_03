
# Enhanced Ultra Smart Rasa Chatbot

An intelligent, AI-powered chatbot with advanced fallback handling and similarity matching for out-of-dataset questions.

## 🚀 Features

- **Smart Intent Clustering**: Automatically groups similar questions
- **Similarity Matching**: Finds similar questions even for out-of-dataset queries
- **Enhanced Fallback**: Provides helpful responses for unknown questions
- **Custom Actions**: Advanced logic for better user experience
- **Improved Training**: Better NLU pipeline configuration

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- A `Conversation.csv` file in the same directory as the script

### 1. Install Dependencies
```bash
pip install rasa pandas pyyaml scikit-learn numpy nltk
```

### 2. Train the Model
Navigate to your project folder and train:
```bash
cd enhanced_rasa_chatbot
rasa train
```

### 3. Start the Action Server
In one terminal:
```bash
rasa run actions
```

### 4. Start the Rasa Server
In another terminal:
```bash
rasa run -m models --enable-api --cors "*"
```

### 5. Chat with Your Bot
```bash
rasa shell
```

## 🎯 Key Improvements

- **Better Out-of-Dataset Handling**: Uses similarity matching to find related answers
- **Enhanced Fallback Messages**: More natural and helpful responses
- **Custom Actions**: Intelligent fallback logic with dataset search
- **Improved Training**: Better configuration for accuracy and understanding
- **Extended Intent Coverage**: More natural conversation patterns

## 📁 Project Structure
```
enhanced_rasa_chatbot/
├── actions/              # Custom action server files
├── data/                 # Training data (NLU, rules, stories)
├── models/               # Trained models
├── config.yml            # Enhanced NLU/Core configuration
├── domain.yml            # Bot's domain with custom actions
├── credentials.yml       # Channel credentials
└── endpoints.yml         # Action server endpoints
```

## 🔧 Troubleshooting

If the bot isn't responding to out-of-dataset questions:
1. Make sure the action server is running (`rasa run actions`)
2. Check that your CSV file is in the correct location
3. Verify the similarity threshold in the custom actions

## 📝 Customization

You can modify the similarity threshold and fallback responses in `actions/actions.py` to better suit your needs.
