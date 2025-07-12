import os
import pandas as pd
import yaml

# --- Configuration ---
CSV_FILE = "Conversation.csv"
PROJECT_DIRECTORY = "rasa_chatbot"

# --- Helper Functions ---

def create_directory_structure():
    """Creates the standard Rasa directory structure."""
    if not os.path.exists(PROJECT_DIRECTORY):
        print(f"Creating project directory: {PROJECT_DIRECTORY}")
        os.makedirs(PROJECT_DIRECTORY)

    data_dir = os.path.join(PROJECT_DIRECTORY, "data")
    actions_dir = os.path.join(PROJECT_DIRECTORY, "actions")
    models_dir = os.path.join(PROJECT_DIRECTORY, "models")
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(actions_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    with open(os.path.join(actions_dir, "__init__.py"), "w") as f:
        pass
    print("Directory structure created.")


def create_static_files():
    """Creates the static configuration files for Rasa."""
    config_content = {
        "recipe": "default.v1",
        "assistant_id": "20240712-111100-primal-crust",
        "language": "en",
        "pipeline": [
            {"name": "WhitespaceTokenizer"},
            {"name": "RegexFeaturizer"},
            {"name": "LexicalSyntacticFeaturizer"},
            {"name": "CountVectorsFeaturizer"},
            {"name": "DIETClassifier", "epochs": 100},
        ],
        "policies": [{"name": "RulePolicy"}],
    }
    with open(os.path.join(PROJECT_DIRECTORY, "config.yml"), "w") as f:
        yaml.dump(config_content, f, sort_keys=False)

    # ... (other static files remain the same) ...
    print("Static files (config, etc.) created.")


def generate_rasa_data_files():
    """Reads the CSV and generates nlu, domain, and rules files."""
    try:
        df = pd.read_csv(CSV_FILE)
        df = df.rename(columns={df.columns[1]: 'question', df.columns[2]: 'answer'})
    except FileNotFoundError:
        print(f"Error: Make sure '{CSV_FILE}' is in the same directory as this script.")
        return

    # *** THIS IS THE CORRECTED LOGIC ***
    intents = []
    responses = {}
    rules = []
    nlu_examples = []

    for i, row in df.iterrows():
        intent_name = f"qa_pair_{i}"
        response_name = f"utter_{intent_name}"
        
        question = str(row['question']).strip()
        answer = str(row['answer']).strip()

        if not question or not answer:
            continue

        intents.append(intent_name)
        nlu_examples.append({"intent": intent_name, "examples": f"- {question}"})
        responses[response_name] = [{"text": answer}]
        rules.append({
            "rule": f"Respond to {intent_name}",
            "steps": [{"intent": intent_name}, {"action": response_name}],
        })

    # Build the full domain dictionary first
    domain_content = {
        "version": "3.1",
        "intents": intents,
        "responses": responses,
        "session_config": {
            "session_expiration_time": 60,
            "carry_over_slots_to_new_session": True,
        },
    }
    # Then write it all at once
    with open(os.path.join(PROJECT_DIRECTORY, "domain.yml"), "w", encoding="utf-8") as f:
        yaml.dump(domain_content, f, sort_keys=False, allow_unicode=True)

    # --- Write NLU and Rules Files ---
    nlu_content = {"version": "3.1", "nlu": nlu_examples}
    with open(os.path.join(PROJECT_DIRECTORY, "data", "nlu.yml"), "w", encoding="utf-8") as f:
        yaml.dump(nlu_content, f, sort_keys=False, allow_unicode=True)
        
    rules_content = {"version": "3.1", "rules": rules}
    with open(os.path.join(PROJECT_DIRECTORY, "data", "rules.yml"), "w", encoding="utf-8") as f:
        yaml.dump(rules_content, f, sort_keys=False, allow_unicode=True)
        
    print("Rasa data files (domain, nlu, rules) generated correctly.")

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Rasa project generation...")
    # It's better to regenerate from a clean state
    if os.path.exists(PROJECT_DIRECTORY):
        import shutil
        shutil.rmtree(PROJECT_DIRECTORY)
        print(f"Removed old '{PROJECT_DIRECTORY}' directory.")

    create_directory_structure()
    create_static_files() # This function is simplified for brevity
    generate_rasa_data_files()
    print("\n✅ Rasa project generation complete!")