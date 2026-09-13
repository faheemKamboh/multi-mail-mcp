# multi-mail-mcp

Provider-agnostic mail intelligence core under active development.

The project is building a read-first mail assistant that can normalize messages from different providers, extract sender and authentication evidence, group sender streams per account, classify mail, and propose auditable actions. Gmail-compatible ingestion is the first adapter target, but provider-specific behavior stays behind adapters.

## Current phase

Phase 1 focuses on a credential-free, read-only core using synthetic fixtures and injected fake provider clients. Production mailbox credentials, private mailbox data, and destructive mailbox actions are intentionally excluded from the repository and current development loop.

Current dependency path:

```text
synthetic Gmail-like message
        |
        v
normalization
        |
        v
authentication evidence (SPF/DKIM/DMARC)
        |
        v
sender identities
        |
        v
account-scoped sender stream key
        |
        v
production normalizer
        |
        v
read-only provider contract
        |
        v
credential-free Gmail-style adapter
```

## Development model

The repository includes a bounded GitHub Actions development harness:

1. a local model proposes edits only to files allowed by a trusted task manifest;
2. deterministic fixed tests verify the proposal;
3. an independent adversarial reviewer evaluates the verified diff;
4. deterministic tests run again before publication;
5. reviewed changes are pushed for maintainer review and merge.

A durable companion scheduler advances dependency-ordered tasks while preventing overlapping agent runs and stopping after repeated unresolved failures. Autonomous merge remains disabled.

## Benchmarking and qualification

Synthetic email benchmarks remain an important subsystem. They are used to qualify local models and agent behavior on structured mail-processing tasks without exposing real mailbox data.

## Safety and privacy boundaries

- Synthetic fixtures only in the public repository.
- No OAuth tokens, cookies, credentials, or real mailbox content.
- Mailbox writes remain disabled during the read-only phase.
- External research tools provide evidence; they do not own mailbox access or make mailbox decisions.
- Provider-specific payloads are normalized behind adapter boundaries.
- Agent edits are constrained by trusted manifests and fixed deterministic tests.

See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) for the current queue and implementation status, and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the architecture direction.
