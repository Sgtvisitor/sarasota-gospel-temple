from dotenv import load_dotenv
load_dotenv()
import requests
import os

CLEARSTREAM_API_KEY = os.getenv("CLEARSTREAM_API_KEY")
url = "https://api.getclearstream.com/v1/threads"
headers = {"X-Api-Key": CLEARSTREAM_API_KEY, "Content-Type": "application/x-www-form-urlencoded"}
data = {
    "mobile_number": "+19415382650",  # Your test number
    "reply_header": "Sarasota Gospel Temple",
    "reply_body": "Welcome to Sarasota Gospel Temple!"
}
response = requests.post(url, headers=headers, data=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")