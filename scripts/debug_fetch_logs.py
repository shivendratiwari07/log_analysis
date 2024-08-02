import os
import requests

# GitHub environment variables for accessing logs
repo = os.getenv('GITHUB_REPOSITORY')
run_id = os.getenv('GITHUB_RUN_ID')
token = os.getenv('GITHUB_TOKEN')

# Verify that environment variables are set
if not repo or not run_id or not token:
    raise Exception("GITHUB_REPOSITORY, GITHUB_RUN_ID, and GITHUB_TOKEN must be set")

# GitHub API endpoint for workflow run logs
logs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"

# Print the URL for debugging
print(f"Logs URL: {logs_url}")

# Download logs
headers = {'Authorization': f'token {token}'}
response = requests.get(logs_url, headers=headers)

print(f"HTTP Status Code: {response.status_code}")
print(f"Response Content: {response.content}")

if response.status_code == 200:
    print("Logs fetched successfully.")
elif response.status_code == 403:
    print("Access denied. Ensure the GITHUB_TOKEN has the required permissions.")
elif response.status_code == 404:
    print("Logs not found. Ensure the GITHUB_REPOSITORY and GITHUB_RUN_ID are correct.")
else:
    print(f"Failed to download logs: {response.status_code} - {response.text}")
