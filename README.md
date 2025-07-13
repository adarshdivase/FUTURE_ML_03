
# Ultra Smart Rasa Chatbot

An intelligent, AI-powered chatbot generated from a CSV file. This project uses machine learning to cluster intents and generate a production-ready Rasa setup.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ & pip
- A `Conversation.csv` file in the same directory as the script.

### 1. Installation
Install the required Python libraries for your chatbot:
```bash
pip install rasa
```

### 2. Train the Model
Navigate into your generated project folder (`cd rasa_chatbot`) and train the Rasa model:
```bash
rasa train
```

### 3. Run the Chatbot
Start the Rasa server (this bot does not require a separate action server):
```bash
rasa run -m models --enable-api --cors "*"
```

### 4. Talk to Your Bot
Open a new terminal and use the shell to chat:
```bash
rasa shell
```

## Project Structure
```
rasa_chatbot/
├── data/                 # Training data (NLU, rules, stories)
├── models/               # Trained models
├── config.yml            # NLU/Core configuration
├── domain.yml            # Bot's domain
├── credentials.yml       # Channel credentials
└── endpoints.yml         # Action server endpoints
```
