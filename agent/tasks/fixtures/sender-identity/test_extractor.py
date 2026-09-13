from extractor import extract_sender_identity


assert extract_sender_identity({
    "from": "Billing Example <Billing@Example.TEST>",
    "reply_to": "Support <support@example.test>",
    "return_path": "<bounce@example.test>",
    "list_id": "Billing Updates <billing.example.test>",
}) == {
    "from_address": "billing@example.test",
    "from_domain": "example.test",
    "reply_to_address": "support@example.test",
    "reply_to_domain": "example.test",
    "return_path_address": "bounce@example.test",
    "return_path_domain": "example.test",
    "list_id": "billing.example.test",
}

assert extract_sender_identity({
    "from": "person@sub.example.test",
    "reply_to": None,
    "return_path": None,
    "list_id": None,
}) == {
    "from_address": "person@sub.example.test",
    "from_domain": "sub.example.test",
    "reply_to_address": None,
    "reply_to_domain": None,
    "return_path_address": None,
    "return_path_domain": None,
    "list_id": None,
}
