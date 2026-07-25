# tasklist — deep-silence golden (残タスク C)

- [x] loop_step.rs / features.rs の沈黙フロア・f6 算出を読み、fixture 要件を特定
- [x] `deep_silence.ndjson` 生成 (削除→2.6s ポーズ×2 で ctx.f6>0・約43s 沈黙)
- [x] golden 生成し f6/f3 が沈黙域で >0 を確認 (max f6=1.0/f3=0.22)
- [x] TransitionPath ctx フロア + SilencePath 両方を踏むことを実測確認
- [x] 決定論 (2回生成同一)・round-trip exit 0
- [x] `replay_snapshot_goldens_byte_equal` に deep_silence を追加
- [x] `cargo test --bin gse-replay` 全23パス・fmt clean
- [ ] コミット → PR
