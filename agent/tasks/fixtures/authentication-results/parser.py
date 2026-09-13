from __future__ import annotations

import re


MECHANISMS = ("spf", "dkim", "dmarc")


def parse_authentication_results(value: str) -> dict[str, str]:
    """Extract bounded SPF/DKIM/DMARC verdicts from a synthetic header."""
    results: dict[str, str] = {}
    for mechanism in MECHANISMS:
        match = re.search(
            rf"\b{mechanism}\s*=\s*([A-Za-z]+)",
            value,
            flags=re.IGNORECASE,
        )
        results[mechanism] = match.group(1).lower() if match else "unknown"
    return results
