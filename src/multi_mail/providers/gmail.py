from __future__ import annotations

from multi_mail.normalize import normalize_provider_message
from multi_mail.providers.base import ReadOnlyMailProvider


class GmailReadOnlyAdapter(ReadOnlyMailProvider):
    """Read-only Gmail adapter around an injected Gmail-style client."""

    def __init__(self, client, *, user_id: str = "me") -> None:
        self.client = client
        self.user_id = user_id

    def list_message_refs(self, *, page_token: str | None = None) -> tuple[list[dict], str | None]:
        kwargs = {"userId": self.user_id}
        if page_token is not None:
            kwargs["pageToken"] = page_token
        response = self.client.users().messages().list(**kwargs).execute()
        refs = [
            {
                "provider_message_id": item.get("id"),
                "thread_id": item.get("threadId"),
            }
            for item in response.get("messages", [])
        ]
        return refs, response.get("nextPageToken")

    def get_message(self, provider_message_id: str) -> dict:
        message = (
            self.client.users()
            .messages()
            .get(userId=self.user_id, id=provider_message_id, format="metadata")
            .execute()
        )
        return normalize_provider_message(message)
