# Project status

Last updated: 2026-09-13

## Goal

Build a personal-first, provider-agnostic mail assistant that can ingest mail read-only, classify and cluster it, verify uncertain senders/claims using external research, propose labels/actions with evidence, and only later perform approved mailbox writes.

## Repository split

- `faheemKamboh/multi-mail-mcp` — active public foundation and synthetic benchmarks.
- `faheemKamboh/multi-mail-cloud` — private repository, intentionally parked for now.

## Current phase

**Phase 0: benchmark + development harness**

The active work is PR #3 (`benchmark-qualification`), which contains the broader synthetic email benchmark. PR #1 (`phase-0-model-benchmark`) is an older large-model qualification path and should be reviewed as a possible source of useful workflow pieces, then closed as superseded if nothing unique remains.

## Decisions locked so far

- Use GitHub Actions for reproducible development, tests, agent/model qualification, and later historical batch jobs.
- Do not use GitHub Actions as the permanent production mailbox runtime.
- Keep real mailbox data out of this public repository.
- Gmail is the first provider, but the application architecture must keep provider-specific code behind adapters.
- Agent Reach is a research/verification skill. It is not the mailbox decision authority and should receive only the minimum information needed for a check.
- Classification results should eventually include: decision, confidence, evidence, rule used, verifier, and timestamp.
- Start read-only/dry-run. Mailbox writes come only after review gates are proven.

## Definition of first usable state

Target engineering estimate: about 2–3 focused working days from a stable foundation.

Usable means one Gmail account can be processed in read-only mode to produce:

1. normalized email/thread records;
2. sender/domain clustering;
3. classification and importance;
4. sender/claim verification when needed;
5. suggested labels/actions;
6. confidence + evidence/audit output;
7. dry-run report with no mailbox mutation.

## Phase plan

### Phase 0 — current

- [x] Synthetic benchmark direction established.
- [x] Broader benchmark fixture set exists on PR #3.
- [x] Small-model candidates defined.
- [x] Prompt-injection/untrusted-email cases included.
- [ ] Add cheap deterministic CI separate from expensive model runs.
- [ ] Add manual GitHub Actions model benchmark workflow.
- [ ] Fix benchmark documentation drift.
- [ ] Run/collect qualification evidence and decide which model path is worth carrying forward.
- [ ] Resolve PR #1 vs PR #3 duplication.

### Phase 1 — read-only usable core

- [ ] Provider interface and normalized mail schema.
- [ ] Gmail read-only adapter.
- [ ] Thread normalization and sender/domain identity extraction.
- [ ] Sender clustering/profile cache.
- [ ] Classification policy and dry-run action proposal.
- [ ] Structured audit record.
- [ ] Synthetic + fixture-based integration tests in GHA.

### Phase 2 — verification intelligence

- [ ] Define verification request/result schema.
- [ ] Add Agent Reach adapter behind a generic verifier interface.
- [ ] Prefer official/public sources; track evidence and provenance.
- [ ] Separate sender identity verification from claims inside an email.
- [ ] Cache sender/company verification so repeated mail does not trigger repeated research.

### Phase 3 — controlled mailbox writes

- [ ] Human approval flow.
- [ ] Label creation/application behind explicit permission.
- [ ] Idempotency and rollback/recovery strategy.
- [ ] Reusable sender policy rules for future messages.

### Later

- Multi-account named agents.
- All-accounts coordinator.
- Persistent production service/database.
- Private/cloud product work after the personal-first workflow is proven.

## Immediate next actions

1. Finish CI/workflow foundation on PR #3.
2. Review benchmark scripts and correct obvious scoring/documentation issues.
3. Run the cheapest useful model qualification first; do not launch every expensive candidate blindly.
4. Record results and reject weak candidates conclusively.
5. Begin Phase-1 normalized schema/provider interface in a separate follow-up PR once the benchmark harness is stable.

## Handoff rule

A new session should read `AGENTS.md` and this file first, then inspect open PRs/issues and GHA results. Update this file after meaningful work so unfinished work is never silently abandoned.
