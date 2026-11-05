# 03r5: Round-5 Gate C signature

**What to build:** the operator's Gate C Option-1 signature over the
reviewed round-5 candidate — one signing operation via the production
signing surface only (payload derivation → canonical bytes → signature →
record write), bound to the freshly staged candidate's exact seal, with the
seed mechanics exactly as the rounds of record already ran them (memory-only
extraction, env-only, never printed or filed), followed by read-only
post-state verification.

**Blocked by:** 02r5 (Round-5 independent review) — the operator signing
approval is the in-session gate that authorizes it.

**Status:** done 2026-11-05 (operator approval in-session; ONE signing
operation, first invocation, zero refusals, zero re-writes)

- [x] Pre-write refusal gates hold: gate surface absent (no
      AUTHORIZATION/CLAIM/LAUNCH-CONSUMED/terminal artifacts), live seal ==
      sidecar == the operator-approved seal
      `d4715fd3b2d0a9f5be831dfcd9f80188a87ef6460173a55763a2ee2457537741`,
      hard-asserted twice before any write; fresh round-5 signer script
      `/tmp/opencode/t004_gate_c_cargoflow2_c5.sh` (the candidate-1/2-bound
      scripts never reused), transcript
      `/tmp/opencode/t004_gate_c_cargoflow2_c5_output.txt`
- [x] Payload digest `aa936f19498971f549e6906a30d852882e0b8a5ea9c5da13a5a6257b4e518d25`
      cross-checked == the production staged-payload digest derivation;
      operator key identity unchanged of record
      `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`
      (pre-write `public_from_seed(seed)` == pinned anchor `5063982bd28d…880f`;
      env-only `CARGOFLOW_GATE_SEED`, memory-only 48-byte-PKCS#8 final-32
      window, never printed/filed/argument-passed, unset + empty verified)
- [x] `AUTHORIZATION.json` written exactly once; record sha256 of record
      `57284ae0fd812f20e0152bc175f486230ba0f02b9c7c8df8acc8ff931382b01e`;
      no signing ever repeated
- [x] Post-write read-only state: root = 5 entries (4 staged files +
      `AUTHORIZATION.json`; no CLAIM / no LAUNCH-CONSUMED); seal byte-equal
      after the write (`d4715fd3…41ad`); preflight PASS with the
      authorization present; standalone `verify` still `CLAIM_ABSENT` /
      `AUTHORIZATION_UNVERIFIED` exit 1 by design (the claim mints at the
      launch boundary only)
- [x] No candidate bytes beyond the authorization record touched; candidates
      1–4 re-digested byte-identical; historical zones byte-untouched;
      `git diff --check` clean; `CONTEXT.md` pin intact; no commit/push by
      the signer
- [x] Signing row appended to the PoC backlog status log (record digest,
      payload digest, operator identity, one-write discipline)
