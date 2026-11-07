# 05: Candidate-8 Gate C signature

**What to build:** the operator's Gate C Option-1 signature over the
reviewed candidate-8 — one signing operation via the production signing
surface, bound to candidate-8's exact seal, the seed mechanics exactly as
the rounds of record ran them.

**Blocked by:** 04. **Blocked-to:** 06 (the one launch)

**Status:** done 2026-11-06 (the operator's combined in-session grant
"Grant Gate C + ONE launch — Recommended" covering this round and the
ONE native launch of ticket 06 with no further pausing; fresh
round-bound signer driver `/tmp/opencode/gate_c_cargoflow2_c9.py`
(never reused), transcript `/tmp/opencode/gate_c_c9_output.txt`; ONE
signing operation, first invocation, zero refusals, zero re-writes;
one commit, no push)

- [x] Pre-write refusal gates hold: gate surface absent (root exactly
      the 4 staged entries — no AUTHORIZATION / no CLAIM / no
      LAUNCH-CONSUMED / no result artifact); live seal == sidecar ==
      the operator-approved seal
      `b29c03a4388d87262377cbf96d3b206feea33623400f338b20f95559d49389fa`
      hard-asserted before any write; authorization payload digest of
      record `14cec703…76b40` cross-checked == the production
      re-derivation (`staged_cargoflow2_authorization_payload_digest`,
      reprised inside the driver == digest derived from
      `authorization_payload(read_prelaunch, seal)` first); the
      attempted scope binds this round's own staged identity
      (`route_version 2` beside `schedule_version 2`, plan digest
      `3132bfa0…5e0527`, attempt `D5-CARGOFLOW-2`, candidate-9 at the
      lineage constant)
- [x] Seed mechanics of record: the operator-held armored PKCS#8 PEM
      (`~/.local/share/openttd-operator/operator-private.pem`, its
      48-byte DER carrying the final-32 RFC 8032 seed window, parsed
      in memory only, verified pre-run without reading or printing the
      key bytes any further) carried into the seed window memory-only,
      env-only `CARGOFLOW_GATE_SEED` (base64), never printed, never
      filed, never passed on any command line; pre-write
      `public_from_seed(seed)` == the pinned anchor
      `5063982b…880f` (full:
      `5063982bd28d48573705f334ed4f396618c4930ce21083789dfbbf13a564880f`)
      and the operator key identity unchanged of record
      `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`
- [x] `AUTHORIZATION.json` written exactly once; record sha256 of
      record `0cbc505eec734e604a2d14ffa97db172007536c99855bc71c6a9de64181b6095`;
      production `verify_authorization` passes against the seeded
      anchor (record digest bound: True; operator key identity equal);
      no signing ever repeated; the seed-window variables dropped from
      the driver's memory immediately after the write and the env unset
- [x] Post-write read-only state: root = 5 entries (4 staged files +
      `AUTHORIZATION.json`; no CLAIM / no LAUNCH-CONSUMED); seal
      byte-equal after the write; production `preflight` re-run
      `PREFLIGHT PASS` exit 0 with the authorization present;
      standalone `verify` still `AUTHORIZATION_UNVERIFIED` /
      `CLAIM_ABSENT` exit 1 by design (the claim mints at the launch
      boundary only); seed env unset + empty in a fresh shell; all
      seven candidates' PRELAUNCH byte-pictures before == after; one
      commit, no push
