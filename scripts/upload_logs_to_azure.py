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

print(f"GITHUB_REPOSITORY: {repo}")
print(f"GITHUB_RUN_ID: {run_id}")
print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")

# GitHub API endpoint for workflow run status
run_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"

print(f"Run URL: {run_url}")

# Retry mechanism for checking run status
max_retries = 30
retry_delay = 60  # seconds

# Check the status of the run until it's completed
for attempt in range(max_retries):
    headers = {'Authorization': f'token {token}'}
    run_response = requests.get(run_url, headers=headers)

    print(f"Run Attempt {attempt + 1}/{max_retries}: HTTP Status Code: {run_response.status_code}")
    if run_response.status_code != 200:
        print(f"HTTP Status Code: {run_response.status_code}")
        print(f"Response Headers: {run_response.headers}")
        print(f"Response Content: {run_response.content}")
    else:
        run_data = run_response.json()
        print(f"Run Data: {run_data}")
        if run_data['status'] == 'completed':
            print("Run is completed, fetching logs URL...")
            break
        else:
            print(f"Run status: {run_data['status']}, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)

if run_data['status'] != 'completed':
    raise Exception("Run did not complete within the expected time frame.")

# GitHub API endpoint for workflow run logs
logs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
print(f"Logs URL: {logs_url}")

# Check log availability with retry mechanism
log_retries = 15
log_retry_delay = 30  # seconds

for log_attempt in range(log_retries):
    headers = {'Authorization': f'token {token}'}
    log_response = requests.get(logs_url, headers=headers)

    print(f"Log Attempt {log_attempt + 1}/{log_retries}: HTTP Status Code: {log_response.status_code}")
    if log_response.status_code != 200:
        print(f"HTTP Status Code: {log_response.status_code}")
        print(f"Response Headers: {log_response.headers}")
        print(f"Response Content: {log_response.content}")
    else:
        logs_content = log_response.content
        print("Logs fetched successfully.")
        break
    if log_response.status_code == 404:
        if log_attempt < log_retries - 1:
            print(f"Logs not available yet, retrying in {log_retry_delay} seconds... (Attempt {log_attempt + 1}/{log_retries})")
            time.sleep(log_retry_delay)
        else:
            raise Exception("Logs not found after multiple attempts. Ensure the GITHUB_REPOSITORY and GITHUB_RUN_ID are correct.")
    else:
        raise Exception(f"Failed to download logs: {log_response.status_code} - {log_response.text}")

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
