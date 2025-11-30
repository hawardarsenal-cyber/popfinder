# backend/open_client.py

import os
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing. Check .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)


class OpenAIClient:
    @staticmethod
    def ask_gpt(prompt: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate only URLs or concise event data."},
                {"role": "user", "content": prompt}
            ]
        )

        # FIXED: new OpenAI API returns message.content as an attribute
        return response.choices[0].message.content
