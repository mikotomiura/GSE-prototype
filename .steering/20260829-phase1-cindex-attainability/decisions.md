# 重要な設計判断

## 判断 1: 到達可能性診断は forking paths にあたらない

- **判断日時**: 2026-08-29
- **背景**: PreReg-4 は C-index のゲート閾値 (`CINDEX_GO_MEDIAN=0.65` / `CINDEX_GO_ALL_MIN=0.55` /
  `CINDEX_KILL_MEDIAN=0.55` / `CINDEX_KILL_PER_SUBJECT=0.50`) を凍結している。
  本タスクはこれらの閾値に対する「到達可能性 (bool)」を新しい出力フィールドとして追加するが、
  これは事前登録の合否契約に事後的な自由度を持ち込む forking paths ではないか、という懸念が
  前セッションで検討され、コードで解決済みだった (ハンドオフ文書 §3)。ここでは自分の言葉で
  論証を再確認する。

- **選択肢**:
  - A: 到達可能性 bool を出さず、比較可能ペア数の生データ (Vec・最小値・中央値) のみ報告する
  - B: 到達可能性 bool を、既存の凍結定数 (`CINDEX_GO_MEDIAN` 等) を参照する形で算出し、
    数値を直書きしない
  - C: 独自の「妥当な最小ペア数」等の新しい閾値を新設し、それを基準に到達可能性を判定する

- **採用**: B

- **理由**:
  1. **新しい閾値を 1 つも導入していない**。到達可能性の判定は「このペア数 `k` で
     `(concordant + 0.5·tie) / k` が理論上 `CINDEX_GO_MEDIAN` 以上になり得るか」という
     純粋な算術命題であり、`CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN` という**既存の凍結定数**を
     参照するだけである。これは `AxisDispersion.degenerate` (`calibration_eval.rs:664-669`) が
     「比較可能ペア 0 件なら concordance は定義不能」という算術的事実を出しているのと同型であり、
     C-index の値域が `0.5/k` 刻みであるという数学的性質を明示しているに過ぎない。
  2. **判定母数を変えていない**。`model_gate()` / `cohort_verdict()` の `gate_eligible` 判定条件
     (`v.included_in_primary && has_median && prereg5_ok && v.measurement.per_subject_pass`,
     `cohort.rs:437-438`) には一切手を入れず、除外規則も追加していない。到達可能性は
     「ゲート母数に**既に**含まれている被験者」について、追加の記述統計として併記するだけである。
  3. **合格経路を 1 本も増やしていない**。到達可能性 `false` を理由に被験者を Kill に落とす、
     あるいは到達可能性 `true` を理由に Go に昇格させる、といった分岐は判定関数
     (`model_gate` / `measurement_gate` / `cohort_verdict`) のどこにも追加していない。
     到達可能性は `notes` や `CohortSubjectSummary` に併記される記述統計であり、
     `CohortDecision` (`Go` / `Kill` / `Inconclusive` / `DataInsufficient`) の算出経路には
     一切関与しない。
  4. 選択肢 A (bool を出さない) も forking paths の懸念自体は生じないが、比較可能ペア数を
     見て「この被験者は 0.55 を超えられたはずがなかった」と**人間が毎回暗算する**運用になり、
     G1 側 (`attainable_min_p_for_this_subject` / `test_can_reject_at_all`) との対称性が崩れる。
     選択肢 C は明確に forking paths (新しい閾値の事後追加) にあたるため却下。

- **トレードオフ**: `x_q1_min_session_gate_attainable` は「この被験者のゲート値への理論的到達可能性」を
  示すのみで、「実際に (コホート全体として) ゲートを通ったか」の判定は引き続き `model_gate` /
  `cohort_verdict` が別途行う。読み手が両者を混同しないよう、フィールド名とドキュメントコメントに
  「理論的到達可能性」であることを明記する。

- **影響範囲**: `calibration_eval.rs` の `SubjectCindex` / `CalibrationReport` (JSON 出力に
  フィールド追加)、`cohort.rs` の `SubjectCalibrationView` / `CohortSubjectSummary` (同様)。
  `model_gate` / `measurement_gate` / `cohort_verdict` の判定ロジックには変更なし。

- **見直しタイミング**: 到達可能性 bool を判定ロジック (`model_gate` 等) の入力として使う
  提案が出た場合は、それは判定基準の変更にあたるため、本判断の前提(「報告専用」)が崩れる。
  その時点で改めて forking paths の検討が必要。

## 判断 2: 当初の `x_q1_min_session_gate_attainable` は恒真関数だった → 「完全一致でなくても超えられるか」に定義し直した

- **判断日時**: 2026-08-29
- **背景**: 実装前に「G1 の `attainable_min_p_for_this_subject` / `test_can_reject_at_all` と対称な
  診断を作る」という前提で設計したが、`code-reviewer` サブエージェントのレビューで
  **当初実装が実質的に恒真関数 (常に `Some(true)`) であり、既存の `x_q1_session_median.is_some()`
  と情報量が完全に同一**という HIGH 指摘を受けた。この節はその指摘と修正内容の記録である
  (`verify-before-claiming` の精神: 前提を鵜呑みにせず実装後も検証を止めない)。
- **発見した事実 (当初実装の欠陥)**: 二項検定の p 値には「サンプル数 `n` が小さいと、どんな結果
  (例: 全問正解) でも有意水準 `α` を下回れない」という**構造的な下限**がある
  (G1 の `attainable_min_p_for_this_subject` はこの下限そのもの)。一方 C-index は
  `(concordant + 0.5·tie) / k` であり、比較可能ペアが **1 件でもあれば理論的最良値は `k` に
  関わらず常に `1.0`** になる。`CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN` はいずれも `1.0` 未満
  なので、「最良値がゲートを超えるか」を問う当初の判定は「寄与するセッションが 1 つ以上ある」
  場合に事実上常に `Some(true)` を返していた——G1 との構造的な非対称性を見落としていた。
- **修正 (`calibration_eval.rs` の `cindex_min_session_gate_attainable`)**: 問いを
  「**最良値が超えるか**」(恒真) から「**1 段階だけ劣化した次善値 `(2k-1)/(2k)` でもなお
  `CINDEX_GO_ALL_MIN` を超えるか**」に変更した。`k` に依存する非自明な判定になり、
  `k=1` (P013 感度の実例) では次善値が `0.5` で `0.55` を超えないため `Some(false)`
  (=「完璧な結果以外あり得ない」)、`k≥2` では次善値が `0.75` 以上になり `Some(true)` になる
  (テスト `gate_attainable_false_when_only_a_perfect_session_could_pass` /
  `gate_attainable_true_when_a_non_perfect_result_could_still_pass` で固定)。
  あわせて `CINDEX_GO_MEDIAN` (コホート横断の中央値条件) の参照はやめた ——
  それは被験者 1 人の比較可能ペア数からは語れない性質であり、per-subject フィールドに
  中央値条件を畳み込むのは別の指摘 (MEDIUM) だったため。
- **診断としての主情報は今も bool 単体ではなく生データの方にある**:
  `x_q1_session_comparable_pairs` / `min` / `median` が実際のペア数を語り、
  修正後の bool は「その中で最も脆弱なセッションが、完璧さに依存せずゲートを超えられる
  見込みがあるか」という**要約**を添えるものである。
- **見直しタイミング**: 本判断は完了したものとして扱う。`§5` 議題 4 (旧: リネーム検討) は
  本修正で実質的に解消したため取り下げる。

## 判断 3: 判断 2 の修正はスコープを超えて「この被験者」を主張していた → フィールド名を再スコープした

- **判断日時**: 2026-08-29
- **背景**: `/cross-review` (Claude 独立検証 + Codex `gpt-5.5`) が、判断 2 で修正した
  `cindex_gate_attainable()` の docstring に対し**両者独立に同じ根本原因の指摘**をした
  (両者一致は優先度最高。`cross-review` skill の運用方針通り採用)。
- **反例 (Claude が数式から構成し実測はしていないが `median_f64` / `concordance_index_detailed`
  の定義から数学的に導出できることを確認)**: セッション A (`k=1`, X タイ → C-index `0.5`) と
  セッション B (`k=10`, 9 concordant/1 discordant → C-index `0.9`) を持つ被験者の
  `x_q1_session_median = (0.5+0.9)/2 = 0.7`。これは `CINDEX_GO_ALL_MIN=0.55` を
  **非完全一致のまま**超えている。しかし `min(1,10)=1` を渡された旧
  `cindex_gate_attainable(Some(1))` は `Some(false)` を返し、docstring は「この被験者が
  ゲートを超えるには完璧な結果以外あり得ない」と主張していた——**現に超えているのに、
  である。** 関数自体の算術 (次善値 `(2k-1)/(2k)`) は判断 2 の時点で既に正しかったが、
  **「最小ペア数セッション 1 本の余裕度」を「被験者全体の到達可能性」であるかのように
  docstring とフィールド名が過大主張していた**ことが根本原因。
- **修正**:
  1. 関数名・フィールド名を `cindex_gate_attainable` / `x_q1_gate_attainable` から
     `cindex_min_session_gate_attainable` / `x_q1_min_session_gate_attainable` に変更し、
     「最小ペア数セッション単体」に対する値であることを名前自体に固定した。
  2. `calibration_eval.rs` の docstring と `SubjectCindex` / `CohortSubjectSummary` の
     フィールド doc に、上記の反例と「これは被験者全体の到達可能性ではない」という
     警告を明記した。
  3. 判定ロジック (`model_gate` / `cohort_verdict`) には元々使われておらず (判断 1)、
     合否判定への実害はゼロ。修正は名前・ドキュメントの是正のみで、算術ロジックは不変
     (回帰テストは既存のまま全緑)。
  4. あわせて Codex 指摘 (LOW): `(2*k-1)/(2*k)` の乗算をやめ `1.0 - 0.5/k` に書き換え、
     大きな `k` での乗算オーバーフロー経路を構造的に無くした (挙動は数学的に同一)。
  5. あわせて Codex 指摘 (MEDIUM): `cohort_verdict()` を経由して `Some(...)` 値が
     `CohortSubjectSummary` まで正しく伝播することの end-to-end テスト
     (`cohort_subject_summary_propagates_some_attainability_values_through_verdict`) を追加した
     (既存テストは `None` の伝播しか検証していなかった)。
- **見直しタイミング**: 「最小ペア数セッション単体」という限定されたスコープでも、
  研究者が引き続き誤読するようであれば、判断 2 で検討した「中央値全体を考慮した再設計」
  (最小ペア数セッションだけを次善値に固定し他は実測値のまま中央値を再計算) を次回実装で
  検討する。本タスクでは report-only の原則 (判断 1) を優先し、最小修正 (名前の是正) に留めた。

---

## §5 次の改訂の議題 (⚠️ 研究者判断・こちらでは決めない)

以下は凍結文書 (`docs/preregistration-v0.3.md`) の次回改訂で検討してほしい議題である。
**本タスクではコードのみを変更し、凍結文書は 1 バイトも書き換えていない。**

| # | 議題 | 出所 |
|---|---|---|
| 1 | ⚠️★★★ `PreReg-4` の「十分なデータがある全員で `>0.55`」は `all()` 型のコホートゲートである。 | 2026-08-27 カード 2 |
| | 被験者 5 名・1 人あたり通過率 0.8 なら **コホート通過率 0.328**、0.7 なら **0.168**。 | |
| | コードでも見える (`calibration_eval.rs` の `model_gate`): | |
| | `let all_above = subject_cindices.iter().all(\|&c\| c > CINDEX_GO_ALL_MIN);` | |
| | 被験者を増やすほど通りにくくなる (G1 の `analyze.py` の `all(m["passed"])` と同じ構造)。 | |
| 2 | Kill 条件に**計器側の枝**を足す —— 比較可能ペアが極小の被験者を `Kill` でなく | [V90] Fayant 逐語「a failed MC could be attributed to |
| | `InstrumentInsufficient` として扱えるか。本タスクで追加した `x_q1_session_min_comparable_pairs` / | measurement problems」 |
| | `x_q1_min_session_gate_attainable` はこの判断のための**材料**であり、判定ロジックには組み込んでいない。 | |
| 3 | `notes.md` の「X→Q1 は 5 名全員で 0.52 以下」に**ペア数を併記**する | 2026-08-28 の実測 (`§2-3`) |
| | (P013 感度は **1 ペア**由来であることを、生の観測値と一緒に読めるようにする)。 | |
| ~~4~~ | ~~判断 2 で発見した恒真バグ~~ → **実装時に修正済み** (`code-reviewer` HIGH 指摘への対応)。 | 本タスクの実装 (2026-08-29) |
| | `x_q1_min_session_gate_attainable` は「完全一致でなくても `CINDEX_GO_ALL_MIN` を超えられるか」を問う | |
| | `k` 依存の非自明な判定に定義し直した (判断 2 参照)。研究者側の追加対応は不要。 | |

⚠️ **1・2 は研究者判断である。こちらで決めない。**
