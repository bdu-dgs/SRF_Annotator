import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Step 1 — Get Access Token
resp = requests.post(
    "https://login.microsoftonline.com/4ccca3b5-71cd-4e6d-974b-4d9beb96c6d6/oauth2/v2.0/token",
    data={
        "grant_type":    "client_credentials",
        "client_id":     os.getenv("WUSTL_CLIENT_ID"),
        "client_secret": os.getenv("WUSTL_CLIENT_SECRET"),
        "scope":         "api://bbeee386-60d6-4ba4-b9a7-631763f66065/.default",
    },
)
resp.raise_for_status()
token = resp.json()["access_token"]


# Step 2 — Chat Completion
headers = {
    "Authorization": f"Bearer {token}",
    "X-Api-Key":     os.getenv("WUSTL_API_KEY"),
    "Content-Type":  "application/json",
}

resp = requests.post(
    "https://aiapi.wustl.edu/models/v2/chat/completions",
    headers=headers,
    json={
        "model":    os.getenv("MODEL_NAME"),
        "messages": [{"role": "user", "content": "Hello!"}]
    },
)
resp.raise_for_status()
print(resp.json()["choices"][0]["message"]["content"])