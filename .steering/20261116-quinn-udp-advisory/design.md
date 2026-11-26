# 設計

## アプローチ

`src-tauri/Cargo.lock` の quinn-udp を 0.5.15 → 0.5.16 にする（decisions 判断 1・2 行の書き換え）。

## 変更対象

- `src-tauri/Cargo.lock`（2 行: version と checksum）

## テスト戦略

- 対照: main の lock で `scripts/check_dependency_audit.py` が exit 1（0538）を出すこと
- 本体: この枝で exit 0・除外 2 件・stale 0・informational（unmaintained=12, unsound=7, yanked=3）が同じ
- `cargo metadata --locked`・`cargo test --locked --workspace`・`gse-replay` minimal のゴールデン
- 終わったら worktree の target を消す（自前ランナーの空きの下限）
