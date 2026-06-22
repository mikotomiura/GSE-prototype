# capture-schema-freeze (WBS M0: 検証基盤フリーズ — 捕捉スキーマ凍結)

## 背景

WBS v2 (`wbs_検証用docs/GSE_マイルストーン_WBS_半年版_v2.docx`, 2026-06-22) と
codex-review v0.4 (同 `ユーザー検証_codex-review_v0.4.docx`) が、旧設計
(`decisions.md D7` 2026-06-20 / `roadmap-xy.md` / `handoff-phaseA-capture.md`) の
**(b)自力解決率の定義を置換**した。

- v0.4 §4.2: 「diff量 ÷ 総打鍵数」を**廃止** → `manual_contribution_ratio` /
  `productive_manual_recovery_rate` に置換。新指標は**キーストローク由来の文字数カウンタ**
  (`manual_insert_chars` / `external_paste_chars`) から算出され、**成果物 (git diff) を必要としない**。
  → 旧 handoff の **A3 (成果物スナップショット機構) は廃案**。
- v0.4 §9: `dismiss_reason` 4択を「Need 誤りと Opportunity 誤りの分離に**必須**」と格上げ。
  → 旧 A2 (汎用介入応答ログ) は `dismiss_reason` を中核に存続・鋭利化。

支配原則 (捕捉の不可逆性 = 「録り損ねたら永久に失う」) は不変。変わったのは**捕捉対象**:
成果物スナップショットではなく **content-free な文字数カウンタ＋固定カテゴリ**。
これらは M0「検証基盤フリーズ」のクリティカルパス (M0→M1→M2) 上にあり、
パイロット (Phase 1a) 着手前に NDJSON schema を凍結する必要がある。

## ゴール

パイロット前に失うと不可逆な NDJSON 捕捉フィールドを、**1 回の coordinated schema bump** で凍結する。
派生指標 (replay 側で再計算可能なもの) は捕捉済みデータから後で算出できる状態にする。

## スコープ

### 含むもの (WBS 0.4 / 0.8 / 0.9-capture / 0.11)
- `Paste{t}` → `external_paste_chars` (ペースト**文字数=カウント**) を追加。中身は記録しない。
- `dismiss_reason` 4択 (詰まってない / 今はもがきたい / 閉じる / 無言) の固定カテゴリ記録 + UI。
- `SessionMeta` に `condition` (blind-calibration / A|B / nudge|defer) を追加。
- `label_pool` タグ (calibration_blind / post_intervention) のプール分離。
- schema 変更の必須手順: emit_schema 再生成 → `src-tauri/schema/current.json` →
  gse-dataset 同期 → `check_schema_parity.py` 緑。

### 含まないもの (別タスク・捕捉変更不要)
- `source_role` (ペースト元の内部/外部分類。content-free 判定が非自明 → 設計フォーク含むため後置)。
- `manual_contribution_ratio` / `productive_manual_recovery_rate` の**算出**
  (gse-replay --metrics 側。`manual_insert_chars` は既存 `Key` 列から replay で導出可能 → 捕捉不要)。
- 0.10 派生 metrics / 0.5 C-index 両端集計 (実装済) / 運用・PreReg 項目 (0.6/0.7/0.12-0.16)。
- features / HMM への組み込み (FeatSnapshot 不変を維持)。

## 受け入れ条件

- [ ] `Paste` が `external_paste_chars` を持ち、ペースト文字数 (中身なし) が NDJSON に残る。
- [ ] `dismiss_reason` 4択が固定カテゴリ + 時刻で NDJSON に残る (UI から発火)。
- [ ] `SessionMeta.condition` が記録される。
- [ ] `label_pool` タグで calibration_blind / post_intervention を区別できる。
- [ ] schema 変更 → emit_schema 再生成 → gse-dataset 同期 → parity 緑。
- [ ] `cargo test --workspace` green / `gse-replay --snapshot` byte-equal (FeatSnapshot 不変)。
- [ ] gse-replay が新 variant で panic しない (fixture に行追加で確認)。
- [ ] code-reviewer / security-checker CRITICAL/HIGH なし (特に**中身非漏洩** = カウントとカテゴリのみ)。

## 関連ドキュメント

- WBS v2 §4.0 (M0 0.4/0.8/0.9/0.11) / codex-review v0.4 §4.1/4.2/9
- `.steering/20260619-user-validation-data-collection/handoff-phaseA-capture.md` (**A3 廃案で supersede**)
- `.steering/20260619-user-validation-data-collection/decisions.md` D7 (**(b)定義 supersede**)
- `docs/development-guidelines.md` §3 (Replay-as-Truth) / §10 (data repo)
- Skill: `data-privacy` (最優先) / `intervention-design` (dismiss 意味論) / `architecture-rules` / `rust-standards`

## 運用メモ
- /reimagine 適用: **No**
- 理由: 設計フォークを含む A3 / source_role は明示的にスコープ外へ後置済み。残るのは
  確定済みの content-free フィールド追加 (schema variant 拡張) で、最良案は自明
  (既存 `Paste` / `SessionMeta` / `InterventionDecision` の確立パターンに倣う)。
- 前提解消済: PR #16 は main マージ済 (`e0d683d`、`Paste{t}` 在)。**main 基点で別ブランチ**。
