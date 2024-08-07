import requests
import sys
import os

def analyze_logs_with_openai(log_filename):
    url = "https://www.dex.inside.philips.com/philips-ai-chat/chat/api/user/SendImageMessage"
    headers = {
        'Cookie': '.AspNetCore.Cookies=YOUR_COOKIE_HERE',  # Replace with your actual cookie
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

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_logs.py <log_filename>")
        sys.exit(1)

    log_filename = sys.argv[1]
    print(f"Analyzing log file: {log_filename}")

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

if __name__ == "__main__":
    main()
