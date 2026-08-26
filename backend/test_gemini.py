import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

prompt = "Hello"
base_payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
}

grounded_payload = dict(base_payload)
grounded_payload["tools"] = [{"googleSearch": {}}]

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

print("Testing grounded payload...")
r1 = requests.post(url, params={"key": api_key}, json=grounded_payload)
print(f"Status: {r1.status_code}")
print(f"Response: {r1.text}")

print("\nTesting standard payload...")
r2 = requests.post(url, params={"key": api_key}, json=base_payload)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text}")
