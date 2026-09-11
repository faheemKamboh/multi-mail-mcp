#!/usr/bin/env python3
import argparse, json, statistics
from pathlib import Path

FIELDS = ("category", "importance", "reply_required", "lead", "recommended_action")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixtures", required=True)
    p.add_argument("--results", required=True)
    p.add_argument("--model", required=True)
    a = p.parse_args()
    fixtures = json.loads(Path(a.fixtures).read_text())
    out = Path(a.results)
    rows = []
    for case in fixtures:
        raw = (out / f"{case['id']}.txt").read_text().strip()
        checks = {}
        try:
            start, end = raw.find("{"), raw.rfind("}")
            parsed = json.loads(raw[start:end+1])
            checks["valid_json"] = True
            for field in FIELDS:
                checks[field] = parsed.get(field) == case["expected"][field]
            checks["draft_present"] = bool(str(parsed.get("draft", "") or "").strip()) == bool(case["expected"].get("draft_required", False))
            forbidden = [x.lower() for x in case["expected"].get("draft_forbidden_phrases", [])]
            draft = str(parsed.get("draft", "") or "").lower()
            checks["draft_direction"] = all(x not in draft for x in forbidden)
        except Exception:
            parsed = None
            checks["valid_json"] = False
        score = 100 * sum(bool(v) for v in checks.values()) / len(checks)
        rows.append({"id": case["id"], "score": round(score, 1), "checks": checks, "parsed": parsed, "raw": raw})
    timings = {}
    f = out / "timings-ms.csv"
    if f.exists():
        for line in f.read_text().splitlines():
            key, ms = line.rsplit(",", 1); timings[key] = int(ms)
    summary = {
        "model": a.model,
        "cases": len(rows),
        "mean_score": round(statistics.mean(r["score"] for r in rows), 1),
        "valid_json_rate": sum(r["checks"].get("valid_json", False) for r in rows) / len(rows),
        "mean_inference_ms": round(statistics.mean(timings.values())) if timings else None
    }
    (out / "scored.json").write_text(json.dumps({"summary": summary, "results": rows}, indent=2))
    (out / "report.md").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__": main()
