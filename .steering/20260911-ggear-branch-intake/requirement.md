# 要件 — G-GEAR ブランチ取り込み

- タスク名: `20260911-ggear-branch-intake`
- 対象ブランチ: `origin/feat/resumption-outcome-arbitration` (e80f79c)
- 基点: `main` = 2f7d114 / merge-base = 8961333

## 背景

`feat/resumption-outcome-arbitration` (通称 G-GEAR) が main から大きく分岐したまま
放置されている。ADR-023〜028 と `analysis/metrics.rs` の `recovery` → `pflow_exit` 改名を
含むため、main に入れないと以後の作業が二重管理になる。

⚠️ 引き継ぎメモ (`.steering/_handoff/next-session-prompt-ggear-intake.md`) の規模の数字は
**`main..branch` の二点差分**で数えられており、main 側 60 コミットの「巻き戻し」を
取り込み量に数え込んでいた。本タスクは `merge-base..branch` の実測でやり直す。

| | メモ | 実測 (merge-base..branch) |
|---|---|---|
| ファイル | 246 | **199** |
| 行 | +26,681 / −4,870 | **+28,054 / −670** |
| Rust | 6 | **5** (+ メモ未記載の `.github/workflows/ci.yml` / `.codex/budget.json` / `.gitignore` / `.claude/skills/*` 5 本) |

## ゴール (検証可能な形)

1. G-GEAR の 199 ファイルが 2 本の PR として main に向けて open している。
2. **PR-A (Rust)**: `cd src-tauri && cargo test --workspace` が緑、かつ
   ゴールデン 6 本すべてで `gse-replay --snapshot` が byte-equal で一致する
   (＝ `HMM_VERSION` bump 不要の裏づけ。exit code 0)。
3. **PR-B (それ以外)**: `bash scripts/secrets-filter-test.sh` が緑、
   schema parity (`emit_schema` ↔ `schema/current.json`) が byte-equal。
4. 衝突 6 ファイルの解決方針が `decisions.md` に根拠つきで記録されている。

## スコープ外 (やらないこと)

- **merge そのもの** — CI 確認後の merge は研究者判断。PR を open するまで。
- 引き継ぎメモ §3 の残雑務 (ブランチ掃除 / 遅れブランチの cherry-pick / 被験者への配り直し /
  Windows blockers #3)。
- 引き継ぎメモ §4 の未検証事項 (SIGSEGV の陽性対照など)。
- `docs/adr/` の既存本文 (001–022) の書き換え。事前登録の凍結節。`Form_G1/` `Form_O1/`。

## 運用メモ

- /reimagine 適用: **No**
- 理由: 設計の創出ではなく既存ブランチの取り込み。判断分岐は「分割の切り方」だけで、
  実測 (衝突 6 件) によって選択肢が絞れたため代替案生成の余地が小さい。
