# intervention-design: 介入状態遷移図

```
                        p_stuck ≤ 0.60
                    ┌──────────────────────┐
                    │                      │
             ┌──────▼──────┐               │
             │             │               │
             │   IDLE      │               │
             │ (介入なし)   │               │
             └──────┬──────┘               │
                    │                      │
           p_stuck > 0.60                  │
                    │                      │
             ┌──────▼──────┐               │
             │             │               │
             │   NUDGE     ├───────────────┘
             │  (Lv1)      │  p_stuck ≤ 0.60 で自動解除
             └──────┬──────┘
                    │
         p_stuck > 0.70 が 30秒累積
         かつ Monk Mode = false
                    │
             ┌──────▼──────┐
             │             │
             │    WALL     │◄── QR スキャン待ち
             │   (Lv2)     │    Zen Timer 起動待ち
             └──────┬──────┘
                    │
          POST /unlock (Zen Timer完了後)
          または Early Unlock タップ
          または 長時間キーボードアイドル
                    │
                    └──────► IDLE へ戻る

Monk Mode 有効時:
  - NUDGE → WALL への遷移をスキップ
  - NUDGE は通常通り表示
```

## 状態テーブル

| 状態 | wallActive | showNudge | stuckAccumMs |
|---|---|---|---|
| IDLE | false | false | 0 |
| NUDGE | false | true | 累積中 or 0 |
| WALL | true | 非表示(Wall が覆う) | リセット |

## Monk Mode の効果

```
Monk Mode = false (デフォルト):  IDLE → NUDGE → WALL
Monk Mode = true:               IDLE → NUDGE のみ（WALL に遷移しない）
```
