import requests
import json

# API URL
url = "https://www.dex.inside.philips.com/philips-ai-chat/chat/api/user/SendImageMessage"

# Payload
data = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Who is Prime minister of INDIA?"
                }
            ]
        }
    ]
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Sending the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Validating the response
if response.status_code == 200:
    print("API connection successful!")
    try:
        # Try to parse the response as JSON
        response_json = response.json()
        print("Response:", response_json)
    except json.JSONDecodeError:
        # If response is not JSON, print the raw response text
        print("Received non-JSON response:")
        print(response.text)
else:
    print(f"Failed to connect, status code: {response.status_code}")
    print("Response:", response.text)

import requests
import json

# API URL
url = "https://www.dex.inside.philips.com/philips-ai-chat/chat/api/user/SendImageMessage"

# Payload
data = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Who is Prime minister of INDIA?"
                }
            ]
        }
    ]
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Sending the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Validating the response
print(f"Status Code: {response.status_code}")
print(f"Response Headers: {response.headers}")

if response.status_code == 200:
    content_type = response.headers.get('Content-Type')
    if 'application/json' in content_type:
        try:
            # Try to parse the response as JSON
            response_json = response.json()
            print("Response in JSON:")
            print('responseoutpu'+response_json)
            print(json.dumps(response_json, indent=4))  # Pretty-print the JSON response
        except json.JSONDecodeError:
            # If JSON decoding fails
            print("JSON Decode Error: Unable to parse JSON response")
            print("Response Text:")
            print(response.text)
    else:
        # Print the content type and raw response if it's not JSON
        print(f"Unexpected Content Type: {content_type}")
        print("Response Text:")
        print(response.text)
else:
    print(f"Failed to connect, status code: {response.status_code}")
    print("Response Text:")
    print(response.text)


