import os
import time
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
run_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"

# Print the URL for debugging
print(f"Logs URL: {logs_url}")
print(f"Run URL: {run_url}")

# Retry mechanism for checking run status
max_retries = 15
retry_delay = 120  # seconds

for attempt in range(max_retries):
    # Check run status
    headers = {'Authorization': f'token {token}'}
    run_response = requests.get(run_url, headers=headers)

    print(f"Run Attempt {attempt + 1}/{max_retries}: HTTP Status Code: {run_response.status_code}")
    print(f"Run Response Content: {run_response.content}")

    if run_response.status_code == 200:
        run_data = run_response.json()
        if run_data['status'] == 'completed':
            print("Run is completed, fetching logs...")
            break
        else:
            print(f"Run status: {run_data['status']}, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
    else:
        raise Exception(f"Failed to check run status: {run_response.status_code} - {run_response.text}")

# Retry mechanism for fetching logs
max_log_retries = 10
log_retry_delay = 60  # seconds

for attempt in range(max_log_retries):
    # Download logs
    headers = {'Authorization': f'token {token}'}
    response = requests.get(logs_url, headers=headers)

    print(f"Log Attempt {attempt + 1}/{max_log_retries}: HTTP Status Code: {response.status_code}")
    print(f"Log Response Content: {response.content}")

    if response.status_code == 200:
        logs_content = response.content
        print("Logs fetched successfully.")
        break
    elif response.status_code == 403:
        raise Exception("Access denied. Ensure the GITHUB_TOKEN has the required permissions.")
    elif response.status_code == 404:
        if attempt < max_log_retries - 1:
            print(f"Logs not found, retrying in {log_retry_delay} seconds... (Attempt {attempt + 1}/{max_log_retries})")
            time.sleep(log_retry_delay)
        else:
            raise Exception("Logs not found after multiple attempts. Ensure the GITHUB_REPOSITORY and GITHUB_RUN_ID are correct.")
    else:
        raise Exception(f"Failed to download logs: {response.status_code} - {response.text}")

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
