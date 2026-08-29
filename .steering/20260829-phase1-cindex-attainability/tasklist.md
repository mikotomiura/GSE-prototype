# タスクリスト

## 準備
- [x] `.steering/_handoff/next-session-prompt-phase1-cindex-attainability.md` を読む
- [x] `calibration_eval.rs` (313-340 / 470-530 / 565-580 / 650-720 / 940-985) を読む
- [x] `cohort.rs` (8-30 / 125-200 / 420-500) を読む
- [x] forking paths にならないことの論証を `decisions.md` に自分の言葉で書く
- [x] git 前提の確認 (`git fetch` / `git rev-list --left-right --count origin/main...HEAD` /
      `src-tauri/` の交差確認) — 実施済み: origin/main は `src-tauri/src/analysis/` 未変更
- [x] `feat/phase1-cindex-attainability` ブランチを作成 (origin/main から)

## 実装
- [x] `concordance_index_detailed(pairs) -> Option<(f64, u64)>` を新設し、
      `concordance_index()` をその薄いラッパにする
- [x] `SubjectCindex` に `x_q1_session_comparable_pairs` / `y_q2_session_comparable_pairs` /
      `x_q1_session_min_comparable_pairs` / `x_q1_session_median_comparable_pairs` /
      `x_q1_gate_attainable` を追加
- [x] `compute_calibration_metrics()` の per-session ループを書き換え、
      値とペア数を同じ `filter_map` (`.unzip()`) で収集する (順序・母数を一致させる)
- [x] `cindex_gate_attainable()` を新設し、`CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN` を参照する
      (数値直書きなし。既存 `median_u64` ヘルパを再利用)
- [x] `cohort.rs` の `CindexView` / `CohortSubjectSummary` に対応フィールドを配線する
- [x] `cohort_verdict()` の判定ロジック (`gate_eligible` / `model_gate` 呼び出し) は変更しない (確認済み)

## テスト
- [x] 比較可能ペア 1 件のセッションでペア数が 1 と報告されるテスト
- [x] 比較可能ペア 0 件のセッションが中央値母数・ペア数 Vec の両方から一致して除外されるテスト
- [x] 既存 `x_q1_session_median` 等の値が変わらない回帰テスト
- [x] `concordance_index()` と `concordance_index_detailed()` の第 1 要素が一致するテスト
- [x] `cindex_gate_attainable()` の境界ケーステスト
- [x] `cohort.rs` の新フィールドのデシリアライズテスト (新 JSON / 旧 JSON 両方)
- [x] `cargo test --workspace` (src-tauri/ から) が全緑 (520 lib + 30 replay-bin + 1 integration)
- [x] `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json`
      が byte-equal で通ることを実測確認 (`OK: 15 snapshots match`)
- [x] `cargo run --bin emit_schema` の drift check (対象外だが実測: drift なし)
- [x] `cargo fmt --check` / 変更ファイルの `cargo clippy` (無関係な既存 warning のみ・新規指摘なし)

## レビュー
- [x] code-reviewer によるレビュー — HIGH 1 件 (`cindex_gate_attainable` が恒真関数) /
      MEDIUM 5 件 / LOW 6 件
- [x] security-checker によるレビュー — CRITICAL/HIGH 0 件。MEDIUM 1 件は `bin/cohort.rs` の
      既存の穴 (本 diff 範囲外・別 PR 推奨)
- [x] HIGH 指摘への対応 — `cindex_gate_attainable` を「完全一致でなくても閾値を超えられるか」
      (`k` 依存の非自明な判定) に再実装。MEDIUM 5 件のうち本 diff 範囲内の 4 件対応
      (doc の過大主張修正・自己完結化・None 分岐の統合テスト追加・commit 前提の明記)。
      LOW のうち借用順コメントは修正で不要化、y_q2 doc 明確化・median_u64 切り捨て注記・
      debug_assert 追加を実施
- [x] `/cross-review` (Claude + Codex 独立レビュー) — `/finish-task` Step 3 で必須。
      両者一致 HIGH 1 件: `cindex_gate_attainable` が「最小ペア数セッション単体」の到達可能性を
      「この被験者全体」の到達可能性であるかのように過大主張していた反例を発見 → 関数・
      フィールド名を `cindex_min_session_gate_attainable` / `x_q1_min_session_gate_attainable`
      に再スコープし docstring を是正 (判断 3)。Codex 単独 MEDIUM 1 件 (cohort_verdict 経由の
      Some(...) 伝播テスト欠如) + LOW 1 件 (乗算オーバーフロー経路) も対応。
      rustdoc lint 指摘は CI に該当ステップ無しのため却下 (妥当)。判定ロジックへの実害は
      終始ゼロ (判断 1 で確認済み)

## ドキュメント
- [x] `§5` の議題 (PreReg-4 の all() 型ゲート構造・Kill 条件の計器側の枝・
      notes.md へのペア数併記) を `decisions.md` に起票する (研究者判断・こちらで決めない)
- [x] 凍結文書 (`docs/preregistration-v0.3.md`) は変更しない (`git diff HEAD` で 0 差分を実測確認)

## 完了処理
- [x] design.md の最終化
- [x] decisions.md の最終化 (§5 議題を含む・判断 2 は当初実装の恒真バグと修正内容を記録)
- [x] git commit (`ef8286d`)
- [ ] `/finish-task` (Step 3 の `/cross-review` を飛ばさない。main へマージしないなら
      Step 5 の CI 発火確認は N/A と明記する)
- [ ] `! git fetch origin && git rebase origin/main && git push -u origin feat/phase1-cindex-attainability`
      を研究者に渡す形で提示する (push/rebase は dev から実行できない)
