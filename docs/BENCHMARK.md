# Email model benchmark

This repository compares small language models on synthetic email-processing tasks.

## Qualification matrix

The current pass includes deliberately weak/small baselines and larger 3B-4B candidates so model size can be compared against quality and CPU cost.

## Qualification suite

The first pass uses 10 synthetic cases covering leads, newsletters, invoices, appointments, existing clients, personal mail, dormant-client opportunities, multi-message threads, embedded instructions, and obvious spam.

Each candidate is evaluated on structured JSON output, classification, reply decisions, lead decisions, recommended actions, draft presence, draft direction, and inference time.

Models that perform well in this qualification pass can advance to a 50+ case suite. Models that fail basic structure, routing, or draft-direction checks should be rejected before deeper testing.

Only synthetic data is used in this repository.
