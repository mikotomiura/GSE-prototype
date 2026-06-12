# tasklist.md

## フェーズ 0: 本タスク(レビュー＋設計) — 完了
- [x] v0.2(.docx)精読・関連 docs/コード/Skill 把握
- [x] codex 独立レビュー併用(相互検証)
- [x] 厳密レビュー(Part A, High×6 + Med/Low)
- [x] 具体設計(Part B, スキーマ/解析/事前登録/kill 基準)
- [x] コーナー段階介入 UI 設計(Part C)
- [x] steering 記録(requirement/design/decisions/tasklist)

## フェーズ 1: 立て付け確定(ユーザー判断 → docs 反映)
- [x] **Lv2 = ソフトのみで確定**(2026-06-12 承認)。walk-hard は実装しない(D-5)
- [ ] スモークの主張を「探索的＋測定法較正」に降格する方針の合意
- [ ] ※ 2026-06-12 時点: **設計レビューで一旦停止**。以降フェーズは未着手(指示待ち)
- [ ] PreReg-1..5 を `docs/` に新規ドキュメントとして登録・凍結
- [ ] glossary 改訂: Wall(Lv2) の定義、cue_condition/segment_origin 等の新語追加
- [ ] `intervention-design` Skill のルール 1/7(クリックブロック前提)を更新

## フェーズ 2: スキーマ拡張(別タスク /start-task → /add-feature)
- [ ] `LogEntry` + `schema_dto.rs` に 6 バリアント + 付随 enum を同期追加(B-5)
- [ ] producer 側で不変条件を強制(dont_remember⇒null, q1>=4⇒stuck_kind)
- [ ] emit_schema 再生成 → current.json 更新 → CI drift 緑(/finish-task の schema check)

## フェーズ 3: 解析パイプライン(別タスク)
- [ ] gse-replay に retro_label 取り込み + 順序混合モデル出力(B-6)
- [ ] 対照区間 3 層化 + 包含確率記録(B-4/B-8)
- [ ] dismiss_kind 内訳・⏸率を metrics.json に追加

## フェーズ 4: コーナー介入 UI 実装(別タスク /add-feature)
- [ ] `intervention/CornerCompanion` + stages(Peek/Pause/Walk)+ EdgeVignette + useInterventionStage(C-4)
- [ ] `.wall-layer` 全画面廃止、setIgnoreCursorEvents 常時 true 化
- [ ] record_intervention_dismiss 拡張(dismiss_kind/level/latency_ms)+ InterventionDismiss ログ
- [ ] モダン CSS(spring overshoot / glass / grid 展開 / vignette / prefers-reduced-motion)(C-5)
- [ ] code-reviewer + data-privacy + intervention-design Skill で検証

## フェーズ 5: 測定法較正研究(確証分析の前提)
- [ ] cue 3 条件(feature_waveform / temporal_only / realtime_bridge)の一致率測定
- [ ] PreReg ゲート判定 → Go なら核検証、No-Go なら設計差し戻し
