from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from multi_mail.providers.gmail import GmailReadOnlyAdapter


RAW_MESSAGE = {
    "id": "gm-001",
    "threadId": "gt-009",
    "labelIds": ["INBOX"],
    "snippet": "Hello from Gmail fixture",
    "payload": {
        "headers": [
            {"name": "From", "value": "Sender <sender@example.test>"},
            {"name": "To", "value": "user@example.test"},
            {"name": "Subject", "value": "Fixture message"},
        ]
    },
}


class Request:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class MessagesResource:
    def __init__(self):
        self.calls = []

    def list(self, **kwargs):
        self.calls.append(("list", kwargs))
        return Request(
            {
                "messages": [
                    {"id": "gm-001", "threadId": "gt-009"},
                    {"id": "gm-002", "threadId": "gt-010"},
                ],
                "nextPageToken": "page-2",
            }
        )

    def get(self, **kwargs):
        self.calls.append(("get", kwargs))
        assert kwargs["id"] == "gm-001"
        return Request(RAW_MESSAGE)


class UsersResource:
    def __init__(self, messages):
        self._messages = messages

    def messages(self):
        return self._messages


class FakeGmailClient:
    def __init__(self):
        self.messages_resource = MessagesResource()
        self.users_resource = UsersResource(self.messages_resource)

    def users(self):
        return self.users_resource


client = FakeGmailClient()
adapter = GmailReadOnlyAdapter(client)

refs, next_page = adapter.list_message_refs(page_token="page-1")
assert refs == [
    {"provider_message_id": "gm-001", "thread_id": "gt-009"},
    {"provider_message_id": "gm-002", "thread_id": "gt-010"},
]
assert next_page == "page-2"
assert client.messages_resource.calls[0] == (
    "list",
    {"userId": "me", "pageToken": "page-1"},
)

message = adapter.get_message("gm-001")
assert message == {
    "provider_message_id": "gm-001",
    "thread_id": "gt-009",
    "from": "Sender <sender@example.test>",
    "to": "user@example.test",
    "subject": "Fixture message",
    "reply_to": None,
    "return_path": None,
    "list_id": None,
    "authentication_results": None,
    "label_ids": ["INBOX"],
    "snippet": "Hello from Gmail fixture",
}
assert client.messages_resource.calls[1] == (
    "get",
    {"userId": "me", "id": "gm-001", "format": "metadata"},
)

# No credentials, tokens, writes, or mutation methods are part of this adapter contract.
for forbidden in ("send_message", "delete_message", "apply_label", "archive_message", "trash_message"):
    assert not hasattr(adapter, forbidden), forbidden
