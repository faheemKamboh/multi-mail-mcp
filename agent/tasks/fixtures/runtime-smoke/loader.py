import json
from pathlib import Path


def describe_model():
    entry = json.loads(Path(__file__).with_name("manifest.json").read_text())
    return f"{entry['repo_id']}:{entry['filename']}"
