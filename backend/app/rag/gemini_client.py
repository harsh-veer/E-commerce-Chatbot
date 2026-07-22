import logging
import requests

logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

print("KEY FOUND:", API_KEY is not None)
print("KEY START:", API_KEY[:8] if API_KEY else None)

class GeminiClient:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-flash-latest:generateContent"
        )
    def generate(self, prompt: str) -> str:

        payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024
        }
        }
        response = requests.post(
        self.url,
        params={"key": self.api_key},
        json=payload,
        timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        import json
        print("\n========== GEMINI FULL RESPONSE ==========")
        print(json.dumps(data, indent=2))
        print("==========================================\n")

        return data["candidates"][0]["content"]["parts"][0]["text"]