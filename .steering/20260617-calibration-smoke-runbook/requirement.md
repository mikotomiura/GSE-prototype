# Task — calibration-smoke-runbook (自己ドッグフード→3-5名スモークの実行基盤)

## 背景

v0.3 較正の計測基盤 (A schema / B probe scheduler / C collect UI / D offline解析 / E cohort判定 /
blind dashboard) は全て main に統合済だが、**実データで一度も駆動されていない**。Task E の残課題
「(2) 自己ドッグフード→ end-to-end 確認、(3) 3-5名スモーク→ PreReg 判定」を実行可能にする。

実データ収集の**核は実機手動** (GUI アプリを起動し実キーストロークを OS フックで記録) であり headless
不可。本タスクは「人間が collection を回せるようにする周辺整備」と「解析パイプラインの非GUI検証」を担う。

注意点 (調査で判明):
- logger は `$GSE_DATASET/raw/P000/` に **P000 固定**で NDJSON を書く (`logger::default_log_path`)。
  多人数収集では各収集分を運用側で `P001/P002/...` に整理する必要がある。
- 既存 `sync-session.*` / `sync-all.*` は v0.2 `--metrics` 経路。v0.3 は `--calibration`→`gse-cohort` で別経路。
- NDJSON は本リポにも gse-dataset にもコミットしない。共有は metrics/calib JSON (集計値) のみ (§10)。

## ゴール

1. **ビルド検証**: A〜E+blind 統合アプリがビルドできることを確認 (cargo build + npm run build、可能なら tauri build)。
2. **較正パイプライン helper**: NDJSON ツリー → 被験者別 `*.calib.json` (`gse-replay --calibration`) →
   `gse-cohort` を 1 コマンドで回す helper を `scripts/` に追加 (既存 sync-* の I/O 契約に整合)。
3. **収集ランブック**: dogfood (自己1セッション) → smoke (3-5名) の手順書。env 設定 (GSE_DATASET=C:\gse-dataset)・
   P000 固定の整理手順・PreReg-5 最低要件 (eval≥6・probe≥16/人)・判定の読み方を明記。
4. **end-to-end ドライラン**: 既存 fixture (calib_subject NDJSON + cohort calib.json) で helper を通し、
   実収集前にコマンド連鎖が動くことを実証。

## スコープ

### 含むもの
- scripts/ の較正パイプライン helper (bash + 可能なら ps1)。
- 収集ランブック (docs/ または .steering/)。
- ビルド検証と fixtures ドライラン。

### 含まないもの
- 製品コード (`src-tauri/src/`, `src/`) の挙動変更 (logger の P000 固定の改修も含めない。運用で吸収)。
- 実データ収集そのもの (GUI 実機・人手。私の役割は基盤整備と非GUI検証)。
- PreReg 閾値・判定契約の変更。比較条件/波形 cue/コーナー介入 (別タスク)。
- gse-dataset リポへの実データ commit。

## 受け入れ条件

- [ ] 統合アプリのビルドが通る (少なくとも `cargo build` + `npm run build` 緑。tauri build は可能なら)。
- [ ] 較正パイプライン helper が NDJSON ツリー → calib.json → cohort 判定を 1 コマンドで実行できる。
- [ ] helper を既存 fixture でドライランし、`gse-cohort` 判定 JSON が出ることを実証。
- [ ] ランブックに env 設定・P000 整理手順・PreReg-5 最低要件・Go/Kill/INCONCLUSIVE/DataInsufficient の
      読み方が記載され、未達時は「データ拡充」と正直報告する運用が明記される。
- [ ] 製品コード無変更。NDJSON を commit しない。

## 関連
- `.steering/20260616-probe-analysis/` (D) / `.steering/20260617-probe-e2e/` (E)
- `src-tauri/src/bin/{replay,cohort}.rs`, `src-tauri/src/logger.rs` (default_log_path)
- `docs/development-guidelines.md` §10 / `docs/preregistration-v0.3.md`
- `scripts/sync-session.*` / `scripts/sync-all.*` (I/O 契約の参考)

## 運用メモ
- /reimagine 適用: **No** (既存パイプラインの薄い wrapper + 手順書。設計の再構築なし)。
- ブランチ: `chore/calibration-smoke-runbook` (起点 = origin/main 294176b = A..E+blind+env 統合済)。
