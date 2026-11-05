# Record of the English-version check (Appendix E) / 英語版の照合の記録（付録 E）

- Date / 日付: 2026-11-06
- Japanese version / 日本語版: `prereg-draft.md` (v10), SHA-256 `b3a3b36dc138442f5b4e7b8b11f46ea924f617cb48052d7ecdf21475a5cf7ddd`
- English version / 英語版: `prereg-draft.en.md` (v10), SHA-256 `91450ffb43fe4af20ce547077afc9e5e1be2365af3b6ee27064201cd7d58d7b1`
- Checker / 照合のスクリプト: `check_prereg_en.py`, SHA-256 `a621c06c884d9acb29eb57c6bb18cbe0f2b2e7ce8315ac6d2bb0120915760bd2`

## (1) Mechanical check / 機械の照合

`python3 -I check_prereg_en.py prereg-draft.md prereg-draft.en.md` → 「一致」 (exit code 0). It compares, per section (P0–P11, Terms, Appendix A–F), all numbers, hexadecimal hashes and commits, backtick code names, citation keys [Vnnn], and inequality signs (≥ ≤ ± and spaced < >). Counter words (1 つ, 2 段目 …, one/two/third …), placeholders in angle brackets, and Japanese number units (億・万 ↔ million) are normalised.
Positive controls (run on throw-away copies): changing one 0.45 to 0.46 → 6 mismatches reported; turning one ≥ into ≤ → 1 mismatch reported.
Limitations of the checker fixed during the check (not translation errors): counter words, angle-bracket placeholders, 「1 分あたり」 = "per minute".
After a code review of the checker (Claude and Codex), it was strengthened: signs are kept, numbers are compared by number of occurrences (decimals, signed numbers and numbers ≥ 10) or as sets (single-digit integers, whose occurrence counts legitimately differ between the languages because of counter words), code names and hashes are taken from the raw text before normalisation, only hex strings containing a letter are treated as hashes, and the title section is included.
Mutation test (every number outside code spans in the English changed one at a time, on throw-away copies): decimals, signed numbers and numbers ≥ 10 — 519 of 519 detected; sign removal — 2 of 2 detected; single-digit integers — 108 of 214 detected (limitation: a single-digit integer that also appears elsewhere in the same section is not detected; branch numbers, stage numbers and counts of this kind are covered by the meaning check (2)).

## (2) Meaning check / 意味の照合

An agent separate from the two translating agents (a separately launched LLM agent that did not write the translation) read both versions in full, section by section and cell by cell, checking negation, qualifiers, conditions, quantifiers, list membership, direction words, tense, and the quoted output sentences.
Result: 0 discrepancies that change a rule, 0 that change a reported wording, 3 minor nuances:
- D1 Terms: the translator's renderings table added glosses ("run-up (the 30 s before u)", "positive control (the check …)"). Fixed: the table is labelled non-normative and the glosses were removed.
- D2 Appendix B table: the English added "on unmatched windows, that the learners can detect a rise". Fixed: removed, so the English follows the Japanese literally.
- D3 Appendix F: 「条件の文書で新しく実装して」 rendered "according to the conditions document". Fixed: "in the conditions document (specified there)".
After the fixes, (1) was re-run: 「一致」.
Ambiguities present in both versions alike (not translation discrepancies; left as written): whether "only one of the two values of ε is branch 1" (P0) is per signal or overall — read per signal-and-ε combination as listed in the same item; window endpoint inclusiveness at u and resumption (P7) — the code governs unstated details (P11).

## Translation history / 訳の経緯

English drafted from v7/v8 by one agent, updated to v9 and v10 by two further agents (one each), then checked by the separate agent above. The SHA-256 values above are those at the end of the check.
