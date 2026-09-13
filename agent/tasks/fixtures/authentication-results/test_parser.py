from parser import parse_authentication_results


assert parse_authentication_results(
    "mx.example.test; SPF=pass smtp.mailfrom=example.test; dkim=PASS header.d=example.test; dmarc=pass header.from=example.test"
) == {
    "spf": "pass",
    "dkim": "pass",
    "dmarc": "pass",
}

assert parse_authentication_results(
    "mx.example.test; spf=fail; dkim=neutral; dmarc=fail"
) == {
    "spf": "fail",
    "dkim": "neutral",
    "dmarc": "fail",
}
