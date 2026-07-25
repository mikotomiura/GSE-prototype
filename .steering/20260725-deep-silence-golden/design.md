# design — deep-silence fixture 設計・カバレッジ・検証

## fixture 設計 (deep_silence.ndjson)
`run_replay` は event 間を仮想時刻で 1Hz ゲート駆動する (replay.rs:1614-1620) ため、長い gap は
沈黙 tick を生む。これを利用:
1. 打鍵バースト (~7.6s): 「削除(BS) → 2.6s ポーズ → 再開」を **2回**入れる。f6 = 「BS 直後に ≥2000ms 停止した
   割合」(features.rs:213-224) なので、BS を ≥2s ポーズが追う形にして **ctx.f6 > 0** を pre_silence_features に積む。
   BS を含めることで f3(訂正率) も >0。
2. 最後の打鍵 (up=base+7640) から **約43秒沈黙**。次 event を base+51000 に置く。
3. 沈黙明けの打鍵で復帰スナップショットを出す。

## カバレッジ (loop_step.rs 314-345)
- silence 8–~37s: バッファに実データ残存 (f1>0) → **TransitionPath**。ctx フロア
  (f6_floor=ctx.f6×time_scale, f3_floor=ctx.f3×time_scale, time_scale=(silence-8)/30)。
- silence ~37–43s: 打鍵が 30s 窓から抜けバッファ枯渇 (f1=0) → **SilencePath** (make_silence_observation)。
- 実測: f6 は 0→0.5→1.0 とランプ (47 snaps>0)、f3 は →0.22 (50 snaps>0)。従来 fixture は f6 恒常 0。

## テスト
- `replay_snapshot_goldens_byte_equal` の cases に `("deep_silence.ndjson","deep_silence.json")` を追加。
- golden は `gse-replay deep_silence.ndjson > tests/snapshots/deep_silence.json` で生成。
- 決定論 (2回生成 diff 空)・round-trip exit 0・`cargo test --bin gse-replay` 全23パスを確認。

## 決定論の担保
仮想時刻駆動・RNG/実時刻なし・`is_repeat` は cfg(windows) 限定 (aarch64 では不使用)。flaky リスクなし。
HMM_VERSION bump 時は本 golden も他3本と同様に再生成が必要 (テストが強制)。
