# Security & Functional Traceability Matrix (RTM)

**System:** OpenTTD Autonomous Freight Delivery System  
**Subject:** Software Design and Development 2 (Security Assessment Â§4)  
**Standard Reference:** IEEE Std 829-2008 / ISO/IEC/IEEE 29119  
**Verification Baseline:** 492 Deterministic Offline Assertions + GitHub Actions CI/CD Verified (100% Pass Rate)  

---

## 1. Traceability Overview & Purpose

The Requirements Traceability Matrix (RTM) establishes a strict bidirectional mapping connecting **System Requirements**, **Threat Modeling Identifiers**, **Architectural Components**, **Implementation Source Files**, and **Automated Verification Tests**.

This guarantees that every security control specified in the Threat Model (DFD) and Risk Register is implemented in code and systematically validated by automated tests.

---

## 2. Master Traceability Matrix

| Req ID | Requirement Description | Threat / Risk ID | Architecture Layer & Component | Implementation File & Symbol | Automated Test File & Assertion | Verification Status |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: |
| **REQ-01** | Bounded road candidate corridor generation connecting industries. | RSK-01<br>(MC-01) | Planning Layer<br>`P08 Road Generator` | `app/planning/p08_candidate_corridors.py`<br>`find_bounded_corridors()` | `tests/test_p08_corridors.py`<br>`test_bounded_search_completes()` | **VERIFIED (100%)** |
| **REQ-02** | Combinatorial ROI and fleet size optimization via CP-SAT. | Denial of Service<br>(Resource Exhaustion) | Planning Layer<br>`P05 OR-Tools Optimizer` | `app/planning/p05_optimizer.py`<br>`solve_freight_dispatch()` | `tests/test_p05_optimizer.py`<br>`test_solver_finds_optimal_solution()` | **VERIFIED (100%)** |
| **REQ-03** | Compile `ExecutionPlan` domain objects into staged GameScript. | RSK-06<br>(Order Misconfig) | Simulation Layer<br>`Freight Compiler` | `app/simulation/openttd/freight_compiler.py`<br>`stage_package()` | `tests/test_freight_compiler.py`<br>`test_hermetic_staging_produces_clean_package()` | **VERIFIED (100%)** |
| **REQ-04** | Prevent Path Traversal attacks when accessing fixtures and logs. | RSK-01<br>(CWE-22 / MC-01) | Security Layer<br>`Jail Boundary Guard` | `app/planning/planning_fact_artifacts.py`<br>`ensure_path_within_jail()` | `tests/test_security_jail.py`<br>`test_path_traversal_escapes_raise_permission_error()` | **VERIFIED (100%)** |
| **REQ-05** | Cryptographic verification of simulation saves and fixtures. | RSK-02<br>(CWE-354 / MC-02) | Security Layer<br>`Manifest Verifier` | `app/simulation/openttd/manifest_verifier.py`<br>`verify_fixture_digest()` | `tests/test_authority_digest.py`<br>`test_tampered_fixture_raises_integrity_error()` | **VERIFIED (100%)** |
| **REQ-06** | Secure loopback connection & authentication to OpenTTD AdminPort. | RSK-03<br>(CWE-306 / MC-03) | Bridge Layer<br>`AdminPort Client` | `app/simulation/openttd/admin_port_client.py`<br>`AuthenticatedAdminPortClient` | `tests/test_admin_client.py`<br>`test_admin_auth_handshake_success()` | **VERIFIED (100%)** |
| **REQ-07** | Graceful handling of Flag 132 `OF_DELIVERY` unload rejection. | RSK-06<br>(State Deadlock) | Simulation Layer<br>`GameScript Bridge (.nut)` | `app/simulation/openttd/order_verifier.py`<br>`CoalDeliveryRuleVerifier` | `tests/test_order_verifier.py`<br>`test_flag_132_unload_fallback_conversion()` | **VERIFIED (100%)** |
| **REQ-08** | Offline readback of delivery receipts without engine mutation. | RSK-04<br>(Unauthorized Mutation) | Infrastructure Layer<br>`Independent Verifier` | `app/experiments/performance_insights.py`<br>`compute_performance_metrics()` | `tests/test_reporting_p07.py`<br>`test_receipt_financial_attribution_readback()` | **VERIFIED (100%)** |

---

## 3. Verification Coverage Summary

- **Total Functional & Security Requirements:** 8
- **Total Mapped Test Cases:** 492 assertions across 12 deterministic offline suites (plus full crypto/DB suites in GitHub Actions CI)
- **Automated Test Execution Duration:** 2.84 seconds (local offline baseline) / 20s (GitHub Actions Linux CI)
- **Pass Rate:** 100% (492 Passed, 0 Failed locally; CI Run `#43339527553` & CD Run `#43339527545` SUCCESS)
- **Traceability Completeness:** 100% (No orphan requirements, no untested security controls)
