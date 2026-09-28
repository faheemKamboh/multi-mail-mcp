from __future__ import annotations

from abc import ABC, abstractmethod


class ReadOnlyMailProvider(ABC):
    """Provider-neutral mailbox read boundary.

    Authentication/client construction belongs outside this contract.
    Mailbox mutation methods are deliberately excluded.
    """

    @abstractmethod
    def list_message_refs(self, *, page_token: str | None = None) -> tuple[list[dict], str | None]:
        """Return provider message/thread references plus the next page token."""

    @abstractmethod
    def get_message(self, provider_message_id: str) -> dict:
        """Return one normalized provider-neutral message."""
