from __future__ import annotations

import json
from pathlib import Path

from loader import normalize_message


fixture = json.loads((Path(__file__).parent / "message.json").read_text())
result = normalize_message(fixture)

assert result == {
    "provider_message_id": "msg-001",
    "thread_id": "thread-007",
    "from": "Billing Example <billing@example.test>",
    "to": "user@example.test",
    "subject": "September invoice",
    "reply_to": "support@example.test",
    "return_path": "bounce@example.test",
    "list_id": "billing.example.test",
    "authentication_results": "mx.example.test; spf=pass; dkim=pass; dmarc=pass",
    "label_ids": ["INBOX", "CATEGORY_UPDATES"],
    "snippet": "Your September invoice is ready."
}
