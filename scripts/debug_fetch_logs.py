import os
import sys
import requests
from azure.storage.blob import BlobServiceClient

def read_run_id(run_id_file):
    with open(run_id_file, 'r') as file:
        run_id = file.read().strip()
    return run_id

def get_failed_steps(owner, repo, run_id, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    jobs = response.json()["jobs"]
    failed_steps = []
    
    for job in jobs:
        job_logs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job['id']}/logs"
        for step in job["steps"]:
            if step["conclusion"] == "failure":
                failed_steps.append({
                    "job_name": job["name"],
                    "step_name": step["name"],
                    "job_logs_url": job_logs_url
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
    print(f"Starting upload to Azure Blob Storage: {file_path} as {blob_name}")
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(file_path, 'rb') as log_file:
            blob_client.upload_blob(log_file, overwrite=True)
        
        print(f"File uploaded successfully to {blob_name}.")
        return True
    except Exception as e:
        print(f"Failed to upload file: {str(e)}")
    return False

def analyze_logs_with_openai(log_filename):
    url = "https://www.dex.inside.philips.com/philips-ai-chat/chat/api/user/SendImageMessage"
    headers = {
    'Cookie': '.AspNetCore.Cookies=CfDJ8KMy4_c-Wz5PjYx8z8V0OI6X9mfAfNIFv7JM3m4npf4GWwi8UZSa45_fwViSYioAAnP1DZ_LPgUmgujAsrTUxKUEkmPPeIzCXOQxAdda5uw0BsTjNcU_NpLUbPoaKGnob3oC3His37hjzv8gqGdzIu0xhxaXSTzGsM6ZMut6KsU3A2R8v6XnzlrIoc6gh0Qpjv_y1WR41PloTDlDMPp5Qy5IOWD7eA1YTCpCqb_6s0poFtbADoGSH8WMvEMtE85UTQfiKJfB8JkJU0UOGBG_Rrd0BJbdPOpiOL8TYrgp7jOodTOrws_yB1kr4JIPbakMuCjnrvvIxahFJ0mqCEIsArytAO1wj15ObnVDdepS7xUylLojEcRkDOkxk-xASWwzVwnIH3quxt3yqcBHWAK8VbRs_5jpHhZKP-akrrZIHLiWtEovUrSuY15GGfRJBMZUYqqEyHCON9JyAG2zg1s5AFNrXQhyfgWXMk5K4P7LGE3pNMqdpj5hX5_Yy_JiU0tj2KFvZxdc9Zpykca6vAfD9UZma5f7ROErVozy7U2AV-Ub4F97smDe6RvdlCxtwY4GZ7nHtjS-K8D3ILz6PL5g22WXN5BGo9Pz4DpG5dOrQ93YcHJ14hoJn-TEaHCKDpWvevZxWmBTJlGO5d4aCYEdo5dq_ehetUNdFy56RY8wfuZU-O7estmhnS-BJH9u5IAce3t4Z40aCxKrf7wVLh9x6-VqeK5IOXVzYKg0HaQdgwyzgPekipX4xRckR-dCWGaBiLIemjGRdArnoo8UfDZOWr7WCnlQVL4HGdZ_ZN3dc0qUXm8M4c1POFlnbvpvTVB_YNgbFNMfzg9eKwlmbk1AOq9QdzuqxaBxkDZ5xP9n6Selg3l_g1AinbWuefFemkcr2RktMliowTczMeiPqx1DFr0bIu_qSO9Ap7AlnQIOu60CdauIyG777FJ6O0sQaJ2_ZeaTfzwY9pnjFbJ9s6dsxTkwPcLA4x3_2j6bQ4sFCuQkOLwM92KpvrqM_lhojLgBPfbzEUKoliNGdhj4Y5ThH9o3rq5QBwfeLkFNOithALu_EKzX2ICtSH8C6lVNh3vaQ6wQvkael0T4GpzUeskjCF7D515qh6qhfldh_eCpwLvz4nwMU-LKpU499N0lLpsJ6nEkHJUiD_Z1eKEh4G3aGiSL4A3TrEiTIJGu1wNzAPxE-FqOuPjORBgDTfkEUY9Tb1tcgirvWj5LZhjK1ZXXqb2DIb0-A_EknjwaS3cKZQOu2YAhYdNy09Y5aGQ3Jq0CYQnbuxteyyi5oh8ImRV3y2cZmJ5CJSBd6VING2YoxIqygqc0q058bosvY7REllcT__EpkqHLvqSsG-CjmWf29Y0bngGzteetlRporvYGBLP5lw2HZD83IRJdHdfxZTj1GUSpBoX1QflyEX4EiS6szHAZY-rJsXnp3POiObYGmPAsM41QDWHJcAOY9Pos8Kt9Li30tzNc875XpDx6QBEoiobP4nBb2NknoKDk8vHHjpUXI1VYkDKeBNMKfJ287oNPEAYffgHy44Qj3c-RSWxzM5PgE06zmYM2s-F-SIEwUnr9hQSRHsgx3XeiAL0MODuFkAggFOazKbfb6n9WURMWTZ5RTX8b2mLpMD1EJt8R7Vdjik9MEId2X1blyEBG8Af9-RSQj09fe8M_46_rb43KIKR0wf4ySrQxn9rFjMCjON9cQQwRa2xg2iiRiSbTeM8JJ-FEFivCtfoIyrXMbmwDTJQYgn8APcSIHkPYQmR3xyslT-U_bxmZzgvrpU96Gy7m7qYcjA57LnC7RxgMZleIIa8x7PhXB0dMvYIxlpTZygkSAq6XxmJ665fZ7bhe3tvvx669VP2Jqo0reN1kZo3AHuETQUpKmINpKAKCym99o5o1HDcVEiFeA5MqN1UDSo-5LO3ZkGFK7rkiwYy1HlLBj9QICT0-zhZh5bZa6WMGZ0FaCHfB68bTPuQjWG_vsQQRlxz5wkH1eTFQvzZmDidIe7vbXRtMA_MApLqkab9yDGQA8G-a__O_JozKgSNQO56JccuMX0j7agbtFk5ZQnBWja9bLOsJ1d8z4rQk0EtFI1wOWecF-jFD8fxsRWuFElIodi6GVQEU24isErJP25tNO4XwrcD3HeEr7t4PstEf2PQytKS8MYhll1BV3kdgZ6pZleAL-PY5EnNWn_7_FXZo-nhVA9Oq2K_0zBdLeVtP-nCtvatbPzDkwDf1I9OnU8gQ8wr1E3gaEfPoN2tsM87rXTXVJv3Wsnp7jrwfSzNM-Tj1zJ8DzU9ogfZvl_3oPaRu2WGLDnsj6f6EgmXdAnRnshWpvR6sSJR4hJ0_Hi0E_S6AWd1kpy8Wd2ODkAQ-I_LqLyIGPI_IFb2y0dLgPpvhZFwNbSPcPzMQg8Sdl4ANUon2Z2_cYtoB8fQ43SQl4HPdRncZpjomDaMndt44VVliKPD0tcf7Y5Z5eWSx9PQk0uxZBV-XFn5VO1AZIQZ5cweRrgNf2LtM2dn4ZViKbjokkubbMM4tHGVOVsb7z0eEEug01QgXvbuzRfWwv_jdpWxGtRbOMW6pig61wuIBKVq7ivRma9nPsl-gJnMK1SGQQxjJZsqvASgm_PGZHumkS6o5lTie3SMNQ-JsF8ppa3t5F6OHk__EbjQklsqhbPLNSJFgwK5XOeQr3kYMcp1ilws8YsfOE4twxzxYNT91R1SDrtnAKIoWvRCuMYQri22ApsKdcDRPaxs4vmrd77YfEKrUKyXuaxswxcuadhRnZrK6BAQ; ai_user=V5697lqIHSnfr+8ozVDooj|2024-07-23T07:32:44.735Z; ARRAffinitySameSite=8da8ccc8fe610cb85ae6bee641a7cdab56856c5b0031afc971de42132583be1e; ai_session=8ovnE+MUKwSVCL20sII5OV|1722580808141|1722580810784; ARRAffinity=8da8ccc8fe610cb85ae6bee641a7cdab56856c5b0031afc971de42132583be1e',
    'Content-Type': 'application/json'
    }
    with open(log_filename, 'r') as file:
        log_content = file.read()
        
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": log_content
                    }
                ]
            }
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def list_blob_containers(blob_service_client):
    print("Listing Blob Containers:")
    containers = blob_service_client.list_containers()
    for container in containers:
        print(f"Container Name: {container['name']}")

def main(run_id_file):
    run_id = read_run_id(run_id_file)

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
        list_blob_containers(blob_service_client)  # List all blob containers
    except Exception as e:
        print(f"Failed to connect to Azure Blob Storage: {str(e)}")
        return

    for step in failed_steps:
        log_filename = f"{step['job_name']}_{step['step_name']}_logs.txt"
        if not download_logs(step["job_logs_url"], headers, log_filename):
            print(f"Failed to download logs for {step['job_name']} - {step['step_name']}")
            continue

        blob_name = f'github_actions_logs_{run_id}_{step["job_name"]}_{step["step_name"]}.txt'
        if not upload_logs_to_azure(blob_service_client, container_name, blob_name, log_filename):
            print(f"Failed to upload logs for {step['job_name']} - {step['step_name']}")
            continue

        print(f"Analyzing log file: {log_filename}")
        try:
            analysis_result = analyze_logs_with_openai(log_filename)
            summary = analysis_result.get('choices', [{}])[0].get('message', {}).get('content', 'No summary available')

            # Ensure the summary is no more than 5 lines
            summary_lines = summary.split('\n')
            if len(summary_lines) > 5:
                summary = '\n'.join(summary_lines[:5])
            
            analysis_filename = log_filename.replace('_logs.txt', '_analysis.txt')
            with open(analysis_filename, 'w') as analysis_file:
                analysis_file.write(summary)
            
            print(f"Analysis saved to {analysis_filename}")
            print("Analysis summary:")
            print(summary)

            blob_name = f'github_actions_analysis_{os.path.basename(analysis_filename)}'
            if not upload_logs_to_azure(blob_service_client, container_name, blob_name, analysis_filename):
                print(f"Failed to upload analysis for {log_filename}")
        except Exception as e:
            print(f"Failed to analyze logs for {log_filename}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_fetch_logs.py <run_id_file>")
        sys.exit(1)
    main(sys.argv[1])





########$$$$$$$$$$$$$$ THIS SCRIPT IS STORING FAILED STEPS LOG
# import os
# import sys
# import requests
# from azure.storage.blob import BlobServiceClient

# def read_run_id(run_id_file):
#     with open(run_id_file, 'r') as file:
#         run_id = file.read().strip()
#     return run_id

# def get_failed_steps(owner, repo, run_id, headers):
#     url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
    
#     jobs = response.json()["jobs"]
#     failed_steps = []
    
#     for job in jobs:
#         job_logs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job['id']}/logs"
#         for step in job["steps"]:
#             if step["conclusion"] == "failure":
#                 failed_steps.append({
#                     "job_name": job["name"],
#                     "step_name": step["name"],
#                     "job_logs_url": job_logs_url
#                 })
    
#     return failed_steps

# def download_logs(logs_url, headers, output_filename):
#     response = requests.get(logs_url, headers=headers)
#     response.raise_for_status()
    
#     if not response.content:
#         raise Exception("Received empty content from GitHub API.")
    
#     with open(output_filename, 'wb') as file:
#         file.write(response.content)
    
#     print(f"Logs downloaded successfully to {output_filename}.")
#     return True

# def upload_logs_to_azure(blob_service_client, container_name, blob_name, file_path):
#     try:
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#         with open(file_path, 'rb') as log_file:
#             blob_client.upload_blob(log_file, overwrite=True)
        
#         print(f"Logs uploaded successfully to {blob_name}.")
#         return True
#     except Exception as e:
#         print(f"Failed to upload logs: {str(e)}")
#     return False

# def main(run_id_file):
#     run_id = read_run_id(run_id_file)

#     account_name = "githubactions02"
#     account_key = os.getenv('AZURE_STORAGE_KEY')
#     container_name = "actionslogs"
#     repo_owner = os.getenv('REPO_OWNER')
#     repo_name = os.getenv('REPO_NAME')
#     token = os.getenv('GITHUB_TOKEN')

#     if not all([repo_owner, repo_name, run_id, token]):
#         raise Exception("REPO_OWNER, REPO_NAME, GITHUB_RUN_ID, and GITHUB_TOKEN must be set")

#     headers = {
#         "Accept": "application/vnd.github+json",
#         "Authorization": f"Bearer {token}",
#         "X-GitHub-Api-Version": "2022-11-28"
#     }

#     failed_steps = get_failed_steps(repo_owner, repo_name, run_id, headers)
#     if not failed_steps:
#         print("No failed steps found.")
#         return

#     try:
#         connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
#         blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#         print("Connected to Azure Blob Storage")
#     except Exception as e:
#         print(f"Failed to connect to Azure Blob Storage: {str(e)}")
#         return

#     for step in failed_steps:
#         log_filename = f"{step['job_name']}_{step['step_name']}_logs.txt"
#         if not download_logs(step["job_logs_url"], headers, log_filename):
#             print(f"Failed to download logs for {step['job_name']} - {step['step_name']}")
#             continue

#         blob_name = f'github_actions_logs_{run_id}_{step["job_name"]}_{step["step_name"]}.txt'
#         if not upload_logs_to_azure(blob_service_client, container_name, blob_name, log_filename):
#             print(f"Failed to upload logs for {step['job_name']} - {step['step_name']}")
#             continue

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python debug_fetch_logs.py <run_id_file>")
#         sys.exit(1)
#     main(sys.argv[1])





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
