# GUI vs `--headless` execution mode — decision of record (qualification attempt, ticket 05)

Date: 2026-11-08. Status: **decided** (offlines-only decision round; no native
run, no AdminPort connection, no staging, no `artifacts/` mutation, no
operator grant consumed). This decision resolves the discrepancy between the
product spec `docs/specs/ramrom-product.md` §1/§3.3 (spectator GUI clauses)
and the qualification attempt of record, which runs `--headless`, so the next
native grant request carries one execution mode with one recorded rationale.

## 1. The question of record

Spec §1 (product definition, lines 17–21) says the product "plays on real
OpenTTD 15.3 with the spectator GUI showing the process" and that "closing
the spectator window ends a phase softly (ended-by-operator, never a system
failure)"; spec §3 item 3 (lines 104–108) makes the operator's window close
one of the three soft cycle ends. The command of record for the native loop
qualification — ticket-05 acceptance list plus command block (lines 194–208),
`REPRODUCE.md` addenda #2–#5, and the E145 granted attempt — is
`run --headless --random-world --seed 2026 --towns 3 --industries 3
--stop-on-delivery --cycles 2`. A headless run launches no graphical client
(`app/openttd_demo.py:348`, help "Server only; no GUI validation"), prints
"Headless mode: GUI/playability is not being tested." instead of starting one
(`app/openttd_demo.py:96–98`), and returns immediately at delivery because
`if self.headless or self.view_seconds == 0: return` (`app/openttd_demo.py:188`).
The command of record also carries `--stop-on-delivery` ("Close after all
selected services deliver; no viewing hold", `app/openttd_demo.py:356–360`),
so the post-delivery viewing hold is disabled by the command of record itself,
with or without a window. In `--headless`, therefore, the §3.3 window-close
soft end is unreachable: the only operator soft end is Ctrl+C on the runner,
which is a typed abort of the attempt, not the ended-by-operator window close.

## 2. Evidence relied on

- **Every acceptance bar of record is receipt-based; none names a GUI.** The
  §2 native bar is "the battery produces ≥1 verified native plan + delivery
  cycle without a `NO_FEASIBLE_SERVICES` terminal, and every terminal of any
  battery run stays honestly typed" (spec lines 78–84). The loop
  qualification bar is the ticket-05 acceptance list (lines 196–207): one
  launch at `--cycles 2`, first cycle delivering ≥1 verified service,
  per-cycle replay via `verify` printing `verified_loop_cycles`, the pacing
  fence `pause_pairs == captured_relationships` with no `pause_resume_error`,
  and — if reached — the typed `abandoned_world` end at two consecutive
  zero-service cycles. Verified services, replayed recordings and typed
  terminals are the gates; window visibility is not one of them.
- **The entire native history of the random-world line is headless.** The
  retained one-shot facts of E139 and E141 and the E145 typed pre-launch
  failure were all produced by headless server runs. GUI-bearing native
  records exist on other identities only: E4/E8 (seed-17 smoke, spectator
  joining/navigation verified) and E140 (seed-42 GUI demo in which the
  operator's mid-run window close was recorded as the typed terminal
  `RuntimeError: Graphical client exited (0)` with `result.json` FAILED —
  the recorded motivation for the soft-close clause, retained at its own
  FAILED identity, never relabeled).
- **The loop engine was built and pinned against this command of record.**
  E143–E147 (loop engine, verify/record rework, seam fix, lifecycle tests)
  all define, test and verify the native remainder in headless receipt
  terms: `verified_loop_cycles`, per-cycle `loop-cycle-{k}` recordings,
  scaled budgets 174/66/66,690/2400/384. No criterion anywhere depends on
  the spectator window.

## 3. Decision: the qualification attempt of record stays `--headless`

The next native qualification attempt keeps exactly the command of record:
`--headless` with `--stop-on-delivery`, `--cycles 2`, seed 2026, towns 3,
industries 3. The §1 spectator clause and the §3.3 window-close soft end are
**product-definition scope, not acceptance gates of the qualification
attempt**, so the discrepancy is resolved without changing any command,
criterion or budget. The command of record, the E144/E146/E147 test pins and
all books stay byte-for-byte as they are; this decision only records the
authoritative reading so no future session re-litigates the mode or drifts
the command.

## 4. What stays owed — never silently dropped, never silently satisfied

The spectator window and its §3.3 window-close soft end remain owed product
elements. A later, separately granted GUI-bearing element must: run the
random-world product line without `--stop-on-delivery` with a graphical
spectator client, exercise the post-delivery viewing hold and the operator
window-close soft end on the continuous loop world, and retain receipts of
the ended-by-operator phase end. Two recorded facts bind that element: in a
headless attempt the only operator soft end is Ctrl+C; and E140's historical
window close was typed FAILED (`RuntimeError: Graphical client exited (0)`)
under the classic runtime, so the GUI element will have to make the
ended-by-operator path actually soft (never a system failure) where today's
viewer types a client exit as a failure. Until that element runs, the
window-close soft end is natively unexercised — recorded honestly, not
assumed.

## 5. Changes made and verification of record

No code change; no acceptance criterion changed; no budget changed.
Documents only: this decision doc, a ticket-05 appended section, the E148
evidence row, a TASKS ledger row, an `AI_HANDOFF.md` tail addendum,
`REPRODUCE.md` addendum #6, a backlog status-log entry, and one map decision
line. Offline verification: staging suite `tests/test_random_capture_budgets.py`
13 passed at the unchanged source digests (`app/demo_random_native.py`
`258ba9dbe19c7284`, `app/simulation/openttd/proof/freight_delivery.py`
`2cce3070c125bd41`, `tests/test_random_capture_budgets.py`
`f6a432e2b771231b`); `git diff --check` clean. One commit, no push.
