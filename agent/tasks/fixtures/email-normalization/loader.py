from __future__ import annotations


def normalize_message(message: dict) -> dict:
    """Normalize a Gmail-like synthetic message into the provider-neutral shape."""
    headers = {header["name"].lower(): header["value"] for header in message["payload"]["headers"]}
    
    return {
        "provider_message_id": message.get("id"),
        "thread_id": message.get("threadId"),
        "from": headers.get("from"),
        "to": headers.get("to"),
        "subject": headers.get("subject"),
        "reply_to": headers.get("reply-to"),
        "return_path": headers.get("return-path"),
        "list_id": headers.get("list-id"),
        "authentication_results": headers.get("authentication-results"),
        "label_ids": message.get("labelIds"),
        "snippet": message.get("snippet")
    }