# 03r7: Round-7 Gate C signature

**What to build:** the operator's Gate C Option-1 signature over the
reviewed round-7 candidate-7 (the adjudicated v2-carrying composition)
— one signing operation via the production signing surface only (payload
derivation → canonical bytes → signature → record write), bound to the
freshly staged candidate-7 exact seal `9c5f7272…e19257`, with the seed
mechanics exactly as the rounds of record already ran them (the
operator-held PEM carried into the final-32 seed window memory-only,
env-only, never printed or filed), followed by read-only post-state
verification.

**Blocked by:** 02r7 (Round-7 independent review, `READY-FOR-GATE-C`)
— the operator signing approval is the in-session gate that authorizes
it (granted in-session 2026-11-06 via the explicit gate option "Grant
Gate C signing round", which also covers the books commit convention).

**Status:** done 2026-11-06 (operator approval in-session; ONE signing
operation, first invocation, zero refusals, zero re-writes)

- [x] Pre-write refusal gates hold: gate surface absent (no
      AUTHORIZATION/CLAIM/LAUNCH-CONSUMED/result artifacts), live seal ==
      sidecar == the operator-approved seal
      `9c5f727200efa7b896ab2b8016d5183b1f1ee62baff7bfa204eb60bf01e19257`,
      hard-asserted before any write; authorization payload digest of
      record `f1d210cf17704fd1ad21d706160d1d6d03d417e0fa7585ac6a3d30a3e41df15c`
      cross-checked == the production staged-payload digest derivation
      (`staged_cargoflow2_authorization_payload_digest`, staged ==
      re-derivation); the attempted scope binds this round's own staged
      identity (`route_version 2` beside `schedule_version 1`, plan
      digest `5c0998f2…bf2d`, attempt `D5-CARGOFLOW-2`); fresh round-7
      signer driver `/tmp/opencode/gate_c_cargoflow2_c7.py` (the
      round-bound prior drivers never reused), transcript
      `/tmp/opencode/gate_c_c7_output.txt`
- [x] Seed mechanics of record: the operator-held armored PKCS#8 PEM
      (`~/.local/share/openttd-operator/operator-private.pem`, its
      48-byte DER carrying the final-32 RFC 8032 seed window, verified
      pre-run without reading or printing the key bytes any further) is
      carried into the seed window memory-only, env-only
      `CARGOFLOW_GATE_SEED` (base64), never printed, never filed, never
      passed as an argument; pre-write `public_from_seed(seed)` ==
      pinned anchor
      `5063982bd28d48573705f334ed4f396618c4930ce21083789dfbbf13a564880f`
      and operator key identity unchanged of record
      `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`
- [x] `AUTHORIZATION.json` written exactly once; record sha256 of record
      `24ccab3ec5b1140cb2c008eda7217810f4612aa4254e8bd98166813a3d9b6417`;
      production `verify_authorization` reads the written record and
      passes against the seeded anchor (record digest bound: True); no
      signing ever repeated; the seed-window variables dropped from the
      driver's memory immediately after the write
- [x] Post-write read-only state: root = 5 entries (4 staged files +
      `AUTHORIZATION.json`; no CLAIM / no LAUNCH-CONSUMED); seal
      byte-equal after the write (`9c5f7272…e19257`); production
      `preflight` re-run `PREFLIGHT PASS` exit 0 with the authorization
      present; standalone `verify` still `AUTHORIZATION_UNVERIFIED` /
      `CLAIM_ABSENT` exit 1 by design (the claim mints at the launch
      boundary only)
- [x] No candidate bytes beyond the authorization record touched; all
      seven candidates' PRELAUNCH byte-pictures before == after
      (the seal is candidate-7's own digest); historical zones
      byte-untouched; `git diff --check` clean; `CONTEXT.md` pin
      intact; seed env unset + empty verified at the end in a fresh
      shell
- [x] Signing row appended to the PoC backlog status log (record
      digest, payload digest, operator identity, one-write discipline);
      ticket + row booked in one commit per the grant
