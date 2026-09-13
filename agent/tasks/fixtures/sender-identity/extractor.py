from __future__ import annotations


def extract_sender_identity(message: dict) -> dict:
    """Extract sender-related identities from a normalized message.

    This scaffold is intentionally incomplete. The bounded development worker
    repairs it under the trusted task manifest and fixed test.
    """
    return {
        "from_address": message.get("from"),
    }
