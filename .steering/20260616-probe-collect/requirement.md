# Task C — frontend 収集

## 背景

v0.3 較正スモーク(D-14)の最小核。実装順 A→(B∥C)→D→E。A(schema, PR#4 merge 済)・
B(backend probe scheduler, feature/probe-scheduler に実装済・cross-review 済)に続く frontend +
回答記録 command タスク。C は B が emit する `probe_triggered` イベントを消費して回答カードを出し、
回答を logger に記録する。

stacked on feature/probe-scheduler(B 未 merge のため・C は B の emit を消費して end-to-end を成立させる)。

## ゴール

被験者がセッション中に (1) 開始時 task_kind を宣言、(2) ランダムプローブ発火時に Q1摩擦/Q2前進を
回答(or skip)、(3) 初回に 8 ビネットで尺度理解を確認 — の 3 経路を frontend で提供し、
それぞれ `session_meta` / `realtime_label` / `vignette_response` として backend command 経由で記録する。
窓(analysis_window_*)は B から受領しそのまま realtime_label に転記する(DB-4)。

## スコープ

### 含むもの (Task C のみ)
1. **session_meta 宣言 UI** + `record_session_meta` command:
   task_kind(argumentative|correspondence|creative|vibe_coding)/track(main|exploratory)/
   monk_mode/intervention_enabled を宣言 → `LogEntry::SessionMeta`(§3・§14)。
2. **プローブ回答カード** + 記録 command:
   `probe_triggered` を listen → Q1摩擦(1-5)/Q2前進(1-5) スライダー + skip(dont_remember|dismissed)
   + latency_ms 計測。回答→`realtime_label_answered` / skip→`realtime_label_skipped`。
   **受領 probe_id を backend で再検証**([A-Za-z0-9_-]・長さ16 = cross-review #7)。窓は受領値を転記。
   source=random_probe→ProbeRef::RandomProbe{probe_id} / self_marker→ProbeRef::SelfMarker。
3. **8 ビネット初回フロー** + `record_vignette_response` command:
   §6.3 の 8 シナリオ(①フロー/②スタック/③インキュベーション/④惰性 ×2)に Q1/Q2 回答 →
   `LogEntry::VignetteResponse`。PreReg-1 ゲート(8問中6問以上が想定象限)を表現。

### 含まないもの
- 解析窓抽出・C-index・2段ゲート・MNAR・ビネット採点(Task D)。
- context_beacon / waveform_label / task_checkpoint(D-14 延期)、コーナー介入 UI・intervention_dismiss(Phase4)。
- 窓の確定・clamp は B 側で実施済(C は受領窓を転記するのみ)。

## 受け入れ条件

- [ ] `probe_triggered`(random_probe/self_marker)受信で回答カードが表示され、回答/skip が realtime_label として記録。
- [ ] 受領 probe_id が `[A-Za-z0-9_-]{16}` でない場合 command がエラーを返す(#7)。self_marker は probe_id=null を強制。
- [ ] session_meta 宣言が `record_session_meta` で記録され、不正な task_kind/track はエラー。
- [ ] 8 ビネットフローが vignette_response を記録し、PreReg-1 ゲート判定(6/8)を表示。
- [ ] X/Y/p_stuck/推定状態を UI に一切表示しない(原則5)。プローブ選定方法も教示しない。
- [ ] data-privacy: ログは数値・固定カテゴリ・不透明 ID のみ。本文/タイトル/選択文字列/Unicode 非保存。
      ビネット場面文は保存しない(vignette_id + expected_quadrant + q1/q2 のみ)。
- [ ] latency_ms = カード表示〜回答。frontend で計測し command に渡す。
- [ ] schema 不変: schema_dto.rs / current.json を touch しない。VignetteResponse の q1/q2 は producer で 1..=5 clamp。
- [ ] `cargo test` / `cargo clippy`(新規警告ゼロ)/ `npm run build` 緑。既存テスト不変。

## 関連ドキュメント
- `.idea/GSE_事後ラベリングシステム設計書_v0.3.md` §3 / §4 / §6 / §14 / §2 原則5 / §16
- `.steering/20260616-probe-scheduler/decisions.md` DB-4(B↔C 契約)/ DB-9 / DB-11(#7)
- `.steering/20260612-retro-labeling-and-corner-intervention/tasklist.md` Task C
- Skill: typescript-standards / architecture-rules / data-privacy

## 運用メモ
- /reimagine 適用: **Yes**
- 理由: 設計判断が2点(回答カードの居場所 / session_meta・ビネットの起動導線)あり複数案ありうる(handoff 推奨)。
