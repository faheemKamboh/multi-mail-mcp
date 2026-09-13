# Architecture direction

## Principle

Keep mailbox access, classification, and external research as separate capabilities.

```text
Mail provider
    |
    v
Provider adapter
    |
    v
Normalizer -> thread/sender identity -> sender profile cache
    |
    v
Policy/classification engine
    |
    +------ enough confidence ------> dry-run action proposal
    |
    +------ verification needed ----> verifier interface
                                         |
                                         +-> Agent Reach adapter
                                         +-> future verifier adapters
                                              |
                                              v
                                      evidence/result
                                         |
                                         v
                               policy/classification engine
                                         |
                                         v
                               audited dry-run proposal
```

## Mail provider boundary

The core should not depend directly on Gmail-specific shapes. A provider adapter converts provider data to a normalized internal representation. Gmail is first; future providers can implement the same boundary.

## Verification boundary

The verifier receives a narrowly scoped request such as sender domain, company name, URL, or a specific claim. It should receive only the data required for that check.

The verifier returns evidence; it does not perform mailbox actions.

Suggested result shape:

```json
{
  "status": "verified|unverified|conflicting|insufficient",
  "confidence": 0.0,
  "evidence": [],
  "sources": [],
  "checked_at": "timestamp"
}
```

## Decision and audit boundary

Every proposed action should eventually be explainable by a structured record:

```json
{
  "decision": "label|archive|reply|review|ignore",
  "confidence": 0.0,
  "evidence": [],
  "rule_used": "identifier",
  "verifier": "none|agent-reach|other",
  "timestamp": "timestamp"
}
```

## Historical mailbox strategy

Do not investigate every historical email independently. Extract sender/domain/list identities, cluster them, verify or profile a sender once where possible, and apply that learned profile to matching historical messages. Claims specific to one message remain separate verification tasks.

## GitHub Actions role

GHA is appropriate for deterministic tests, synthetic model qualification, adversarial evaluation, and bounded historical batch jobs. The production mailbox runtime should eventually be persistent infrastructure rather than an Actions workflow.
