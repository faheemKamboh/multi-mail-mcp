#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:?usage: run_llama_benchmark.sh <hf-model:quant>}"
OUT_DIR="${2:-benchmark-results}"
PORT="${PORT:-8080}"
mkdir -p "$OUT_DIR"

SYSTEM_PROMPT="$(cat benchmark/prompts/system.txt)"

llama-server -hf "$MODEL" --host 127.0.0.1 --port "$PORT" >"$OUT_DIR/server.log" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null

jq -c '.[]' benchmark/fixtures/email_cases.json | while IFS= read -r case_json; do
  id="$(jq -r '.id' <<<"$case_json")"
  sender="$(jq -r '.from' <<<"$case_json")"
  subject="$(jq -r '.subject' <<<"$case_json")"
  thread="$(jq -r '.thread' <<<"$case_json")"
  user_text=$(printf 'Analyze this synthetic email/thread.\n\nFrom: %s\nSubject: %s\n\nThread:\n%s\n\n/no_think' "$sender" "$subject" "$thread")

  request=$(jq -n \
    --arg system "$SYSTEM_PROMPT" \
    --arg user "$user_text" \
    '{model:"local",temperature:0,max_tokens:220,messages:[{role:"system",content:$system},{role:"user",content:$user}]}' )

  started=$(date +%s%3N)
  curl -fsS "http://127.0.0.1:${PORT}/v1/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "$request" >"$OUT_DIR/${id}.response.json"
  finished=$(date +%s%3N)

  jq -r '.choices[0].message.content // ""' "$OUT_DIR/${id}.response.json" >"$OUT_DIR/${id}.txt"
  printf '%s,%s\n' "$id" "$((finished-started))" >>"$OUT_DIR/timings-ms.csv"
done

python3 benchmark/score_results.py \
  --fixtures benchmark/fixtures/email_cases.json \
  --results "$OUT_DIR" \
  --model "$MODEL"
