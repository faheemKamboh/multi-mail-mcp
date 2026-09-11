#!/usr/bin/env bash
set -euo pipefail
MODEL_KEY="${1:?model key required}"
OUT="results/${MODEL_KEY}"
python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install -r benchmark/requirements.txt
python3 benchmark/run_transformers_benchmark.py --model-key "$MODEL_KEY" --output-dir "$OUT"
python3 benchmark/score_results.py --fixtures benchmark/fixtures/email_cases.json --results "$OUT" --model "$MODEL_KEY"
