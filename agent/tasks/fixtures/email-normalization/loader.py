from __future__ import annotations


def normalize_message(message: dict) -> dict:
    """Normalize a Gmail-like synthetic message into the provider-neutral shape.

    This scaffold is intentionally incomplete. The bounded development worker
    repairs it under the trusted task manifest and fixed test.
    """
    return {
        "provider_message_id": message.get("id"),
        "thread_id": message.get("threadId"),
    }
