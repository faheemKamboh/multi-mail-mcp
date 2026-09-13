import json
from pathlib import Path


FIELDS = ("category", "reply_required")


def score():
    case = json.loads(Path("case.json").read_text())
    expected = case["expected"]
    actual = case["actual"]
    checks = {field: actual.get(field) == expected.get(field) for field in FIELDS}
    return sum(checks.values()) / len(checks), checks


if __name__ == "__main__":
    print(score())
