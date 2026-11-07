# 03r6: Round-6 Gate C signature

**What to build:** the operator's Gate C Option-1 signature over the
reviewed round-6 candidate — one signing operation via the production
signing surface only (payload derivation → canonical bytes → signature →
record write), bound to the freshly staged candidate-6 exact seal, with the
seed mechanics exactly as the rounds of record already ran them (memory-only
extraction, env-only, never printed or filed), followed by read-only
post-state verification.

**Blocked by:** 02r6 (Round-6 independent review) — the operator signing
approval is the in-session gate that authorizes it (granted in-session
2026-11-05 via the explicit gate option "Approve Gate C", which also covers
the books commit convention).

**Status:** done 2026-11-05 (operator approval in-session; ONE signing
operation, first invocation, zero refusals, zero re-writes)

- [x] Pre-write refusal gates hold: gate surface absent (no
      AUTHORIZATION/CLAIM/LAUNCH-CONSUMED/terminal artifacts), live seal ==
      sidecar == the operator-approved seal
      `e929d7b2e749f2a14af9bb19fdf12f76f96fe912e7f1d716af733a44d926ec49`,
      hard-asserted before any write; authorization payload digest of record
      `5433b7e5477ec2ffedf722b623ad1d3cc8f5777b7469b11d65659da420a108eb`
      cross-checked == the production staged-payload digest derivation
      (`staged_cargoflow2_authorization_payload_digest`, staged ==
      re-derivation), fresh round-6 signer driver
      `/tmp/opencode/gate_c_cargoflow2_c6.py` (the round-bound prior scripts
      never reused), transcript
      `/tmp/opencode/t6_gate_c_output.txt`
- [x] Seed mechanics of record: the operator-held PEM
      (`~/.local/share/openttd-operator/operator-private.pem`, 48-byte
      PKCS#8 window verified pre-run, never opened by anything else) is
      carried into the final-32 seed window memory-only, env-only
      `CARGOFLOW_GATE_SEED` (base64), never printed, never filed, never
      passed as an argument; pre-write `public_from_seed(seed)` == pinned
      anchor `5063982bd28d48573705f334ed4f396618c4930ce21083789dfbbf13a564880f`
      and operator key identity unchanged of record
      `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`
- [x] `AUTHORIZATION.json` written exactly once; record sha256 of record
      `e938eb62807965e864f3c5dade973d5259675187a406745a963bb724712f7e5c`;
      production `verify_authorization` reads the written record and passes
      against the seeded anchor (record digest bound: True); no signing ever
      repeated
- [x] Post-write read-only state: root = 5 entries (4 staged files +
      `AUTHORIZATION.json`; no CLAIM / no LAUNCH-CONSUMED); seal byte-equal
      after the write (`e929d7b2…ec49`); production `preflight` re-run
      `PREFLIGHT PASS` exit 0 with the authorization present; standalone
      `verify` still `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`
      exit 1 by design (the claim mints at the launch boundary only)
- [x] No candidate bytes beyond the authorization record touched; candidates
      1–6 PRELAUNCH byte-pictures before == after; historical zones
      byte-untouched; `git diff --check` clean; `CONTEXT.md` pin intact;
      seed env unset + empty verified at the end
- [x] Signing row appended to the PoC backlog status log (record digest,
      payload digest, operator identity, one-write discipline); ticket +
      row booked in one commit per the grant
