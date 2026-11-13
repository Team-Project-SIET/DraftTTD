# Threat Modeling & Data Flow Analysis (DFD)

**System:** OpenTTD Autonomous Freight Delivery System  
**Subject:** Software Design and Development 2 (Security Assessment Â§1)  
**Standard Reference:** NIST SP 800-53, OWASP Threat Dragon, Microsoft Threat Modeling (STRIDE)  
**Status:** Certified Architecture Baseline  

---

## 1. System Scope & Objective

The OpenTTD Autonomous Freight Delivery System couples an offline combinatorial route optimizer (Python + Google OR-Tools CP-SAT) with a real-time game simulation engine (OpenTTD Server + Squirrel 2.2 GameScript) through an encrypted TCP AdminPort bridge.

Due to the execution of automated infrastructure commands and handling of external file fixtures, the system enforces a strict **zero-trust, fail-closed security boundary** to guarantee that:
1. Malicious or malformed inputs cannot escape the project sandbox (Path Traversal / CWE-22).
2. Architectural models, binary targets, and simulation receipts cannot be tampered with (Data Integrity / CWE-354).
3. OpenTTD engine instances cannot be commanded without verified cryptographic authorization (Missing Authentication / CWE-306).

---

## 2. DFD Level 0: Context Diagram

The Context Diagram defines the interaction between the system boundary, external human operators, and the isolated OpenTTD simulation engine.

```
                  +----------------------------------------------+
                  |              External Operator               |
                  |              (CLI / Automation)              |
                  +----------------------------------------------+
                                         |
                                         | (1) Config, CLI Flags & Commands
                                         v
+----------------------------------------------------------------------------------+
|                   OPENTTD AUTONOMOUS FREIGHT CONTROL SYSTEM                      |
|                                                                                  |
|   - Input Sanitization & Jail Enforcement                                        |
|   - Bounded Road Explorer (P08) & CP-SAT Combinatorial Optimizer (P05)           |
|   - Package Staging & Freight Script Compiler                                    |
|   - Encrypted AdminPort Monocypher Bridge Client                                 |
+----------------------------------------------------------------------------------+
                                         |
                                         | (2) Authenticated TCP Loopback Commands
                                         v
                  +----------------------------------------------+
                  |         OpenTTD Engine Dedicated Host        |
                  |        (Server Game Loop + GameScript)       |
                  +----------------------------------------------+
```

---

## 3. DFD Level 1: Detailed System Decomposition

The Level 1 diagram decomposes the internal processes, external entities, data stores, data flows, and explicitly demarcates the **Three Trust Boundaries**.

### 3.1 Architectural DFD Diagram

```
================================================================================================
[TRUST BOUNDARY 1: UNTRUSTED EXTERNAL ZONE]
================================================================================================
  [ External Operator / CLI ]
             |
             | (1) Raw CLI Arguments & File Path Configurations
             v
  ( Process 1: Input Sanitizer & Path Jail Guard )
             |
             +--- (2) Validate SHA-256 Digest ---> [ Data Store 1: Authority Manifest ]
             |                                     (docs/authority/*.json)
             v (Clean Configuration Spec)
------------------------------------------------------------------------------------------------
[TRUST BOUNDARY 2: SECURE PYTHON PLANNING CONTAINER]
------------------------------------------------------------------------------------------------
  ( Process 2: Road Corridor Generator - P08 )
             |
             +--- (3) Read / Write Terrain Cache ---> [ Data Store 2: Corridor Cache ]
             |                                        (p08_candidates.json)
             v (4) Filtered Road Candidates JSON
  ( Process 3: CP-SAT Combinatorial Optimizer - P05 )
             |
             v (5) Validated ExecutionPlan Domain Object
  ( Process 4: Package Stager & Freight Compiler )
             |
             +--- (6) Hermetic Package Deployment ---> [ Data Store 3: Staged Package ]
             |                                         (freight_delivery_package/)
             v (Order Specs)
  ( Process 5: Monocypher AdminPort Client )
------------------------------------------------------------------------------------------------
[TRUST BOUNDARY 3: OPENTTD SIMULATION ENGINE RUNTIME]
------------------------------------------------------------------------------------------------
             |
             | (7) Encrypted Challenge-Response & Command Frames (TCP 127.0.0.1:3977)
             v
  [ OpenTTD AdminPort Listener ]
             |
             | (8) Execute Company Directives (GSCompanyMode)
             v
  ( Process 6: GameScript Runner - .nut Bridge )
             |
             +--- (9) Mutate Game World State ---> [ Data Store 4: World Savegame ]
             |                                     (*.sav binary state)
             v (10) Operation Telemetry & Unload Receipts
  ( Process 7: Independent Readback Verifier )
             |
             +--- (11) Persist Immutable Proof ---> [ Data Store 5: Run Receipts Store ]
                                                    (artifacts/runtime/*)
================================================================================================
```

---

## 4. Trust Boundaries Specification

| Boundary ID | Boundary Name | Outside (Less Trusted) | Inside (More Trusted) | Security Controls Enforced |
| :--- | :--- | :--- | :--- | :--- |
| **TB-1** | **Untrusted External Zone** | Human CLI input, OS Environment Variables, File Paths | Input Sanitizer (Process 1) | Strict Argument Parsing, Canonical Path Resolution (`.resolve()`), Base Jail Verification (`is_relative_to`), Denial of relative `../` traversal |
| **TB-2** | **Python Planning Container** | Sanitized Specs, Ephemeral File System | P08, P05, Freight Compiler (Processes 2-5) | SHA-256 Digest Verification, In-memory Domain Modeling (`ExecutionPlan`), Hermetic Package Staging, Separation of Concerns |
| **TB-3** | **OpenTTD Engine Runtime** | AdminPort Client TCP Socket | OpenTTD C++ Core, GameScript (.nut) Engine | Monocypher Passphrase Handshake, Loopback Socket Binding (`127.0.0.1`), Non-blocking Fallback Strategy for GameScript Orders |

---

## 5. Critical Asset Inventory

The assets of the system are categorized by the CIA Triad (Confidentiality, Integrity, Availability):

| Asset ID | Asset Name | Description & Location | Security Tier | Primary CIA Requirement | Business & Safety Impact |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **AST-01** | **Authority Manifests** | SHA-256 Digest Manifests (`docs/authority/`) | **CRITICAL** | **Integrity** | Tampering would permit execution of untested, uncertified binary code or modified game saves. |
| **AST-02** | **AdminPort Passphrase** | Shared secret token for OpenTTD AdminPort connection | **CRITICAL** | **Confidentiality / Integrity** | Compromise enables arbitrary unauthorized vehicle purchases and demolition of company assets. |
| **AST-03** | **ExecutionPlan Spec** | Domain object containing vehicle dispatch orders | **HIGH** | **Integrity** | Corrupted plan flags cause vehicles to jam at depots or reject cargo unloads (Flag 132 bug). |
| **AST-04** | **Candidate Road Cache** | Pre-computed road network tiles (`p08_candidates.json`) | **MEDIUM** | **Integrity** | Malformed data crashes the CP-SAT solver or causes infinite pathfinding loops. |
| **AST-05** | **Run Receipts & Proof** | Historical immutable evidence (`artifacts/runtime/`) | **MEDIUM** | **Integrity** | Must remain read-only to preserve legal and grading evidence of software correctness. |

---

## 6. Formal Misuse Cases

To ensure thorough defensive engineering, three concrete Misuse Cases have been formally modeled:

### MC-01: Path Traversal Injection (CWE-22)
* **Threat Actor:** Malicious local user or compromised script environment.
* **Attack Vector:** Providing crafted parameters such as `--config-path=../../../../etc/shadow` or passing symlink directory traps.
* **Intended Impact:** Read sensitive system secrets or overwrite root authority manifests.
* **Defensive Mitigation:** Process 1 enforces canonicalization via `Path(untrusted).resolve()` and asserts `resolved.is_relative_to(BASE_JAIL_DIR)`. Any violation raises `PermissionError` immediately (Fail-Closed).

### MC-02: GameScript Payload Tampering (CWE-354 / Tampering)
* **Threat Actor:** Malicious background process on host.
* **Attack Vector:** Modifying `.nut` files staged inside `freight_delivery_package/` before OpenTTD loads them into `GSCompanyMode`.
* **Intended Impact:** Execute unauthorized game script commands (e.g. bankrupting company funds or deleting rival infrastructure).
* **Defensive Mitigation:** Staged packages are verified against cryptographic hashes recorded in the project manifest before triggering OpenTTD launch.

### MC-03: AdminPort Command Injection & Replay (CWE-306 / Spoofing)
* **Threat Actor:** Local unauthorized process listening or sending packets on port 3977.
* **Attack Vector:** Sending forged TCP frames to inject `VehicleOrder` commands without completing the authentication handshake.
* **Intended Impact:** Desynchronize Python planning state from game engine state, causing truck deadlocks.
* **Defensive Mitigation:** AdminPort interface requires an initial Monocypher encrypted handshake. Subprocess listens strictly on `127.0.0.1` and terminates upon any socket framing anomaly.

---

## 7. Security Requirements Specification (SRS)

- **SR-01 (Strict Path Jail):** All file operations accessing fixtures, saves, or configurations MUST resolve the absolute path and verify containment within the repository root jail via `Path.is_relative_to()`.
- **SR-02 (Cryptographic Integrity Gate):** Execution of native engine runs MUST verify the SHA-256 hash of `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE` against values pinned in `docs/authority/`.
- **SR-03 (Authenticated Administrative Bridge):** The Python client connecting to OpenTTD AdminPort MUST authenticate using the configured password before issuing any company directives.
- **SR-04 (Read-Only Historical Evidence):** All retained test and execution receipts in `artifacts/` MUST be treated as immutable historical records; no process may overwrite existing attempt directories.
- **SR-05 (User-Gated Native Authorization):** Native execution of the OpenTTD binary and live AdminPort socket connections MUST remain blocked unless explicitly authorized by the operator via `--run-openttd`.
- **SR-06 (Fail-Closed Exception Discipline):** Any cryptographic mismatch, path traversal attempt, or protocol framing error MUST terminate execution immediately without graceful fallback to insecure defaults.
