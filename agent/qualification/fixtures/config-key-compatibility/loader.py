import json
from pathlib import Path


def describe_model():
    entry = json.loads(Path("manifest.json").read_text())
    return f"{entry['repo_id']}:{entry['filename']}"


if __name__ == "__main__":
    print(describe_model())
