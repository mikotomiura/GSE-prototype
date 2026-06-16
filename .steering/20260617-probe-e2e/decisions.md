# decisions.md — Task E「通し検証 (cohort orchestration)」

## ED-1 ブランチは feature/probe-collect (A+B+C+D 統合 tip) から分岐 (2026-06-17 ユーザー承認)
- **判断**: handoff の 2 択 (a) collect→main の PR を先に出す / (b) collect から直接分岐 のうち **(b)** を採用。
  main マージは E 完了後に回す。未コミットの infra(Codex bridge)+docs 39 ファイルは E と分離 (放置・選択 add)。
- **根拠**: 最速で A+B+C+D 統合ツリー上で E に着手できる。handoff 本文は「probe-analysis から分岐」と緩く書くが
  実際の統合 tip は `feature/probe-collect` (probe-analysis は merge+handoff コミットぶん遅れている) のため collect を起点とした。

## ED-2 cohort 設計は v2 採用 (D に一切触れない・read-model DTO + 独立バイナリ) (/reimagine 1 回目)
- **判断**: /reimagine で v1 (cohort_verdict を calibration_eval に追記・CalibrationReport 全体に Deserialize 派生追加・
  I/O 形態未確定) と v2 (D 無変更・新規 analysis/cohort.rs + 独立バイナリ gse-cohort・必要フィールドだけの
  read-model DTO) を比較し **v2** を採用 (2026-06-17 ユーザー判断)。
- **根拠**: handoff 最重要制約「D を再実装しない／凍結」を最も忠実に満たす。`calibration_eval.rs`・`replay.rs`・
  `schema_dto.rs` を 1 文字も変えない。serde の未知フィールド無視で軽量 read-model を作れば重い
  CalibrationReport 全体の Deserialize 化が不要。独立バイナリは入力モデル (JSON ツリー vs 1 NDJSON) の違いに
  素直で、凍結 `--snapshot` 回帰経路を保護する。詳細は design-comparison.md。

## ED-3 cohort ゲート駆動 = session-median C-index (凍結契約に従う・設計判断 B)
- **判断**: handoff 設計判断 B (pooled vs session-median) は **session-median** に確定。
- **根拠**: PreReg-4 は凍結済みで文言が「各人の C-index **中央値**」。凍結契約を曲げない (forking paths 排除)。
  `x_q1_pooled` は頑健性参考値として cohort レポートに併記するがゲート判定には使わない。
  session_median が `None` (セッション不足) の被験者は判定母数から除外し notes に記録 (§11)。

## ED-4 最終判定に DataInsufficient を追加し「無理に Go と言わない」を構造化
- **判断**: 判定を `Go`/`Kill`/`Inconclusive`/`DataInsufficient` の 4 値とし、PreReg §2 の優先順位で合成。
  PreReg-5 充足が一部被験者のみなら model Go でも `Inconclusive` (データ拡充) に降格させる。
- **根拠**: requirement「PreReg-5 未達なら『データ拡充』と正直報告・無理に Go と言わない」(§11 主張限界) を
  enum とロジックで強制する。Kill/Inconclusive に押し込めず DataInsufficient を分けることで「測定不能」と
  「測定して Kill/判定保留」を区別する。

## ED-5 review 対応: PreReg-2 被験者要件をゲート母数条件に追加 (code-reviewer HIGH)
- **判断**: モデルゲート母数を「主指標 & session_median 有 & PreReg-5 充足 & **per_subject_pass**」に変更。
- **根拠**: PreReg-2 の latency≤10s・有効≥20件は D が `per_subject_pass` に畳み込んでいる。これを母数条件に
  含めないと測定品質不十分な被験者の C-index が Go 母数に混入する。`excluded_for_measurement_quality` で監査。

## ED-6 review 対応: 提示プローブ0件は DataInsufficient (code-reviewer MEDIUM)
- **判断**: `decide_overall` で総提示プローブ0件を測定法 Kill より先に DataInsufficient へ分岐。
- **根拠**: 回答率 0.0 を「測定法 Kill」と誤断定しない。提示0件は測定不能であって測定法の失敗ではない。

## ED-7 review 対応: drift ガード強化 + I/O 安全化 (code-reviewer MEDIUM / security MEDIUM)
- **判断**: (a) read-model drift ガードテストを空レポートだけでなく **非ゼロ実レポート** (compute_calibration_metrics に
  回答済み probe を渡す) でも検証。(b) `scan_base` は `metrics` が実体 dir のときだけ採用 (symlink follow 防止)。
  (c) `load_subject` は `File::take(MAX+1)` で TOCTOU と無上限 read を排除。(d) 被験者数の早期 bail。
- **根拠**: serde の `#[serde(default)]` がフィールド名 rename を静かに飲むリスク (空レポートでは検出不能) を
  非ゼロ値で塞ぐ。基点 symlink follow / stat→read 間の差し替えという「自称する防御契約」と実装の乖離を閉じる。

## 受容 (根拠付き / 延期)
- **median_f64 の局所重複**: `calibration_eval` の private median と意図的に分離 (D 凍結方針)。共通 stats 切り出しは
  将来タスク。doc コメントで分離理由を明記。
- **skip 被験者 (calib JSON 0/複数件) は CohortReport notes に載らず CLI stderr のみ**: cohort_verdict は走査前の
  ディレクトリ事情を知らないため。stderr の tracing::warn で可視化し、JSON には載らない旨を design に記録 (LOW)。
- **自己ドッグフード (実アプリ起動→実セッション記録) は実機手動**: input/ の OS フックは headless 不可 (CLAUDE.md
  「input/ は実機手動確認」)。E2E は (1) D の実出力 JSON が read-model に載る drift ガードテスト + (2) fixture ツリーを
  gse-cohort に通す実行確認でコード経路を担保し、GUI 実セッション記録は運用手順として残課題に明記。
- **docs (functional-design/repository-structure/glossary) の E 追記は作業ツリーに残置**: Task D の docs 追記分と
  混在しており (PR#5 未収録)、E の**コード**コミットには docs を含めず新規ソース + steering のみ選択 add する (ED-1)。
