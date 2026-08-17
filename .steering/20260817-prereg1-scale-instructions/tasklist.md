# tasklist — PreReg-1 尺度理解ゲート 再設計

## 0. 前提の検算

- [x] 一次資料で「通過率 0.00」の実体を確認 → **未実施**（5 名全員 `vignette.total = 0`）
- [x] `research-positioning.md:397` / `calibration-smoke-runbook.md:99` の「延期」記述を確認
- [x] `calibration_eval.rs:924` に `total > 0` ガードが無いことを確認（誤読の機械的原因）
- [x] 引き継ぎ §0 の前提誤りを研究者へ報告し、スコープを再確定

## 1. 器の再設計

- [x] 教示文の再設計（1–5 の刻み定義 / 二軸の直交性 / 中点の扱い）
- [x] 8 ビネットの再設計（アンカー語の逐語ヒント除去・提示順の交互化）
- [x] 教示を独立画面に分離し、各問から再表示できるようにする
- [x] 完了画面に**反応性の打ち消し文**を追加（L5 軽減策・省略禁止）

## 2. 採点器と入力 UI

- [x] スライダーの初期値を撤廃（`number | null`）。両軸に答えるまで次へ進めない
- [x] 「既定位置 3 をそのまま選ぶ」操作を `onPointerUp` / `onKeyUp` で取りこぼさない
- [x] `VignetteScore.administered` を追加（未実施と不合格の分離）
- [x] 完了ガード `total >= VIGNETTE_TOTAL(8)` を追加（⚠️ D-10・研究者確認事項）
- [x] `cohort.rs`: 未実施を「未達」と別の `decision_reason` にする
- [x] `cohort.rs`: **GATE1 未実施のまま `Go` へ昇格させない**
- [x] `VignetteView::was_administered`（旧 JSON の後方互換 = `total > 0` fallback）
- [x] ⚠️ `VIGNETTE_PASS_MIN = 6` / `VIGNETTE_COHORT_PASS_FRACTION = 0.80` を**変更していない**

## 3. 記録項目

- [x] `vignette_response` に `elapsed_ms` / `changes` を追加（logger / lib / schema_dto）
- [x] data-privacy 適合を確認（数値のみ・本文/タイトル/選択文字列なし・ローカル FS のみ）
- [x] `emit_schema` で `schema/current.json` 再生成
- [x] `check_schema_parity.py --dataset` で gse-dataset と整合（⚠️ 下記「未コミット」参照）

## 4. 実測検証（`empirical-prompt-tuning`）

- [x] シナリオ 5 本（median / edge-low / edge-high / adversarial ×2）
- [x] iteration 0–5 を実施（計 22 実行）。記録は `tuning-log.md`
- [x] hold-out 2 本で過適合チェック（導入時 8/8・低下なし）
- [x] ⚠️ **空振り検査**: straight-lining ペルソナが 5/5 回で不合格（最大 2/8）
- [x] ⚠️ v2 で入れた 2 行が妥当性を壊していたことを実測で検出し**撤回**
- [x] 全 22 実行で `tool_uses = 0`（repo を読まれていない = 測定が成立している）
- [ ] ⚠️ **skill の収束基準（連続 2 回で新規不明瞭点 0）は未達**。残余 R1–R4 は `tuning-log.md` §5 に記録

## 5. テスト

- [x] `vignette_not_administered_is_not_a_failure`（＋反証: 施行済みなら `administered = true`）
- [x] `vignette_partial_completion_does_not_pass`（＋反証: 8 問なら合格）
- [x] `vignette_exactly_six_matches_passes_and_five_does_not`（凍結閾値の両側）
- [x] `vignette_straight_lining_cannot_reach_pass_threshold`（定数 25 通り全数＋反証）
- [x] `all_subjects_unadministered_reports_deferred_not_failure`（＋反証: 1 名施行済みなら「未達」）
- [x] `unadministered_vignette_blocks_promotion_to_go`（＋反証: 施行済みなら `Go`）
- [x] `scripts/check_vignettes.py`（C1 禁止語 / C2 隣接象限 / C3 均等配置 / C4 不透明 ID）
- [x] ⚠️ `check_vignettes.py --self-test`（C1–C4 が**壊した入力で赤になる**ことの確認）

## 5.5 レビュー指摘の反映（`code-reviewer`）

⚠️ レビュアーの HIGH 2 件（tsc 20 エラー / `check_vignettes.py` 未配線）は
**リファクタ途中のファイルを読んだもの**で、一次で検算したところ既に解消済みだった
（`npx tsc --noEmit` exit 0 / `ci.yml:181,185` に配線済み）。以下は**実在した**指摘。

- [x] **HIGH**: ⚠️★★★ **再受験で 8/16 合格する穴**（D-10 の完了ガードが作った）
      → `vignette_id` で施行に切り、**最後の 1 施行だけ**を採点（D-14）。
      `VignetteRecord.vignette_id` / `VignetteScore.attempts` を追加
- [x] **HIGH**: ⚠️ `onKeyUp` が **Tab でのフォーカス到着で発火**し、キーボード操作では
      未操作と「3 を選んだ」の分離が無効化されていた → `onKeyDown` ＋ キー限定（D-17）
- [x] **MEDIUM**: 部分施行（`0 < administered < total`）が `decision_reason` に出ない → 織り込み（D-16）
- [x] **MEDIUM**: 旧 JSON の `passed` を鵜呑みにしていた → read 側で再導出＋警告（D-15）
- [x] **MEDIUM**: テストの doc が「旧 JSON 形で作る」と謳いながら serde を通していなかった
      → 実際に Phase1 当時の JSON 文字列をパースさせる
- [x] **MEDIUM**: `cohort_verdict` の doc（判定フロー）が新分岐に追随していない → 追記
- [x] **MEDIUM**: `assert!(r.passed == false)` が clippy `bool_comparison` を発火 → `!r.passed`
- [x] **LOW**: 不要な `#[allow(clippy::too_many_arguments)]` を削除
- [x] **LOW**: `onPointerCancel` 未処理（タッチのスクロール割り込み）→ 追加
- [x] **LOW**: `changes: u16` の上限超えで IPC ごと失敗し**被験者が進めなくなる**
      → frontend で `MAX_CHANGES` に飽和
- [x] **LOW**: `matches >= 6` のマジックナンバー → `VIGNETTE_PASS_MIN` 定数に
- [x] **LOW**: `elapsed_ms` が再送時に累積になる点を schema / logger の説明文に明記
- [x] **LOW**: Go 降格時の理由文にも施行状況の説明を持たせる（D-16 で統一）
- [ ] ⚠️ **LOW（未対応・意図的）**: `schema/current.json` の `required` に `elapsed_ms` /
      `changes` を入れたため、**この日より前の NDJSON は schema 検証を通らない**。
      ★ 一次確認: schema は `check_schema_parity.py`（2 repo 間の drift 検知）にしか
      使われておらず、**NDJSON を検証する経路は無い**（`gse-replay` は当該 2 フィールドを読まない）。
      ★ ビネットの実データは gse-dataset に **1 件も無い**ので移行対象も無い。
      → `Option` 化して新ログの保証を弱めるより、**破壊を明示して残す**判断
- [ ] ⚠️ **LOW（未対応）**: `inferQuadrant` が Rust / TypeScript で二重実装されており、
      一致を守るテストが無い。★ 定数 `VIGNETTE_PASS_MIN` は TS 側にも置いたが、
      **関数の一致は人力頼み**のまま

## 5.6 レビュー指摘の反映（`security-checker`）

★ **CRITICAL 0 件 / HIGH 0 件。** プライバシー規約は全項目 pass
（ルール 1: 追加 2 フィールドは純粋な数値で復元経路なし・`metrics.json` にも生値は載らない /
ルール 2: `VignetteTest.tsx` に `fetch`/`XHR` 0 件 / 場面文の参照は描画 1 箇所のみ）。

- [x] **MEDIUM**: ⚠️★★ **「書くが読まない」** —— `elapsed_ms` / `changes` を NDJSON に書くのに
      解析経路 (`replay.rs` / `VignetteRecord`) が消費しておらず、
      **目的（読まずに送った回答の事後分離）が実行不能**だった。目的限定・最小化の逸脱。
      → `gse-replay` で読み、`VignetteScore` に `elapsed_ms_median` / `elapsed_ms_min` /
      `changes_total` として集約（D-18）。⚠️ **記述統計であり合否には使わない**
- [x] **LOW**: `split_attempts` が NDJSON 由来の `vignette_id` を無検証で `HashSet` キーにしていた
      → 読込側でも `is_valid_opaque_id` を通す。規則は `calibration_eval.rs` に単一化し、
      `lib.rs` の IPC 境界も委譲（二重管理をやめた）
- [x] **LOW**: CI の `python` → `python3`（ランナーのエイリアス有無に依存させない）
- [x] **自己発見**: ⚠️ 旧ログで `elapsed_ms = 0` が「即答」と読めてしまう
      → `Option` にして `None`（未記録）と `0`（即答）を分離。pretty 出力は `n/a`。
      実測で両分岐を確認（旧 fixture → `n/a` / 新形式 → 実値）
- [ ] ⚠️ **未対応（別タスク推奨）**: `npm audit` に既存の HIGH 4 件
      （vite / postcss / nanoid ほか）。★ **本差分は `package.json` / `Cargo.toml` を
      変更していない**ので本変更が導入したものではない。いずれもビルド時 dev 依存で
      Tauri 実行時バンドルには載らない。★ 本 PR に混ぜると差分の焦点がぼける
- [ ] ⚠️ **未対応**: `cargo audit` が**本機に未インストール**のため Rust 側の依存監査は未実施

## 6. 検証実行結果（実測）

- [x] `cargo test --workspace` → **369 passed / 0 failed**（レビュー反映後）
- [x] `cargo clippy --workspace --all-targets` → **本タスクの変更ファイル由来の警告 0**
      （残る警告は既存コード由来: `metrics.rs` の lifetime / `logger.rs` の引数数 等）
- [x] `gse-replay` ゴールデン **4 本**すべて byte-equal
      （`minimal` 15 / `phase1_ime_heavy` 6 / `category_coverage` 2 / `deep_silence` 51）
- [x] `HMM_VERSION` bump **不要**を実測で確認（特徴量・行列に触れていないため）
- [x] `npx tsc --noEmit` → exit 0
- [x] `check_vignettes.py` → OK（提示順 flow→stuck→incubation→idle ×2）
- [x] `check_schema_parity.py --dataset /c/gse-dataset` → OK（21332 bytes canonical）

## 7. ドキュメント反映

- [x] `experiments/.../notes.md` §2.2 に「この誤読は実際に起きた」を追記
- [x] `docs/research-positioning.md` §5 に「延期は不合格ではない」を明記
- [x] `docs/research-positioning.md` §8 に「延期のコストが顕在化した」と
      「尺度理解ゲートは落とす器であって離脱を防ぐ器ではない」を追記
- [x] `.steering/` に requirement / design / decisions / tasklist / tuning-log

## 8. ⚠️ 未完了・引き継ぐもの

- [ ] ⚠️ **`gse-dataset` の `schema/current.json` が未コミット**（本リポジトリとは別 repo）。
      研究者がコミットする必要がある。`git push` は deny 設定のため代行できない
- [ ] ⚠️ **施行計画（誰に・いつ当てるか）は未定**（研究者判断・D-4）。
      GATE1 は依然として**未発効**であり、本タスクの成果物は「施行した」ではなく
      「**施行できる状態**」である
- [ ] ⚠️ **GATE1 を実際に発効させる段では `preregistration-v0.3` → `v0.4` を切って再凍結する**
      （D-3。採点関数を「未発効の実装詳細」として直した整理は、発効後には使えない）
- [ ] ⚠️ **施行後に Q1/Q2 の分布を施行前と比較する**（教示文の反応性 L5 の残余を点検する。
      「8 つの場面は…はっきりするように書いてあります」が本番へ癖を持ち越していないか）
- [x] ~~`check_vignettes.py` を CI に接続する~~ → **本タスクで実施**
      （`.github/workflows/ci.yml` の `frontend-check` に `--self-test` と本検査の 2 ステップを追加。
      ⚠️ `check_citations.py` と同じ「手で叩く限り陳腐化する」問題を先送りしないため）
- [ ] ⚠️ `check_citations.py` の CI 接続は**未実施のまま**（`_handoff` §5「検査の常設化」）。
      本タスクの射程外だが、同型の負債として残っている
- [ ] ⚠️ **D-10 の完了ガード（8 問そろわないと不合格）の採否を研究者が確認する**
