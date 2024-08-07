import os
import sys
import requests
from azure.storage.blob import BlobServiceClient

def get_failed_steps(owner, repo, run_id, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    jobs = response.json()["jobs"]
    failed_steps = []
    
    for job in jobs:
        for step in job["steps"]:
            if step["conclusion"] == "failure":
                failed_steps.append({
                    "job_name": job["name"],
                    "step_name": step["name"],
                    "log_url": step["log_url"]
                })
    
    return failed_steps

def download_logs(logs_url, headers, output_filename):
    response = requests.get(logs_url, headers=headers)
    response.raise_for_status()
    
    if not response.content:
        raise Exception("Received empty content from GitHub API.")
    
    with open(output_filename, 'wb') as file:
        file.write(response.content)
    
    print(f"Logs downloaded successfully to {output_filename}.")
    return True

def upload_logs_to_azure(blob_service_client, container_name, blob_name, file_path):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(file_path, 'rb') as log_file:
            blob_client.upload_blob(log_file, overwrite=True)
        
        print(f"Logs uploaded successfully to {blob_name}.")
        return True
    except Exception as e:
        print(f"Failed to upload logs: {str(e)}")
    return False

def main(run_id_file):
    with open(run_id_file, 'r') as file:
        run_id = file.read().strip()

    account_name = "githubactions02"
    account_key = os.getenv('AZURE_STORAGE_KEY')
    container_name = "actionslogs"
    repo_owner = os.getenv('REPO_OWNER')
    repo_name = os.getenv('REPO_NAME')
    token = os.getenv('GITHUB_TOKEN')

    if not all([repo_owner, repo_name, run_id, token]):
        raise Exception("REPO_OWNER, REPO_NAME, GITHUB_RUN_ID, and GITHUB_TOKEN must be set")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    failed_steps = get_failed_steps(repo_owner, repo_name, run_id, headers)
    if not failed_steps:
        print("No failed steps found.")
        return

    try:
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        print("Connected to Azure Blob Storage")
    except Exception as e:
        print(f"Failed to connect to Azure Blob Storage: {str(e)}")
        return

    for step in failed_steps:
        log_filename = f"{step['job_name']}_{step['step_name']}_logs.txt"
        if not download_logs(step["log_url"], headers, log_filename):
            print(f"Failed to download logs for {step['job_name']} - {step['step_name']}")
            continue

        blob_name = f'github_actions_logs_{run_id}_{step["job_name"]}_{step["step_name"]}.txt'
        if not upload_logs_to_azure(blob_service_client, container_name, blob_name, log_filename):
            print(f"Failed to upload logs for {step['job_name']} - {step['step_name']}")
            continue

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_fetch_logs.py <run_id_file>")
        sys.exit(1)
    main(sys.argv[1])



# import os
# import requests
# import zipfile  # Import the zipfile module
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
# print(f"GITHUB_TOKEN: {token}")
# # print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")
# print(f"Environment REPO_OWNER: {os.getenv('REPO_OWNER')}")
# print(f"Environment REPO_NAME: {os.getenv('REPO_NAME')}")
# print(f"Environment GITHUB_RUN_ID: {os.getenv('GITHUB_RUN_ID')}")
# print(f"Environment GITHUB_TOKEN: {os.getenv('GITHUB_TOKEN')}")
# print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")

# print("#####################################################################")
# print(f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/logs")
# # Download the logs using curl
# curl_command = f"""
# curl -L \
#   -H "Accept: application/vnd.github+json" \
#   -H "Authorization: Bearer {token}" \
#   -H "X-GitHub-Api-Version: 2022-11-28" \
#   https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/logs \
#   --output logs.zip
# """
# print(f"Running command: {curl_command}")
# os.system(curl_command)

# print(f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/logs")

# # Verify the logs have been downloaded
# if not os.path.exists('logs.zip'):
#     raise Exception("Failed to download logs using curl.")

# print("Logs downloaded successfully. Checking file content...")

# # Check file size
# file_size = os.path.getsize('logs.zip')
# if file_size == 0:
#     raise Exception("Downloaded logs file is empty.")

# print(f"Logs.zip file size: {file_size} bytes")

# # Check if file is a valid zip file
# # try:
# #     with zipfile.ZipFile('logs.zip', 'r') as zip_ref:
# #         zip_ref.extractall('logs')
# #         extracted_files = zip_ref.namelist()
# #         print(f"Extracted files: {extracted_files}")
# # except zipfile.BadZipFile:
# #     print("File is not a valid zip file. Checking content...")
# #     with open('logs.zip', 'r') as log_file:
# #         content = log_file.read()
# #         print(content)
# #         if "message" in content and "status" in content:
# #             print("GitHub API response:", content)
# #     raise

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
##


#####################################################  WORKING SCRIPT  ##########################
# import os
# import sys
# import requests
# from azure.storage.blob import BlobServiceClient

# def download_github_logs(logs_url, headers, output_filename):
#     """
#     Downloads GitHub logs to the specified file.
#     """
#     try:
#         # Make the request to the GitHub API
#         response = requests.get(logs_url, headers=headers)
#         response.raise_for_status()  # Raise error for HTTP errors
        
#         if not response.content:  # Check if response content is empty
#             raise Exception("Received empty content from GitHub API.")
        
#         # Write the content to the output file
#         with open(output_filename, 'wb') as file:
#             file.write(response.content)
        
#         print("Logs downloaded successfully.")
#         return True
#     except requests.exceptions.HTTPError as http_err:
#         print(f"HTTP error occurred: {http_err}")
#         print(f"Response status code: {response.status_code}")
#         print(f"Response content: {response.content.decode('utf-8')}")
#     except Exception as err:
#         print(f"Other error occurred: {err}")
#     return False

# def upload_logs_to_azure(blob_service_client, container_name, blob_name, file_path):
#     """
#     Uploads the specified file to Azure Blob Storage.
#     """
#     try:
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#         with open(file_path, 'rb') as log_file:
#             blob_client.upload_blob(log_file, overwrite=True)
        
#         print("Logs uploaded successfully.")
#         return True
#     except Exception as e:
#         print(f"Failed to upload logs: {str(e)}")
#     return False

# def main(run_id_file):
#     # Read the GITHUB_RUN_ID from the provided file
#     with open(run_id_file, 'r') as file:
#         run_id = file.read().strip()

#     # Azure Storage account details
#     account_name = "githubactions02"
#     account_key = os.getenv('AZURE_STORAGE_KEY')
#     container_name = "actionslogs"

#     # GitHub environment variables for accessing logs
#     repo_owner = os.getenv('REPO_OWNER')
#     repo_name = os.getenv('REPO_NAME')
#     token = os.getenv('GITHUB_TOKEN')

#     # Verify that environment variables are set
#     if not repo_owner or not repo_name or not run_id or not token:
#         raise Exception("REPO_OWNER, REPO_NAME, GITHUB_RUN_ID, and GITHUB_TOKEN must be set")

#     # Logging to ensure env vars are set correctly
#     print(f"REPO_OWNER: {repo_owner}")
#     print(f"REPO_NAME: {repo_name}")
#     print(f"GITHUB_RUN_ID: {run_id}")
#     print(f"GITHUB_TOKEN: {'***' if token else 'MISSING'}")

#     logs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs/{run_id}/logs"
#     print(f"Logs URL: {logs_url}")

#     headers = {
#         "Accept": "application/vnd.github+json",
#         "Authorization": f"Bearer {token}",
#         "X-GitHub-Api-Version": "2022-11-28"
#     }

#     # Print the headers to ensure they are set correctly
#     print(f"Headers: {headers}")

#     output_filename = 'logs.zip'
#     if not download_github_logs(logs_url, headers, output_filename):
#         print("Failed to download logs.")
#         return

#     if not os.path.exists(output_filename) or os.path.getsize(output_filename) == 0:
#         print("Downloaded logs file is empty or does not exist.")
#         return

#     try:
#         connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
#         blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#         print("Connected to Azure Blob Storage")
#     except Exception as e:
#         print(f"Failed to connect to Azure Blob Storage: {str(e)}")
#         return

#     blob_name = f'github_actions_logs_{run_id}.zip'
#     if not upload_logs_to_azure(blob_service_client, container_name, blob_name, output_filename):
#         print("Failed to upload logs to Azure Blob Storage.")
#         return

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python debug_fetch_logs.py <run_id_file>")
#         sys.exit(1)
#     main(sys.argv[1])
