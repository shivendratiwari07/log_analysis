import os
import requests

def list_workflow_runs(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for HTTP errors
        runs = response.json()
        for run in runs.get("workflow_runs", []):
            print(f"ID: {run['id']}, Status: {run['status']}, Conclusion: {run['conclusion']}, Created At: {run['created_at']}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content.decode('utf-8')}")
    except Exception as err:
        print(f"Other error occurred: {err}")

if __name__ == "__main__":
    owner = os.getenv('REPO_OWNER', 'shivendratiwari07')
    repo = os.getenv('REPO_NAME', 'log_analysis')
    token = os.getenv('GITHUB_TOKEN')

    list_workflow_runs(owner, repo, token)
