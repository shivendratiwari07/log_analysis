import os
import requests
from azure.storage.blob import BlobServiceClient

# Azure Storage account details
account_name = "githubactions02"
account_key = os.getenv('AZURE_STORAGE_KEY')
container_name = "actionslogs"

# GitHub environment variables for accessing logs
repo = os.getenv('GITHUB_REPOSITORY')
run_id = os.getenv('GITHUB_RUN_ID')
token = os.getenv('GITHUB_TOKEN')

# Verify that environment variables are set
if not repo or not run_id or not token:
    raise Exception("GITHUB_REPOSITORY, GITHUB_RUN_ID, and GITHUB_TOKEN must be set")

# Print the environment variables for debugging
print(f"GITHUB_REPOSITORY: {repo}")
print(f"GITHUB_RUN_ID: {run_id}")
print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")

# GitHub API endpoint for workflow run logs
logs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"

# Print the URL for debugging
print(f"Logs URL: {logs_url}")

# Download logs using GitHub API
headers = {'Authorization': f'token {token}'}
log_response = requests.get(logs_url, headers=headers)

print(f"Log Fetch Attempt: HTTP Status Code: {log_response.status_code}")
if log_response.status_code != 200:
    print(f"HTTP Status Code: {log_response.status_code}")
    print(f"Response Headers: {log_response.headers}")
    print(f"Response Content: {log_response.content}")
    raise Exception(f"Failed to download logs: {log_response.status_code} - {log_response.text}")

logs_content = log_response.content
print("Logs fetched successfully.")

# Azure Blob Storage connection string
connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Upload logs to Azure Blob Storage
blob_client = blob_service_client.get_blob_client(container=container_name, blob=f'github_actions_logs_{run_id}.zip')

try:
    blob_client.upload_blob(logs_content, overwrite=True)
    print("Logs uploaded successfully.")
except Exception as e:
    print(f"Failed to upload logs: {str(e)}")
