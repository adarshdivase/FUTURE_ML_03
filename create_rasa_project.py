import os
import pandas as pd
import yaml
import shutil
import stat
import time

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
    
    config_path = os.path.join(PROJECT_DIRECTORY, "config.yml")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_content, f, sort_keys=False, allow_unicode=True)

    # Create credentials.yml
    credentials_content = {
        "# This file contains the credentials for the voice & chat platforms",
        "# which your bot is using.",
        "# https://rasa.com/docs/rasa/messaging-and-voice-channels/",
        "",
        "rest:",
        "#  # you don't need to provide anything here - this channel doesn't",
        "#  # require any credentials",
        "",
        "#facebook:",
        "#  verify: \"<verify>\"",
        "#  secret: \"<your secret>\"",
        "#  page-access-token: \"<your page access token>\"",
        "",
        "#slack:",
        "#  slack_token: \"<your slack token>\"",
        "#  slack_channel: \"<the slack channel>\"",
        "#  slack_signing_secret: \"<your slack signing secret>\"",
        "",
        "#socketio:",
        "#  user_message_evt: <event name for user message>",
        "#  bot_message_evt: <event name for bot message>",
        "#  session_persistence: <true/false>",
        "",
        "#mattermost:",
        "#  url: \"https://<mattermost instance>/api/v4\"",
        "#  token: \"<bot token>\"",
        "#  webhook_url: \"<callback URL>\"",
        "",
        "# This entry is needed if you are using Rasa X. The entry represents the",
        "# speech-to-text service in case you are using Rasa X with voice assistants.",
        "#rasa:",
        "#  url: \"http://localhost:5002/api\""
    }
    
    credentials_path = os.path.join(PROJECT_DIRECTORY, "credentials.yml")
    with open(credentials_path, "w", encoding="utf-8") as f:
        for line in credentials_content:
            f.write(line + "\n")
    
    # Create endpoints.yml
    endpoints_content = {
        "# This file contains the different endpoints your bot can use.",
        "# Server where the models are pulled from.",
        "# https://rasa.com/docs/rasa/model-storage#fetching-models-from-a-server",
        "",
        "#models:",
        "#  url: http://my-server.com/models/default_core@latest",
        "#  wait_time_between_pulls:  10   # [optional](default: 100)",
        "",
        "# Server which runs your custom actions.",
        "# https://rasa.com/docs/rasa/custom-actions",
        "",
        "#action_endpoint:",
        "#  url: \"http://localhost:5055/webhook\"",
        "",
        "# Tracker store which is used to store the conversations.",
        "# By default the conversations are stored in memory.",
        "# https://rasa.com/docs/rasa/tracker-stores",
        "",
        "#tracker_store:",
        "#    type: redis",
        "#    url: <host of the redis instance>",
        "#    port: <port of your redis instance>",
        "#    username: <username used for authentication>",
        "#    password: <password used for authentication>",
        "#    db: <number of your database within redis>",
        "",
        "# Event broker which all conversation events should be streamed to.",
        "# https://rasa.com/docs/rasa/event-brokers",
        "",
        "#event_broker:",
        "#  type: pika",
        "#  url: localhost",
        "#  username: username",
        "#  password: password",
        "#  queue: queue"
    }
    
    endpoints_path = os.path.join(PROJECT_DIRECTORY, "endpoints.yml")
    with open(endpoints_path, "w", encoding="utf-8") as f:
        for line in endpoints_content:
            f.write(line + "\n")
    
    print("Static files (config, credentials, endpoints) created.")


def generate_rasa_data_files():
    """Reads the CSV and generates nlu, domain, and rules files."""
    try:
        df = pd.read_csv(CSV_FILE)
        # Ensure we have the right column names
        if len(df.columns) < 2:
            print("Error: CSV file must have at least 2 columns (question, answer)")
            return
        
        df = df.rename(columns={df.columns[0]: 'question', df.columns[1]: 'answer'})
        print(f"Loaded {len(df)} rows from CSV")
    except FileNotFoundError:
        print(f"Error: Make sure '{CSV_FILE}' is in the same directory as this script.")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Initialize data structures
    intents = []
    responses = {}
    rules = []
    nlu_examples = []

    # Process each row
    for i, row in df.iterrows():
        intent_name = f"qa_pair_{i}"
        response_name = f"utter_{intent_name}"
        
        question = str(row['question']).strip()
        answer = str(row['answer']).strip()

        # Skip empty rows
        if not question or not answer or question == 'nan' or answer == 'nan':
            continue

        # Add to intents list
        intents.append(intent_name)
        
        # Add NLU example
        nlu_examples.append({
            "intent": intent_name,
            "examples": f"- {question}"
        })
        
        # Add response
        responses[response_name] = [{"text": answer}]
        
        # Add rule
        rules.append({
            "rule": f"Respond to {intent_name}",
            "steps": [
                {"intent": intent_name}, 
                {"action": response_name}
            ]
        })

    print(f"Generated {len(intents)} intents from CSV data")

    # Create domain.yml
    domain_content = {
        "version": "3.1",
        "intents": intents,
        "responses": responses,
        "session_config": {
            "session_expiration_time": 60,
            "carry_over_slots_to_new_session": True
        }
    }
    
    domain_path = os.path.join(PROJECT_DIRECTORY, "domain.yml")
    with open(domain_path, "w", encoding="utf-8") as f:
        yaml.dump(domain_content, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    
    print(f"Domain file created with {len(intents)} intents and {len(responses)} responses")

    # Create nlu.yml
    nlu_content = {
        "version": "3.1",
        "nlu": nlu_examples
    }
    
    nlu_path = os.path.join(PROJECT_DIRECTORY, "data", "nlu.yml")
    with open(nlu_path, "w", encoding="utf-8") as f:
        yaml.dump(nlu_content, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    
    print(f"NLU file created with {len(nlu_examples)} examples")

    # Create rules.yml
    rules_content = {
        "version": "3.1",
        "rules": rules
    }
    
    rules_path = os.path.join(PROJECT_DIRECTORY, "data", "rules.yml")
    with open(rules_path, "w", encoding="utf-8") as f:
        yaml.dump(rules_content, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    
    print(f"Rules file created with {len(rules)} rules")


def remove_readonly(func, path, _):
    """Remove read-only attribute and retry deletion."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def safe_remove_directory(directory):
    """Safely remove directory with Windows permission handling."""
    if not os.path.exists(directory):
        return True
    
    try:
        # First attempt: normal removal
        shutil.rmtree(directory)
        print(f"Successfully removed old '{directory}' directory.")
        return True
    except PermissionError:
        try:
            # Second attempt: handle read-only files
            shutil.rmtree(directory, onerror=remove_readonly)
            print(f"Successfully removed old '{directory}' directory (with permission fix).")
            return True
        except Exception as e:
            print(f"Warning: Could not remove old '{directory}' directory: {e}")
            print("This might be because files are in use. Please close any applications")
            print("that might be using files in the directory and try again.")
            
            # Try to rename it instead
            try:
                backup_name = f"{directory}_backup_{int(time.time())}"
                os.rename(directory, backup_name)
                print(f"Renamed old directory to '{backup_name}'.")
                return True
            except Exception as rename_error:
                print(f"Could not rename directory: {rename_error}")
                return False


def validate_yaml_files():
    """Validates that all YAML files are properly formatted."""
    yaml_files = [
        os.path.join(PROJECT_DIRECTORY, "domain.yml"),
        os.path.join(PROJECT_DIRECTORY, "config.yml"),
        os.path.join(PROJECT_DIRECTORY, "data", "nlu.yml"),
        os.path.join(PROJECT_DIRECTORY, "data", "rules.yml")
    ]
    
    for yaml_file in yaml_files:
        if os.path.exists(yaml_file):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
                print(f"✅ {yaml_file} is valid")
            except yaml.YAMLError as e:
                print(f"❌ {yaml_file} has YAML syntax error: {e}")
                return False
        else:
            print(f"❌ {yaml_file} does not exist")
            return False
    
    return True


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Rasa project generation...")
    
    # Clean up old project directory with Windows permission handling
    if not safe_remove_directory(PROJECT_DIRECTORY):
        print("\n❌ Could not remove old project directory.")
        print("Please manually delete the 'rasa_chatbot' folder and try again.")
        print("Or close any applications that might be using files in that folder.")
        exit(1)

    # Create project structure
    create_directory_structure()
    create_static_files()
    generate_rasa_data_files()
    
    # Validate YAML files
    print("\nValidating YAML files...")
    if validate_yaml_files():
        print("\n✅ Rasa project generation complete! All YAML files are valid.")
        print(f"\nTo train your model, run:")
        print(f"cd {PROJECT_DIRECTORY}")
        print(f"rasa train")
    else:
        print("\n❌ Some YAML files have errors. Please check the output above.")