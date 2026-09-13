from __future__ import annotations


def sender_stream_key(account_id: str, identity: dict) -> dict | None:
    """Return a stable account-scoped sender stream key.

    This scaffold is intentionally incomplete. The bounded development worker
    repairs it under the trusted task manifest and fixed test.
    """
    return None
