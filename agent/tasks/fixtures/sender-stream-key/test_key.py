from key import sender_stream_key


assert sender_stream_key("acct-a", {
    "from_address": "marketing@shop.test",
    "from_domain": "shop.test",
    "list_id": "deals.shop.test",
}) == {
    "account_id": "acct-a",
    "kind": "list_id",
    "value": "deals.shop.test",
}

assert sender_stream_key("acct-a", {
    "from_address": "orders@shop.test",
    "from_domain": "shop.test",
    "list_id": None,
}) == {
    "account_id": "acct-a",
    "kind": "from_address",
    "value": "orders@shop.test",
}

assert sender_stream_key("acct-b", {
    "from_address": None,
    "from_domain": "shop.test",
    "list_id": None,
}) == {
    "account_id": "acct-b",
    "kind": "from_domain",
    "value": "shop.test",
}

assert sender_stream_key("acct-b", {
    "from_address": None,
    "from_domain": None,
    "list_id": None,
}) is None

assert sender_stream_key("acct-b", {
    "from_address": "marketing@shop.test",
    "from_domain": "shop.test",
    "list_id": "deals.shop.test",
}) != sender_stream_key("acct-a", {
    "from_address": "marketing@shop.test",
    "from_domain": "shop.test",
    "list_id": "deals.shop.test",
})
