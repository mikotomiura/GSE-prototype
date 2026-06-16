# 次セッション用プロンプト — Task E「通し検証(cohort orchestration + 自己ドッグフード→3-5名スモーク)」

> 用途: 新しいセッションの最初にこのファイルの「プロンプト本文」を貼り付ける。
> 新セッションは CLAUDE.md / MEMORY.md を自動ロードする前提。
> 背景: A(schema, main merge済 PR#4)/ B(scheduler)/ C(frontend)/ **D(オフライン解析)** 実装・cross-review 済。
>        実装順 A→(B∥C)→D→**E**。次は最後の **E = 通し検証**。

---

## ⚠️ 着手前の前提確認(ブランチ整理)

**2026-06-17 時点の実状**: PR #5(D)は **`feature/probe-collect` を base にマージ済**(main ではない)。よって:
- `main` = **A のみ**(PR#4)。
- `feature/probe-collect` = **A+B+C+D が統合された tip**(B scheduler + C frontend + D 解析が全部入り)。
- B/C/D はまだ **main に届いていない**(`feature/probe-collect → main` の PR が未作成)。

E は A+B+C+D 統合ツリーが必要(自己ドッグフードで実アプリを動かす)。着手前に状態を確認し選ぶ:
1. **推奨**: `feature/probe-collect → main` の PR を出してマージ(差分 = B+C+D。A は main 済)→ **main から `feature/probe-e2e` を分岐**。以降は通常の main 起点に戻る。
2. 先に進めるなら **`feature/probe-collect`(= A+B+C+D 統合 tip)から `feature/probe-e2e` を分岐**。
※ どちらにするか・`feature/probe-collect → main` を今出すかをユーザーに確認してから着手する(勝手にマージしない)。
※ 作業ツリーに未コミットの infra(Codex bridge)+ docs 変更が残存する。Task D の docs 追記分もそこに混在
   (PR #5 未収録)。E で docs を touch/commit する際は混在に注意し、E 関連ファイルのみ選択 add する。

---

## プロンプト本文(ここから下をコピペ)

```
Task E「通し検証」を開始する。v0.3 較正スモーク(D-14)実装順 A→(B∥C)→D→E の最後の E。
A(schema)/B(probe scheduler)/C(frontend collect)/D(オフライン解析 calibration_eval + gse-replay --calibration)
は実装・cross-review 済(D は PR #5)。E は (1) 被験者横断 cohort orchestration の実装と
(2) 自己ドッグフード→3-5名スモークによる通し検証 + PreReg ゲート最終判定(Go/Kill/INCONCLUSIVE)。

【最初に】ブランチ整理を確認する。B/C/D はスタック(未マージ)。E は A+B+C+D 統合ツリーが要る。
推奨: B→C→D を順にマージして main 統合 → main から feature/probe-e2e。あるいは統合済みの
feature/probe-analysis から分岐。どちらにするかユーザーに確認してから着手する(勝手にマージしない)。

まず以下を読んで文脈を固める:
- .steering/20260616-probe-analysis/{requirement,design,decisions}.md(D の成果・DD-1..DD-9・責務境界)
- src-tauri/src/analysis/calibration_eval.rs(compute_calibration_metrics は 1 被験者・複数セッション。
  被験者横断ゲート model_gate(&[f64])/measurement_gate(overall, &[f64]) は純関数として実装済・golden test 済。
  CalibrationReport の per-subject フィールドと notes(assignment gap/skip/時刻単調性)を確認)
- src-tauri/src/bin/replay.rs(--calibration <s1..sN> --json で 1 被験者 metrics.json を出力。
  load_calibration_session の抽出形・MAX_CALIBRATION_FILES)
- docs/preregistration-v0.3.md(PreReg-1..8・Go/Kill/INCONCLUSIVE 契約・凍結・変更禁止)
- docs/development-guidelines.md §10(gse-dataset 連携: metrics/P*/<os>/*.metrics.json)
  + reference_gse_dataset_layout(本機は C:\gse-dataset・GSE_DATASET env + fallback)
- .idea/GSE_事後ラベリングシステム設計書_v0.3.md §7(2段ゲート)/§8(holdout 最低 eval≥6・probe≥16/人)/§11(主張限界)

手順(CLAUDE.md 厳守):
1. /start-task で probe-e2e を初期化([YYYYMMDD]-probe-e2e)。
2. /add-feature で実装(cohort orchestration はコード、ドッグフードは運用)。設計判断が複数案ありなら
   Step C 設計承認後に /reimagine。
3. 調査は file-finder + dependency-checker。実装後は code-reviewer + test-runner を並行。
4. /finish-task で完了。Step 3 で /cross-review(Claude code-reviewer ∥ Codex codex-review)が
   タスク完了ごとに必須(2026-06-16 ポリシー)。安全ゲートでブロック時のみ Claude 単独へ縮退し理由明記。

実装スコープ(Task E):
- (1) 被験者横断 cohort orchestration: gse-dataset の P000/P001/... ツリー(各被験者の複数セッション
  NDJSON or metrics.json)を走査し、被験者ごとに D の compute_calibration_metrics を適用 →
  被験者別 C-index 中央値の集合 → model_gate / measurement_gate でコホート Go/Kill/INCONCLUSIVE を算出 →
  cohort レポート(JSON)。実装方法は要設計(gse-replay に --cohort mode 追加 vs 別バイナリ vs Python script。
  D が出す per-subject metrics.json を集約する薄い層が素直)。D の純関数を再利用し再実装しない。
- (2) 自己ドッグフード: A+B+C+D 統合アプリをビルドして実セッションを 1 本記録(GSE_DATASET 設定先 = C:\gse-dataset)
  → gse-replay --calibration で解析が通り metrics.json が出ることを end-to-end 確認。input/ の OS フックは実機手動確認。
- (3) 3-5名スモーク: 実データ収集 → cohort orchestration で PreReg-1..8 ゲート判定。
  PreReg-5 最低要件(評価セッション≥6/人・ランダムプローブ≥16/人)を満たすか確認し、満たさなければ
  「データ拡充」と正直に報告(無理に Go と言わない・§11 主張限界)。

要件・制約(CLAUDE.md / agent-shared 厳守):
- **D の calibration_eval は再実装しない**。compute_calibration_metrics / model_gate / measurement_gate を再利用。
- **PreReg は凍結・変更禁止**(forking paths 排除)。閾値をデータに合わせて動かさない。
- **track=exploratory は主指標に混ぜない**。Recall 点推定は出さない(PreReg-6)。MNAR は範囲報告(PreReg-7)。
- **キーストローク内容・NDJSON 生ログは外部送信禁止**(data-privacy)。共有は metrics.json(集計値)のみ(§10)。
- analysis は OS API を呼ばない。schema 不変(A 凍結・schema_dto.rs touch しない)。
- 既存テスト無断削除禁止。cargo test/clippy 緑・gse-replay --snapshot 回帰維持・main ビルド可。
- 実装作業は .steering/[YYYYMMDD]-probe-e2e/ に記録(requirement/design/tasklist 必須)。

設計判断(/reimagine で 2 案比較推奨):
- A. cohort orchestration の実装形態: gse-replay に --cohort サブモード追加 / 独立バイナリ(gse-cohort) /
  Python 集約スクリプト(scripts/)。入力は被験者別 metrics.json か NDJSON ツリーか。
- B. 被験者別 C-index の代表値: D は pooled と session-median の両方を出す。横断ゲートにどちらを入れるか
  (PreReg-4「各人の C-index 中央値」の文言 → session-median 寄り。だが pooled の方がペア数多く頑健)。

スコープ厳守: 上記 (1)〜(3) 以外は追加しない。
- 比較条件(context_beacon/波形 cue)・統制課題(task_checkpoint)・コーナー介入 UI は Phase 4 以降(別タスク)。
- Recall 点推定・三層対照は v0.3 では取らない(延期)。
```

---

## メモ(Task D セッションからの申し送り)
- D は **1 被験者・複数セッション**を `--calibration s1 s2 s3` で受け、被験者内 C-index/holdout/測定法統計/
  MNAR/ビネット/二軸性を算出する。**被験者横断**(全員/2人以上の判定)は `model_gate`/`measurement_gate` を
  純関数として実装済み・合成多被験者で golden test 済(E はこれを実データで駆動するだけ)。
- D は窓集約を `AggSpec{source,stat}`(既定 ewma 中央値)で差替可能にしてある。感度比較が要れば E で活用。
- D の CalibrationReport は assignment↔label gap・skip 件数・時刻単調性を notes/フィールドで監査出力する
  (silent missingness 可視化)。E の cohort 集約でこれらを拾って「データ品質」を報告に含めると良い。
- docs(architecture/functional-design/glossary/repository-structure)の Task D 追記分は infra 変更と
  同一ファイル内で未コミット(PR #5 には含めず作業ツリーに残置)。E でこれら docs を触るなら混在に注意。
