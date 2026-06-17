# Phase 0 評価結果 — reason 別 HIR 分解 + nudge_need sweep (P000 13 session)

実行: `gse-replay <13 sessions> --sweep`（production 不変のオフライン反実仮想リプレイ）。
回復窓 W = 15 分（暫定、D5）。日付: 2026-06-18。生 JSON: `p000_sweep.json`。

## 0. production 再現の確認（受け入れ条件①）

`nudge_need=0.60`（= production 既定）で **既存 `results.md` の POOLED 行と完全一致**:
HIR=0.647 / Precision=0.353 / STALL recall=0.073 / DC=0.933 / ACT=34（nudge 34・wall 0）。
→ 評価器の拡張が production 挙動を変えていないことの数値的証明。
（加えて golden snapshot byte-equal・schema drift なし・`cargo test --workspace` 163+12 緑）

## 1. Nudge FP の犯人 reason（受け入れ条件②）

`nudge_need=0.60` での opportunity reason 別分解（pooled labeled cells; fp=ACT∩PROTECT=有害）:

| reason | ACT | fp(harm) | tp | HIR | Prec |
|---|---:|---:|---:|---:|---:|
| short_pause | 0 | 0 | 0 | n/a | n/a |
| medium_pause | 0 | 0 | 0 | n/a | n/a |
| long_pause | 0 | 0 | 0 | n/a | n/a |
| active_typing | 0 | 0 | 0 | n/a | n/a |
| **post_burst_pause** | **0** | 0 | 0 | n/a | n/a |
| **correction_after_pause** | **34** | **22** | 12 | **0.647** | 0.353 |
| active_correction_loop | 0 | 0 | 0 | n/a | n/a |

**結論: HIR=0.647 の犯人は 100% `correction_after_pause`。** post_burst_pause（健全なバースト後
小休止）由来の nudge は P000 では **1 件も発火していない**。最も harmful が集中した session
`033257`（9 nudge 全 FP, HIR=1.0）も全件 correction_after_pause。

### 解釈
- `correction_after_pause` は `f3>=0.20 または f6>=0.30`（修正多発／delete 後ポーズ多い）+ 2–30 秒
  ポーズで +0.15。これに short/medium pause の素点（+0.45 / +0.35）が乗り、nudge 閾値 0.35 を越える。
- GT 上は Flow 区間で起きており（forward-fill GT の限界つき・§9）、「修正しながら考えている健全な
  推敲」を stuck と誤認して軽介入している像。これは improvement-plan §2.2 の
  「correction context は paused 時 +0.15」の設計が **P000 では over-trigger 気味**であることを示す。
- post_burst_pause が 0 なのは、P000 のポーズが概ね correction を伴う（純粋な低 f3/f6 バースト後
  ポーズが少ない）ためで、reason 精度の差ではなく **データ分布**の反映。

## 2. nudge_need sweep（受け入れ条件③）

other thresholds は production 既定固定。pooled over 13 session。ACT は nudge_need 上昇で単調非増加。

| nudge_need | ACT | fp | tp | HIR | Prec | Recall | DC | Burden/min |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.50 | 40 | 28 | 12 | 0.700 | 0.300 | 0.073 | 0.947 | 0.612 |
| 0.55 | 38 | 26 | 12 | 0.684 | 0.316 | 0.073 | 0.941 | 0.581 |
| **0.60**(現行) | 34 | 22 | 12 | 0.647 | 0.353 | 0.073 | 0.933 | 0.520 |
| 0.65 | 32 | 21 | 11 | 0.656 | 0.344 | 0.067 | 1.000 | 0.490 |
| **0.70** | 31 | 20 | 11 | 0.645 | 0.355 | 0.067 | 1.000 | 0.474 |
| 0.75 | 25 | 16 | 9 | 0.640 | 0.360 | 0.055 | 1.000 | 0.383 |
| **0.80** | 14 | 5 | 9 | **0.357** | 0.643 | 0.055 | 1.000 | 0.214 |
| 0.85 | 10 | 3 | 7 | 0.300 | 0.700 | 0.043 | 1.000 | 0.153 |
| 0.90 | 5 | 2 | 3 | 0.400 | 0.600 | 0.018 | 1.000 | 0.077 |

観察:
- **0.60→0.75 は HIR がほぼ横ばい（0.647→0.640）**。閾値を上げても correction_after_pause 由来の
  FP は need 0.60–0.75 帯に厚く分布しており、軽い引き上げでは害が減らない。
- **0.80 に明確な knee**: HIR 0.640→0.357（ほぼ半減）、Precision 0.360→0.643（ほぼ倍）。tp は 9→9 と
  維持され、**recall 低下は 0.055→0.055 でゼロ**、burden も 0.383→0.214 へ低下。
- 0.85 は HIR 0.300 が最小だが recall 0.043（tp 9→7）に減り、ACT=10/fp=3 と n が小さい。
- 0.90 で HIR が 0.400 へ反転するのは ACT=5（fp=2,tp=3）の小標本ノイズ。

## 3. 閾値変更候補（3 案以内）

| 案 | nudge_need | 狙い | HIR | Recall | Burden | 評価 |
|---|---:|---|---:|---:|---:|---|
| **A（保守）** | 0.70 | DC=1.0 化＋微 burden 減、害ほぼ同 | 0.645 | 0.067 | 0.474 | 害は減らない。recall ほぼ維持。低リスク微調整 |
| **B（推奨・knee）** | 0.80 | HIR 半減・Precision 倍・recall 不変 | 0.357 | 0.055 | 0.214 | **害/負担を最も効率よく削減**。tp 維持。第一候補 |
| **C（積極）** | 0.85 | HIR 最小 | 0.300 | 0.043 | 0.153 | HIR 最小だが recall・tp 低下、n 小。慎重 |

## 4. 限界・次への申し送り（厳守）

- これは **screening であって verdict ではない**（§9 / decisions.md D2）。HIR 基線は forward-fill GT に
  よる**上限寄り**推定で ACT 分母が小さく数件の増減に敏感。0.80 の fp=5 / tp=9 も小標本。
  「0.80 が良い」は **同一 GT 仮定・同一 W・同一 ACT 分母**での相対比較として扱う。
- **真因は閾値ではなく reason 設計の可能性が高い**: 害は need 帯ではなく `correction_after_pause`
  という単一 reason に集中している。nudge_need を上げる（B/C）と correction 由来 FP も健全 tp も
  同時に削るため、本質的解決は **correction_after_pause の加点/ゲートを reason 別に絞る**
  （improvement-plan §5「Nudge opportunity を reason 別に閾値分け」）方向。これは production
  ロジック変更を伴うため Phase 0 外。本タスクは「測れるようにする」までで、変更は提案に留める。
- Phase 1（Need 校正）着手是非は、この reason 偏在を踏まえ holdout で判断する材料が揃った。
  ただし P000 単一被験者・nudge 34（うち correction 34）では校正は過学習する（§2.3）。
  → ラベル付き session を増やしてから。

## 5. 生成物
- `p000_sweep.json` — pooled sweep の機械可読出力（reason 別分解を全閾値点で含む）。
- 本 `results.md` — reason 別 HIR 分解 / sweep Pareto 表 / 閾値候補 3 案。
