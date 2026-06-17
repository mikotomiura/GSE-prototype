# decisions.md — calibration-smoke-runbook

## SD-1 製品コードを触らず周辺整備に限定 (logger P000 固定は運用で吸収)
- **判断**: logger の `raw/P000` 固定は改修せず、多人数収集は runbook の手動 `P001/P002` 整理で吸収。
- **根拠**: blind 化と同様、収集の本質は実機手動。schema/logger 改修はスコープ外で回帰リスクを増やす。
  helper + runbook + 検証に絞ることで最小リスクで「実行可能化」を達成。

## SD-2 helper は .sh (git-bash) のみ (ユーザー承認)
- **判断**: PowerShell 版は作らず bash 1 本。runbook に git-bash 前提を明記。
- **根拠**: hook/scripts は bash 前提 (agent-shared)。PS5.1 の落とし穴対応の churn を避ける。

## SD-3 出力レイアウトは gse-cohort 契約に合わせる
- **判断**: `metrics/Pxxx/<os>/Pxxx.calib.json` を生成 (os は uname 判定)。
- **根拠**: gse-cohort の `scan_base` (metrics/ 優先) + `MAX_SCAN_DEPTH=3` 再帰走査に収まる。replay の
  `<sessions...> --calibration --json` は positional 先頭でパーサと整合。セッションは辞書順=時刻順。

## SD-4 review 対応 (code-reviewer HIGH/MEDIUM)
- **H1 atomic write**: `> out_file` 直書きは失敗時に空 calib.json を残し後続 cohort を毒する →
  一時ファイル + 成功時 `mv`。さらに 1 被験者の失敗で batch を止めない (warn+continue, failed フラグ)。
- **H2 (false positive・検証済)**: gse-cohort は全 verdict で exit 0 (判定は JSON の overall)。
  非ゼロは I/O/parse エラー時のみ。ドライランで report 行到達を実証。コメントで明記。
- **MEDIUM**: `ls|sort|while read` → 純 glob (nullglob)。`MAX_CALIBRATION_FILES=64` 超過は warn+skip。
- **LOW**: REPO_ROOT をスクリプト位置基準に (dataset 側からの実行に堅牢)。OS unknown 時 warn。
- **security-checker = PASS**: NDJSON は read-only・集計 JSON のみ write・git add/送信ゼロ。dataset 側
  `.gitignore` が raw NDJSON を二重防御。runbook は「metrics/cohort の集計 JSON のみ共有」を明記。

## 申し送り
- **Codex /cross-review は jq 不在でスキップ** (Claude code-reviewer + security-checker のみ実施)。
  [[project-codex-review-needs-jq]]。
- **実データ収集 (GUI 実機) は未実施** (headless 不可)。本タスクは収集を回せる基盤 + 非GUI検証まで。
  実 PreReg 判定は実データ収集後に `scripts/run-calibration-cohort.sh` を実行して取得する。
- `cargo test --workspace` は製品コード無変更のため省略 (main の 157+12 と同一)。
