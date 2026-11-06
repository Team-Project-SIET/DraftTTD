# 10: Selected-route delivered attempt

**What to build:** the optimizer-selected route carried through its own full
gated ladder to native delivery — a fresh candidate identity composed from
the parameterized contract with the selected route binding, staged,
independently reviewed, Gate-C-signed, launched once, replayed read-only and
certified-clean — ending the corridor's "no competing executable route"
finding of record with the delivered receipts of a second route. All five
gates are separate explicit operator approvals; this ticket encodes them and
never bypasses them.

**Blocked by:** 09 (Selection of record (M8 part 2)).

**Status:** ready-for-agent

- [x] Fresh round identity of record: new candidate directory constant per
      the staging precedent; the staged composition carries the selected
      route binding with staged↔source byte-correspondence — the round
      identity advanced candidate-6 → candidate-7 (one constant + lineage
      comment, 2026-11-06); the staged composition carries the adjudicated
      second admission (`route_version = 2` beside `schedule_version = 1`)
      with the staged↔source correspondence held by the freeze chain
      (3,502 entries — PRELAUNCH PASS first attempt, E121)
- [x] Prerequisite pins re-verified on disk (depot-mutation after-save
      world lineage, binary/OpenGFX pins, funds floor of record) — the
      preflight of the staged candidate-7 re-derived the pinned depot
      prerequisite (D5-F12-DEPOT-3 after-save `183b2027…6ea6`), the pinned
      binary pin and the funds floor of record (PREFLIGHT PASS, E121)
- [ ] The gate ladder executes once in order — staging (PRELAUNCH PASS,
      standalone preflight PASS, pre-auth verify CLAIM_ABSENT) → independent
      read-only review (READY-FOR-GATE-C, zero reconciliation debt) →
      Gate C signature (bound to the fresh seal, one write) → ONE launch
- [ ] The launch's outcome reconciles read-only exactly (delivered receipts
      or a preserved halt class — which routes through ticket 05's mechanism
      re-entered on this round's identity)
- [ ] On delivery: the E36 finding of record closes — both routed attempts
      with native receipts, the selection artifact pointing at the delivered
      example route
- [ ] Every sub-step's ledger row + status-log entry; `git diff --check`
      clean; `CONTEXT.md` pin intact; no commit/push

**Adjudication of record (2026-11-06, explicit operator decision "Carry
v2, competing route").** Ticket 09's selection of record (E119) points at
the delivered route of record (v1 — the delivered route's descriptive
duplicate), while this ticket's own goal sentence ends the corridor finding
"with the delivered receipts of a second route" and the spec's M8 rule
states that descriptive duplicates do not count and the E36 finding closes
only when a genuinely competing executable route carries native receipts.
Both readings cannot hold — carrying the selection (v1) can never close
E36, and carrying v2 contradicts the literal "optimizer-selected route
carried" — so the ticket text is superseded by an explicit operator
adjudication, exactly the ticket-06 reframe precedent: **the attempt of
this ticket carries the second admission (v2, the corner-swap competing
route, binding id 2)**; the selection artifact of record stays pointing at
the v1 arm (never relabeled); the refused-but-admitted v2 arm is
adjudicated to the attempt lane; E36's closure condition lives in the
spec's own rule and closes only on the competing route's native receipts.

**Widening round of record (2026-11-06, granted as the first sub-step of
the adjudicated plan; ONE commit covered by the round grant per the
established round convention — no push, no staging, no claim, no
signature, no launch, no native run):** the native pipeline of record
(`app/simulation/openttd/proof/corridor_cargoflow2_native.py`) was widened
from v1-locked to route-binding-parameterized, keeping the fail-closed
default byte-equal everywhere:

- **Landing surface (one binding-resolution thread):** the attempt plan
  guard (`_require_cargoflow2_plan`) now resolves a plan's schema version
  through the route registry of record and pins its digest to that
  binding's own guarded factory derivation, with an optional explicit
  exact pin for the per-policy pairing the verify gates ride;
  `cargoflow2_pipeline_plan(route_version)` derives the named binding's
  admitted plan (default stays the route of record, byte-equal); a new
  `_cargoflow2_policy_route_version` resolver reads the plan policy's own
  `route_version` (absent fields — every retained pre-parameterization
  candidate of record — resolve the default through the same registry,
  and foreign, string, None or bool namings refuse);
  `staged_cargoflow2_schedule` binds the pairing too; the staged plan
  policy carries `route_version` next to the unchanged
  `schedule_version = 1` and cross-locks its ladder rows against the
  binding's own wire derivation; `prepare_cargoflow2_candidate(...,
  route_version=...)`, the preflight, the single-attempt identity verify,
  the replay verify and the run executor all resolve the binding from the
  staged record's own policy and pin the exact plan-pairing.
- **The five default-derivation pin tables stay as they are, by proof:**
  the schedule gate, the E99 hypothesis record, the ladder grid, the
  funds-model fence and the budget table derive no plan digest and are
  byte-equal across both admitted bindings (asserted in the new
  composition-of-record test) — they are the binding-shared instrument.
- **Nothing else in the repo changed**: the wire contract module
  (`corridor_cargoflow2.py`) was untouched — its binding family,
  registry, import guard and per-binding factories (ticket 07/08 surface)
  already provide everything the widened pipeline consumes; the staged
  candidate directory constant stays `d5-corridor-cargoflow2-native-candidate-6`
  until this ticket's own identity-advance staging round  bumps the round
  identity as a separate operator gate.
- **Figures of record:** route-binding digests unchanged (v1
  `9a4a0778…93e45e`, v2 `26408e77…6b274`); plan digests of record (v1
  `98d055c4…f506ca` REQUEST_PLAN_DIGEST, plan v2 `e1cafb23…c08b0`); the
  staged schedule digest of the one ladder of record stays
  `5c0998f2…bf2d` — the ladder rows are byte-equal across bindings.
- **Tests:** the ladder-of-record test advanced truthfully to carry the
  second admission's ladder invariance; seven new tests insert the
  parameterization of record (second-admission policy composition,
  fail-closed resolver table, unregistered-schema-version refusal, the
  two-admission staged-composition pin chain, per-binding identity/plan
  pairing with crossed-pairing refusals, second-admission preflight
  re-derivation, unconsumed second-admission fail-closed verify).
- **Verification figures:** suites 142 passed (85 wire + 46 native + 11
  VM — the native suite is 39 + the 7 new) in one run; `ruff check` clean
  on both touched paths; `uvx ty check` clean on the test path and
  reports ONE pre-existing diagnostic on the native pipeline path (the
  `connect` override report at the untouched backend-override region —
  present at HEAD before this round; recorded, not introduced, not
  silenced); `git diff --check` clean; `CONTEXT.md` pin
  `847d710a…984d` intact; the evidence zone byte-untouched.
- **Not performed this round:** staging, staging seal, fresh round
  identity, preflight, review, Gate C, launch, route-read probe — every
  ladder gate of this ticket remains its own explicit operator
  approval, none granted by the widening round.

**Staging round of record (2026-11-06, granted in-session; ONE commit
carrying the identity advance + the CLI option + books; the staged bytes
live under the evidence zone per the retained-artifact convention; no
push, no claim, no signature, no launch, no native run):** the round
identity advanced candidate-6 → candidate-7 at the module's own
round-identity constant (one site, lineage comment truthfully carried:
candidates 1–2 consumed with verdicts; 3–4 seal-superseded, staged
never-launched; candidate-5 terminal halt-class history; candidate-6
terminal COMPLETE-not-delivered history; candidate-7 composes from the
widened tree and carries the adjudicated second admission), the CLI
gained its honest `--route-version` option (default = the route binding
of record, byte-equal behavior for the v1 rounds), and the staged
candidate of record was composed once: `prepare
artifacts/experiments/d5-corridor-cargoflow2-native-candidate-7
--route-version 2` → **PRELAUNCH PASS first attempt** (exit 0), the
standalone `preflight` re-run → **PREFLIGHT PASS** (exit 0), and the
pre-auth `verify` → **AUTHORIZATION_UNVERIFIED / CLAIM_ABSENT** (exit
1). Figures of record: seal `9c5f727200efa7b896ab2b8016d5183b1f1ee62baf
f7bfa204eb60bf01e19257` (PRELAUNCH.sha256 sidecar byte-equal);
`route_version = 2` / `schedule_version = 1` in the staged plan policy
(ladder schema `d5-cargoflow2-ladder-grid-v1`); plan-model digest
`e1cafb23…c08b0` (binding 2's own admitted plan — the corner-swap
competing route of record); staged schedule digest `5c0998f2…bf2d` (the
one ladder of record, unchanged); frozen chain 3,502 entries;
prerequisite D5-F12-DEPOT-3 after-save `183b2027…6ea6` (the pinned
world of record, re-verified on disk); budgets 1 launch / 0 retries /
32 requests; hypothesis state `RETAINED_PROBE_REBOUND`; no CLAIM.json,
no AUTHORIZATION.json, no launch artifact anywhere in the candidate
root (correct pre-consumption state, manually verified). The staged
source is the widened tree (commit `8fc8c26` + this round's identity
advance). Transcripts: `/tmp/opencode/c7_stage_output.txt`,
`/tmp/opencode/c7_preflight_output.txt`, `/tmp/opencode/
c7_verify_output.txt` (the offline-staging transcript convention).

**Review round of record (2026-11-06, granted in-session; fresh-context
read-only re-derivation audit per the per-round method; no repo write by
the audit, no staging rerun, no signing, no claim, no launch, no native
run, no push):** the fresh audit script of record
(`/tmp/opencode/c7_review.py`; transcript
`/tmp/opencode/c7_review_output.txt`, outside the repo tree) re-derived
every binding from disk and the live widened tree against the staged
bytes and ended in **`READY-FOR-GATE-C` — 21/21 checks, exit 0, zero
findings, zero reconciliation debt**. The audit confirmed: round
identity candidate-7 with no consumed round-6 identity riding any staged
byte and the retained candidate-6 record byte-intact (nothing
relabeled); the lineage quartet at the module pins; seal
`9c5f7272…e19257` == sidecar == the staging figure, byte-equal
before == after the audit; the freeze-pin chain re-deriving clean
against the live tree with the D2 source closure and dependency
inventory re-verified against `CARGOFLOW2_CLOSURE_ROOT`; the staged
GameScript identity byte-checking the live re-derived save-restore
composition (`staged_cargoflow2_composition()`); the v2-carrying
derivation — `route_version = 2` beside `schedule_version = 1`,
plan-model digest `e1cafb23…c08b0` == binding 2's own live guarded
factory derivation, the staged schedule the one ladder of record
(`5c0998f2…bf2d`, `cargoflow2_schedule()` == the wire module's
`cargoflow2_schedule_rows(binding 2)`); the staged plan policy equal to
the full live `cargoflow2_plan_policy(2)` field-for-field (zero diff);
the five binding-shared instrument tables byte-equal across both
admitted bindings' live derivations (the E120 invariance promise, now
evidenced by audit); metadata expected-readback and budgets equal to
their live derivations (1 launch / 1 connection / 0 retries / 32
requests); prerequisite `D5-F12-DEPOT-3` after-save `183b2027…6ea6`
with the staged source save re-verified on disk; the candidate root
exactly the staged 4 entries, pre-consumption, no CLAIM /
AUTHORIZATION / LAUNCH-CONSUMED / result marker anywhere; the pinned
binary re-digested `276d5b69…904c`; and the production preflight
re-ran clean (`PREFLIGHT PASS`, exit 0). Audit-side honesty: the first
execution aborted 10/21 (exit 1) on a mis-placement of the
expected-readback axis inside the plan-policy comparison (the staged
record carries `expected_readback` at the metadata level beside the
budgets); nothing repo-side was touched, the corrected script re-ran
the full table end-to-end, and the first-pass transcript (one output
path, overwritten by the re-run) is not retained — recorded, not
re-created. The landed review book is
`.scratch/d5-corridor-poc-tail/issues/02-round7-independent-review.md`.

**Standing gates after the review round (each its own explicit operator
approval, none granted):** the Gate C signature round (Option-1
checklist bound to the fresh seal `9c5f7272…e19257`, one write) and the
ONE launch round — the launch carries the corner edge 50351↔50352 as
its typed open precondition (a preserved halt class on the ONE launch
is terminal for candidate-7 and re-enters via ticket 05's mechanism);
tickets 11–13 remain blocked behind them.

**Gate C round of record (2026-11-06, granted in-session; the operator's
Option-1 signature over the reviewed candidate-7 via the production
signing surface only — one signing operation, first invocation, zero
refusals, zero re-writes; no staging rerun, no claim, no launch, no
native run, no push; the books commit covered by the same grant):** the
fresh round-7 signer driver of record
(`/tmp/opencode/gate_c_cargoflow2_c7.py`; transcript
`/tmp/opencode/gate_c_c7_output.txt`, outside the repo tree; the
round-bound prior drivers never reused) held every pre-write refusal
gate before anything was signed or written: the gate surface absent,
the live seal == sidecar == the operator-approved seal of this round
`9c5f7272…e19257`, and the authorization payload digest of record
`f1d210cf17704fd1ad21d706160d1d6d03d417e0fa7585ac6a3d30a3e41df15c`
cross-checked == the production staged-payload digest derivation
(staged == re-derivation), with the attempted scope binding this
round's own staged identity (route_version 2 beside schedule_version 1,
plan digest `5c0998f2…bf2d`, attempt `D5-CARGOFLOW-2`). Seed mechanics
of record: the operator-held armored PKCS#8 PEM's 48-byte DER
final-32 RFC 8032 seed window carried memory-only, env-only
`CARGOFLOW_GATE_SEED` (base64) — never printed, never filed, never
passed as an argument; the pre-write identity gate re-derived
`public_from_seed(seed)` == the pinned anchor `5063982b…880f` and the
operator key identity unchanged of record
`sha256-ed25519-public-key:cbb63ff5…40c614` (a wrong extraction would
have refused before any write). `AUTHORIZATION.json` written exactly
once — **record sha256 of record
`24ccab3ec5b1140cb2c008eda7217810f4612aa4254e8bd98166813a3d9b6417`** —
and production `verify_authorization` read the written record and
passed against the seeded anchor (the seed-window variables dropped
from the driver's memory immediately after the write). Post-write
read-only state: root exactly the staged 4 entries +
`AUTHORIZATION.json`, no CLAIM / LAUNCH-CONSUMED; the seal byte-equal
after the write; all seven candidates' PRELAUNCH byte-pictures
before == after; the production `preflight` re-run **`PREFLIGHT PASS`
exit 0** with the authorization present; the standalone `verify` still
**`AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT` exit 1 by design** (the
claim mints at the launch boundary only); the seed env unset + empty
verified at the end in a fresh shell. The landed signing book is
`.scratch/d5-corridor-poc-tail/issues/03-round7-gate-c-signing.md`.

**Standing gate after Gate C (the only remaining gate of ticket 10, its
own explicit operator approval, none granted):** the ONE launch round —
the single native launch of the signed candidate-7 bound to record
`24ccab3e…6417` via the production pipeline CLI, one attempt, no
retry, no reconnect; the launch carries the corner edge 50351↔50352 as
its typed open precondition (a preserved halt class on the ONE launch
is terminal for candidate-7 and re-enters via ticket 05's mechanism);
tickets 11–13 remain blocked behind it.
