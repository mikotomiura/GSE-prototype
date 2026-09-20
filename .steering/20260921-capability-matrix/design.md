# 設計 — capability matrix

## 実装アプローチ

★ 成果物は **文書 1 本**（`docs/architecture/offline-replay-capability-matrix.md`）。コード変更は無い。
★ 判定の作り方を 3 段に固定した（⚠️ 判断 5 の実証範囲 A）:

1. **静的分析**: `src-tauri/schema/current.json`（★ 行種 22 の機械列挙）と
   `src-tauri/src/analysis/feat_offline/`（★ 7 モジュールの実装フィールド）を突き合わせ、
   `.idea/survey §6.1` の候補列と 1 対 1 に並べる。
2. **実測 replay**: `gse-replay --features` を既存 fixture に当て、
   ★ **Tier 別の非 null 率**を数える（⚠️ 「実装がある」と「値が出ている」を分ける）。
3. **既測の引用**: 起票 6（macOS ライブ変換・実機）／ 起票 7（`dwell_ms` の合算）／
   起票 19（macOS で修飾キーが届かない）／ `capabilities.rs` の WinEvent 実機計測。

## ⚠️ 層別の扱い（★ 本表の発見）

★ `ADR-032 D5` の指示どおり `W` / `M-off` / `M-on` の 3 層に分けたが、
⚠️★★★ **受け取った NDJSON から層を識別できない**ことが分かった
（★ `meta` にライブ変換のフィールドが無く、⚠️ macOS の `defaults` にもキーが存在しない）。
→ ★ 表の既定の読み方を「**macOS は `M-on` の最悪値で読む**」に固定し、`M-off` は参考として併記した。

## 変更対象

### 新規作成するファイル
- `docs/architecture/offline-replay-capability-matrix.md` — 本体

### 修正するファイル
- （★ 裁定の載せ方が決まってから決める）

## テスト戦略

⚠️ 文書なので単体テストは無い。★ 代わりに次を回す:
- `PYTHONUTF8=1 python3 scripts/check_citations.py`（★ `[Pn]` が active か）
- `PYTHONUTF8=1 python3 scripts/check_doc_lexicon.py`（★ 禁止用語）
- ★ 文中の実測値は**すべてその場で再実行して得た**（⚠️ 引き写しをしない）

## ロールバック計画

★ 文書 1 本なので削除で戻る。⚠️ ただし**実測値は再取得できる**ので、
削除するより「どこが誤っていたか」を追記するほうが安い。
