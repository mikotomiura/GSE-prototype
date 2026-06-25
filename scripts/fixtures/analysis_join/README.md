# analysis_join fixture (synthetic — no real data)

`scripts/build_analysis_db.py` の end-to-end 検証用 合成 fixture。実被験者データは含まない。
gse-dataset の最小レイアウトを模す (decisions.md D5)。

## レイアウト

```
metrics/P###/<os>/<session>.metrics.json   ③ gse-replay --metrics --json 出力 (SessionMetrics)
survey/*.csv                               ② フォーム由来 (P-ID + phase + 尺度得点)
sessions.csv                               session→phase(pre/post) 割当 (任意)
```

## survey CSV 最小スキーマ (仮置き — PreReg 凍結待ち)

Google Form の実列名は未確定。実フォーム確定時に追従する前提で最小列のみ仮置き:

| 列 | 意味 |
|---|---|
| `participant_id` | P### (必須・join キー) |
| `phase` | `pre` / `post` (必須・join キー) |
| `gse_total` | (c) 一般性自己効力感 GSE 合計 (10-40, D3) |
| `nasa_tlx_total` | NASA-TLX 合計 (任意) |
| `walk_done` / `returned_to_work` / `inconvenience_benefit_accepted` | (D8 WoZ) 散歩受容の post 自己申告 (本 fixture では省略。正準スキーマは `scripts/templates/`) |

⚠️ **実名・メール等の PII 列は禁止**。混入時はハーネスが exit 6 で停止する
(data-privacy / decisions.md D1。実名↔P-ID 対応表は repo 外)。

> この fixture は join の 4 象限検証用に最小列のみ持つ。運用で配る正準 survey スキーマ
> (D8 WoZ 列込み) と配置規約は `scripts/templates/README.md` / `docs/pilot-runbook.md` 参照。

## 被験者構成 (4 象限を網羅)

| P-ID | metrics | survey | phase | 検証する象限 |
|---|---|---|---|---|
| P101 | ✓ (pre/post) | ✓ (pre/post) | pre, post | 完全 join |
| P102 | ✓ (pre, paste=0) | ✓ (pre) | pre | 実測ゼロ ≠ データ無し |
| P103 | ✗ | ✓ (pre/post) | pre, post | metrics 欠落 (has_metrics=false) |
| P104 | ✓ (manifest 未登録) | ✗ | unknown | survey 欠落 + phase=unknown |
