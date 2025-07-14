
# Enhanced Ultra Smart Rasa Chatbot

This project contains an intelligent, AI-powered chatbot automatically generated from a Q&A dataset. It features proper fallback handling and can intelligently respond to out-of-dataset questions by finding similar known questions.

## Key Features

- **Intelligent Intent Clustering**: Uses AI to analyze conversational data and group similar questions into meaningful intents.
- **Advanced Fallback Handling**: Includes a custom fallback action that tries to find a similar question if an input is not understood.
- **Automated File Generation**: Automatically creates all necessary Rasa files.
- **Rich Core Intents**: Comes pre-packaged with extensive examples for common intents.
- **Optimized Configuration**: The `config.yml` is pre-configured with a robust NLU pipeline.

## How to Use This Project

1. **Install Rasa**: `pip install rasa`
2. **Install additional dependencies**: `pip install rasa[transformers]`
3. **Navigate to project**: `cd enhanced_rasa_chatbot`
4. **Train the Model**: `rasa train`
5. **Run the Action Server**: In a new terminal, `rasa run actions`
6. **Talk to Your Bot**: In the first terminal, `rasa shell`

## Troubleshooting

If you encounter training errors:
- Make sure all dependencies are installed
- Check that your CSV file has 'question' and 'answer' columns
- Verify the generated YAML files are properly formatted
- Try reducing the number of intents if you have memory issues

## Project Structure

```
enhanced_rasa_chatbot/
├── data/
│   ├── nlu.yml          # Training examples
│   ├── rules.yml        # Conversation rules
│   └── stories.yml      # Example conversations
├── actions/
│   └── actions.py       # Custom actions
├── config.yml           # Pipeline configuration
├── domain.yml           # Domain specification
├── credentials.yml      # Channel credentials
└── endpoints.yml        # Action server endpoints
```
