# 設計

## 実装アプローチ

★ **2 本立てにする。** 実測データの後処理（不可逆・先にやる）と、P-1 が見つけた不具合の是正
（可逆・後でよい）を混ぜない。

1. **データ**: `.age` 復号 → `gse-dataset` 配置 → 転記 → 検査 → 刻印
2. **是正**: 課題文 → ページ → 手順書 → 検査の追加

⚠️ ★ **判定（`§3`）には一切触れない。** `analyze.py --verify-blocks` は
「ラベルを一切読まない」経路であり、これを走らせても「解析結果を見た」ことにならない
（`analyze.py` の docstring / `protocol.md §2.3-3`）。★ **この経路以外は使わない。**

## 変更対象

### 修正するファイル

- `experiments/.../materials/topic02_lo.md` — 割引券の額面を定額制に合わせる（D-1）
- `experiments/.../writing-pad.html` — ボタンラベルを実装に合わせる ＋ 次の行き先を明記（D-5）
- `experiments/.../build_task_pages.py` — `promise_check()` を追加し、生成時と selftest で発火させる
- `experiments/.../protocol.md` — 当日チェックリストのボタン名（D-5）
- `experiments/.../record-sheet-pilot.md` — 同上
- `experiments/.../env.md` — P-1 macOS 回の実測記録（実施順の逆転・実測長・未記録項目）
- `experiments/.../config.json` — `reproducibility.hmm_version` の刻印
- `experiments/.../notes.md` — 2026-08-05 の節

### 変更するが**コミットされない**ファイル（`.gitignore` 対象）

- `experiments/.../blocks/PILOT-mac.json` — `file` × 4 ＋ `execution_mode`
  ★ **NDJSON 名にはセッション日時が入る**ので、ここが gitignore されているのは意図的である
  （`blocks/.gitignore`）。★ **本 repo は一時 public にする運用があるため、成果物側には書かない。**

### repo の外に置くもの

- `~/gse-dataset/raw/PILOT-mac/*.ndjson` — 復号した 4 本
  （`gse-dataset` 側の `.gitignore` が `raw/**/*.ndjson` を除外している）

### 新規作成するファイル

- `.steering/20260805-g1-p1-analysis-and-material-fix/` — 本記録一式

## 影響範囲

| 変更 | 影響 | 対処 |
|---|---|---|
| `topic02_lo` 本文 | Drive の mac `block03.html` が古くなる | D-4（確証配布でまとめて作り直す） |
| ボタンラベル | Drive の全 `block0N.html` が古くなる | D-4 |
| `hmm_version` 刻印 | ⚠️ Windows 回が別の値を出したら**両方記録する**（上書きしない） | `config.json` の `hmm_version_stamping` に明記 |
| `promise_check` 追加 | 生成が赤くなる可能性 | ★ 現行テンプレートで緑を確認済み |

## 既存パターンとの整合性

- `promise_check()` は `leak_check()` の**隣に置くが混ぜない**。壊れる理由が違うため
  （漏れ＝課題文の中身 / 約束＝テンプレートの文言と実装のズレ）。
  ★ 「**空回りしていないか**をわざと壊して確かめる」という `build_task_pages.py --selftest`
  の既存の書き方をそのまま踏襲した。
- `HMM_VERSION` は `protocol.md §6.1` の刻印手順どおり **env.md → config.json** の順。
  ★ ⚠️ **`engine.rs` を読んで代用しない**という既存の警告を守り、
  **配布バイナリが書いた `meta` 行から実測**した。

## テスト戦略

★ 機械検査は「緑になること」ではなく「**赤にできること**」で確かめる。

| 何 | どう確かめたか |
|---|---|
| probe 行 0 | `grep -c` で**数字を読む**（0 件でも `0` を出す。「何も出ない」で判断しない） |
| 転記 | `validate_blocks.py --dataset` = 緑（転記前は `[FAIL]` だったことを確認済み） |
| 課題文の制約 | `validate_materials.py --strict` = 緑（総文字数差 3.1%） |
| `promise_check` | ★ **旧ラベルへ戻したページが赤になること**を `--selftest` に組み込んだ |
| 全体 | `run.sh` = GREEN |
