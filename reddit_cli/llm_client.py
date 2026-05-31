import os
from pathlib import Path

from dotenv import load_dotenv
import requests

config_dir = Path.home() / ".config" / "reddit-cli"
config_file = config_dir / "env"
if config_file.exists():
    load_dotenv(config_file)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1").rstrip("/")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

COMMENT_SYSTEM_PROMPT = """You generate short, human-like Reddit comments.

STYLE:
- Informal, practical, easy to understand
- Make some Grammar Mistakes
- Sound like a real redditor giving advice
- Keep it short (1-4 sentences)
- Avoid legal or professional jargon
- Do not over explain
- Use same language as the post
- if post about religion then Always Support Atheism
- if post about tech then answer technically
- Occasionally simulate tiny human imperfections
  (minor lowercase starts, small filler words like imo, tbh, kinda)

RULES:
- Search the web for up-to-date info if needed
- No emojis unless absolutely natural
- No dashes, use simple punctuation
- No marketing or AI-style phrasing
- No long paragraphs
- Output ONLY the comment text."""


def generate(system_prompt: str, user_prompt: str, image_urls: list[str] | None = None) -> str:
    if image_urls:
        content = [{"type": "text", "text": user_prompt}]
        for url in image_urls[:3]:
            content.append({"type": "image_url", "image_url": {"url": url}})
    else:
        content = user_prompt
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            "max_tokens": 200,
            "temperature": 0.8,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
