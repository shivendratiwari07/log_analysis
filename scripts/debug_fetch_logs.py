# import os
# import requests
# from azure.storage.blob import BlobServiceClient

# # Azure Storage account details
# account_name = "githubactions02"
# account_key = os.getenv('AZURE_STORAGE_KEY')
# container_name = "actionslogs"

# # GitHub environment variables for accessing logs
# repo_owner = os.getenv('REPO_OWNER')
# repo_name = os.getenv('REPO_NAME')
# run_id = os.getenv('GITHUB_RUN_ID')
# token = os.getenv('GITHUB_TOKEN')

# # Verify that environment variables are set
# if not repo_owner or not repo_name or not run_id or not token:
#     raise Exception("REPO_OWNER, REPO_NAME, GITHUB_RUN_ID, and GITHUB_TOKEN must be set")

# print(f"REPO_OWNER: {repo_owner}")
# print(f"REPO_NAME: {repo_name}")
# print(f"GITHUB_RUN_ID: {run_id}")
# print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")

# # Download the logs using curl
# os.system(f"""
# curl -L \
#   -H "Accept: application/vnd.github+json" \
#   -H "Authorization: Bearer {token}" \
#   -H "X-GitHub-Api-Version: 2022-11-28" \
#   https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/logs \
#   --output logs.zip
# """)

# # Verify the logs have been downloaded
# if not os.path.exists('logs.zip'):
#     raise Exception("Failed to download logs using curl.")

# print("Logs downloaded successfully. Uploading to Azure...")

# # Azure Blob Storage connection string
# connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
# blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# # Upload logs to Azure Blob Storage
# blob_client = blob_service_client.get_blob_client(container=container_name, blob=f'github_actions_logs_{run_id}.zip')

# try:
#     with open('logs.zip', 'rb') as log_file:
#         blob_client.upload_blob(log_file, overwrite=True)
#     print("Logs uploaded successfully.")
# except Exception as e:
#     print(f"Failed to upload logs: {str(e)}")


import os
import requests
import zipfile  # Import the zipfile module
from azure.storage.blob import BlobServiceClient

# Azure Storage account details
account_name = "githubactions02"
account_key = os.getenv('AZURE_STORAGE_KEY')
container_name = "actionslogs"

# GitHub environment variables for accessing logs
repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')
run_id = os.getenv('GITHUB_RUN_ID')
token = os.getenv('GITHUB_TOKEN')

# Verify that environment variables are set
if not repo_owner or not repo_name or not run_id or not token:
    raise Exception("REPO_OWNER, REPO_NAME, GITHUB_RUN_ID, and GITHUB_TOKEN must be set")

print(f"REPO_OWNER: {repo_owner}")
print(f"REPO_NAME: {repo_name}")
print(f"GITHUB_RUN_ID: {run_id}")
print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")

# Download the logs using curl
curl_command = f"""
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer {token}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/logs \
  --output logs.zip
"""
print(f"Running command: {curl_command}")
os.system(curl_command)

# Verify the logs have been downloaded
if not os.path.exists('logs.zip'):
    raise Exception("Failed to download logs using curl.")

print("Logs downloaded successfully. Checking file content...")

# Check file size
file_size = os.path.getsize('logs.zip')
if file_size == 0:
    raise Exception("Downloaded logs file is empty.")

print(f"Logs.zip file size: {file_size} bytes")

# Check if file is a valid zip file
try:
    with zipfile.ZipFile('logs.zip', 'r') as zip_ref:
        zip_ref.extractall('logs')
        extracted_files = zip_ref.namelist()
        print(f"Extracted files: {extracted_files}")
except zipfile.BadZipFile:
    print("File is not a valid zip file. Checking content...")
    with open('logs.zip', 'r') as log_file:
        print(log_file.read())
    raise

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
