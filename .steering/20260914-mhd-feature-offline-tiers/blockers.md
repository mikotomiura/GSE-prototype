# 詰まりと起票 — タスク 2（Mh-D 特徴量の Tier 別オフライン実装）

> ⚠️★★★ **このファイルは「本タスクでは閉じないが、閉じないまま黙らせてはいけないもの」の台帳**である。
> ★ 裁定済みのものは `decisions.md`、実行の記録は `issues/*.md` の Execution Result にある。

---

## 起票 1: ⚠️★★★ `meta` 行に `os` が無いので、`schema_dto.rs` が約束した判別ができない

- **起票日**: 2026-09-15（★ issue 002 の `security-checker` 指摘 M2 から派生）
- **何が食い違っているか**（★ 一次資料で確認・⚠️ 推測ではない）:
  - `src-tauri/src/schema_dto.rs:296` 逐語:
    「**由来は meta 行の os と capabilities 宣言で判別する。両 OS のデータを混ぜて学習・評価してはならない。**」
  - ⚠️ ところが **`"os"` は `logger.rs` / `capabilities.rs` / `schema_dto.rs` のどこにも無い**
    （★ 実測: 3 ファイルへの `grep '"os"'` が **0 件**）。
  - ⚠️ **機械生成の JSON Schema (`src-tauri/schema/current.json`) にも `os` キーが存在しない**
    （★ 実測: `grep -o '"os"'` が 0 件）。
  - ★ `meta` の実書式は `logger.rs:1628` / `:1640` の書式文字列がすべてで、
    `session_start` / `hmm_version` /（`g1_mode`）/ `app_version` / `capabilities` のみ。
- **なぜ効くか**: `capabilities.rs:216-233` が逐語で
  「**由来だけでなく「母数」も違う**」「⚠️ **`abandon` 率を OS 間で直接比べてはならない**」と述べ、
  その判別手段として **`meta` 行の OS** を指定している。
  → ★★★ **指定された手段が存在しないので、規約が履行不能である。**
  ⚠️ issue 002 で `ime_dwell_ms` / `ime_nav` / `ime_abandon` が `--features` の出力に載ったので、
  **下流が Win/mac を混ぜて平均できる状態**が実際に生まれた。
- **本タスクで閉じない理由**: ⚠️ `meta` へのフィールド追加は **計器変更**であり、
  issue 002 / 007 の Scope Out（`logger.rs` / `schema_dto.rs` / `capabilities.rs` を触らない）に直撃する。
  ★ 計器変更の裁定は **ADR-032 の領域**（→ `.steering/20260914-instrument-change-arbitration/`）。
- **★ 次に何をするか**（⚠️ 順序を飛ばさない）:
  1. ★ ADR-013 の Migration として「`meta` に `os` を足す」是非を裁定する
     （★ `os` は**端末環境の宣言**であって被験者由来データではないので、
     `data-privacy` ルール 1 / ルール 7 には抵触しない —— ⚠️ ただし
     **指紋性**は ADR-013 D6 逐語「粗い semver のみ」と同じ基準で検討すること）。
  2. ⚠️ 足すまでの間は、**`schema_dto.rs:296` の「meta 行の os」という記述が実体と食い違っている**
     ことを承知して読む。★ 直すなら「一次へ戻す」（= 記述を実体に合わせるか、実体を記述に合わせるか）を
     裁定してから（`feedback_stale_doc_revert_to_primary`）。
- **⚠️ 部分的に閉じるもの**: ★ `capabilities` 側の欠落は **issue 007（`Q`）が
  `quality.capabilities` / `quality.hook_health` を行に載せることで閉じる**。
  ⚠️ **`os` は閉じない**（★ `capabilities` 宣言は OS 名を含まない）。

---

## 起票 2: ⚠️ `--features` の出力に「由来の封筒」が無い

- **起票日**: 2026-09-15（★ `security-checker` 指摘 M2 の後半）
- **中身**: `--features` の出力はトップレベルが **`FeatureRow` の配列**であり、
  セッション単位の事実（`capabilities` / `app_version` / OS / fixture 名）を持たない。
  → ⚠️ 複数セッションの出力を結合したとき、**どの行がどの計器条件で取れたか**が失われる。
- **本タスクで閉じない理由**: ★ 出力形状の変更は **002〜007 の全 `acceptance.sh` の前提**
  （`jq 'all(.[]; ...)'` が配列を仮定している）を壊す。
  ⚠️ 途中で変えると走り終えた issue の検査が全部無効になる。
- **★ 次に何をするか**: ★ **issue 007 が `quality` を行に載せ終えてから**、
  「行ごとに持つ」か「封筒に出す」かを 1 度だけ裁定する
  （⚠️ 007 の `quality.capabilities` は**行ごと**なので、封筒にすると二重になる）。

---

## 起票 3: ⚠️ `permission_denials` の中身が依然未検証

- **起票日**: 2026-09-15（★ `decisions.md` 判断 8 の未決 3 を引き継ぐ）
- **中身**: Loop モードC は `permission_denials=N` を件数だけ events に残す。
  ★ issue 002 の 6 attempt では **1 / 2 / 5 / 10 件**が記録されたが、**何が拒否されたかは分からない**。
  ⚠️ events_path が worktree の cwd 境界外にあるため「必ず 1 件は出る」ことは分かっているが、
  ★ **10 件の内訳は説明できない**。
- **★ 次に何をするか**: `scripts/loop-run.sh:342` の `res` を `WORK_TMP` に保存する改修を先に入れる。
  ⚠️ それまでは「非致命」という扱いの妥当性を**確かめていないまま使っている**と承知する。
