# Software Security Risk Register & Assessment

**System:** OpenTTD Autonomous Freight Delivery System  
**Framework:** ISO 31000 / STRIDE Risk Assessment Framework  
**Subject:** Software Design and Development 2 (Security Assessment Â§2)  
**Evaluation Standard:** NIST Special Publication 800-30 Rev. 1  

---

## 1. Risk Assessment Methodology

Risks are assessed based on the qualitative evaluation of **Likelihood** (frequency or feasibility of exploitation) and **Impact** (severity of damage to system integrity, assets, or academic correctness).

### 1.1 Scoring Scales (1 to 5)

* **Likelihood Scale:**
  1. **Rare:** Requires theoretical attack vector, extensive reverse-engineering, and internal collusion.
  2. **Unlikely:** Feasible under non-standard configurations with insider access.
  3. **Moderate:** Possible with standard CLI access or crafted local file payloads.
  4. **Likely:** Readily accessible vector via parameter passing or script modification.
  5. **Almost Certain:** Common bug class; trivial to trigger without security controls.

* **Impact Scale:**
  1. **Insignificant:** Minor cosmetic or telemetry log format variation.
  2. **Minor:** Non-fatal warning; transient process delay.
  3. **Moderate:** Single run termination or simulation vehicle order rejection.
  4. **Major:** Desynchronization of simulation state; unauthorized asset expenditure.
  5. **Catastrophic:** System file compromise, arbitrary code execution, or destruction of immutable historical evidence.

### 1.2 Risk Matrix & Evaluation Thresholds

$$ \text{Risk Score} = \text{Likelihood} \times \text{Impact} \quad (\text{Range: } 1 \text{ to } 25) $$

* **Extreme Risk (16 - 25):** Red Alert â€” Deployment blocked until mitigation verified.
* **High Risk (10 - 15):** Urgent â€” Requires architectural defense and unit test assertion.
* **Medium Risk (5 - 9):** Moderate â€” Defensive validation and exception handling required.
* **Low Risk (1 - 4):** Acceptable â€” Routine operational monitoring.

---

## 2. Comprehensive System Risk Register

| Risk ID | Threat Description & Attack Vector | STRIDE | Initial L | Initial I | Initial Score | Preventive & Detective Controls (Mitigation) | Residual L | Residual I | Residual Score | Risk Status | Verification Artifact |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **RSK-01** | **Path Traversal via Config or Fixture Path (CWE-22)**<br>Passing `../../` or symlinks to read sensitive files outside workspace. | Elevation of Privilege | 4 | 5 | **20 (EXTREME)** | Strict canonical path resolution via `.resolve()` and verification using `Path.is_relative_to(ROOT_JAIL)`. Rejection of all parent dir sequences. | 1 | 3 | **3 (LOW)** | **MITIGATED** | `app/planning/planning_fact_artifacts.py`<br>`tests/test_security_jail.py` |
| **RSK-02** | **Tampering with Authority Manifests or Savegames (CWE-354)**<br>Direct modification of test fixtures or authority hashes to force false test passes. | Tampering | 3 | 5 | **15 (HIGH)** | Cryptographic SHA-256 Digest Lock recorded in `docs/authority/`. Pre-execution hash validation against immutable git-pinned values. | 1 | 2 | **2 (LOW)** | **MITIGATED** | `docs/authority/*.json`<br>`tests/test_authority_digest.py` |
| **RSK-03** | **Unauthorized AdminPort Socket Access (CWE-306)**<br>Local rogue process connects to port 3977 and commands in-game vehicles. | Spoofing | 3 | 4 | **12 (HIGH)** | Binding AdminPort strictly to `127.0.0.1` (loopback). Enforcement of Monocypher cryptographic challenge-response before accepting orders. | 1 | 3 | **3 (LOW)** | **MITIGATED** | `app/simulation/openttd/`<br>`tests/test_admin_client.py` |
| **RSK-04** | **Unintended / Ungated Native OpenTTD Execution**<br>Accidental launch of native engine modifying unreviewed state. | Information Disclosure | 4 | 3 | **12 (HIGH)** | User-Gated execution contract. Engine launch hard-blocked unless `--run-openttd` is explicitly set in interactive turn. Single attempt, zero reconnect. | 1 | 4 | **4 (LOW)** | **MITIGATED** | `app/openttd_demo.py`<br>`AGENTS.md` Â§Safety |
| **RSK-05** | **Race Condition on AdminPort Command Delivery (CWE-367)**<br>Python sends orders faster than OpenTTD game ticks process them, dropping commands. | Denial of Service | 3 | 3 | **9 (MEDIUM)** | Tick-synchronized handshake and non-blocking readback verification. Awaiting acknowledgment receipt before emitting subsequent frames. | 1 | 3 | **3 (LOW)** | **MITIGATED** | `app/simulation/openttd/freight_canonical_dispatch.py` |
| **RSK-06** | **Vehicle Order Flag 132 Unload Rejection Bug**<br>Engine rejects `OF_DELIVERY` flag causing trucks to block depots indefinitely. | Denial of Service | 4 | 3 | **12 (HIGH)** | GameScript-level fallback handler decomposing `OF_DELIVERY` into sequential non-blocking `OF_UNLOAD` and `OF_NO_LOAD` flags. | 1 | 2 | **2 (LOW)** | **MITIGATED** | `app/simulation/openttd/freight_delivery_package/corridor_freight_v2.nut` |

---

## 3. Residual Risk Burn-Down Analysis

The implementation of architectural safeguards has systematically eliminated all Extreme and High severity risks:

```
  Initial Risk Profile:
    [ Extreme: 1 ] [ High: 4 ] [ Medium: 1 ] [ Low: 0 ]
    
  Post-Mitigation Residual Risk Profile:
    [ Extreme: 0 ] [ High: 0 ] [ Medium: 0 ] [ Low: 6 ]
```

### 3.1 Defense Depth Justification
* **Fail-Closed Principle:** Under RSK-01 and RSK-02, any validation failure raises immediate fatal exceptions (`PermissionError`, `IntegrityError`) terminating execution before any native state mutation occurs.
* **Separation of Privileges:** Development and CI testing run strictly in offline mode (`tests/test_*.py`) without requiring OpenTTD native execution or network sockets.
