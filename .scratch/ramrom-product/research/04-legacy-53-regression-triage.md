# Legacy 53 Regression Triage & Wayfinder Exit-Gate Resolution Plan

**File of record:** `.scratch/ramrom-product/research/04-legacy-53-regression-triage.md`  
**Working Branch:** `Rarekk/legacy-53-regression-audit`  
**Reference Map:** `.scratch/ramrom-product/map.md` (Lines 42–45, 66–72)  
**Evidence Index Reference:** `EVIDENCE_INDEX.md` (E139–E154)  
**Safety & Historical Protection:** `AGENTS.md`, `CONTEXT.md` (Authority-pinned, strictly no regeneration of git-ignored `artifacts/`, no relabeling of immutable attempts).

---

## 1. Executive Summary & Inventory of the 53 Legacy Reds

In `.scratch/ramrom-product/map.md` (lines 42–45 and 66–72), the project ledger isolates the **53 legacy offline reds**:
> *"The 53 legacy offline reds (controlled P08 e2e ×51, corridor ladder VM ×1, structural-world fixture ×1) are sealed until the exit regression pass; they are never mixed into feasibility engineering work."*

These 53 failures are not random regressions introduced during the recent ramrom-seed continuous loop implementation; they are pre-existing sealed offline test failures spanning three discrete subsystems:

| Failure Group | Test Location | Count | Primary Failure Mechanism |
| :--- | :--- | :--- | :--- |
| **Group A: Controlled P08 E2E** | `tests/test_p08_controlled_e2e.py` | 51 | P08 / WPO contract & schema evolution vs static controlled fixture |
| **Group B: Corridor Ladder / VM** | `tests/test_corridor_cargoflow2.py` / `_vm.py` | 1 | Git-ignored retained native artifact absence (`artifacts/experiments/...`) |
| **Group C: Structural-World Fixture** | `tests/test_structural_world.py` | 1 | Windows CRLF checkout / raw byte sha256 mismatch against `manifest.json` |
| **Total** | | **53** | |

---

## 2. Analysis of `legacy53_pytest.txt`

The diagnostic log recorded in `legacy53_pytest.txt` captures:
```text
.\.venv\Scripts\pytest.exe : ImportError while loading conftest 'C:\softdev2\tests\conftest.py'.
At line:1 char:1099
+ ... .txt" 2>&1; .\.venv\Scripts\pytest.exe tests/test_p08_15_3_controlled ...
    + CategoryInfo          : NotSpecified: (ImportError whi...s\conftest.py'.:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

tests\conftest.py:7: in <module>
    from app.database.base import Base
E   ModuleNotFoundError: No module named 'app'
```

### Key Findings from Log Inspection:
1. **Runner Invocation Defect (`sys.path` exclusion):**
   - Executing `.\.venv\Scripts\pytest.exe` directly in Windows PowerShell does not automatically place the repository root (`C:\softdev2`) onto `sys.path`.
   - In `tests/conftest.py:7`, Python executes `from app.database.base import Base` and immediately fails with `ModuleNotFoundError: No module named 'app'`.
   - **Rule of record in `REPRODUCE.md`:** All repository invocations must run as `.venv/bin/python -m pytest ...` or with `PYTHONPATH=.`. When invoked with `python -m pytest`, the current directory is injected into `sys.path[0]`, resolving the conftest import.
2. **Target Path Naming Slip:**
   - The command in the log targeted `tests/test_p08_15_3_controlled...` (a typo from historical documentation titles like `docs/p08-15-3-controlled-terrain-road-query.md`). The actual tracked file of record is `tests/test_p08_controlled_e2e.py`.

---

## 3. Deep Root-Cause Breakdown by Group

### Group A: Controlled P08 E2E (51 Failures)
* **File:** `tests/test_p08_controlled_e2e.py`
* **Underlying Architecture:**
  - `test_p08_controlled_e2e.py` exercises the complete offline planning pipeline: `admit(owned)` -> `import_planning_facts` -> `import_prepared_source` -> `ValidatedPlanningFactInput` -> `generate_road_scenario` -> `optimize_candidate_network`.
  - The test suite contains 26 test functions expanding into 62 parametrized test cases, of which 51 fail when evaluated against current production code.
* **Root Causes:**
  1. **Schema & Policy Digest Drift:**
     - The fixture `tests/fixtures/p08_controlled_e2e/` was frozen against early P08 schema conventions (pre-ADR-012, pre-ADR-013, pre-Ticket-03).
     - Ticket 03 widened capture parameters (`capture_tile_limit` 2048, `random-rectangle-2048-v1`, `capture_edge_pad` 6).
     - `admit()` enforces `assert imported.trust == prepared.correspondence.trust == SourceTrust.CONTROLLED_FIXTURE` and compares `record` against `tests/fixtures/p08_controlled_e2e/verification.json`.
     - Fields in `verification.json` (`policy_digest`, `policy_version`, `scenario_hash`, `plan_hash`) assert exact historical hashes that drifted when P08 / CP-SAT optimizer structures were refined.
  2. **Mocking & Bridge Boundaries:**
     - `qualified_fixture()` in `test_p08_controlled_e2e.py` patches `test_structural_world.IndustryCargoCapability` and `CargoCatalogRecord`.
     - Changes to the structural world session and qualification stability models in `app/simulation/openttd/structural_world.py` and `app/planning/p08_adapter.py` reject the synthetic mocks as incomplete component observations.

---

### Group B: Corridor Ladder / VM (1 Failure)
* **Files:** `tests/test_corridor_cargoflow2.py` and `tests/test_corridor_cargoflow2_vm.py`
* **Target Test:** `tests/test_corridor_cargoflow2.py::test_delivered_verdict_never_fires_on_the_terminal_class`
* **Root Cause:**
  - `test_delivered_verdict_never_fires_on_the_terminal_class` explicitly executes:
    ```python
    for name in ("candidate-6", "candidate-7"):
        phase = json.loads(
            (
                REPO
                / "artifacts"
                / "experiments"
                / f"d5-corridor-cargoflow2-native-{name}"
                / "result.json"
            ).read_text()
        )["phase"]
    ```
  - `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-6/` is a **git-ignored retained native evidence path**.
  - In fresh clones or developer environments where git-ignored historical runtime artifacts were not transferred via secure reviewed archives, `result.json` does not exist on disk, producing an immediate `FileNotFoundError`.
  - **Governing Discipline (`AGENTS.md` & `REPRODUCE.md`):**
    > *"Tests backed by retained `artifacts/` evidence can fail on a clone — that means missing evidence, not a code bug. The fix is never regenerating evidence."*
  - The failure is an **evidence presence dependency**, not a code logic flaw.

---

### Group C: Structural-World Fixture (1 Failure)
* **File:** `tests/test_structural_world.py`
* **Target Test:** `test_real_catalog_and_enrichment_regression_fixtures_are_valid_but_separate_runs`
* **Lines 700–703:**
  ```python
  fixture = Path("tests/fixtures/cargo_catalog_checkpoint")
  for name, digest in json.loads((fixture / "manifest.json").read_text())["sha256"].items():
      assert hashlib.sha256((fixture / name).read_bytes()).hexdigest() == digest
  ```
* **Root Cause:**
  - `tests/fixtures/cargo_catalog_checkpoint/` contains text-based payload files: `stderr.log`, `page-requests.jsonl`, `page-responses.jsonl`, `page-receipts.jsonl`, `page-verifications.jsonl`, and `runtime-identity.json`.
  - On Windows checkouts without `core.autocrlf=false` / strict `.gitattributes` binary enforcement, newline conversion (`\n` -> `\r\n`) alters the file byte sequence without changing character content.
  - As a result, `hashlib.sha256((fixture / name).read_bytes()).hexdigest()` differs from the strict sha256 recorded in `manifest.json`, triggering an exact assertion failure on the fixture integrity check.

---

## 4. Single-Purpose Branch Resolution Plan (`Rarekk/...`)

To resolve all 53 legacy reds cleanly at the Wayfinder exit gate without contaminating ongoing feasibility engineering, work must be sequenced into isolated, single-purpose branches.

```mermaid
flowchart TD
    Main[Branch: devmodule2 / Wayfinder Map Exit Gate] --> BranchC[Branch 1: Rarekk/fix-structural-fixture-crlf]
    Main --> BranchB[Branch 2: Rarekk/corridor-offline-fixture-guard]
    Main --> BranchA[Branch 3: Rarekk/p08-controlled-e2e-realignment]
    BranchC --> Verification[Exit Gate Full Regression Pass]
    BranchB --> Verification
    BranchA --> Verification
    Verification --> ExitPass[All 53 Legacy Reds Green / Exit Gate Cleared]
```

### Branch 1: `Rarekk/fix-structural-fixture-crlf`
* **Target:** Resolve Group C (1 failure in `tests/test_structural_world.py`).
* **Scope:**
  - Verify line endings for `tests/fixtures/cargo_catalog_checkpoint/*` and `tests/fixtures/industry_enrichment_v4_checkpoint/*`.
  - Add explicit `.gitattributes` entries ensuring `tests/fixtures/**` files are treated as raw binary / LF-only (`eol=lf`).
  - Re-assert `sha256` matching against `manifest.json`.
* **Safety Rule:** No modification of digest values in `manifest.json`; restore disk bytes to match the historical SHA-256 manifest.

### Branch 2: `Rarekk/corridor-offline-fixture-guard`
* **Target:** Resolve Group B (1 failure in `tests/test_corridor_cargoflow2.py`).
* **Scope:**
  - Address the missing `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-{6,7}/result.json` check.
  - Follow the exact repo convention established in `tests/test_phase_c_feasibility.py` (line 1269 of `REPRODUCE.md`: *"retained-evidence pins skip honestly when evidence absent"*).
  - Use `pytest.mark.skipif(not candidate_dir.exists(), reason="Retained native evidence candidate-6/7 absent on clone; not a defect")`.
  - Alternatively, provide an offline-checked fallback fixture if verified by an authority record, but prefer honest skipping on clone per `AGENTS.md`.

### Branch 3: `Rarekk/p08-controlled-e2e-realignment`
* **Target:** Resolve Group A (51 failures in `tests/test_p08_controlled_e2e.py`).
* **Scope:**
  - Fix runner documentation/scripts so `python -m pytest tests/test_p08_controlled_e2e.py` is invoked with proper `PYTHONPATH`.
  - Update `test_p08_controlled_e2e.py` adapter mocks to provide complete component observations adhering to current `WorldPlanningObservation` contracts.
  - Reconcile `verification.json` and `accepted-digests.json` for the controlled synthetic fixture: re-materialize synthetic test fixtures using `materialize(owned)` without touching any real native historical evidence.
* **Safety Rule:** Under `AGENTS.md`, `tests/fixtures/p08_controlled_e2e/` is explicitly a *synthetic controlled fixture* (docstring line 203: *"Generate new test artifacts only; never changes retained fixture inputs"*). Updating synthetic test-only fixtures is strictly permitted, unlike `artifacts/`.

---

## 5. Verification Gate for Exit

Before merging back to `devmodule2` at the Wayfinder exit gate:
1. Run:
   ```bash
   .venv/bin/python -m pytest tests/test_structural_world.py -k test_real_catalog_and_enrichment
   .venv/bin/python -m pytest tests/test_corridor_cargoflow2.py -k test_delivered_verdict
   .venv/bin/python -m pytest tests/test_p08_controlled_e2e.py
   ```
2. Verify:
   - 0 failures across all 3 files.
   - All 53 legacy reds converted to PASS or honest evidence-absence SKIP.
   - Touched code passes `ruff check`, `ruff format --check`, and `git diff --check`.
