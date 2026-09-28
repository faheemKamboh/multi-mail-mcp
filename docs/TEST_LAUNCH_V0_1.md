# Test Launch V0.1

Status: scope frozen for private testing.

## Goal

Ship a usable read-only mail assistant quickly enough to expose real weaknesses. V0.1 is not a completeness milestone and must not expand into general SaaS/product polish before daily use begins.

## Required launch path

1. connect one to three Gmail accounts;
2. show All Inboxes and per-account views;
3. normalize messages behind a provider-neutral read-only contract;
4. process obvious cases with deterministic rules where possible;
5. use a small private/local model for routine classification;
6. accept high-confidence local decisions;
7. route uncertain, standard-sensitivity items into a packed external-review queue;
8. keep protected/sensitive uncertain items out of the ordinary external batch;
9. record route, confidence, reason, model/policy identity, and resulting suggestion;
10. keep Gmail write actions disabled during the first real-mail test.

## Inference routing

```text
message
  -> deterministic rules/cache
  -> local model when AI is needed
       -> high confidence: accept local suggestion
       -> low confidence + standard sensitivity: external review queue
       -> low confidence + protected sensitivity: protected/human review
```

External review uses normal packed requests: multiple compact review items are sent in one model request. Formal provider batch APIs are not required for V0.1.

Default external batch limits are implementation details, not product promises. The initial core supports item-count and payload-size bounds.

## Protected routing

The first deterministic gate treats financial, authentication/security, medical, legal, payroll/tax, configured protected sender domains, and similar signals as protected. This is a conservative routing hint, not a claim that all sensitive mail can be perfectly detected.

Protected uncertain mail must not enter the ordinary external batch.

## Launch classification output

V0.1 only needs:

- category;
- importance;
- requires-action indication;
- suggested label;
- confidence;
- short reason;
- inference route.

Suggested labels remain recommendations during the initial test; Gmail mutation is postponed.

## Explicitly postponed

- sending or replying;
- automatic delete/archive/trash;
- automatic Gmail label application;
- multi-user/tenant authentication;
- billing;
- Outlook/GoDaddy/other provider production integration;
- theme switching;
- exhaustive model benchmarking;
- enterprise administration/compliance features;
- autonomous destructive actions.

## Exit criterion

V0.1 is ready to move into daily testing when the owner can connect real Gmail accounts, read mail in the workspace, see useful classifications/recommendations and their route/reason, and use the product for several days without developer-console intervention.
