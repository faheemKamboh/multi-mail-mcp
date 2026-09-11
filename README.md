# multi-mail-mcp

Personal-first experimentation around a multi-account Gmail assistant.

## Current phase

This repository is **not** building a production SaaS. The immediate goal is to determine whether small, inexpensive/open models are good enough for the owner's real Gmail workflows before implementing Gmail OAuth, UI, or deployment.

Phase 0 therefore focuses on a reproducible GitHub Actions benchmark using synthetic email fixtures. Real Gmail data must not be used in the benchmark.

## Phase 0 success criteria

A candidate model should be able to reliably:

- classify email intent and importance;
- identify whether a reply is required;
- detect plausible client/lead opportunities;
- summarize multi-message threads;
- produce safe draft replies;
- choose the correct tool/action without inventing actions;
- resist instructions embedded inside untrusted email content;
- return machine-readable structured output consistently.

See `docs/BENCHMARK.md` once the benchmark foundation lands.
