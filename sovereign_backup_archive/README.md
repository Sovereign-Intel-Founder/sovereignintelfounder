# Sovereign Seed Commons

## A utility mesh for ephemeral AI research cells

Sovereign Seed Commons is a **Git-native coordination layer** for independent, temporary research cells.

A cell can run on a server, workstation, container, or other authorized environment. It receives one bounded objective, performs the work locally, produces verifiable evidence, and returns the result through a branch and pull request.

GitHub provides the durable layer for:

- project state;
- identity and lineage;
- experiment definitions;
- evidence manifests;
- review history;
- governance;
- accepted changes.

The compute cell is temporary. The evidence and history are durable.

> **Temporary compute performs the work. Git preserves the lineage. Pull requests control what becomes active.**

---

## Why this exists

Many distributed and agentic systems make it difficult to answer basic questions:

- What code ran?
- Which version ran it?
- What task was it given?
- What data or configuration did it use?
- What result did it produce?
- Can another participant reproduce the result?
- Who reviewed the change?
- Why was the result accepted or rejected?

Sovereign Seed Commons treats those questions as part of the protocol rather than as afterthoughts.

The goal is to create a transparent utility layer for collaborative experimentation, reproducibility, and governed software evolution.

---

## The cell model

A cell is an **authorized, ephemeral execution environment**.

It is not a permanent daemon, server, or background service.

A typical cell lifecycle is:

```text
opt in
  ↓
obtain a bounded objective
  ↓
verify repository state and lineage
  ↓
run one controlled experiment
  ↓
generate evidence
  ↓
create a branch
  ↓
submit a pull request
  ↓
terminate
