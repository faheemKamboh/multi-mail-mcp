# Autonomous development loop

This project can use GitHub Actions as a bounded development and review harness for well-defined tasks. The goal is reproducible assistance, not unrestricted repository autonomy.

## Design principles

- Development must work against synthetic fixtures and deterministic tests; real mailbox credentials are not required.
- GitHub Issues are the task queue. Only explicitly eligible tasks may be picked up by an agent workflow.
- A worker and reviewer must run independently. The reviewer must not inherit the worker's conversation or hidden state.
- Runners exchange durable repository state, pull-request diffs, and artifacts rather than depending on a live runner-to-runner HTTP service.
- Deterministic tests remain authoritative where a requirement can be expressed deterministically.
- Agent output is untrusted until it passes validation and independent review.
- No autonomous merge is enabled during qualification.

## Task lifecycle

```text
Issue / task specification
        |
        v
Eligibility gate
(owner-approved + bounded scope)
        |
        v
Worker runner
        |
        +--> inspect allowed repository context
        +--> propose patch
        +--> apply patch on task branch
        +--> run deterministic tests
        |
        v
Pull request + worker artifact
        |
        v
Independent reviewer runner
        |
        +--> read task specification
        +--> read PR diff
        +--> run tests from a clean checkout
        +--> adversarially inspect behavior/security
        |
        v
Reviewer verdict
  |                 |
  | pass            | changes required
  v                 v
ready-for-review   correction task / next iteration
```

## Issue eligibility

The public repository must not execute arbitrary issue text as privileged instructions. An autonomous task is eligible only when all of the following are true:

1. the task is explicitly marked for agent execution by the repository owner or another trusted maintainer;
2. the requested changes are confined to the public repository;
3. the task does not request credentials, secrets, mailbox data, production access, or external account actions;
4. the task identifies acceptance criteria and deterministic verification where practical;
5. the task does not authorize workflow/security-policy changes unless that is the task's explicit bounded purpose.

The first implementation should use a dedicated marker such as an `agent-ready` label or a checked-in task manifest. Until the authorization gate is proven, workflows should be manually dispatchable or run against checked-in qualification tasks only.

## Worker contract

A worker receives a bounded task plus selected repository context. It should return a machine-readable proposal containing:

- summary of intended changes;
- files to create/update/delete;
- patch or complete file content;
- tests it expects to pass;
- assumptions or unresolved risks.

The harness, not the model, applies the change. The harness rejects proposals that escape the allowed paths, are unparsable, modify protected files without permission, or fail deterministic tests.

## Reviewer contract

The reviewer receives the task specification and resulting diff, not the worker's reasoning. It independently evaluates:

- acceptance-criteria coverage;
- test adequacy and regressions;
- prompt-injection or untrusted-input boundaries;
- accidental credential/private-data handling;
- public-repository suitability;
- unnecessary scope expansion;
- whether the patch should pass, fail, or require changes.

Reviewer output must be structured and preserved as an artifact or pull-request review.

## Model qualification

A model that performs email classification well is not automatically a good coding agent. Coding-agent qualification should therefore have a separate synthetic/repository-local suite covering tasks such as:

- identify and fix a schema/config mismatch;
- add or repair a deterministic validation rule;
- update stale documentation from repository facts;
- implement a small adapter behind an existing interface;
- detect a security boundary violation in a proposed patch;
- review a deliberately flawed patch and explain the blocking defect.

Qwen3 14B Q4 is an initial local candidate, not a committed dependency. It must meet quality, latency, memory, disk, and reliability thresholds before it is allowed to create task branches automatically.

## Continuity without an interactive session

Once the workflows are merged to the default branch, work can continue from GitHub events or a bounded schedule. A task can progress through worker and reviewer stages without an interactive chat being present. Durable state lives in Issues, branches, PRs, artifacts, and test results.

This does not make an interactive assistant session persistent. It moves repeatable development work into GitHub's event-driven execution environment, where each run can recover its complete state from GitHub.

## Initial safety gates

During qualification:

- no production credentials;
- no real email data;
- no autonomous merge;
- no write access to unrelated repositories;
- no inbound public model API;
- no execution of arbitrary third-party issue/PR instructions with privileged tokens;
- bounded model context and runtime;
- deterministic tests before reviewer approval.

These gates can be relaxed only after the corresponding behavior is tested and documented.
