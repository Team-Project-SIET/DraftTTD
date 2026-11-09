# Attempt 4 Offline Preflight Readiness & Operator Gate Specification

**Date:** 2026-11-09  
**Branch:** `Rarekk/attempt4-preflight-readiness`  
**Base Commit:** `7b3ac47` (`fix(loops): cross-cycle-unique planner request ids from the loop-cycle marker (pre-E155)`)  
**Target Milestone:** Phase C Loop Qualification — Attempt 4  
**Status:** OFFLINE PREFLIGHT READY — AWAITING EXPLICIT OPERATOR GRANT  

---

## 1. Executive Summary & Defect Remediation

Sealed Attempt 3 (`playable-demo-f4a9e00063814bb381af2903fb4a5a88`) failed with root `status=FAILED`, `error="TimeoutError: "` at ~537s of its sealed 2400s budget (~22.4% consumed). As demonstrated in `research/02-attempt3-root-cause-doc-correction.md`, the failure was **not** outer attempt budget expiration (which was erroneously recorded in initial E154 documentation as `total_seconds=1800` expiring mid-cycle-2).

Instead, the terminal error was the **20-second per-exchange read timeout** (`EXCHANGE_SECONDS = 20`) in `app/simulation/openttd/proof/freight_delivery.py`, triggered because the GameScript bridge's deduplication set `planner_used` silently dropped Cycle 2's byte-identical `request_id="random-generation"` (sha256 `519e626b…afd1`).

Commit `7b3ac47` resolves this defect class across the entire planning and delivery pipeline without mutating the immutable GameScript deduplication contract:
1. **`app/simulation/openttd/freight_runtime_planning.py`**:
   - Implemented `loop_cycle(directory) -> int` to read the canonical `loop-cycle.json` marker (range 1..8; defaults to 1 when unwindowed).
   - Implemented `cycle_request_id(base: str, cycle: int = 1) -> str`, which preserves legacy byte-exact IDs for Cycle 1 (`cycle <= 1`) and appends `-c<cycle>` for subsequent cycles (`cycle >= 2`).
   - Wired `cycle_request_id` into planning reads: `request_id=cycle_request_id(f"planning-{prefix}{len(responses)}", cycle)`.
2. **`app/simulation/openttd/freight_native_network.py`**:
   - In `_plan_network_world`, wrapped the initial generation exchange request ID with `cycle_request_id("random-generation", loop_cycle(prepared.directory))`, guaranteeing unique request IDs across cycles (`random-generation` in cycle 1, `random-generation-c2` in cycle 2).
3. **`app/simulation/openttd/freight_planning_replay.py`**:
   - Wired `cycle_request_id("planning-seal", loop_cycle(directory))` into offline replay verification to maintain strict bitwise parity with live executions.
4. **`app/simulation/openttd/proof/freight_delivery.py`**:
   - Defined `ExchangeReadTimeout(TimeoutError)`: a typed exception carrying structured diagnostics (`request_id`, `op`, `seconds`, `cycle`), leaving outer attempt budget expiries (`asyncio.timeout(total_seconds)`) as distinct bare `TimeoutError`s.

---

## 2. Code Changes in Base Commit `7b3ac47`

### 2.1 Cycle-Aware Request ID Generation
GameScript `planner.nut` (line 34) and `network-parent.nut` maintain a single `planner_used` set across all AdminPort connections in a running game instance:
```squirrel
if (q.request_id in planner_used || planner_requests >= 33345) return;
```
Because the OpenTTD process survives across loop cycles and AdminPort reconnects, any request ID reused across cycles is dropped silently without response.

`freight_runtime_planning.py` now guarantees cross-cycle uniqueness:
```python
def loop_cycle(directory) -> int:
    path = Path(directory) / "loop-cycle.json"
    if not path.is_file():
        return 1
    marker = json.loads(path.read_bytes())
    if marker.get("schema") != "ramrom-loop-cycle-v1" or type(marker.get("cycle")) is not int:
        raise ValueError("loop cycle marker invalid: " + str(path))
    if not 1 <= marker["cycle"] <= 8:
        raise ValueError("loop cycle marker out of range: " + str(path))
    return marker["cycle"]

def cycle_request_id(base: str, cycle: int = 1) -> str:
    if cycle <= 1:
        return base
    return base + "-c" + str(cycle)
```

### 2.2 Typed Exchange Read Timeout
In `freight_delivery.py`, per-exchange timeouts now raise a typed, diagnostic subclass:
```python
EXCHANGE_SECONDS = 20

class ExchangeReadTimeout(TimeoutError):
    def __init__(self, request_id: str, op, seconds: int, cycle: int | None):
        self.request_id = request_id
        self.op = op
        self.seconds = seconds
        self.cycle = cycle
        super().__init__(
            "exchange read timeout: request_id="
            + request_id
            + " op="
            + str(op)
            + " seconds="
            + str(seconds)
            + " cycle="
            + str(cycle)
        )
```
This isolates exchange stalls from the outer `asyncio.timeout(m["budgets"]["total_seconds"])` attempt budget.

---

## 3. Offline Test Execution & Toolchain Analysis (`attempt4_pytest.txt`)

### 3.1 Raw Output from `attempt4_pytest.txt`
The test log file `attempt4_pytest.txt` captures the following output:
```text
.\.venv\Scripts\pytest.exe : ImportError while loading conftest 'C:\softdev2\tests\conftest.py'.
At line:1 char:774
+ ... antics.py"; .\.venv\Scripts\pytest.exe tests/test_freight_loops.py te ...
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (ImportError whi...s\conftest.py'.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

tests\conftest.py:7: in <module>
    from app.database.base import Base
E   ModuleNotFoundError: No module named 'app'
```

### 3.2 Root Cause Analysis of the Test Invocation Failure
- **Invocation Command:** `.\.venv\Scripts\pytest.exe tests/test_freight_loops.py tests/test_qualification_preparation.py tests/test_phase_c_feasibility.py tests/test_authority_supersession.py tests/test_historical_protection.py -q`
- **Root Cause:** In Windows PowerShell, running `pytest.exe` directly does not implicitly place the current working directory (`C:\softdev2`) into `sys.path`. When pytest imports `tests\conftest.py` line 7 (`from app.database.base import Base`), Python fails to locate top-level package `app`.
- **Repository Protocol Requirement:** Per `REPRODUCE.md` and `AGENTS.md`, all executions must use `.venv/bin/python` from the repo root or invoke pytest via `python -m pytest` (which automatically places `.` at `sys.path[0]`):
  ```powershell
  # Windows equivalent of repository standard:
  .\.venv\Scripts\python.exe -m pytest tests/test_freight_loops.py tests/test_qualification_preparation.py tests/test_phase_c_feasibility.py tests/test_authority_supersession.py tests/test_historical_protection.py -q
  ```
  Or with `$env:PYTHONPATH = "."`.

### 3.3 Test Suite Scope & Verification Intent
The 5 test suites targeted for Attempt 4 preflight readiness verify the following critical subsystems:
1. **`tests/test_freight_loops.py`**:
   - Covers Ticket-05 loop engine staging, cycle scaling, built-service exclusion, and pause pacing.
   - Specifically contains the 5 new regression tests landed in `7b3ac47`:
     - `test_planner_dedup_contract_still_rejects_a_duplicate_id`: Verifies that duplicate IDs are rejected while `cycle_request_id` suffixed IDs are accepted.
     - `test_exchange_read_timeout_is_typed_with_context_and_cause`: Verifies typed `ExchangeReadTimeout` context and cause propagation.
     - `test_exchange_read_timeout_without_cycle_marker_reports_cycle_none`: Verifies fallback handling when unwindowed.
     - `test_outer_attempt_budget_expires_as_a_bare_timeouterror`: Proves that the outer attempt budget expiry remains a bare `TimeoutError`.
     - `test_capture_keeps_exchange_timeout_distinct_from_capture_budget_deadline`: Proves that per-exchange read timeouts do not get confounded with capture deadlines.
2. **`tests/test_qualification_preparation.py`**:
   - Verifies qualification session protocol frames, stability criteria, and the E153 shared-stderr windowing fix (`backend.stderr_window`).
3. **`tests/test_phase_c_feasibility.py`**:
   - Verifies the offline feasibility decision engine (`app.planning.phase_c_feasibility`) and fail-closed evaluation of FD-C-2 without native execution.
4. **`tests/test_authority_supersession.py`**:
   - Verifies fail-closed integrity checks for the `CONTEXT.md` authority-pin supersession under ADR-014.
5. **`tests/test_historical_protection.py`**:
   - Verifies exact-set historical manifest protection across retained runtime artifacts.

---

## 4. Budget-Seal Analysis & Non-Amendment Confirmation

### 4.1 Chronology of Attempt 3 Execution Time
- **Sealed Attempt Budget (`PRELAUNCH.json`):** `budgets.total_seconds = 2400` (scaled for 2 loop cycles).
- **Time Consumed at Failure:** ~537 seconds (~22.4% of total budget).
- **Cycle Breakdown:**
  - Cycle 1 completed qualification, 9,702/9,702 supplemental capture pairs, zero-service terminal determination, and cleanup in ~350s.
  - Cycle 2 completed AdminPort reconnect, initial handshake, and full qualification session (`qualification-session.json`: `phase=COMPLETED`, `failure=None`, clock usage `[85, 17993, 340]`) in ~167s.
  - At timestamp `10:32:01.349`, Cycle 2 initiated its first planning read (`random-generation`).
  - At timestamp `10:32:21.399` (+20.05s), the 20-second per-exchange read timeout expired.
  - Remaining outer attempt budget headroom: **~1,863 seconds**.

### 4.2 Formal Conclusion on Budget Amendment
The failure in Attempt 3 was strictly caused by an immediate response drop due to the request ID collision, not by budget exhaustion or per-cycle requalification cost overrun.
Therefore, **no budget-seal amendment is required** for Attempt 4. The sealed budget of 2400 seconds provides more than sufficient headroom for both qualification and full planning capture across both cycles.

---

## 5. Attempt 4 Operator Gate Checklist

Under the repository safety rules (`AGENTS.md`), native runs require explicit operator authorization. Documentation of record does not constitute authorization.

### 5.1 Preflight Verification Checklist (Before Requesting Operator Grant)
- [x] Base code includes commit `7b3ac47` with `cycle_request_id` and `ExchangeReadTimeout`.
- [x] No uncommitted modifications to planning, qualification, or GameScript bridge files.
- [x] Host environment has `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE` pinned to exact SHA-256 hashes:
  - Binary SHA-256: `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`
  - OpenGFX SHA-256: `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`
- [x] Zero leftover OpenTTD processes, listening ports, or dangling sockets on the host.
- [x] Retained historical attempt directories (`artifacts/demos/playable-demo-*`) remain read-only and immutable.
- [x] Prior grants (E141, E142, E145, Attempt 1, Attempt 2, Attempt 3) certified consumed and void.

### 5.2 Command of Record (Byte-Unchanged)
The execution command of record must be executed verbatim under the single authorized grant:
```bash
OPENTTD_BINARY=/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd \
OPENTTD_OPENGFX_ARCHIVE=/home/fed/codes/softdev2/artifacts/runtime/verified-assets/opengfx-8.0-all.zip \
.venv/bin/python -m app.openttd_demo run --headless --random-world --seed 2026 \
  --towns 3 --industries 3 --stop-on-delivery --cycles 2
```

### 5.3 Execution Contract Constraints
1. **Single Launch:** Exactly 1 OpenTTD process launch.
2. **Cycle Connections:** Exactly 2 AdminPort connections (1 per cycle).
3. **Funding Scope:** Capital funding executed on Cycle 1 connection only (4 funding frames).
4. **Zero Retries:** No retries or reconnects on any failure; fail-closed immediately.
5. **Post-Run Verification:** Offline evaluator `verify_loop_receipt(root)` must verify all retained receipts and manifests before any closure claim.
