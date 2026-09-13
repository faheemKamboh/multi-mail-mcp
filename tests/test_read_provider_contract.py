from __future__ import annotations

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from multi_mail.providers.base import ReadOnlyMailProvider


assert inspect.isabstract(ReadOnlyMailProvider)

try:
    ReadOnlyMailProvider()
except TypeError:
    pass
else:
    raise AssertionError("read-only provider contract must not be directly instantiable")


class FakeProvider(ReadOnlyMailProvider):
    def list_message_refs(self, *, page_token: str | None = None):
        return ([{"provider_message_id": "m1", "thread_id": "t1"}], None)

    def get_message(self, provider_message_id: str):
        return {"provider_message_id": provider_message_id}


provider = FakeProvider()
refs, next_page = provider.list_message_refs()
assert refs == [{"provider_message_id": "m1", "thread_id": "t1"}]
assert next_page is None
assert provider.get_message("m1") == {"provider_message_id": "m1"}

# The Phase 1 provider boundary is intentionally read-only.
for forbidden in ("send_message", "delete_message", "apply_label", "archive_message", "trash_message"):
    assert not hasattr(ReadOnlyMailProvider, forbidden), forbidden
