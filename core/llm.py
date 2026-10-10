
import json
import os
import re
from typing import Any, Iterator

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GroqService:
    def __init__(self):
        self.key = os.getenv("GROQ_API_KEY", "").strip()
        self.fast_model = os.getenv(
            "GROQ_MODEL_FAST", "openai/gpt-oss-20b"
        ).strip()
        self.reasoning_model = os.getenv(
            "GROQ_MODEL_REASONING", "openai/gpt-oss-120b"
        ).strip()

        self.client = Groq(api_key=self.key) if self.key else None

    @property
    def live(self) -> bool:
        return self.client is not None

    def chat(
        self,
        system: str,
        user: str,
        model: str | None = None,
        temperature: float = 0.25,
        max_tokens: int = 1800,
    ) -> str:
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is missing.")

        response = self.client.chat.completions.create(
            model=model or self.fast_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_completion_tokens=max_tokens,
        )

        return response.choices[0].message.content or ""

    def stream_text(
        self,
        system: str,
        user: str,
        model: str | None = None,
        temperature: float = 0.25,
        max_tokens: int = 1800,
    ) -> Iterator[str]:
        """Yield generated text chunks as soon as Groq returns them."""
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is missing.")

        stream = self.client.chat.completions.create(
            model=model or self.fast_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content
            if isinstance(content, str) and content:
                yield content

    def stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.35,
        max_tokens: int = 1600,
    ):
        """Backward-compatible raw Groq streaming API."""
        if not self.client:
            raise RuntimeError("GROQ_API_KEY is missing.")

        return self.client.chat.completions.create(
            model=model or self.reasoning_model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            stream=True,
        )

    def json(
        self,
        system: str,
        user: str,
        model: str | None = None,
        max_tokens: int = 3000,
    ) -> dict[str, Any]:
        raw = self.chat(
            system=system,
            user=user,
            model=model,
            temperature=0.1,
            max_tokens=max_tokens,
        ).strip()

        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            start, end = raw.find("{"), raw.rfind("}")
            if start < 0 or end <= start:
                raise ValueError("Model did not return valid JSON.")
            result = json.loads(raw[start:end + 1])

        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object.")

        return result


groq_service = GroqService()
