# hmm-analysis: 現行パラメータリファレンス

## HMM 構造

- **状態数**: 3（Flow, Incubation, Stuck）
- **観測ビン数**: 26（5×5 グリッド + ペナルティビン obs=25）
- **更新頻度**: 1Hz（Analysis スレッド）

## EWMA パラメータ

| パラメータ | 値 | 説明 |
|---|---|---|
| α (通常) | 0.15 | 潜在軸の EWMA 平滑化係数 |
| α (サイレンス 10-30s) | 0.18 | 長い沈黙での緩やかな遷移 |
| α (サイレンス 30s〜) | 0.25 | さらに遅い追従 |
| α_h (ヒステリシス) | 0.3 | display_probs の平滑化係数 |
| κ (正規化) | 2.0 | φ(x, β) の感度係数 |

## バースト・休止の閾値

| パラメータ | 値 | 説明 |
|---|---|---|
| バースト判定 | < 200ms | 連続打鍵の間隔閾値 |
| 休止判定 | ≥ 2000ms | Pause として計上する沈黙閾値 |
| ペナルティ閾値 | 14 連続バックスペース | obs=25 を発火 |

## コールドスタート

```
forward_probs = [0.80, 0.15, 0.05]  // Flow, Incubation, Stuck
display_probs = [0.80, 0.15, 0.05]
```

## 変更履歴（セッションログ検証済み）

| バージョン | 変更内容 | 根拠 |
|---|---|---|
| v2.14 | Silence→Stuck gradient 緩和 + Frontend resilience | fix-report-20260308 |
| v2.15 | y_bin=2 Flow 識別改善 + IME_ACTIVE ログ追加 | fix-report-20260308 |
| v2.16 | obs=12→17 の emission cliff 平滑化 | fix-report-20260308 |
| v2.18 | Stuck friction limiter 解除・early silence onset | fix-report-20260309 |
| v2.19 | macOS parity: emission table, friction floor, logger flush | fix-report-20260309 |

## 30s ローリングウィンドウ

```
バッファサイズ: VecDeque<InputEvent>, max 600 イベント（~30秒分）
ウィンドウ: 最新 30 秒のイベントのみ保持
```
