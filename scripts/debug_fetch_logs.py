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

print(f"GITHUB_REPOSITORY: {repo}")
print(f"GITHUB_RUN_ID: {run_id}")
print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")

# Download the logs using curl
os.system(f"""
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer {token}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs \
  --output logs.zip
""")

# Verify the logs have been downloaded
if not os.path.exists('logs.zip'):
    raise Exception("Failed to download logs using curl.")

print("Logs downloaded successfully. Uploading to Azure...")

# Azure Blob Storage connection string
connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Upload logs to Azure Blob Storage
blob_client = blob_service_client.get_blob_client(container=container_name, blob=f'github_actions_logs_{run_id}.zip')

try:
    with open('logs.zip', 'rb') as log_file:
        blob_client.upload_blob(log_file, overwrite=True)
    print("Logs uploaded successfully.")
except Exception as e:
    print(f"Failed to upload logs: {str(e)}")
