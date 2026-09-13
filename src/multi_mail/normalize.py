from __future__ import annotations


def normalize_provider_message(message: dict) -> dict:
    """Convert a Gmail-like provider message into the fixed provider-neutral shape.

    This production scaffold is intentionally incomplete. The bounded worker
    repairs it under a trusted manifest and fixed acceptance test.
    """
    return {
        "provider_message_id": message.get("id"),
        "thread_id": message.get("threadId"),
    }
