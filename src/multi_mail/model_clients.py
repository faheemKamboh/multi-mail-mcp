from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Mapping, Protocol

import httpx


class HTTPResponse(Protocol):
    def raise_for_status(self) -> None: ...
    def json(self) -> dict: ...


PostJSON = Callable[..., HTTPResponse]


def _default_post(url: str, **kwargs) -> HTTPResponse:
    return httpx.post(url, **kwargs)


def _json_object_from_content(content: object) -> dict:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        raise ValueError("model response content must be a JSON object or JSON string")

    value = content.strip()
    if value.startswith("~~~"):
        lines = value.splitlines()
        if lines and lines[0].startswith("~~~"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "~~~":
            lines = lines[:-1]
        value = "\n".join(lines).strip()
        if value.lower().startswith("json\n"):
            value = value[5:].lstrip()

    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("model response JSON must be an object")
    return parsed


@dataclass
class OpenAICompatibleJSONClient:
    """Minimal OpenAI-compatible chat-completions client for JSON tasks.

    The same boundary works for a private local server and OpenRouter. Tests can
    inject a credential-free fake post callable, so network access is not
    required to qualify routing and response parsing.
    """

    base_url: str
    model: str
    api_key: str = ""
    timeout_seconds: float = 45.0
    json_mode: bool = False
    extra_headers: Mapping[str, str] = field(default_factory=dict)
    post_json: PostJSON = _default_post

    @property
    def endpoint(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    def complete_json(self, *, system: str, payload: dict) -> dict:
        headers = {"Content-Type": "application/json", **dict(self.extra_headers)}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body: dict = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                },
            ],
        }
        if self.json_mode:
            body["response_format"] = {"type": "json_object"}

        response = self.post_json(
            self.endpoint,
            headers=headers,
            json=body,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("model response did not contain choices[0].message.content") from exc
        return _json_object_from_content(content)


class OpenRouterFreeJSONClient(OpenAICompatibleJSONClient):
    """OpenRouter free-router client with no product-specific policy."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "openrouter/free",
        base_url: str = "https://openrouter.ai/api/v1",
        site_url: str = "",
        site_name: str = "Multi-Mail",
        timeout_seconds: float = 45.0,
        post_json: PostJSON = _default_post,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OpenRouter API key is required")
        headers: dict[str, str] = {}
        if site_url.strip():
            headers["HTTP-Referer"] = site_url.strip()
        if site_name.strip():
            headers["X-Title"] = site_name.strip()

        super().__init__(
            base_url=base_url,
            model=model,
            api_key=api_key.strip(),
            timeout_seconds=timeout_seconds,
            json_mode=True,
            extra_headers=headers,
            post_json=post_json,
        )
