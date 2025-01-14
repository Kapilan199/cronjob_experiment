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
    g = Github(GITHUB_TOKEN)
    user = g.get_user(GITHUB_USERNAME)
    repo = user.get_repo(REPO_NAME)

    # Step 2: Clone the repository if not already cloned
    if not os.path.exists(LOCAL_REPO_PATH):
        print(f"Cloning repository {REPO_NAME}...")
        Repo.clone_from(repo.clone_url, LOCAL_REPO_PATH)

    # Print the resolved local repository path
    print(f"Resolved local repository path: {os.path.abspath(LOCAL_REPO_PATH)}")

    # Step 3: Add or update the text file with the current timestamp
    timestamp = datetime.now().isoformat()  # Get the current timestamp in ISO format
    file_path = os.path.join(LOCAL_REPO_PATH, TEXT_FILE_NAME)

    # Write the timestamp to the file
    with open(file_path, "w") as f:
        f.write(timestamp)

    # Step 4: Commit and push changes
    repo_local = Repo(LOCAL_REPO_PATH)
    repo_local.git.add(TEXT_FILE_NAME)

    commit_message = f"Update {TEXT_FILE_NAME} with timestamp {timestamp}"
    repo_local.git.commit(m=commit_message)
    print("Committed changes.")

    # Push changes
    origin = repo_local.remote(name="origin")
    origin.push()
    print("Pushed changes to GitHub.")

    return timestamp

@app.route('/update-timestamp', methods=['POST'])
def update_timestamp_endpoint():
    try:
        timestamp = update_timestamp()
        return jsonify({"message": "Timestamp updated successfully", "timestamp": timestamp}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
