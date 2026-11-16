# quinn-udp を上げて供給網の検査の赤（RUSTSEC-2026-0538）を消す

## 背景

PR #416 の CI の `audit`（`.github/workflows/supply-chain.yml`・run 43742332833）が赤になった。
`RUSTSEC-2026-0538  quinn-udp 0.5.15  patched: >=0.5.16, <0.6.0, >=0.6.3`。
main の `src-tauri/Cargo.lock` に quinn-udp 0.5.15 があり、PR と関係なく main 側の問題。
入口は `.steering/_handoff/next-session-gse-quinn-udp-advisory.md`。

## ゴール

`python3 scripts/check_dependency_audit.py` が main の lock では exit 1（0538）、この枝では exit 0 になる。

## スコープ

### 含むもの
- `src-tauri/Cargo.lock` の quinn-udp を 0.5.16 に上げる

### 含まないもの
- quick-xml の除外 2 件（RUSTSEC-2026-0194/0195・review-by 2026-12-12）の見直し
- リリース・タグ（研究者に確かめる）
- 照合の論文の枝

## 受け入れ条件

- [x] 監査スクリプトが exit 0・除外 2 件のまま・stale 0・informational の件数が変わらない
- [x] `cargo test --locked --workspace` が緑（1360 passed 他・失敗 0）
- [x] `gse-replay` のゴールデン（minimal）が一致（15 snapshots）
- [x] /cross-review（Claude 側は cross-reviewer が一次で検証・Codex は実行済み。指摘は LOW 2 件で decisions に反映）

## 関連ドキュメント

- `docs/verification-runbook.md` §1 (g)
- `.cargo/audit.toml`・`scripts/check_dependency_audit.py`

## 運用メモ
- /reimagine 適用: No
- 理由: lockfile の 1 crate のパッチ版の更新で、設計判断を伴わない
