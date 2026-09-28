from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from multi_mail.model_clients import OpenAICompatibleJSONClient, OpenRouterFreeJSONClient


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class Recorder:
    def __init__(self, content: str):
        self.content = content
        self.calls = []

    def __call__(self, url: str, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": self.content,
                        }
                    }
                ]
            }
        )


local_recorder = Recorder('{"category":"work","confidence":0.91}')
local = OpenAICompatibleJSONClient(
    base_url="http://oracle.internal:8080/v1/",
    model="small-mail-model",
    post_json=local_recorder,
)
assert local.complete_json(system="system", payload={"message": "hello"}) == {
    "category": "work",
    "confidence": 0.91,
}
url, kwargs = local_recorder.calls[0]
assert url == "http://oracle.internal:8080/v1/chat/completions"
assert kwargs["json"]["model"] == "small-mail-model"
assert "Authorization" not in kwargs["headers"]
assert "response_format" not in kwargs["json"]

fence = chr(96) * 3
fenced_recorder = Recorder(fence + "json\n" + '{"ok":true}' + "\n" + fence)
fenced_client = OpenAICompatibleJSONClient(
    base_url="http://local/v1",
    model="m",
    post_json=fenced_recorder,
)
assert fenced_client.complete_json(system="s", payload={}) == {"ok": True}

openrouter_recorder = Recorder('{"results":[]}')
openrouter = OpenRouterFreeJSONClient(
    api_key="test-key",
    site_url="https://mail.example.test",
    post_json=openrouter_recorder,
)
assert openrouter.complete_json(system="system", payload={"items": []}) == {"results": []}
url, kwargs = openrouter_recorder.calls[0]
assert url == "https://openrouter.ai/api/v1/chat/completions"
assert kwargs["headers"]["Authorization"] == "Bearer test-key"
assert kwargs["headers"]["HTTP-Referer"] == "https://mail.example.test"
assert kwargs["headers"]["X-Title"] == "Multi-Mail"
assert kwargs["json"]["model"] == "openrouter/free"
assert kwargs["json"]["response_format"] == {"type": "json_object"}

try:
    OpenRouterFreeJSONClient(api_key="  ")
except ValueError:
    pass
else:
    raise AssertionError("OpenRouter API key must be required")
