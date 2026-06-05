# GSE v2 Redesign

## 目的

GSE v2 は、脳内の認知状態を直接読むシステムではない。

PC 操作に現れる行動的シグナルから、介入判断に必要な作業上の状態を推定し、生産的苦闘を壊さないタイミングで段階的介入を行う。

## 4層モデル

```text
1. 行動シグナル層
   keystroke timing / correction / pause / burst / silence

2. 作業状態推定層
   stuck_likelihood / engagement_score / friction_score
   incubation_like_pause / flow_like_continuation

3. 介入機会判定層
   breakpoint_score / receptivity / cooldown / daily_cap
   recent_dismiss / Monk Mode / task_kind

4. 介入ポリシー層
   none / nudge / wall / zen / defer
```

## MVP Opportunity

MVP では、Need と Opportunity を最小構成で分離する。

### Need

MVP の Need は現行 HMM の `p_stuck` を利用する。

```text
need_score = p_stuck
```

これにより、旧バージョンとの比較可能性を維持する。

### Opportunity

MVP の Opportunity は、キーボード由来の既存特徴量と介入制約だけで構成する。

| 入力 | 役割 |
|---|---|
| `idle_ms` | 短い停止・中程度停止・離席候補の区別 |
| F3 | 修正率。修正摩擦の補助 |
| F4 | バースト長。post-burst pause の補助 |
| F6 | 削除後停止率。修正後の迷いの補助 |
| `cooldown` | 介入直後の再介入抑制 |
| `daily_cap` | 過介入抑制 |
| `recent_dismiss` | 拒否直後の同種介入抑制 |
| `Monk Mode` | Wall 抑制 |

### 初期パラメータ

| 項目 | MVP 値 |
|---|---:|
| Nudge Need | `p_stuck >= 0.60` |
| Wall Need | `p_stuck >= 0.70` |
| Wall 累積時間 | `30_000 ms` |
| Nudge cooldown | `10 min` |
| Wall cooldown | `60 min` |
| Nudge daily cap | `6/day` |
| Wall daily cap | `1/day` |
| recent dismiss | `20 min` |
| short pause | `2-8 s` |
| medium pause | `8-30 s` |
| away idle | `180 s` |

これらは最終値ではなく、検証用の保守的な初期仮説である。

## 実装境界

- OS API は `input/` に閉じる。
- `analysis/` は純粋計算のみ。
- Frontend は `InterventionDecision` に従って表示するだけにし、閾値判定を持たない。
- 本文テキスト、Unicode 文字、選択文字列、ウィンドウタイトルは保存しない。
- セッションログは既存どおりローカル FS のみ。

## 今回実装した MVP

- `analysis::intervention`
- `get_intervention_decision`
- `record_intervention_dismiss`
- `LogEntry::InterventionDecision`
- Frontend の Nudge / Wall 判定を `InterventionDecision` 駆動へ移行

## 次段階

### Phase 2: 操作文脈の追加

本文を読まずに、構造特徴だけを追加する。

| 特徴 | 用途 |
|---|---|
| mouse move bucket | 離席・探索・迷いの補助 |
| click burst | UI 操作摩擦の検出 |
| scroll burst | 読み返し・参照中の識別 |
| focus role | text editor / browser / terminal などの作業種別 |
| selection bucket | 局所修正・大規模修正の補助 |
| caret jump bucket | 読み返し・編集迷いの補助 |

### Phase 3: 個人内調整

`intervention_decision` ログから以下を見て調整する。

- dismiss 率
- 介入後 2 分 / 5 分の作業再開
- Wall 後の early unlock 率
- 1 時間あたり介入回数
- defer 後に自然回復した割合
- UserLabel / ReviewMarker との対応

## 研究上の主張

GSE v2 の独自性は、脳内状態分類の強主張ではなく、以下に置く。

- privacy-preserving な行動シグナルからの作業停滞推定
- Need と Opportunity を分離した不便益介入
- 介入しない判断 `defer` を第一級に扱う設計
- Nudge / Wall / Zen / Physical Anchor へ拡張可能な段階的介入
- 生産性最大化ではなく、生産的苦闘を守る HCI
