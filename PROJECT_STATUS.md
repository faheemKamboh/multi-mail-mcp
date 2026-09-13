# Project status

Last updated: 2026-09-13

## Goal

Build a provider-agnostic mail assistant that can ingest mail read-only, normalize and classify messages, verify uncertain senders or claims using external research, propose actions with evidence, and only perform mailbox writes through explicit, tested controls.

## Current phase

**Phase 0: benchmark + development harness**

Current work focuses on reproducible synthetic benchmarks, deterministic validation, model/agent qualification, and GitHub Actions-based testing.

## Public project decisions

- Use GitHub Actions for reproducible development, tests, qualification runs, and bounded batch jobs.
- Do not use GitHub Actions as the permanent production mailbox runtime.
- Development must not depend on real mailbox credentials or production accounts.
- Use synthetic fixtures, mocks, fake provider responses, and generated mailbox histories until staging/production integration.
- Keep real mailbox content, credentials, tokens, cookies, and account secrets out of the repository.
- Keep provider-specific behavior behind adapters.
- External research tools are verification capabilities; they provide evidence but do not decide or perform mailbox actions.
- Classification and action proposals should be auditable with structured decision, confidence, evidence, rule, verifier, and timestamp fields.
- Prompts, routing policies, thresholds, and verifier behavior are versioned/tested artifacts rather than informal configuration.
- Default to read-only and dry-run behavior until write paths are explicitly enabled and tested.
- Coding workers propose structured edits; the harness controls editable paths, applies changes, and runs fixed deterministic tests.
- Worker and reviewer qualification remain independent; reviewer input is task/diff/test evidence rather than worker reasoning.
- Do not enable autonomous merge while the agent development loop is still being qualified.

## Qualification strategy

GitHub Actions should exercise agents/models against a synthetic mailbox corpus that includes:

- ordinary transactional and promotional mail;
- leads, clients, receipts, security alerts, newsletters, and low-value noise;
- sender/domain clusters and repeated historical patterns;
- ambiguous messages that require abstention or review;
- multilingual and Roman-Urdu cases;
- malformed content and missing metadata;
- prompt injection, adversarial instructions, and untrusted links/content;
- verification requests with synthetic/replayable evidence adapters.

Email-processing qualification and coding-agent qualification are separate. Coding workers are tested against intentionally broken synthetic mini-repositories with fixed acceptance tests. Independent reviewers are tested on correct patches as well as security-boundary omissions, test tampering, and secret/environment exposure.

Each qualification run should produce reproducible scoring and enough artifacts to compare model, prompt, policy, and threshold changes. A model or prompt change should only be promoted when it improves the agreed benchmark without unacceptable regressions.

## Roadmap

### Phase 0 — benchmark and qualification

- [x] Synthetic benchmark direction established.
- [x] Broad fixture coverage added.
- [x] Prompt-injection and untrusted-input cases included.
- [x] Credential-free development/test policy documented.
- [x] Cheap deterministic CI separated from model inference.
- [x] Manually/event-triggered bounded model/agent qualification workflows added.
- [x] Benchmark documentation aligned with the current qualification suites.
- [x] Coding-worker and independent-reviewer qualification harnesses added.
- [x] Duplicate older benchmark PR resolved as superseded.
- [ ] Add repeated practice/evaluation runs for prompt and policy refinement.
- [ ] Record reproducible Qwen3 14B email/coding/reviewer qualification evidence.
- [ ] Decide whether Qwen3 14B is viable as a bounded worker/reviewer candidate.
- [ ] Add the first trusted task-queue/orchestrator workflow after qualification gates pass.

### Phase 1 — read-only core

- [ ] Provider interface and normalized mail schema.
- [ ] Gmail-compatible read-only adapter with fixture/mock implementation first.
- [ ] Thread normalization and sender/domain identity extraction.
- [ ] Sender clustering and profile cache.
- [ ] Classification policy and dry-run action proposal.
- [ ] Structured audit records.
- [ ] Synthetic and fixture-based integration tests in GitHub Actions.

### Phase 2 — verification intelligence

- [ ] Define verification request/result schemas.
- [ ] Add a generic verifier interface and research-tool adapter.
- [ ] Provide fake/replay verifier implementations for deterministic tests.
- [ ] Prefer official/public sources and record evidence provenance.
- [ ] Separate sender identity verification from message-specific claim verification.
- [ ] Cache sender/company verification to avoid unnecessary repeated research.

### Phase 3 — controlled mailbox writes

- [ ] Human approval flow.
- [ ] Label creation and application behind explicit permission.
- [ ] Idempotency and rollback/recovery strategy.
- [ ] Reusable sender policies for future messages.

## Contribution rule

Keep public documentation focused on reusable project behavior, architecture, benchmarks, and reproducible implementation status. Do not include private account data, credentials, personal mailbox details, or unrelated private project context.
