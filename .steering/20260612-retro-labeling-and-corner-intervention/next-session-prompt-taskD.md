# 次セッション用プロンプト — Task D「オフライン解析 gse-replay 拡張」

> 用途: 新しいセッションの最初にこのファイルの「プロンプト本文」を貼り付ける。
> 新セッションは CLAUDE.md / MEMORY.md を自動ロードする前提。
> 背景: A(schema, PR#4 merge 済)/ B(backend scheduler, feature/probe-scheduler)/
>        C(frontend collect, feature/probe-collect, B にスタック) 実装・cross-review 済。
>        実装順 D-14: A→(B∥C)→**D**→E。次は **D**。
> 重要: Task D は **NDJSON を読む解析のみ**で B/C のランタイムに非依存(frontend を起動しない)。
>        → **main から分岐**してよい(A の schema があれば足りる)。合成 NDJSON fixture で開発し、
>        実データ検証は Task E(自己ドッグフード)で行う。

---

## プロンプト本文(ここから下をコピペ)

```
Task D「オフライン解析 gse-replay 拡張」を開始する。v0.3 較正スモーク(D-14)の実装順 A→(B∥C)→D→E の D。
A(schema)/B(probe scheduler, probe_assignment + probe_triggered emit)/C(frontend: realtime_label /
session_meta / vignette_response 記録) は実装済。D は記録された NDJSON を読み、時間隔離窓で X↔主観を
照合する**オフライン解析パイプライン**を gse-replay に足す。**frontend は起動しない**(NDJSON 解析のみ)。

ブランチ: Task D は NDJSON 解析のみで B/C ランタイム非依存。**main から feature/probe-analysis を分岐**する
(A の schema で足りる)。合成 NDJSON fixture で開発し、実データ検証は Task E。

まず以下を読んで文脈を固めてから着手すること:
- .idea/GSE_事後ラベリングシステム設計書_v0.3.md の
  §4.2(時間隔離窓 t−31s..t−1s)/ §7(2段ゲート・順序 C-index・方向性)/ §8(前向き固定 holdout)/
  §9(Recall はスモークで推定しない)/ §10(MNAR 上下限・範囲報告)/ §6.4(二軸性判定)/ §15(PreReg-1..8)
- .steering/20260612-retro-labeling-and-corner-intervention/decisions.md の
  D-8(窓)/ D-10(2段ゲート・|r|≥0.30 廃止)/ D-11(前向き holdout)/ D-12(Recall/MNAR)/ D-14(metrics.rs 流用禁止)
- .steering/20260616-probe-schema/decisions.md の TA-3(replay.rs は Task D で consumption variant 追加)
- .steering/20260616-probe-collect/decisions.md(C が記録する realtime_label/vignette_response の形)
- src-tauri/src/bin/replay.rs(enum ReplayEvent = 読み込み専用ミラー・未知 type は parse_failed_lines で skip)
- src-tauri/src/analysis/metrics.rs(既存 ConfusionMatrix/precision/recall は **v0.2 流・流用禁止**。C-index 系を別パスで追加=D-14)
- src-tauri/src/analysis/loop_step.rs(FeatSnapshot: ewma_x/ewma_y/raw_x/raw_y/obs 等 = 窓内 X/Y 集約の素)
- src-tauri/src/logger.rs(NDJSON の各 type の正確なフィールド: realtime_label/probe_assignment/session_meta/vignette_response)
- docs/development-guidelines.md §10(gse-dataset 連携・metrics --json 出力)、Skill: ml-workflow / architecture-rules

手順(CLAUDE.md 厳守):
1. /start-task で probe-analysis を初期化(日付 [YYYYMMDD]-probe-analysis)。
2. /reimagine を Step 3 後に実行(下記「設計判断」が複数案ありうるため推奨)。
3. /add-feature で実装。
4. 調査は file-finder + dependency-checker(replay.rs の既存パイプライン・出力 JSON 形を確認)。
   実装後は code-reviewer + test-runner を並行起動。さらに **codex cross-review**(scripts/run-codex-review.sh は
   working-tree diff 前提のため、コミット範囲は手動で codex 実行: A/B/C と同手順)を回す。

実装スコープ(Task D のみ。E は含めない):
- (1) replay.rs に consumption variant 追加: probe_assignment / realtime_label / session_meta /
    vignette_response を ReplayEvent でパース(TA-3)。既存 Feat/Key の再生は不変。
- (2) 時間隔離窓抽出: 各 realtime_label の [analysis_window_start_ms, analysis_window_end_ms] 内の
    FeatSnapshot を集め、X(Cognitive Friction)/Y(Engagement)を集約(中央値 or 平均、要設計)。
    probe 後の窓(t..t+60s)は使わない(D-8)。
- (3) 被験者内 方向付き C-index(§7): 集約 X と Q1摩擦 の順位一致割合(concordance)。0.5=偶然/1.0=完全/
    <0.5=逆。Y と Q2 も。被験者ごとに算出(前向き holdout: 最初の2セッションで β 較正→凍結→残りで評価=§8)。
- (4) 2段ゲート判定(D-10): 測定法ゲート(回答率≥80%・latency 中央値≤10s・有効≥20件/人=PreReg-2、
    ビネット 6/8 かつ 80%通過=PreReg-1)→ 通過時のみモデルゲート(C-index 中央値≥0.65 & 全員>0.55=Go /
    中央値≤0.55 or 2人以上≤0.50=Kill / それ以外=INCONCLUSIVE=PreReg-4)。
- (5) MNAR 上下限(PreReg-7): 未回答を「全て高摩擦」「全て低摩擦」と置いた上下限を併報。被験者除外はしない。
    無回答率 >20% 注意・>30% 主分析不成立。
- (6) ビネット採点(PreReg-1): vignette_response の (q1,q2)→象限推論→expected_quadrant 一致率。
- (7) 出力: metrics.json(gse-replay --metrics --json 形式)に上記を載せ gse-dataset 連携(§10)。

要件・制約:
- **D-14: 既存 metrics.rs の confusion/precision/recall を流用しない**。C-index・2段ゲート・MNAR は新パスで追加。
- **Recall 点推定は出さない**(PreReg-6/§9: 独立陽性<30件では原理的に検出力なし)。分母は一様ランダムプローブのみ。
- **確証と探索の隔離**: main トラックのみ検証対象。session_meta.track=exploratory は主指標に混ぜない(§1.3)。
- **合成 fixture 先行**: 実データ前に、既知の (X系列, realtime_label) を持つ合成 NDJSON で C-index/ゲート/MNAR の
    数値を決定論的に検証する(golden test)。replay の既存スナップショット回帰は壊さない。
- architecture-rules: 解析は analysis/ に閉じ OS API を呼ばない。replay.rs は CLI 配線。
- 既存テスト無断削除禁止。cargo test / clippy 緑、main ビルド可維持。schema は不変(A 凍結)。

設計判断(/reimagine で 2 案比較推奨):
- A. 窓内 X/Y 集約方法: 中央値 vs 平均 vs 末尾値。沈黙・IME 変換中ビンの扱い(除外 or 重み)。
     30秒窓に Feat が疎な場合(沈黙)の堅牢性。
- B. C-index の対象軸とペアリング: X↔Q1(摩擦)単独 vs (X↔Q1 と Y↔Q2)の二軸併報。方向性の符号定義。
     被験者内 holdout の最小セッション数(§8 は 2 較正 + 残り評価だが、スモーク初期はデータ僅少)。

スコープ厳守: 上記 (1)〜(7) 以外は追加しない。
- 前向き holdout の β 再較正ロジックは「最初の2セッションで凍結」までを実装。実データでの multi-session 評価は Task E。
- context_beacon / waveform_label / task_checkpoint の解析、Recall 点推定は含めない(延期)。
- 実データ収集・3-5名スモーク・Go/Kill 最終判定の運用は Task E。
```
