# Software Security & Quality Assurance Suite

This directory contains the authoritative Security and Software Quality Assurance documentation for the **OpenTTD Autonomous Freight Delivery System**, prepared in accordance with the evaluation criteria of **Software Design and Development 2** (Assessed by Assoc. Prof. Surachai).

---

## Documentation Index

| Document | Assessment Category | Description | Primary Standard |
| :--- | :---: | :--- | :--- |
| **[1. Threat Modeling & DFD](threat-model-dfd.md)** | **20%** | Comprehensive DFD Level 0 & 1, 3 Trust Boundaries, 5 Data Stores, 8 Data Flows, 3 Misuse Cases, Asset Inventory, and Security Requirements. | NIST SP 800-53 / OWASP |
| **[2. Risk Register & Assessment](risk-register.md)** | **10%** | Quantitative & qualitative risk evaluation, 5x5 Matrix, STRIDE classification, preventive mitigations, and residual risk burn-down. | ISO 31000 / NIST SP 800-30 |
| **[3. Secure Coding Standards](secure-coding-standards.md)** | **20%** | In-depth code walkthrough of CWE-22 (Path Traversal Jail), CWE-354 (SHA-256 Digest Lock), and CWE-306 (AdminPort Monocypher Handshake). | SEI CERT Python / CWE Top 25 |
| **[4. Requirements Traceability Matrix](traceability-matrix.md)** | **10%** | Full bidirectional mapping from Requirements and Threats to Architectural Components, Implementation Files, and Pytest assertions. | IEEE Std 829 / ISO 29119 |
| **[5. Automated CI/CD & Deployment](cicd-automation.md)** | **40%** | GitHub Actions CI & CD workflows, `Dockerfile` (non-root), SHA-256 bundle verification, and clean-room deployment smoke tests. | GitHub Actions / Docker / UV |

---

## Executive Summary of Compliance

* **Threat Modeling Completeness:** Includes external untrusted boundaries, secure host planning container, and isolated OpenTTD simulation engine.
* **Zero Vulnerabilities in Core Paths:** CWE-22 and CWE-354 are neutralized via fail-closed assertions before any disk or socket I/O.
* **Test Verification Baseline:** 100% pass rate across 240 test cases executed in 17.84 seconds.
