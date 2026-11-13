# Proposal — E154 attempt-3 root-cause documentation correction (2026-11-08)

**Status: PROPOSED, NOT APPLIED.** This file only. It corrects the
interpretation of sealed Attempt 3 that the E154-era records wrote; it does
not touch `artifacts/` (sealed bytes stay untouched, read-only), it does not
change any terminal status, it does not claim Attempt 3 succeeded, and it
does not close Ticket-05 or Phase C. FD-C-2 stays `INCOMPLETE_EVIDENCE`.

Application of this proposal is an append-only amendment: each affected
record keeps its original text and gains a dated correction note referencing
this proposal, under whatever append discipline that record requires
(`CONTEXT.md` header rules do not apply to these files).

## What the sealed evidence actually says (re-derived 2026-11-08, read-only)

Run dir of record (sealed, read-only):
`artifacts/demos/playable-demo-f4a9e00063814bb381af2903fb4a5a88`.

- Root `result.json`: `status=FAILED`, `error="TimeoutError: "`,
  `launches=1`, `connections=2`, `failure_save_error=None`.
- Sealed `PRELAUNCH.json`: `budgets.total_seconds=2400` (not 1800),
  `loop_cycles=2`.
- Root `loop-cycle-2/planning-diagnostic.json`: `status=FAILED`,
  `error="TimeoutError: "`, `capture_requests_attempted=0`,
  `pair_checks=146`.
- `loop-cycle-2/random-generation-request.json` exists (124 bytes, sha256
  `519e626b…afd1`, byte-identical to `loop-cycle-1`'s) and NO
  `random-generation-response.json` exists in cycle 2; cycle 1's response
  exists. Cargo/wire reaction: the request was sent and no result ever
  arrived.
- Cycle 2's qualification session had completed
  (`qualification-session.json`: `phase=COMPLETED`, `failure=None`) before
  the failure: the attempt reached planning, not qualification.

## The corrected root cause

The failure is the **cross-cycle planning request-ID collision in the
GameScript `planner_used` deduplication guard** (`planner.nut:34`, staged
`network-parent.nut:34`):

1. One GameScript instance survives both AdminPort connections
   (per-cycle reconnect reuses it); `planner_used` persists across cycles.
2. Cycle 1 sent `request_id="random-generation"` and it was served
   (response retained).
3. Cycle 2 re-sent the **byte-identical** request id. The GameScript
   recorded the id in `planner_used` and **silently dropped** it
   (`if(q.request_id in planner_used||planner_requests>=33345)return;`).
4. No result arrived; Python's **20-second per-exchange read timeout**
   (`exchange()` in `app/simulation/openttd/proof/freight_delivery.py`)
   expired — timestamps of record: request disc written 10:32:01.349,
   diagnostic recorded 10:32:21.399 ≈ +20.05 s.
5. The bare `TimeoutError` propagated (root handler at
   `freight_delivery.py:2005` prints `type(e).__name__+": "+str(e)` and a
   bare asyncio timeout has an empty message, hence the uninformative
   `TimeoutError: `).

The outer attempt budget `asyncio.timeout(total_seconds)` **never expired**:
the attempt aborted at ~537 s of the sealed 2400 s (~22%). The outer timeout
is not `(total_seconds=1800)`: the sealed budget is 2400, and the docs of
record wrote 1800.

## Affected records and the exact wrong claims

1. **`EVIDENCE_INDEX.md` row E154** — claims "THE FAILURE IS THE SEALED
   ATTEMPT BUDGET ITSELF (`error=TimeoutError:` BARE — THE OUTER
   `asyncio.timeout(total_seconds=1800)` EXPIRED MID P08-CYCLE-2)" and "the
   scaled total expires mid-cycle-2 P08". Wrong on three counts: the outer
   budget never expired (2400 s never reached); the sealed value is 2400,
   not 1800; the typed origin is the 20-s per-exchange timeout on the
   dedup-dropped `random-generation` exchange, before any capture or P08
   pair-check burn (`capture_requests_attempted=0`).
2. **`TASKS.md` (2026-11-08 E154 entry, from line ~3681)** — claims the
   root error came "from the outer `asyncio.timeout` on the sealed
   `total_seconds=1800` loop budget". Same three corrections; requalification
   completed, so no requalification-cost-shortfall narrative either.
3. **`.scratch/ramrom-product` ticket `05-build-loop-product.md`** (the
   "Attempt-3 record …" section, lines ~493–547) — same claim ("from the
   outer `asyncio.timeout` on the sealed `total_seconds=1800` loop budget")
   and the closing "budget-seal" disposition language. The budget-seal gate
   is therefore unnecessary for this failure: the code of record now contains
   the request-identity fix in this proposal's companion round (the
   `cycle_request_id` shared maker), and an Attempt 4 can run the
   byte-unchanged command of record under a fresh explicit operator grant
   without any budget amendment, as far as this defect is concerned.
4. **`AI_HANDOFF.md` "E154 addendum (2026-11-08)" (lines ~798–821)** — same
   claim, plus "the loop `total_seconds` scaling underestimates per-cycle
   requalification cost" as the cause attribution. The requalification
   completed clean; per-cycle requalification is NOT what consumed the
   remaining budget — nothing consumed it; the attempt aborted at 20 s into
   cycle 2's first planner read.

Also correct the collateral misreadings in the same records (keep, but
reframe): `pair_checks=146` in cycle-2's `planning-diagnostic.json` is the
P08 planner's progress counter at the moment the diagnostic froze, not
evidence that P08 burned 146 pair-checks before hanging; the freeze point
was the `random-generation` exchange that precedes capture.

## What stays exactly as written

- Attempt 3's terminal status: `FAILED`, sealed, never relabeled.
- All E154 prose that reports the retained bytes (manifests, funding 2/1,
  E153 live-proof narrative, clock-id quadruples, cycle-1 zero-service
  terminal, 9,702/9,702 capture-pair facts, cleanup certification) — those
  observations were correct and are unaffected.
- FD-C-2: still `INCOMPLETE_EVIDENCE`; Attempt 4 not executed; no grant
  consumed.
- The E153/E152 findings (session-id reuse parse fix and stderr windowing)
  are unchanged — E153 is still proven live natively.

## Suggested application shape (when the operator approves)

Append, under each of the four records, a dated "Correction (2026-11-NN,
per research/02-attempt3-root-cause-doc-correction.md): the attempt-3
terminal `TimeoutError: ` was the 20-second per-exchange read timeout after
the GameScript `planner_used` dedup silently dropped cycle-2's
byte-identical `random-generation` request id (sha256 `519e626b…afd1`);
the outer `total_seconds=2400` attempt budget never expired (~537 s
consumed). Original prose preserved above; no status change." Keep it to
five sentences per record; do not rewrite the historical rows.

## Application of record (2026-11-09)

APPLIED append-only in the 2026-11-09 round at commit `d6342cc` plus the
docs commit minted with this note, per evidence row E155, after
re-verifying all ten claims of this proposal against the sealed bytes
(including the 124-byte/`519e626b5efed716bebd…2bafd1` request disc
byte-identity, the sealed staged guard `planner_requests>=33345`, the
mtime window `10:32:01.349311790` → `10:32:21.399356`, the sealed
`total_seconds=2400` and `loop_cycles=2`, and cycle-2's completed
qualification session). Corrections landed in `EVIDENCE_INDEX.md`
(new row E155; E154 row untouched), `TASKS.md` (dated correction
section after the 2026-11-08 attempt-3 entry),
`.scratch/ramrom-product/issues/05-build-loop-product.md`
("Correction (2026-11-09, E155)" section after the Attempt-3 record)
and `AI_HANDOFF.md` ("E155 addendum" after the E154 addendum). The
proposal's claim citations referenced two line-precise sources worth
noting for future readers: the per-instance staged cap verbatim
(`staged/network-parent.nut:34` inside the attempt's own
`frozen-source.zip`) and `EXCHANGE_SECONDS=20` at
`app/simulation/openttd/proof/freight_delivery.py:1282`. No sealed
artifact, terminal status, FD-C-2 state, budget value or ticket state
changed.
