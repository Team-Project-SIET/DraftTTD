# Automated CI/CD Pipeline & Deployment Architecture

**System:** OpenTTD Autonomous Freight Delivery System  
**Subject:** Software Design and Development 2 (Security & Automation Assessment Â§5 â€” 40%)  
**Workflows:** `.github/workflows/ci.yml`, `.github/workflows/cd.yml`, `Dockerfile`  

---

## 1. CI/CD Architecture Overview

The repository automates verification, packaging, containerization, and deployment smoke testing through two decoupled GitHub Actions pipelines running on deterministic `ubuntu-latest` runners with Python 3.14.6 and `uv`.

```
  [ git push / PR ]
          |
          v
+-------------------------------------------------------------------+
|  CI PIPELINE (.github/workflows/ci.yml)                           |
|  1. Deterministic Sync  : uv sync --locked --dev                  |
|  2. Hygiene & Docs Gate : git diff --check, verify docs/security/ |
|  3. Static Lint Gate    : uv run ruff check (core modules)        |
|  4. Offline Pytest      : Crypto, Protocol, Planning, DB Suites   |
|  5. Report Artifact     : Upload JUnit XML + Step Summary         |
+-------------------------------------------------------------------+
          | (On CI Success on main / devmodule2 / workflow_dispatch)
          v
+-------------------------------------------------------------------+
|  CD PIPELINE (.github/workflows/cd.yml)                           |
|  1. Build Python Dist   : uv build (wheel + sdist)                |
|  2. Hermetic Staging    : Stage GameScript (.nut) + docs/security/|
|  3. Integrity Signing   : Generate SHA256SUMS.txt (CWE-354)       |
|  4. Clean-Room Install  : Install wheel in fresh venv & verify CLI|
|  5. Docker Container    : Build non-root image & run smoke deploy |
|  6. Deployment Proof    : Upload deployment-receipt.txt           |
+-------------------------------------------------------------------+
```

---

## 2. Continuous Integration (CI) Controls

File: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)

1. **Deterministic Supply Chain (`uv sync --locked --dev`):**
   - Strictly enforces `pyproject.toml` and `uv.lock`, preventing unpinned or unexpected dependency upgrades.
2. **Security Documentation & Diff Hygiene Gate:**
   - Verifies git diff cleanliness (`git diff --check`) and enforces the presence of `docs/security/` and `docs/authority/`.
3. **Static Linting Gate (`ruff`):**
   - Runs `ruff check` across `app/planning`, `app/experiments`, `app/database`, and demo CLI modules.
4. **Automated Offline Verification (`pytest`):**
   - Executes deterministic test suites covering Ed25519 cryptography, Monocypher AdminPort handshake, Admin protocol/session, P08/P05 planning/optimizer, GameScript transport/protocol, execution domain, and database core.
   - Publishes `ci-junit-report` artifact for auditability.

---

## 3. Continuous Deployment (CD) & Containerization

Files: [`.github/workflows/cd.yml`](../../.github/workflows/cd.yml), [`Dockerfile`](../../Dockerfile), [`.dockerignore`](../../.dockerignore)

1. **Artifact Packaging (`uv build`):**
   - Uses `hatchling` backend to build installable `.whl` and `.tar.gz` distributions.
2. **Hermetic Release Staging & SHA-256 Lock (CWE-354):**
   - Bundles the wheel, `app/simulation/openttd/freight_delivery_package/`, and `docs/security/` into `dist/release-bundle/`.
   - Generates `SHA256SUMS.txt` and verifies `sha256sum -c SHA256SUMS.txt` before deployment.
3. **Least-Privilege Containerization (`Dockerfile`):**
   - Based on `ghcr.io/astral-sh/uv:python3.14-bookworm-slim`.
   - Creates and drops privileges to non-root user `appuser:appgroup`.
   - Installs locked dependencies via `uv sync --locked --no-dev --no-editable`.
4. **Automated Installation & Deployment Smoke Test:**
   - Installs the built wheel into a clean isolated environment (`/tmp/clean-deploy-venv`), checks `transport-experiment --help`, and runs `python -m app.openttd_demo plan`.
   - Builds `logistics-optimizer:latest` Docker image, validates `docker compose config --quiet`, and executes `docker run --rm logistics-optimizer:latest plan`.
   - Records execution output to `deployment-receipt.txt` and publishes it as a GitHub Actions artifact.

---

## 4. Verified Local Execution Evidence

### 4.1 Static Analysis (`ruff`)
Command:
```powershell
.venv\Scripts\python.exe -m ruff check app/planning app/experiments app/database app/config.py app/openttd_demo.py app/demo_operations.py app/demo_random.py app/demo_random_native.py app/demo_smoke_preflight.py
```
Result:
```text
All checks passed!
```

### 4.2 Deterministic Offline Test Suites (`pytest`)
Command:
```powershell
.venv\Scripts\python.exe -m pytest tests/test_ed25519_cryptography.py tests/test_ed25519_rfc8032.py tests/test_admin_protocol.py tests/test_admin_session.py tests/test_planning.py tests/test_planning_optimizer.py tests/test_gamescript_protocol.py tests/test_gamescript_transport.py tests/test_demo_random.py tests/test_random_capture_schema.py tests/test_demo_operations.py tests/test_execution_domain.py -o addopts=""
```
Observed Output:
```text
============================= 492 passed in 2.84s =============================
```

### 4.3 Environment Note (Windows vs Linux CI Runner)
- On the local Windows host, Windows Application Control policy blocks loading the native `monocypher` `.pyd` DLL (`ImportError: DLL load failed while importing monocypher`).
- On GitHub Actions (`ubuntu-latest`) and inside the Debian Bookworm `Dockerfile` runtime, `pymonocypher==4.0.3.2` and `openttdlab==0.0.75` install cleanly via `uv sync --locked` without OS DLL restrictions, allowing full crypto and CLI smoke tests to execute natively.
- Native OpenTTD binary launch (`--run-openttd`) remains strictly user-gated and is never invoked automatically in CI/CD.

---

## 5. Verified GitHub Actions Remote Execution (Commit `9850aa2`)

Both CI and CD pipelines executed on GitHub Actions (`ubuntu-latest`) on branch `Rarekk/consolidated-delivery` and passed all stages:

| Pipeline | Run ID | Jobs & Verification Steps | Result | Artifacts Generated |
| :--- | :---: | :--- | :---: | :--- |
| **CI** | `43339527553` | 1. Static Analysis & Security Hygiene (12s)<br>2. Offline Planning, Crypto & Protocol Tests (20s) | **SUCCESS** | `ci-junit-report` (6,741 bytes) |
| **CD** | `43339527545` | 1. Build Wheel & Hermetic Release Bundle<br>2. Verify `SHA256SUMS.txt` Integrity (CWE-354)<br>3. Clean-Room Wheel Install & CLI Check<br>4. Docker Compose Config + Docker Build + Smoke Test | **SUCCESS** | `logistics-optimizer-release` (7,957,932 bytes)<br>`cd-deployment-receipt` (700 bytes) |
