import os
from github import Github
from git import Repo
from datetime import datetime
from flask import Flask, jsonify

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "your_default_github_token")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "your_default_github_username")
REPO_NAME = os.getenv("REPO_NAME", "your_default_repo_name")
LOCAL_REPO_PATH = os.getenv("LOCAL_REPO_PATH", os.path.join(os.getcwd(), "local_repo"))
TEXT_FILE_NAME = os.getenv("TEXT_FILE_NAME", "timestamp.txt")

app = Flask(__name__)

def update_timestamp():
    # Step 1: Authenticate with GitHub
    repo_url = f'https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git'

    # Step 2: Clone the repository if not already cloned
    if not os.path.exists(LOCAL_REPO_PATH):
        print(f"Cloning repository {REPO_NAME}...")
        Repo.clone_from(repo_url, LOCAL_REPO_PATH)

    # Configure Git identity (set this for the local repository)
    repo_local = Repo(LOCAL_REPO_PATH)
    with repo_local.config_writer() as config:
        config.set_value("user", "name", "Kapilan Ramasamy")  # Replace with your name
        config.set_value("user", "email", "kapilanr2003@gmail.com")  # Replace with your email

    # Print the resolved local repository path
    print(f"Resolved local repository path: {os.path.abspath(LOCAL_REPO_PATH)}")

    # Step 3: Add or update the text file with the current timestamp
    timestamp = datetime.now().isoformat()  # Get the current timestamp in ISO format
    file_path = os.path.join(LOCAL_REPO_PATH, TEXT_FILE_NAME)

    # Write the timestamp to the file
    with open(file_path, "w") as f:
        f.write(timestamp)

    # Step 4: Commit and push changes
    repo_local.git.add(TEXT_FILE_NAME)

    commit_message = f"Update {TEXT_FILE_NAME} with timestamp {timestamp}"
    repo_local.git.commit(m=commit_message)
    print("Committed changes.")

    # Push changes
    origin = repo_local.remote(name="origin")
    origin.push()
    print("Pushed changes to GitHub.")

    return timestamp

@app.route('/')
def keep_alive():
    return jsonify({"message": "Server is alive."}), 200

@app.route('/update-timestamp', methods=['POST'])
def update_timestamp_endpoint():
    try:
        timestamp = update_timestamp()
        print(timestamp)
        return jsonify({"message": "Timestamp updated successfully"}), 200
    except Exception as e:
        # Limit the response size by returning a concise error message
        return jsonify({"error": "An error occurred during the update. Please check server logs for details."}), 500

if __name__ == '__main__':
    app.run(debug=True)
