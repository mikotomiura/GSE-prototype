# 次セッション用プロンプト — Task C「frontend 収集」

> 用途: 新しいセッションの最初にこのファイルの「プロンプト本文」を貼り付ける。
> 新セッションは CLAUDE.md / MEMORY.md を自動ロードする前提。
> 背景: Task A(probe schema)= PR #4 で main へ merge 済み。
>        Task B(backend probe scheduler)= feature/probe-scheduler に実装済み
>        (commit 7d0f4d5 / 5ea6c5a / 8749362、Claude+Codex cross-review 済み)。
>        実装順 D-14: A→(B∥C)→D→E。**次は C**(B 完了につき)。
> 注意: cross-review の actionable 指摘(DB-9 self_marker 窓 / DB-10 config 検証)は B で修正済み。
>        繰り越しは「受領 ID の backend 再検証(#7)」のみで、本タスク C が内包する。

---

## プロンプト本文(ここから下をコピペ)

```
Task C「frontend 収集」を開始する。v0.3 較正スモーク(D-14)の実装順 A→(B∥C)→D→E のうち、
A(schema, merged)・B(backend scheduler, 実装済)に続く frontend + 回答記録 command タスク。
C は B が emit する `probe_triggered` イベントを消費して回答カードを出し、回答を logger に記録する。

まず以下を読んで文脈を固めてから着手すること:
- .idea/GSE_事後ラベリングシステム設計書_v0.3.md の
  §3(2フェーズ構成・セッション開始の task_kind 宣言), §4(プローブカード Q1摩擦/Q2前進・skip理由・
  latency, 自己マーカー), §6(尺度理解テスト=8ビネット・2×2象限と期待回答), §14(schema),
  §2 原則5(X/Y/p_stuck/推定状態を被験者に一切見せない), §16(教示文方針: 結果非言及・2軸独立明示)
- .steering/20260612-retro-labeling-and-corner-intervention/decisions.md の D-8(時間隔離窓)/D-14(最小核)
- .steering/20260612-retro-labeling-and-corner-intervention/tasklist.md の「Task C」
- .steering/20260616-probe-scheduler/decisions.md の DB-4(B↔C 契約: probe_triggered payload と窓の所有)・
  DB-9(self_marker 窓は backend で clamp 済)・DB-11(#7=受領 ID の再検証は C の責務)
- src-tauri/src/logger.rs:
  realtime_label_answered / realtime_label_skipped(511/537)・ProbeRef(RandomProbe/SelfMarker)・
  SessionMeta(462) / VignetteResponse(495) の variant と format 関数(282/368)
- src/App.tsx, src/components/Overlay.tsx, src/components/Dashboard.tsx, src/main.tsx(既存 invoke/listen パターン)
- docs/architecture.md(Frontend / Tauri IPC / 500ms polling), Skill: typescript-standards / architecture-rules /
  data-privacy(必須)

B が emit するイベント契約(DB-4・既に backend 実装済):
  app.emit("probe_triggered", { probe_id: string|null, source: "random_probe"|"self_marker",
    analysis_window_start_ms: u64, analysis_window_end_ms: u64 })
  → C はこれを listen し、窓 (analysis_window_*) を realtime_label にそのまま転記する。

手順(CLAUDE.md 厳守):
1. /start-task で probe-collect を初期化(ディレクトリは実行日 [YYYYMMDD]-probe-collect)。
2. /reimagine を Step 3 後に実行(下記「設計判断」2点が複数案ありうるため推奨)。
3. /add-feature で実装。
4. 調査は file-finder + impact-analyzer を並行起動(frontend listen 経路・既存 invoke 型定義・
   新規 Tauri command 登録箇所の特定)。実装後は code-reviewer + security-checker + test-runner を並行起動。

実装スコープ(Task C のみ。D/E は含めない):
- (1) session_meta 宣言 UI: セッション開始時に task_kind(argumentative|correspondence|creative|vibe_coding)を
    一打宣言 + track(main|exploratory)/monk_mode/intervention_enabled を確定 → Tauri command で
    LogEntry::SessionMeta を記録(§3・§14)。
- (2) プローブカード: probe_triggered を listen → Q1摩擦(1-5)/Q2前進(1-5)スライダー + skip(理由:
    dont_remember|dismissed)+ latency_ms 計測(カード表示〜回答)。回答/skip で Tauri command を呼び:
      source=random_probe → ProbeRef::RandomProbe{probe_id} で realtime_label_answered/_skipped
      source=self_marker  → ProbeRef::SelfMarker(probe_id=null)で同上
    窓は probe_triggered から受領した analysis_window_* をそのまま渡す(DB-4)。
    **受領 probe_id を backend command で再検証**([A-Za-z0-9_-]・長さ16)= cross-review #7 / defense-in-depth。
- (3) 尺度ビネット 8 問の初回フロー: §6.3 の 8 シナリオ(①フロー/②スタック/③インキュベーション/④惰性 ×2)に
    Q1/Q2 回答 → LogEntry::VignetteResponse(vignette_id, expected_quadrant, q1/q2)を記録。
    本番データ取得の前に 1 回。PreReg-1 ゲート(8問中6問以上が想定象限 かつ 被験者80%以上が通過)を表現。

要件・制約:
- **data-privacy(必須参照)**: ログは数値・固定カテゴリのみ。ビネットの場面文・task_kind 以外の本文・
  選択文字列・Unicode は一切保存しない(ビネットは vignette_id + expected_quadrant + q1/q2 のみログ)。
- **原則5(v0.3 §2)**: X/Y/p_stuck/推定状態を UI に一切表示しない。プローブの選定方法も教示しない
  (アンカリング・逆算の根を断つ)。
- **schema 不変**: session_meta / realtime_label / vignette_response は Task A で追加済。
  → schema_dto.rs / current.json は touch しない(finish-task の tier-3 parity guard を回避)。
  ただし VignetteResponse は直構築だと q1/q2 が clamp されない(Codex cross-review #1)。producer 側で
  1..=5 に clamp してから構築するか、realtime_label と同様の構築子を logger に足す(schema 不変の範囲で)。
- **latency 計測**: カード表示時刻〜回答時刻を frontend で計測し latency_ms として command に渡す。
- **typescript-standards**: any 禁止。invoke/listen のレスポンス型を定義。既存 Overlay/Dashboard の
  IPC パターンに乗る(ゼロから組まない)。
- **architecture-rules**: 新規 Tauri command は lib.rs に追加(状態推定ロジックは frontend に置かない)。
- 既存テスト無断削除禁止。cargo test / clippy / npm run build 緑、main は常にビルド可能を維持。

設計判断(/reimagine で 2 案比較推奨):
- A. 回答カードの居場所: 既存 Overlay ウィンドウ(always-on-top・透過)に出す vs 専用 probe ウィンドウを
     生成する vs Dashboard 内に出す。中断最小化(§1.3 作業フロー非汚染)と「モデル非表示」の両立で選ぶ。
- B. session_meta 宣言 + ビネットフローの起動導線: アプリ起動時 / セッション開始ボタン前 / 初回のみ。
     PreReg-1 ゲート(ビネット不合格なら教示文を作り直し本番データを取らない)をどう UI で表現するか。

スコープ厳守: 上記 (1)〜(3) 以外は追加しない。
- 解析窓抽出・C-index・2段ゲート・MNAR 上下限・ビネット採点(Task D)は含めない。
- context_beacon / waveform_label / task_checkpoint(D-14 で延期)、コーナー介入 UI・intervention_dismiss
  (Phase 4)は追加しない。
- self_marker の realtime_label 記録は C(回答 command)が担うが、窓の確定・clamp は B 側で実施済
  (C は受領窓を転記するのみ)。
```
