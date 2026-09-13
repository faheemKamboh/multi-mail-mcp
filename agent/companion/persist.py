from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", required=True)
    parser.add_argument("--state", default="agent/state/current.json")
    args = parser.parse_args()
    record = json.loads(Path(args.record).read_text())
    Path(args.state).write_text(json.dumps(record["state"], indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
