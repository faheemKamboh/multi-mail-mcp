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
- Keep real mailbox content, credentials, tokens, cookies, and account secrets out of the repository.
- Keep provider-specific behavior behind adapters.
- External research tools are verification capabilities; they provide evidence but do not decide or perform mailbox actions.
- Classification and action proposals should be auditable with structured decision, confidence, evidence, rule, verifier, and timestamp fields.
- Default to read-only and dry-run behavior until write paths are explicitly enabled and tested.

## Roadmap

### Phase 0 — benchmark and qualification

- [x] Synthetic benchmark direction established.
- [x] Broad fixture coverage added.
- [x] Prompt-injection and untrusted-input cases included.
- [ ] Add cheap deterministic CI separate from model inference.
- [ ] Add a manually triggered model benchmark workflow.
- [ ] Keep benchmark documentation aligned with the fixture suite.
- [ ] Record reproducible qualification evidence before selecting a model path.
- [ ] Resolve duplication between benchmark implementations.

### Phase 1 — read-only core

- [ ] Provider interface and normalized mail schema.
- [ ] Gmail read-only adapter.
- [ ] Thread normalization and sender/domain identity extraction.
- [ ] Sender clustering and profile cache.
- [ ] Classification policy and dry-run action proposal.
- [ ] Structured audit records.
- [ ] Synthetic and fixture-based integration tests in GitHub Actions.

### Phase 2 — verification intelligence

- [ ] Define verification request/result schemas.
- [ ] Add a generic verifier interface and research-tool adapter.
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
