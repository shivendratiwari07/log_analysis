import requests

# Define the API endpoint
url = "https://www.dex.inside.philips.com/philips-ai-chat/chat/api/user/SendImageMessage"

# Define the headers with the cookie
headers = {
    'Cookie': '.AspNetCore.Cookies=CfDJ8KMy4_c-Wz5PjYx8z8V0OI6X9mfAfNIFv7JM3m4npf4GWwi8UZSa45_fwViSYioAAnP1DZ_LPgUmgujAsrTUxKUEkmPPeIzCXOQxAdda5uw0BsTjNcU_NpLUbPoaKGnob3oC3His37hjzv8gqGdzIu0xhxaXSTzGsM6ZMut6KsU3A2R8v6XnzlrIoc6gh0Qpjv_y1WR41PloTDlDMPp5Qy5IOWD7eA1YTCpCqb_6s0poFtbADoGSH8WMvEMtE85UTQfiKJfB8JkJU0UOGBG_Rrd0BJbdPOpiOL8TYrgp7jOodTOrws_yB1kr4JIPbakMuCjnrvvIxahFJ0mqCEIsArytAO1wj15ObnVDdepS7xUylLojEcRkDOkxk-xASWwzVwnIH3quxt3yqcBHWAK8VbRs_5jpHhZKP-akrrZIHLiWtEovUrSuY15GGfRJBMZUYqqEyHCON9JyAG2zg1s5AFNrXQhyfgWXMk5K4P7LGE3pNMqdpj5hX5_Yy_JiU0tj2KFvZxdc9Zpykca6vAfD9UZma5f7ROErVozy7U2AV-Ub4F97smDe6RvdlCxtwY4GZ7nHtjS-K8D3ILz6PL5g22WXN5BGo9Pz4DpG5dOrQ93YcHJ14hoJn-TEaHCKDpWvevZxWmBTJlGO5d4aCYEdo5dq_ehetUNdFy56RY8wfuZU-O7estmhnS-BJH9u5IAce3t4Z40aCxKrf7wVLh9x6-VqeK5IOXVzYKg0HaQdgwyzgPekipX4xRckR-dCWGaBiLIemjGRdArnoo8UfDZOWr7WCnlQVL4HGdZ_ZN3dc0qUXm8M4c1POFlnbvpvTVB_YNgbFNMfzg9eKwlmbk1AOq9QdzuqxaBxkDZ5xP9n6Selg3l_g1AinbWuefFemkcr2RktMliowTczMeiPqx1DFr0bIu_qSO9Ap7AlnQIOu60CdauIyG777FJ6O0sQaJ2_ZeaTfzwY9pnjFbJ9s6dsxTkwPcLA4x3_2j6bQ4sFCuQkOLwM92KpvrqM_lhojLgBPfbzEUKoliNGdhj4Y5ThH9o3rq5QBwfeLkFNOithALu_EKzX2ICtSH8C6lVNh3vaQ6wQvkael0T4GpzUeskjCF7D515qh6qhfldh_eCpwLvz4nwMU-LKpU499N0lLpsJ6nEkHJUiD_Z1eKEh4G3aGiSL4A3TrEiTIJGu1wNzAPxE-FqOuPjORBgDTfkEUY9Tb1tcgirvWj5LZhjK1ZXXqb2DIb0-A_EknjwaS3cKZQOu2YAhYdNy09Y5aGQ3Jq0CYQnbuxteyyi5oh8ImRV3y2cZmJ5CJSBd6VING2YoxIqygqc0q058bosvY7REllcT__EpkqHLvqSsG-CjmWf29Y0bngGzteetlRporvYGBLP5lw2HZD83IRJdHdfxZTj1GUSpBoX1QflyEX4EiS6szHAZY-rJsXnp3POiObYGmPAsM41QDWHJcAOY9Pos8Kt9Li30tzNc875XpDx6QBEoiobP4nBb2NknoKDk8vHHjpUXI1VYkDKeBNMKfJ287oNPEAYffgHy44Qj3c-RSWxzM5PgE06zmYM2s-F-SIEwUnr9hQSRHsgx3XeiAL0MODuFkAggFOazKbfb6n9WURMWTZ5RTX8b2mLpMD1EJt8R7Vdjik9MEId2X1blyEBG8Af9-RSQj09fe8M_46_rb43KIKR0wf4ySrQxn9rFjMCjON9cQQwRa2xg2iiRiSbTeM8JJ-FEFivCtfoIyrXMbmwDTJQYgn8APcSIHkPYQmR3xyslT-U_bxmZzgvrpU96Gy7m7qYcjA57LnC7RxgMZleIIa8x7PhXB0dMvYIxlpTZygkSAq6XxmJ665fZ7bhe3tvvx669VP2Jqo0reN1kZo3AHuETQUpKmINpKAKCym99o5o1HDcVEiFeA5MqN1UDSo-5LO3ZkGFK7rkiwYy1HlLBj9QICT0-zhZh5bZa6WMGZ0FaCHfB68bTPuQjWG_vsQQRlxz5wkH1eTFQvzZmDidIe7vbXRtMA_MApLqkab9yDGQA8G-a__O_JozKgSNQO56JccuMX0j7agbtFk5ZQnBWja9bLOsJ1d8z4rQk0EtFI1wOWecF-jFD8fxsRWuFElIodi6GVQEU24isErJP25tNO4XwrcD3HeEr7t4PstEf2PQytKS8MYhll1BV3kdgZ6pZleAL-PY5EnNWn_7_FXZo-nhVA9Oq2K_0zBdLeVtP-nCtvatbPzDkwDf1I9OnU8gQ8wr1E3gaEfPoN2tsM87rXTXVJv3Wsnp7jrwfSzNM-Tj1zJ8DzU9ogfZvl_3oPaRu2WGLDnsj6f6EgmXdAnRnshWpvR6sSJR4hJ0_Hi0E_S6AWd1kpy8Wd2ODkAQ-I_LqLyIGPI_IFb2y0dLgPpvhZFwNbSPcPzMQg8Sdl4ANUon2Z2_cYtoB8fQ43SQl4HPdRncZpjomDaMndt44VVliKPD0tcf7Y5Z5eWSx9PQk0uxZBV-XFn5VO1AZIQZ5cweRrgNf2LtM2dn4ZViKbjokkubbMM4tHGVOVsb7z0eEEug01QgXvbuzRfWwv_jdpWxGtRbOMW6pig61wuIBKVq7ivRma9nPsl-gJnMK1SGQQxjJZsqvASgm_PGZHumkS6o5lTie3SMNQ-JsF8ppa3t5F6OHk__EbjQklsqhbPLNSJFgwK5XOeQr3kYMcp1ilws8YsfOE4twxzxYNT91R1SDrtnAKIoWvRCuMYQri22ApsKdcDRPaxs4vmrd77YfEKrUKyXuaxswxcuadhRnZrK6BAQ; ai_user=V5697lqIHSnfr+8ozVDooj|2024-07-23T07:32:44.735Z; ARRAffinitySameSite=8da8ccc8fe610cb85ae6bee641a7cdab56856c5b0031afc971de42132583be1e; ai_session=8ovnE+MUKwSVCL20sII5OV|1722580808141|1722580810784; ARRAffinity=8da8ccc8fe610cb85ae6bee641a7cdab56856c5b0031afc971de42132583be1e',
    'Content-Type': 'application/json'
}

# Define the payload
payload = {
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

# Make the POST request
response = requests.post(url, json=payload, headers=headers)

# Print the response
print(response.status_code)
print(response.json())




# import requests
# import json

# # API URL
# url = "https://www.dex.inside.philips.com/philips-ai-chat/chat/api/user/SendImageMessage"

# # Payload
# data = {
#     "messages": [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Who is Prime minister of INDIA?"
#                 }
#             ]
#         }
#     ]
# }

# # Headers
# headers = {
#     "Content-Type": "application/json"
# }

# # Sending the POST request
# response = requests.post(url, headers=headers, data=json.dumps(data))

# # Validating the response
# if response.status_code == 200:
#     print("API connection successful!")
#     try:
#         # Try to parse the response as JSON
#         response_json = response.json()
#         print("Response:", response_json)
#     except json.JSONDecodeError:
#         # If response is not JSON, print the raw response text
#         print("Received non-JSON response:")
#         print(response.text)
# else:
#     print(f"Failed to connect, status code: {response.status_code}")
#     print("Response:", response.text)

# import requests
# import json

# # API URL
# url = "https://www.dex.inside.philips.com/philips-ai-chat/chat/api/user/SendImageMessage"

# # Payload
# data = {
#     "messages": [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "Who is Prime minister of INDIA?"
#                 }
#             ]
#         }
#     ]
# }

# # Headers
# headers = {
#     "Content-Type": "application/json"
# }

# # Sending the POST request
# response = requests.post(url, headers=headers, data=json.dumps(data))

# # Validating the response
# print(f"Status Code: {response.status_code}")
# print(f"Response Headers: {response.headers}")

# if response.status_code == 200:
#     content_type = response.headers.get('Content-Type')
#     if 'application/json' in content_type:
#         try:
#             # Try to parse the response as JSON
#             response_json = response.json()
#             print("Response in JSON:")
#             print('responseoutpu'+response_json)
#             print(json.dumps(response_json, indent=4))  # Pretty-print the JSON response
#         except json.JSONDecodeError:
#             # If JSON decoding fails
#             print("JSON Decode Error: Unable to parse JSON response")
#             print("Response Text:")
#             print(response.text)
#     else:
#         # Print the content type and raw response if it's not JSON
#         print(f"Unexpected Content Type: {content_type}")
#         print("Response Text:")
#         print(response.text)
# else:
#     print(f"Failed to connect, status code: {response.status_code}")
#     print("Response Text:")
#     print(response.text)


