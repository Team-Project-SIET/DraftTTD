# 09: E207 triage dossier

Type: task
**What to build:** a per-class triage dossier of record over the first full-suite baseline's failing tests (E207: 6382 collected, 57 failed, 54 skipped), so decision ticket 07 can fix a repair-or-seal disposition behind every red class. From the operator's perspective: after this ticket, every red class has a named mechanism, the four extras carry an evidence-backed new-vs-pre-existing verdict, and each class has a recommended disposition — no red stands unexplained.

**Blocked by:** None (can start immediately).

**Status:** resolved (2026-11-12 — dossier of record at `research/02-e207-triage-dossier.md`)
**Gates:** no native run, no staging, no signing, no claim, no commit; `artifacts/` and `CONTEXT.md` read-only.

- [ ] Each red class of record (P08 controlled e2e ×51; budget-signature ×3 with the shared computed-410×508-vs-sealed-103×508 signature; workspace-retention ×1; corridor family ×1; structural-world fixture ×1) carries a diagnosed mechanism with evidence — no force-fit.
- [ ] The corridor-family description conflict (the failing ladder-of-record test vs the triage's named target that passed) is resolved by evidence into one description of record.
- [ ] The four extras' new-vs-pre-existing status is resolved from evidence — answered, or explicitly recorded as unanswerable with the reason.
- [ ] A recommended repair-or-seal disposition per class, written as decision input for ticket 07.
- [ ] Diagnosis only: no retained evidence modified, no suite behavior changed, no commit.

## Answer

Resolved 2026-11-12. Dossier of record: [research/02-e207-triage-dossier.md](../research/02-e207-triage-dossier.md).

- **P08 e2e ×51** — frozen-fixture byte-serialization drift at `bf6cc0b` (2026-11-01): seal hashes the old compact bytes, payload files re-serialized; pipeline proven content-healthy via a /tmp probe (admit → P05 → semantic checks → evidence content-identical to `verification.json`). Legacy triage's "schema/policy digest drift" refuted. Input: **repair** — restore canonical serialization, no regeneration.
- **Budget-signature ×3** — intentional 512→2048 widening at `5e398db` (2026-11-07) left three 512-era seals (103/52,324 vs computed 410/208,280). Extras' verdict **ANSWERED: pre-existing since 2026-11-07** — the 53's freeze (`bf5262c`) preceded the widening by hours, which is why the trio is absent from it. Input: **repair** the three test seals (prefer deriving from the module constants).
- **Workspace-retention ×1** — kernel-endpoint closure gate refuses an unrelated machine socket on the frozen ephemeral ports and skips the sole disposal call; reproduced on demand. Extras' status: **answered in part** — capable code predates the freeze; pre-E207 firing unanswerable (no prior baseline, kernel rows not retained). Input: **operator choice** — typed seal or narrow gate repair.
- **Corridor ×1** — description of record settled: `test_corridor_cargoflow2_vm.py::test_ladder_of_record_runs_green` (the map's description; the legacy triage's named target was an unobserved inference — its capture ran zero tests). Current red = composition drift: delivered-composition tail step 60 vs the v1 schedule's 55, silent tail drop. Input: **repair (re-key the VM ladder) or typed seal**.
- **Structural-world ×1** — `bf6cc0b` re-indented `runtime-identity.json` (content-identical) without re-sealing the checkpoint manifest; CRLF hypothesis retired by direct blob evidence. Input: **repair** one file's serialization.

Diagnosis only throughout: no code, tests, `artifacts/`, or ticket 07 modified; probes under `/tmp/opencode/`; E207 bytes remain the baseline of record.
