# 05: Candidate-8 Gate C signature

**What to build:** the operator's Gate C Option-1 signature over the
reviewed candidate-8 — one signing operation via the production signing
surface, bound to candidate-8's exact seal, the seed mechanics exactly as
the rounds of record ran them.

**Blocked by:** 04. **Blocked-to:** 06 (the one launch)

**Status:** ready-for-agent (its round needs the operator's signing
approval in-session)

- [ ] Pre-write refusal gates hold: gate surface absent; live seal ==
      sidecar == the operator-approved seal; payload digest of record ==
      production re-derivation; the scope binding this round's staged
      identity
- [ ] Seed mechanics: operator-held armored PEM, 48-byte DER final-32
      RFC 8032 seed window, memory-only, env-only `CARGOFLOW_GATE_SEED`,
      never printed/filed; `public_from_seed(seed)` == the pinned anchor
      and the operator key identity unchanged of record
- [ ] `AUTHORIZATION.json` written exactly once (record digest of record
      booked); production `verify_authorization` passes against the
      seeded anchor; no repeat sign
- [ ] Post-write read-only state: root staged entries +
      `AUTHORIZATION.json`; seal byte-equal; `PREFLIGHT PASS` with
      authorization present; standalone `verify` still
      `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT` exit 1; seed env unset
      + empty at the end; all candidate PRELAUNCH byte-pictures before ==
      after; one commit, no push
