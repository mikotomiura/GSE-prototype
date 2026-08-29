# Phase1 C-index の到達可能性診断を実装する

## 背景

G1（統制タスク実験）の判定が `MANIPULATION_CHECK_FAILED` で止まった件を文献で詰めた結果、
「ゲートが到達不能な水準を要求していた」ことが分かった
（`docs/literature/20260827-manipulation-check-attainability-and-task-complexity.md` カード 2）。

G1 は `§5.2` で到達可能性をラベル非依存の診断値として必ず報告している
（`attainable_min_p_for_this_subject` / `test_can_reject_at_all`）。
一方、Phase1 の C-index ゲート判定（`calibration_eval.rs` / `cohort.rs`）には、
対応する到達可能性診断がまだ無い。

C-index は `(concordant + 0.5·tie) / comparable` で定義され、比較可能ペア数 `comparable` が
極小のセッションでも、100 件のセッションと同じ重みで `session_median` に混ざる
（実測: P013 感度 `x_q1_pooled` は 1 ペア由来の 0.0、P011 主 `y_q2_session_median=1.0` も
極小ペア由来の疑いが強い）。この「何ペアの上に立った値か」が現状不可視である。

## ゴール

- `concordance_index()` の比較可能ペア数を捨てずに取得できるようにする
  （既存シグネチャは壊さない）。
- `SubjectCindex` に、中央値に寄与したセッションの比較可能ペア数（Vec・最小値・中央値）を追加する。
- ゲート閾値（`CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN`）に対する到達可能性を
  算術的事実（bool）として出す。新しい閾値は一切追加しない。
- `cohort.rs` の read-model にも同フィールドを配線する。
- 既存 54 本のテストを緑のまま保ち、上記の観点でテストを追加する。
- `.steering/` に forking paths にならないことの論証（`decisions.md`）と、
  凍結文書への影響の起票（研究者判断に委ねる議題）を記録する。

## スコープ

### 含むもの
- `src-tauri/src/analysis/calibration_eval.rs` へのコード変更・テスト追加
- `src-tauri/src/analysis/cohort.rs` へのコード変更・テスト追加
- `.steering/20260829-phase1-cindex-attainability/decisions.md` への forking paths 論証・議題起票

### 含まないもの
- `docs/preregistration-v0.3.md` の改訂（凍結文書。書き換えない。影響は decisions.md に起票するのみ）
- `experiments/20260731-phase1-calibration-analysis/` の再実行（実データが必要・別タスク）
- G1 側（`experiments/20260801-controlled-friction-task/`）の修正（別トラック）
- 判定閾値（`>0.55` / `≥0.65` / `≥20件/人`）の変更（1 つも動かさない）
- `HMM_VERSION` の bump（挙動を変えないため不要。ただし replay byte-equal は実測確認する）
- 既存 `AxisDispersion.comparable_pairs`（生の Q1/Q2 分布向け）の拡張・流用
  （評価セッションごとの C-index 向けとは母数が異なるため別物として実装する）

## 受け入れ条件

- [ ] `concordance_index_detailed(pairs) -> Option<(f64, u64)>` が新設され、
      既存 `concordance_index()` はその薄いラッパになっている
- [ ] `SubjectCindex` に session ごとの比較可能ペア数（x_q1 / y_q2）が、
      中央値計算と同じ集合・同じ順序で載っている
- [ ] `x_q1_gate_attainable` 等の到達可能性 bool が `CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN` を
      参照して算出され、数値の直書きがない
- [ ] `cohort.rs` の `SubjectCalibrationView` に対応フィールドが配線されている
- [ ] 比較可能ペア 1 件のセッションで C-index が報告されペア数が 1 と出るテストがある
- [ ] 比較可能ペア 0 件（straight-lining）のセッションが中央値の母数からもペア数 Vec からも
      一致して除外されるテストがある
- [ ] 既存の `x_q1_session_median` 等の値が 1 ビットも変わらない回帰テストがある
- [ ] `concordance_index()` と `concordance_index_detailed()` の第 1 要素が常に一致するテストがある
- [ ] `cargo test --workspace`（`src-tauri/` 配下）が全緑
- [ ] `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json`
      が byte-equal で通ることを実測確認済み
- [ ] `decisions.md` に forking paths にならないことの論証（自分の言葉）と、
      §5 の議題（PreReg-4 の all() 型ゲート構造・Kill 条件の計器側の枝・notes.md へのペア数併記）が
      起票されている

## 関連ドキュメント

- `.steering/_handoff/next-session-prompt-phase1-cindex-attainability.md`（本タスクの詳細仕様・SSOT）
- `docs/literature/20260827-manipulation-check-attainability-and-task-complexity.md` カード 2 / カード 7
- `experiments/20260801-controlled-friction-task/preregistration.md` §5.2（G1 側の先例）
- `experiments/20260731-phase1-calibration-analysis/notes.md` §3 / §4
- `docs/preregistration-v0.3.md` PreReg-2 / PreReg-4 / PreReg-5（触ってはいけない閾値の確認）

## 運用メモ
- /reimagine 適用: No
- 理由: 設計判断は前セッションで既に確定済み（§1 の既存実装マップ・§2 の到達可能性の定義・
  §3 の forking paths 論証はすべてハンドオフ文書内でコード根拠付きで解決されている）。
  実装は既存パターン（`AxisDispersion` / `SubjectCalibrationView` の部分ビュー先例）への
  素直な追従であり、複数案の比較や再設計を要しない。
