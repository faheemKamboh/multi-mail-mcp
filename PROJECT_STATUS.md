# Project status

Last updated: 2026-09-28

## Goal

Build a provider-agnostic mail assistant that can ingest mail read-only, normalize and classify messages, verify uncertain senders or claims using external research, propose actions with evidence, and only perform mailbox writes through explicit, tested controls.

## Current phase

**Phase 1: read-only core foundation, still using synthetic credential-free fixtures.**

The benchmark/qualification harness from Phase 0 is operational. Development proceeds through a bounded GitHub Actions worker/reviewer pipeline and a durable dependency queue. Real mailbox credentials and destructive actions remain out of scope.

## Current implementation status

Completed foundations:

- reproducible synthetic mail benchmark and deterministic CI;
- bounded coding worker -> deterministic verifier -> independent adversarial reviewer -> re-verification pipeline;
- trusted task manifests with editable-file allowlists and fixed tests;
- development companion scheduler with dependency-aware task selection and overlap protection;
- durable GitHub-state resolution for merged task PRs and the global failure circuit breaker;
- reviewed-branch publication fallback for repositories where GitHub Actions cannot create pull requests;
- synthetic Gmail-like message normalization merged into `main`;
- SPF/DKIM/DMARC authentication-evidence parsing merged into `main` and retained as a permanent CI regression;
- production Gmail-like message normalization implemented and covered by the fixed acceptance test;
- provider-neutral abstract read-only provider contract implemented;
- credential-free Gmail-style read adapter implemented around an injected client;
- test-launch inference routing primitives implemented for deterministic/local/protected/external-batch decisions;
- compact external-review batching implemented so multiple eligible mail-review jobs can share one normal model request;
- deterministic sensitivity gating prevents protected candidates from entering the ordinary external review batch;
- installable Python package boundary for private-cloud reuse;
- OpenAI-compatible JSON client suitable for a private local endpoint;
- OpenRouter free-router adapter with injectable credential-free test transport;
- strict local classification and external batch-review result validation, including exact per-message ID reconciliation.

Current bounded queue, in dependency order:

1. **in progress:** extract normalized sender identities;
2. choose an account-scoped sender stream key.

The production message normalizer, read-only provider contract, and credential-free Gmail adapter were completed directly in the V0.1 launch-core change and marked done in durable companion state so the development scheduler does not duplicate them.

### Qwen3-14B qualification evidence

The `authentication-results` task exhausted both allowed Qwen3-14B attempts. Both proposals produced the same case-sensitive `SPF=` regex while claiming case-insensitive behavior, and both were rejected by the fixed deterministic test. The task was then repaired through a maintainer PR, preserving the failed model evidence rather than treating it as a pass.

This is evidence against relying on Qwen3-14B as an unsupervised coding worker even for small bounded tasks. Continue collecting evidence on later tasks, but deterministic verification and retry limits remain mandatory.

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

## Known operational constraint

The repository currently prevents GitHub Actions from opening pull requests. A fully verified bounded run can still push its reviewed branch and finish successfully; the maintainer then opens the PR through an authorized GitHub connection. Unknown publication failures still fail hard.

## Test-launch scope

The V0.1 private-test boundary is frozen in `docs/TEST_LAUNCH_V0_1.md`. The launch remains read-only: classification, importance, action-needed indication, suggested labels, confidence, reason, and inference route are in scope; mailbox writes, billing, multi-user SaaS, extra production providers, and theme work are postponed.

The local-first routing direction is deterministic rules/cache -> small private model -> packed external review only for uncertain standard-sensitivity items. Protected uncertain items stay on a protected/human path.

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
- [x] Trusted task queue/orchestrator workflow added and exercised on synthetic work.
- [ ] Accumulate reproducible Qwen3-14B worker/reviewer evidence over additional bounded tasks.
- [ ] Decide whether Qwen3-14B remains viable as a bounded worker/reviewer candidate after repeated evidence.

### Phase 1 — read-only core

- [x] First provider-neutral normalized-message fixture path.
- [x] Parse internal authentication evidence from normalized mail.
- [ ] Normalize sender/reply/bounce/list identities.
- [ ] Add account-scoped sender stream/grouping keys.
- [x] Promote normalized-message behavior into the production source package.
- [x] Define the production-facing read-only provider interface.
- [x] Gmail-compatible read-only adapter with injected fixture/mock client first.
- [ ] Thread normalization and sender/domain identity extraction across provider fixtures.
- [ ] Sender clustering and profile cache.
- [x] Initial V0.1 classification schema, local classifier, and dry-run packed reviewer contracts.
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
