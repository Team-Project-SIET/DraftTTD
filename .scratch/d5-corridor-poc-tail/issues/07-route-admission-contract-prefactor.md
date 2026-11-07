# 07: Route-admission contract parameterization (prefactor, expand-only)

**What to build:** the "make the second route easy" prefactor — the corridor
attempt contract (schedule construction, plan derivation, pin-table
composition, funds-model wiring) parameterized so the corridor route of
record is its default instance chosen at composition time, exactly the way
the survey/extension families already version their schedules. Expansion
only: the corridor-1 contract bytes of record keep validating untouched
(the existing suites stay green unmodified in their semantics), no staging
or candidate action occurs, and the next round's staged composition still
derives the identical default composition at pin-for-pin equality. Competing
route admission itself belongs to ticket 08.

**Blocked by:** None (can start immediately; independent of the round-3
ladder tickets, so it can run in parallel with tickets 01–06).

**Status:** done (2026-11-05; commit `e177d03`, merged to
`miles/fright-delivery` by `26568af`)

- [x] The parameterized contract exposes the corridor route of record as the
      versioned default (v1 bytes and digests of record unchanged when built
      with the default binding)
- [x] Expansion follows the family versioning precedent: version selector in
      the contract module, versioned schedule/plan derivations, prior
      versions byte-preserved and still replay-verified
- [x] Every existing suite passes without semantic edits — the default
      composition digest and schedule digests reproduce exactly
- [x] New suite coverage asserts re-binding: a non-default route binding
      derives its own consistent schedule, plan digests, pin table and
      funds-model wiring, and refuses cross-version composition drift
- [x] No candidate lifecycle action of any kind inside this ticket: no
      staging, no signing, no claim, no launch, no artifacts write
- [x] `git diff --check` clean; `CONTEXT.md` pin intact; focused-suites +
      lint/type results recorded in the row; no commit/push
