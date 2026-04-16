# 設計 v1: Synthetic Friction 再設計 (improvement-roadmap から転記)

> 出典: `.steering/20260414-improvement-roadmap/design.md:300-350`

## 2a.1 散布図分析

`gse-replay --scatter <session.ndjson>` で、`UserLabel` 付きセッションの「沈黙開始前 5 秒の平均 F3/F6（φ 正規化後）」と「その沈黙のラベル」をプロット用 CSV として出力。

## 2a.2 `last_active_features` の追加

`lib.rs` 分析スレッド（step 関数化後）に:

```rust
// silence_secs が 0 → 正値に遷移する瞬間の features を保存
if prev_silence_secs < 2.0 && silence_secs >= 2.0 {
    state.last_active_features = Some(features.clone());
}
```

## 2a.3 文脈条件ゲート

`lib.rs` の TransitionPath / SilencePath 内で:

```rust
let apply_friction = state.last_active_features.as_ref().map_or(false, |laf| {
    let phi_f3 = phi(laf.f3_correction_rate, beta_f3);
    let phi_f6 = phi(laf.f6_pause_after_del_rate, beta_f6);
    phi_f3 >= THRESHOLD_PHI_F3 || phi_f6 >= THRESHOLD_PHI_F6
});

if apply_friction {
    // 既存の F6/F3 フロア適用
} else {
    // フロア適用せず、実測値または 0 で update_silence
}
```

**初期閾値**: `THRESHOLD_PHI_F3 = 0.30` / `THRESHOLD_PHI_F6 = 0.20`（GT データで校正）

**閾値は φ 正規化後の値で判定**（生の F3/F6 ではない）ため、β_coding / β_writing で自動的に適切にスケールする。

## 2a.4 回帰テストと校正

1. Phase 0 のゴールデンスナップショットを新パラメータで再実行 → 差分確認
2. Phase 1 の GT 付き全セッションで `gse-replay --metrics` → precision 低下がないことを確認
3. 差分を `.steering/20260414-improvement-roadmap/phase2a_results.md` に記録

## Phase 2a Go/No-Go

- Stuck precision が変更前から低下していない（同等または改善）
- 思考中沈黙（Incubation ラベル）の Stuck 誤検出率が減少
- ゴールデンスナップショットの差分が意図通り（承認記録あり）
- 閾値を定数として記録し、根拠となる GT データを `.steering/` に添付

## 変更対象

- `src-tauri/src/analysis/loop_step.rs` — `last_active_features` バッファ追加
- `src-tauri/src/analysis/features.rs` — `make_silence_observation()` のゲート条件変更
- `src-tauri/src/analysis/engine.rs` — `THRESHOLD_PHI_F3`, `THRESHOLD_PHI_F6` 定数追加
- `src-tauri/src/bin/replay.rs` — `--scatter` モード追加

## テスト戦略

- ゴールデンスナップショット再生成 + diff 確認
- GT 付きセッション全件で `--metrics` 回帰確認
- φ 閾値境界の合成ユニットテスト
