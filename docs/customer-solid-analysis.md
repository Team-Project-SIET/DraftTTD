# SOLID, cohesion and coupling — source-level analysis (2026-11-13)

This document answers the customer question: *how does the codebase hold up
against SOLID principles, high cohesion and low coupling?* Every claim is
anchored to real source on branch `miles/fright-delivery` (HEAD `90ebadb`),
cited as `file:line`. It is intentionally **not** a claim of wholesale SOLID
compliance: it presents verified examples of each principle where they
materially shape the system, and it names the places where the design is
pragmatic rather than textbook.

Status labels follow the vocabulary in
[CUSTOMER_PRESENTATION_INDEX.md](CUSTOMER_PRESENTATION_INDEX.md) §1. This is a
documentation-only deliverable; it authorizes no runtime action.

## 1. Method

- Classes, protocols and seams were read directly from `app/` before writing;
  no claim is made from documentation alone.
- Each principle is evidenced by one or two source examples that were
  re-read at citation time.
- Where the codebase departs from the principle, that departure is stated
  (§6), so the analysis stays useful and honest.

## 2. SOLID — principle by principle

### 2.1 Single Responsibility Principle (SRP) — VERIFIED example

**Example: `PacketCipher` — `app/simulation/openttd/admin_crypto.py:92-133`.**

```python
class PacketCipher:
    """One persistent directional Monocypher context, closed on any decode failure."""
```

This class has exactly one responsibility and one reason to change: the
framing, integrity and lifecycle of one directional encrypted packet stream.

- It owns only crypto mechanics: length/framing validation
  (`admin_crypto.py:105-114`), encryption (`:116-124`), decryption with
  authentication (`:126-133`), and closing (`:101-103`).
- It knows nothing about the Admin protocol state machine, reconnection
  policy, or GameScript semantics — those live in other modules
  (`secure_admin.py`, `admin_session.py`, `gamescript_transport.py`).
- Its failure posture is part of the single responsibility: any invalid
  framing or failed MAC permanently closes the context (`:107`, `:113`,
  `:131`), so the class cannot be half-used after a failure.

**Second example: `app/planning/validation.py`.** The module's whole surface is
prelaunch validation of a typed plan/scenario pair. `_require(...)` guards
raise typed `PlanningFailureCode` failures (`validation.py:73-77`) and the
public boundary re-parses even typed inputs so validation cannot be bypassed
(`:78-86`). Nothing else — no execution, no I/O — lives in that module.

### 2.2 Open/Closed Principle (OCP) — VERIFIED example (additive extension)

The transport layer was extended across milestones **without modifying
established protocol surfaces**, by adding new numbered protocol families:

- Freight (protocol 5) and survey (protocol 6) sessions coexist with
  explicitly assigned numbers; the box-census round designed *protocol 9* on
  top of "number allocation 4/5/6/7/8 taken" and cites the additive-protocol
  precedent (E59, `docs/d5-box-census-1-protocol-design-2026-11-02.md`).
- The survey pipeline was added as its own narrow pipeline rather than an
  edit to the freight pipeline, explicitly refusing cross-plan abuse: a
  `FreightPlan` fails the survey session's protocol-6 check and vice versa
  (E36-b; `app/simulation/openttd/proof/corridor_accept_survey_native.py`).
- New GameScript package families are composed additively by the staging
  runner (`app/simulation/openttd/freight_delivery_package/` and the census
  package `d5_census_package/`, E60) — staged-package correspondence is
  re-verified per attempt instead of editing a shared mutable package.

The closed-for-modification side is the contract surface: existing retained
attempts replay byte-equal after every extension (E134's fix preserved the
v1 candidates' replay math untouched).

### 2.3 Liskov Substitution Principle (LSP) — VERIFIED example (strengthening subclass)

**Example: `SecureAdminSession.validate_outbound` —
`app/simulation/openttd/secure_admin.py:188-191`.**

```python
def validate_outbound(self, frame: bytes) -> None:
    if self.state is not AuthState.ACTIVE:
        raise AuthProtocolError("Admin application traffic requires ACTIVE")
    super().validate_outbound(frame)
```

The subclass substitutes for its base session everywhere, and only ever
**strengthens** the base contract: it requires the `ACTIVE` state before
application traffic and delegates the base checks unchanged. It never widens
acceptability, never silently drops validation, and fails with a typed
exception instead of tolerating an invalid state. This is the safe direction
of behavioral subtyping: callers written against the base contract remain
correct; the secure variant refuses more, never less.

### 2.4 Interface Segregation Principle (ISP) — VERIFIED example

**Example: `AdminWriter` Protocol —
`app/simulation/openttd/admin_session.py:14-20`.**

```python
class AdminWriter(Protocol):
    def write(self, data: bytes, /) -> None: ...
    async def drain(self) -> None: ...
    def close(self) -> None: ...
    async def wait_closed(self) -> None: ...
    def is_closing(self) -> bool: ...
    def get_extra_info(self, name: str) -> object: ...
```

Consumers of the admin session depend on this six-method structural protocol
rather than on `asyncio.StreamWriter` in full. The session code works with
any object that satisfies the shape (a real writer in production, a stub in
tests), which keeps the protocol logic testable without sockets and keeps the
session module decoupled from asyncio transport internals.

### 2.5 Dependency Inversion Principle (DIP) — VERIFIED example

**Example: frozen contract models at the planning seams —
`app/planning/domain.py:46-47`.**

```python
class Contract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)
```

High-level planning policy does not depend on dicts, raw frames, or the
transport. It depends on frozen, strict, closed-world Pydantic models
(`Contract` and its subclasses such as `ExecutionPlan` and
`PlanningScenario`). Both the producers (P08 candidate generation, P05
optimizer) and the consumer (the prelaunch validation boundary) depend on the
same abstraction:

- The optimizer consumes typed candidate/plan structures
  (`app/planning/optimizer.py`, P05 CP-SAT selection).
- The validation boundary enforces the abstraction at its only public entry
  point, re-parsing even typed inputs so a `model_copy(update=...)` bypass is
  impossible (`app/planning/validation.py:78-86`).

The frozen configuration anchor for planning is `Contract`'s config at
`domain.py:46-47` — immutability is part of the dependency contract, not an
afterthought.

## 3. Cohesion — VERIFIED examples

- **Crypto cohesion:** `PacketCipher` (above) contains only one concern; the
  rest of `admin_crypto.py` is the key-derivation and authentication ceremony
  (`AuthorizedKey`, `DerivedKeys`, `derive_keys`, `authentication_response`,
  `admin_crypto.py:25-89`) — related, single-domain code with no protocol or
  session logic.
- **Canonical identity cohesion:** `app/planning/canonical.py` owns canonical
  digest/identity rules only; consumers (`p08_*`, optimizer, validation)
  reference the rules instead of re-deriving them.
- **Bounded-candidate cohesion:** the P08 modules split by concern —
  `p08_road.py` / `p08_network.py` (candidate construction) versus
  `p08_adapter.py` (the narrow seam into planning; see the adapter's
  single-entry surface, `app/planning/p08_adapter.py:10-59`).

## 4. Coupling — VERIFIED examples

- **Data coupling over shared state:** the transport stack communicates in
  bytes plus typed exceptions (`CryptoError`, `TransportProtocolError`,
  `AuthProtocolError`, `AuthTimeout`, `AuthDisconnected` —
  `secure_admin.py:182-191`); no module reaches into another's internals.
- **Protocol decoupling:** `AdminWriter` (ISP above) means the session module
  is structurally decoupled from the concrete asyncio writer class.
- **Digest coupling:** the proof harness couples components by content —
  sha256 freeze pins verified before any launch
  (`app/simulation/openttd/proof/harness.py:102-104`) — rather than by
  shared mutable configuration.
- **Identity coupling:** planning modules exchange canonical digests
  (`Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]`,
  `app/planning/domain.py:41`), so cross-module agreement is checked against
  a value, not a shared reference.

## 5. Summary table

| Principle | Verdict on the examples cited | Primary evidence |
| --- | --- | --- |
| SRP | Applied where it matters most: crypto, validation | `admin_crypto.py:92-133`, `validation.py` |
| OCP | Applied by additive protocol families and additive package composition | E59, E36-b, E60 |
| LSP | Applied at the secure session seam; subclass strengthens only | `secure_admin.py:188-191` |
| ISP | Applied at the writer boundary | `admin_session.py:14-20` |
| DIP | Applied via frozen typed contracts at planning seams | `domain.py:46-47`, `validation.py:78-86` |
| High cohesion | Strong in crypto/validation/canonical/P08 seams | §3 |
| Low coupling | Bytes + typed exceptions, protocols, digests, freeze pins | §4 |

## 6. Honest departures (no overclaim)

- **Orchestration modules are wide.** The native proof pipelines (for example
  `app/simulation/openttd/proof/corridor_cargoflow2_native.py`) deliberately
  keep staging, preflight, execution and replay in one large module so the
  attempt's whole story stays inspectable; that trades some SRP purity for
  auditability of the ceremony. Refactors here are recorded as future work,
  not claimed as done.
- **SOLID is not a compliance certificate.** These examples show the
  principles actively shaping the security seams and the planning core. They
  do not certify every module, and this document never presents them as such.
- **Test coupling is deliberate.** Focused suites pair offline tests with
  controlled native tests per component (`tests/test_X.py` /
  `tests/test_X_native.py`); some offline tests bind to retained evidence
  digests, which couples tests to artifacts by design (missing evidence
  fails loudly rather than silently passing).

## 7. Related documents

- Class inventory and relationships: [customer-uml-classes.md](customer-uml-classes.md)
- Architecture overview: [customer-architecture.md](customer-architecture.md)
- Security-relevant design of record: [secure-admin-transport.md](secure-admin-transport.md)
