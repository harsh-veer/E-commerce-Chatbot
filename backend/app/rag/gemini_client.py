import json
import logging
import os
import time
import asyncio
import httpx
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

class GeminiClient:
    disable_grounding = False

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash-lite",
            "gemini-flash-latest",
            "gemini-flash-lite-latest"
        ]

    def _build_payloads(self, prompt: str):
        base_config = {
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
                "temperature": 0.3,
                "maxOutputTokens": 2048
            }
        }

        if GeminiClient.disable_grounding:
            return None, base_config

        grounded_payload = dict(base_config)
        grounded_payload["tools"] = [{"googleSearch": {}}]
        return grounded_payload, base_config

    def generate(self, prompt: str) -> str:
        grounded_payload, standard_payload = self._build_payloads(prompt)
        last_error = None

        for model_name in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            payloads = []
            if grounded_payload:
                payloads.append(("grounded", grounded_payload))
            payloads.append(("standard", standard_payload))

            for payload_name, payload in payloads:
                try:
                    response = requests.post(
                        url,
                        params={"key": self.api_key},
                        json=payload,
                        timeout=30,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"Gemini API generation succeeded using model {model_name}")
                        try:
                            return data["candidates"][0]["content"]["parts"][0]["text"]
                        except (KeyError, IndexError):
                            return "Response received from Gemini, but content structure was empty."
                    elif response.status_code == 429:
                        # Check if this is a quota error
                        if "quota" in response.text.lower():
                            if payload_name == "grounded":
                                logger.warning("Search grounding quota exceeded. Disabling search grounding.")
                                GeminiClient.disable_grounding = True
                                # Continue immediately to standard payload
                                continue

                        logger.warning(f"Gemini model {model_name} rate limited (429). Retrying in 1.5s...")
                        time.sleep(1.5)
                        last_error = response.text
                    else:
                        logger.warning(f"Gemini model {model_name} returned HTTP {response.status_code}: {response.text[:150]}")
                        last_error = response.text
                except Exception as e:
                    logger.warning(f"Gemini model {model_name} failed with error: {e}")
                    last_error = str(e)

        raise Exception(f"All Gemini models failed. Last error: {last_error}")

    async def generate_stream(self, prompt: str):
        grounded_payload, standard_payload = self._build_payloads(prompt)
        last_error = None

        async with httpx.AsyncClient(timeout=45.0) as client:
            for model_name in self.models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent"
                payloads = []
                if grounded_payload:
                    payloads.append(("grounded", grounded_payload))
                payloads.append(("standard", standard_payload))

                for payload_name, payload in payloads:
                    try:
                        async with client.stream("POST", url, params={"key": self.api_key, "alt": "sse"}, json=payload) as response:
                            if response.status_code == 200:
                                logger.info(f"Gemini API streaming started using model {model_name}")
                                async for line in response.aiter_lines():
                                    if line.startswith("data: "):
                                        data_str = line[6:].strip()
                                        if data_str:
                                            try:
                                                data = json.loads(data_str)
                                                candidates = data.get("candidates", [])
                                                if candidates and "content" in candidates[0]:
                                                    parts = candidates[0]["content"].get("parts", [])
                                                    for part in parts:
                                                        if "text" in part:
                                                            yield part["text"]
                                            except Exception:
                                                pass
                                return
                            elif response.status_code == 429:
                                err_text = await response.aread()
                                err_str = err_text.decode("utf-8", errors="ignore")
                                if "quota" in err_str.lower():
                                    if payload_name == "grounded":
                                        logger.warning("Search grounding quota exceeded in stream. Disabling search grounding.")
                                        GeminiClient.disable_grounding = True
                                        # Continue immediately to standard payload
                                        continue

                                logger.warning(f"Gemini model {model_name} rate limited (429) during stream. Waiting 1.5s...")
                                await asyncio.sleep(1.5)
                                last_error = err_text
                            else:
                                err_text = await response.aread()
                                logger.warning(f"Gemini model {model_name} stream returned HTTP {response.status_code}: {err_text[:150]}")
                                last_error = err_text
                    except Exception as e:
                        logger.warning(f"Gemini streaming model {model_name} failed: {e}")
                        last_error = str(e)

        if last_error:
            err_str = last_error.decode("utf-8", errors="ignore") if isinstance(last_error, bytes) else str(last_error)
            yield f"\n\n*(Note: Gemini service encountered an issue: {err_str[:100]})*"