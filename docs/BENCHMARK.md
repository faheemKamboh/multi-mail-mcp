# Model qualification

This repository uses synthetic fixtures to qualify models before they are allowed to participate in mail processing or development workflows. Real mailbox data and production credentials are not required for qualification.

## Email-processing qualification

The email suite covers a broad set of synthetic messages and threads, including leads, existing clients, finance, newsletters, appointments, personal mail, spam, multilingual/Roman-Urdu content, ambiguous routing, repeated-thread context, and adversarial/prompt-injection cases.

Candidates are evaluated on:

- valid structured JSON;
- category and importance;
- reply and lead decisions;
- recommended action;
- refusal to follow untrusted instructions embedded in email content;
- draft presence and draft direction;
- inference time and runtime viability.

`benchmark/models.json` contains smaller baseline candidates. `benchmark/large_models.json` contains quantized GGUF candidates, including Qwen3 14B Q4. Large-model runs are bounded and manually/event triggered so model download and CPU inference are not part of cheap deterministic CI.

The weighted scorer gives explicit credit to the untrusted-input boundary. A model that follows instructions embedded in an email cannot receive a perfect result simply by classifying the message correctly.

## Coding-worker qualification

Email classification quality does not imply coding-agent quality. Coding workers are qualified separately against intentionally broken synthetic mini-repositories under `agent/qualification/fixtures/`.

The worker receives a bounded task, selected repository context, an explicit editable-file allowlist, and a fixed test command. It must return a structured proposal containing complete replacement file content. The harness, not the model, applies proposed changes in a temporary workspace and runs the fixed tests.

Initial tasks exercise configuration/schema mismatch repair and security-boundary scoring. More tasks should be added before a model is allowed to create real task branches automatically.

## Reviewer qualification

The reviewer is qualified independently from the worker. It receives only the task, candidate diff, and reported test evidence; it does not inherit the worker's reasoning or hidden state.

Initial review cases require the model to approve a correct bounded fix and reject patches that omit a security boundary, weaken/tamper with tests, or expose environment values that may contain secrets.

## Deterministic gate

`.github/workflows/ci.yml` performs cheap validation on every pull request. It validates fixture/model/task manifests and compiles the benchmark and qualification harnesses without downloading an LLM.

Model workflows run separately and preserve reports as GitHub Actions artifacts. A model is not promoted merely because it produced plausible output; measured task success, reviewer accuracy, latency, memory/disk behavior, and repeatability all matter.

Only synthetic data is used in the public qualification suites.
