# 03: Round-3 Gate C signature

**What to build:** the operator's Gate C Option-1 signature over the
reviewed round-3 candidate — one signing operation via the production signing
surface only (payload derivation → canonical bytes → signature → record
write), bound to the freshly staged candidate's exact seal, with the seed
mechanics exactly as the rounds of record already ran them (memory-only
extraction, env-only, never printed or filed), followed by read-only
post-state verification.

**Blocked by:** 02 (Round-3 independent review) — the operator signing
approval is the in-session gate that authorizes it.

**Status:** ready-for-agent

- [ ] Pre-write refusal gates hold: gate surface absent (no
      AUTHORIZATION/CLAIM/LAUNCH-CONSUMED/terminal artifacts), live seal ==
      sidecar == the operator-approved seal, hard-asserted before any write
- [ ] Payload digest cross-checked against the production staged-payload
      digest derivation; operator key identity unchanged of record
- [ ] `AUTHORIZATION.json` written exactly once; no signing ever repeated
- [ ] Post-write read-only state: root = staged entries + the authorization
      record (no CLAIM / no LAUNCH-CONSUMED); seal byte-equal after the
      write; preflight PASS with the authorization present; standalone
      `verify` still `CLAIM_ABSENT` / `AUTHORIZATION_UNVERIFIED` exit 1 by
      design (the claim mints at the launch boundary only)
- [ ] No candidate bytes beyond the authorization record touched; candidates
      1–2 untouched; historical zones byte-untouched; `git diff --check`
      clean; `CONTEXT.md` pin intact; no commit/push
- [ ] Signing row appended to the PoC backlog status log (record digest,
      payload digest, operator identity, one-write discipline)
