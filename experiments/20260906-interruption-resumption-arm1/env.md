# env.md — 環境固定

## 実行環境 (2026-09-06)

| | |
|---|---|
| OS | Windows-10-10.0.26200-SP0 (Windows 11 Home 26200) |
| Python | **3.11.9** |
| shell | git-bash (⚠️ Hook はすべて bash 前提) |
| 文字コード | ⚠️★★ Windows コンソールは cp932 → **`PYTHONUTF8=1` を必ず付ける** |
| git HEAD | `results/provenance.txt` に刻む |

## 依存

★ `feasibility_probe.py` は **標準ライブラリのみ**。
⚠️★★★ Step 2b (本解析・未実装) が `gse-replay` を使うなら **Cargo.lock を env として固定する**
——★ `Cargo.toml` は **repo 直下に無い** (`src-tauri/`)。
`cargo run --manifest-path src-tauri/Cargo.toml --bin gse-replay` の形にする
(`docs/agent-shared.md` テスト方針)。

## 再現

```bash
GSE_DATASET=C:/gse-dataset bash experiments/20260906-interruption-resumption-arm1/run.sh
```

## ⚠️ `results/provenance.txt` は再実行のたびに変わる

★ `git_head` / `git_dirty` を刻むので、**コミットするたびに差分が出る**。
⚠️ **これは結果が不安定なのではない** —— ★ `results/feasibility.json` と
`results/capabilities.json` は同じ入力に対して **byte 一致**する（★ 実測）。

⚠️★★★ **`git_dirty` の件数は本タスクの未完了分ではない。**
★ 本リポジトリの作業ツリーには**別タスク**（未踏提出資料・設計スライド）の
未コミット変更が同居している。→ ★ 本アームの担当分だけを見るときは
`git status --porcelain experiments/20260906-interruption-resumption-arm1` を使う。
