# タスクリスト

- [x] lib.rs の初期値を false にし、コメントを直す
- [x] App.tsx の第2週を false にし、説明文を直す
- [x] docs と Skill の「Nudge のみ」を直す（decisions D2 の範囲）
- [x] cargo test --workspace（test-runner）
- [x] emit_schema の一致
- [x] tsc
- [x] security-checker（指摘は LOW 1 件・D4）
- [x] /cross-review 1 巡目（HIGH なし・D4 で対応）
- [ ] commit・push（PR は G-GEAR の計算が終わってから研究者に確かめる）

## メモ
- 初期値は定数 `INTERVENTION_ENABLED_DEFAULT` に切り出し、テスト `intervention_is_disabled_by_default` で検査する（static はテスト間で共有されるため）。
- デバッグの「Nudge 強制表示」は `INTERVENTION_ENABLED` の門より前（`lib.rs` の overlay 分岐の `FORCE_NUDGE`）で処理されるので、verification-runbook §2.1・§2.2 はそのまま使える。
- capabilities.rs: intervention 系はもともと config_gated。doc コメントの表だけ直した。
- intervention-design Skill のルール 3（Wall Server）は削除済みの機能の記述で、本タスクの範囲外として触らない。
- 残り: 第2週の `interventionEnabled: false` を守る検査が無い（フロントのテスト基盤が無い）。別タスクの候補。
