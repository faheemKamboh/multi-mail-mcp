from __future__ import annotations

from multi_mail.providers.base import ReadOnlyMailProvider


class GmailReadOnlyAdapter(ReadOnlyMailProvider):
    """Read-only Gmail adapter around an injected client.

    Authentication/client construction deliberately lives outside this class.
    This scaffold is intentionally incomplete for the bounded task worker.
    """

    def __init__(self, client, *, user_id: str = "me") -> None:
        self.client = client
        self.user_id = user_id
