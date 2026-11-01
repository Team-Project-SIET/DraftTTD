---
title: "2026-11-01 D5 v2 Review Addendum"
type: project
status: addendum
updated: 2026-11-01
tags:
  - openttd
  - addendum
  - d5
  - evidence
---

# 2026-11-01 D5 v2 Review Addendum

Append-only addendum note, written 2026-11-01 from repository records on
branch `miles/fright-delivery`, HEAD `fee7459`. No existing file in this
knowledge tree was edited, moved, deleted or renamed. This file only records
what the reviewed design means for the *reference material* kept here; it is
not part of the application and authorizes nothing.

## What was reviewed

The locked D5 Freight Delivery v2 design decisions (Option B stronger
service proof: ≤ 32 protocol exchanges, 900 s, 60 economy days, one launch,
one connection, zero retries; the A1 after-save world `3748e00c…5420bd` at
£490,257; quote-first purchase ≤ £5,000; a pinned engine ID without
fallback; per-cycle `delivered == loaded == monitor_delta`) were independently
adversarially reviewed offline under three fresh-context reviewer workstreams
with cross-review. Verdict: **`DESIGN READY WITH CONDITIONS`**.
Full record: [docs/d5-freight-delivery-v2-design-review-2026-11-01.md](../../docs/d5-freight-delivery-v2-design-review-2026-11-01.md)
(evidence index E50; journal entry in `TASKS.md`; handoff paragraph in
`AI_HANDOFF.md`).

## Why this matters for the reference tree

- **This tree is not an engine-ID authority.** The 2026-11-01 review verified
  (offline, code-backed) that `OpenTTD-Knowledge/` contains **no default
  Temperate engine list and no numeric engine/cargo tables** — the Reference
  section holds API prose and links only
  (`07-Reference/External References.md`). Implementing a *pinned engine ID*
  for D6 requires provenance from an authority outside this tree.
- **The only repository-grounded engine facts are world-bound.** The legacy
  native road-vehicle lifecycle enumerated engine **123**: cargo 1
  (COAL-compatible), capacity 20, price **£4,429**, on seed-42 worlds
  (`docs/road-vehicle-lifecycle-proof.md`). Those facts do not transfer to
  the A1 seed-17 world; the pinned-ID reference stays **UNKNOWN** until a
  read-only native enumeration capture on the pinned runtime, or an
  external authoritative engine table, is acquired.
- **Route/world facts reused here remain provenance-pinned to attempts.**
  Run A = `45747..45743`, Run B = `45999→48047→48303→50095` plus corner
  `45743↔45999`, witness 31 tiles ending `50864, 50863, 50862`, station IDs
  pickup `0` / old bay 50351 `1` / A1 delivery bay `2`. These come from the
  D4/A1 consumed-attempt records (E35, E44), not from this tree's static
  pages, which were last reconciled 2026-10-26 and intentionally stay
  unreconciled history.
- **Reference-study implication for future work:** if engine tables or cargo
  compatibility maps are later added to this tree, they should arrive as new
  dated pages with explicit world/GRF/runtime applicability statements, never
  as edits to this addendum or to the earlier frozen pages.
