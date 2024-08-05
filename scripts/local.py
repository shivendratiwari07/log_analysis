import os
import requests

# GitHub API token and repository details
GITHUB_TOKEN = ""
REPO_OWNER = "shivendratiwari07"
REPO_NAME = "log_analysis"
RUN_ID = "10252490079"

# GitHub API endpoint for workflow run logs
logs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{RUN_ID}/logs"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# Download the logs
response = requests.get(logs_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    with open("workflow_logs.zip", "wb") as log_file:
        log_file.write(response.content)
    print("Logs downloaded successfully.")
else:
    print(f"Failed to download logs: {response.status_code}")
    print(response.json())
