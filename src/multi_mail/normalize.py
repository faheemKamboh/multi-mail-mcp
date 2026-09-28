from __future__ import annotations


_HEADER_NAMES = {
    "from": "from",
    "to": "to",
    "subject": "subject",
    "reply-to": "reply_to",
    "return-path": "return_path",
    "list-id": "list_id",
    "authentication-results": "authentication_results",
}


def normalize_provider_message(message: dict) -> dict:
    """Convert a Gmail-like provider message into the provider-neutral read shape."""

    normalized_headers: dict[str, object] = {}
    payload = message.get("payload") or {}
    for header in payload.get("headers") or []:
        name = str(header.get("name") or "").strip().lower()
        target = _HEADER_NAMES.get(name)
        if target and target not in normalized_headers:
            normalized_headers[target] = header.get("value")

    return {
        "provider_message_id": message.get("id"),
        "thread_id": message.get("threadId"),
        "from": normalized_headers.get("from"),
        "to": normalized_headers.get("to"),
        "subject": normalized_headers.get("subject"),
        "reply_to": normalized_headers.get("reply_to"),
        "return_path": normalized_headers.get("return_path"),
        "list_id": normalized_headers.get("list_id"),
        "authentication_results": normalized_headers.get("authentication_results"),
        "label_ids": list(message.get("labelIds") or []),
        "snippet": message.get("snippet"),
    }
