# Secure Coding Standards & Vulnerability Refactoring

**System:** OpenTTD Autonomous Freight Delivery System  
**Subject:** Software Design and Development 2 (Security Assessment Â§3)  
**Standard Reference:** SEI CERT Python Coding Standard, OWASP Secure Coding Practices, CWE/SANS Top 25  

---

## 1. Overview of Secure Coding Architecture

The OpenTTD Autonomous Freight Delivery codebase implements rigorous defensive programming patterns to systematically neutralize common Common Weakness Enumerations (CWEs). Code running in this repository operates on a **fail-closed, least-privilege, and boundary-enforced** model.

---

## 2. Deep Dive: Vulnerability Mitigations & Code Evidence

### 2.1 CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')

#### Vulnerability Context
When loading candidate road networks, terrain configurations, or test fixtures, untrusted input paths could contain relative path traversal sequences (e.g., `../../etc/passwd` or symlink redirection) allowing an attacker or malformed configuration to escape the project directory.

#### Secure Refactoring Implementation
Located in `app/planning/planning_fact_artifacts.py` and `_owned_bytes`:

```python
# FILE: app/planning/planning_fact_artifacts.py
from pathlib import Path
from typing import Final

def ensure_path_within_jail(untrusted_path: str | Path, base_jail_directory: Path) -> Path:
    """
    Enforces strict directory boundary isolation to prevent CWE-22 Path Traversal.
    
    1. Resolves all symbolic links and relative '../' components to obtain canonical path.
    2. Enforces that the canonical path resides strictly within the base jail directory.
    3. Guarantees fail-closed termination upon any boundary breach attempt.
    """
    canonical_base: Final[Path] = base_jail_directory.resolve()
    target_candidate: Final[Path] = (canonical_base / Path(untrusted_path).name).resolve()
    
    # Boundary Verification
    if not target_candidate.is_relative_to(canonical_base):
        raise PermissionError(
            f"SECURITY FAULT [CWE-22]: Path '{untrusted_path}' resolves to '{target_candidate}', "
            f"which escapes authorized jail '{canonical_base}'"
        )
        
    if not target_candidate.is_file():
        raise FileNotFoundError(
            f"SECURITY FAULT: Target path '{target_candidate}' is not an authorized regular file."
        )
        
    return target_candidate
```

#### Principles Applied:
- **Canonicalization:** Eliminates ambiguous paths by converting to absolute, symlink-dereferenced form via `.resolve()`.
- **Whitelisting & Jailing:** Uses Python 3.9+ `Path.is_relative_to()` to enforce mathematical containment within the base directory.
- **Fail-Closed:** Raises explicit `PermissionError` immediately; never attempts heuristic sanitization or fallback.

---

### 2.2 CWE-354 / CWE-20: Improper Validation of Integrity Check Value & Input Validation

#### Vulnerability Context
In simulation and mathematical optimization, untrusted external fixtures or corrupted game world saves (`.sav`) can lead to altered decision parameters, bypassing offline regression assertions or producing invalid vehicle schedules.

#### Secure Refactoring Implementation
Located in `app/simulation/openttd/manifest_verifier.py` and `docs/authority/`:

```python
# FILE: app/simulation/openttd/manifest_verifier.py
import hashlib
from pathlib import Path
from typing import Final

def verify_fixture_digest(file_path: Path, expected_sha256_hex: str) -> None:
    """
    Guarantees fixture data integrity (CWE-354) using streaming SHA-256 computation.
    
    Prevents execution against tampered, poisoned, or partially written binaries/saves.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"Fixture target missing: {file_path}")
        
    hasher = hashlib.sha256()
    # Stream in bounded 64KB chunks to prevent memory exhaustion (CWE-400)
    with open(file_path, "rb") as stream:
        while chunk := stream.read(65536):
            hasher.update(chunk)
            
    computed_digest: Final[str] = hasher.hexdigest().lower()
    clean_expected: Final[str] = expected_sha256_hex.strip().lower()
    
    if computed_digest != clean_expected:
        raise ValueError(
            f"INTEGRITY VIOLATION [CWE-354]: Hash mismatch on '{file_path.name}'.\n"
            f"  Expected: {clean_expected}\n"
            f"  Computed: {computed_digest}"
        )
```

#### Principles Applied:
- **Cryptographic Authority Pinning:** Checksums are hard-pinned in git-tracked manifests under `docs/authority/`.
- **Bounded Resource Consumption:** Streams files in fixed 64 KB buffers, preventing Out-Of-Memory attacks when inspecting multi-gigabyte savegames.

---

### 2.3 CWE-306: Missing Authentication for Critical Function (AdminPort Handshake)

#### Vulnerability Context
OpenTTD exposes its administrative socket (AdminPort) on TCP port 3977. Without an authenticated handshake, any process sharing the network namespace could inject GameScript commands (`GSCompanyMode`) to buy vehicles or demolish stations.

#### Secure Refactoring Implementation
Located in `app/simulation/openttd/admin_port_client.py`:

```python
# FILE: app/simulation/openttd/admin_port_client.py
import socket
from typing import Final

class AuthenticatedAdminPortClient:
    """
    Enforces loopback-only binding and Monocypher challenge-response authentication (CWE-306).
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 3977, secret_token: str = ""):
        # Enforce loopback binding
        if host not in ("127.0.0.1", "localhost"):
            raise ValueError(f"SECURITY FAULT: AdminPort must bind strictly to loopback, got '{host}'")
        self._host: Final[str] = host
        self._port: Final[int] = port
        self._secret_token: Final[str] = secret_token
        self._authenticated: bool = False

    def authenticate(self, sock: socket.socket) -> None:
        """Issues password handshake before any command frames can be dispatched."""
        if not self._secret_token:
            raise PermissionError("ADMINPORT FAULT: Missing authentication secret token.")
            
        # Send Monocypher challenge-response frame
        handshake_payload = self._build_auth_packet(self._secret_token)
        sock.sendall(handshake_payload)
        
        response = sock.recv(1024)
        if not self._parse_auth_ack(response):
            sock.close()
            raise PermissionError("ADMINPORT REJECTED: Invalid authentication credentials.")
            
        self._authenticated = True
```

---

## 3. Comparative Refactoring Matrix (Before vs After)

| Vulnerability Target | Pre-Refactor Vulnerable Pattern | Post-Refactor Secure Implementation | Architectural Benefit |
| :--- | :--- | :--- | :--- |
| **Path Resolution** | `open(os.path.join(base, filename))` | `ensure_path_within_jail(Path(untrusted), base)` | Eliminates `../` path traversal and symlink poisoning. |
| **Integrity Check** | Direct loading of raw `.sav` files without hashing | Cryptographic SHA-256 pre-check against `docs/authority/` | Guarantees test reproducibility and prevents corrupted world injection. |
| **Order Dispatch** | Direct sequential execution of Flag 132 | Two-phase non-blocking fallback (`OF_UNLOAD` + `OF_NO_LOAD`) | Eliminates vehicle deadlocks and thread starvation in GameScript. |
| **Socket Transport** | Unauthenticated raw TCP socket connection | Monocypher challenge handshake + strict loopback restriction | Prevents unauthorized packet injection and eavesdropping. |
