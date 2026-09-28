# Model Runtime V0.1

## Purpose

Keep inference replaceable and testable while the private launch uses a small
self-hosted model for routine mail and OpenRouter only as a selective reviewer.

Both paths use the same small JSON-task boundary. Neither model client owns
mailbox credentials or mailbox-write permissions.

## Local/private model

The reusable client expects an OpenAI-compatible chat-completions endpoint:

- base URL: configured by the private runtime;
- model slug/name: configured by the private runtime;
- API key: optional for a private endpoint;
- JSON response mode: optional because very small local servers/models may not
  implement it consistently.

The intended Oracle deployment can therefore use a compatible server such as a
llama.cpp-style OpenAI endpoint without changing mail-routing code.

## External reviewer

The initial external adapter targets OpenRouter's OpenAI-compatible API:

- base URL: `https://openrouter.ai/api/v1`;
- chat-completions path: `/chat/completions`;
- initial model: `openrouter/free`;
- bearer API key required;
- JSON response mode requested;
- `provider.zdr=true` is enforced for every request;
- `provider.data_collection="deny"` is enforced for every request;
- optional site URL/title headers are supported.

The product must treat this as a replaceable adapter, not as a permanent free
infrastructure guarantee.

## Data minimization

The external reviewer receives only compact review records produced by the
routing layer. Protected messages are rejected before ordinary external batch
construction. The first launch sends sender, subject, bounded excerpt, local
classification/confidence/reason, and the requested review fields.

No OAuth token, mailbox credential, session cookie, or provider client is part
of the model request contract.

## Model-output safety

Email content is untrusted data. System prompts explicitly forbid following
instructions found inside messages.

Model output is accepted only after deterministic validation:

- category is from the launch allowlist;
- importance is low/normal/high;
- requires_action is boolean;
- confidence is numeric in [0, 1];
- batch results must contain each requested internal ID exactly once;
- unknown, missing, or duplicate IDs fail the whole review operation.

## Credentials

Public CI uses fake HTTP transports and no model API keys.

The private deployment will supply local model URLs/model names and OpenRouter
credentials through runtime environment variables only.
