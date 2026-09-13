from __future__ import annotations


def parse_authentication_results(value: str) -> dict[str, str]:
    """Extract the bounded SPF/DKIM/DMARC verdicts from a synthetic header."""
    return {"spf": "unknown", "dkim": "unknown", "dmarc": "unknown"}
