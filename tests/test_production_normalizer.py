from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from multi_mail.normalize import normalize_provider_message


MESSAGE = {
    "id": "msg-prod-001",
    "threadId": "thread-prod-007",
    "labelIds": ["INBOX", "CATEGORY_UPDATES"],
    "snippet": "Your September invoice is ready.",
    "payload": {
        "headers": [
            {"name": "from", "value": "Billing Example <Billing@Example.Test>"},
            {"name": "TO", "value": "user@example.test"},
            {"name": "Subject", "value": "September invoice"},
            {"name": "Reply-To", "value": "support@example.test"},
            {"name": "Return-Path", "value": "bounce@example.test"},
            {"name": "List-ID", "value": "billing.example.test"},
            {
                "name": "Authentication-Results",
                "value": "mx.example.test; spf=pass; dkim=pass; dmarc=pass",
            },
        ]
    },
}


assert normalize_provider_message(MESSAGE) == {
    "provider_message_id": "msg-prod-001",
    "thread_id": "thread-prod-007",
    "from": "Billing Example <Billing@Example.Test>",
    "to": "user@example.test",
    "subject": "September invoice",
    "reply_to": "support@example.test",
    "return_path": "bounce@example.test",
    "list_id": "billing.example.test",
    "authentication_results": "mx.example.test; spf=pass; dkim=pass; dmarc=pass",
    "label_ids": ["INBOX", "CATEGORY_UPDATES"],
    "snippet": "Your September invoice is ready.",
}

# Missing optional headers stay absent/null rather than being guessed from From.
minimal = {
    "id": "msg-prod-002",
    "threadId": "thread-prod-008",
    "labelIds": [],
    "snippet": "Hello",
    "payload": {"headers": [{"name": "From", "value": "person@example.test"}]},
}
assert normalize_provider_message(minimal) == {
    "provider_message_id": "msg-prod-002",
    "thread_id": "thread-prod-008",
    "from": "person@example.test",
    "to": None,
    "subject": None,
    "reply_to": None,
    "return_path": None,
    "list_id": None,
    "authentication_results": None,
    "label_ids": [],
    "snippet": "Hello",
}
