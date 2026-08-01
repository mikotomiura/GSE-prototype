# data — 入力の来歴

## 入力

Phase1 較正データの **確証カット (calibration_blind)**。
`experiments/20260731-phase1-calibration-analysis/` の主分析と**同一の入力**を使う。

| 項目 | 値 |
|---|---|
| gse-dataset commit | `c2f960c0b9a04778e616dbd212517c65a76f132c` (2026-08-01) |
| 配置 | `<gse-dataset>/raw/P010..P014/*.ndjson` (匿名化済み) |
| ファイル数 | 40 |
| セッション数 | **41** (`session_meta` 数。P010 に 1 ファイル 2 セッションのものが 1 件) |
| `feat` イベント総数 | **124,517** |
| 有効ラベル (`random_probe` かつ `answered`) | **200** |
| `hmm_version` | `0.3.0` (全 40 meta) |
| 収集期間 | 2026-06-29 〜 2026-07-30 |

### 被験者別

| PID | files | sessions | feat | answered random_probe | 連結 sha256 (先頭16) |
|---|---|---|---|---|---|
| P010 | 12 | 13 | — | 103 | `a253214d22aaddc9` |
| P011 | 5 | 5 | — | 21 | `d0c458d0412e2e4d` |
| P012 | 7 | 7 | — | 35 | `8c9a0d57704d7794` |
| P013 | 10 | 10 | — | 7 | `a4f1fff1f82c3a46` |
| P014 | 6 | 6 | — | 34 | `00600a051503f78a` |

(feat の被験者別内訳は `results/diagnostics.json` の `inventory` を参照。
sha256 は `cat P0XX/*.ndjson | shasum -a 256` の先頭 16 文字。)

## カット条件

0731 実験と同一:

- **`label_pool` カット**: `raw/` に置いてあるのは `condition=blind_calibration` /
  `label_pool=calibration_blind` / `intervention_enabled=false` の 40 セッションのみ。
  `post_intervention` の 23 セッション (介入 ON = 推定結果が被験者に呈示された状態) は
  **配置段階で除外**されている。
- **`task_kind`**: 全セッション `argumentative` (task_kind ロック後の収集)。
- **ラベル**: `source=random_probe` かつ `answered=true` のみ (PreReg-6 の分母規約)。
  `self_marker` 由来は主指標に入れない。

## プライバシー

- 入力は**匿名化済み** NDJSON。`vk` 生値なし / 本文・題名・プロセス名なし
  (`category` のみ) / 絶対 epoch 時刻なし (全て session 相対)。
  0731 実験で復号後 63 件を機械監査済み。
- 復号鍵は `~/.gse/age-identity.txt` (repo 外)。
- **生 NDJSON / `.age` は本 repo にも gse-dataset にもコミットしない**
  (`.gitignore` の `*.age` / `P[0-9]*_*.ndjson` / `gse_*.ndjson` で二重防護)。
- `results/` に出力するのは**集計値のみ**。セッション単位の生値・タイムスタンプ列は出さない。
- 外部 LLM への送信なし (`data-privacy` Skill)。
- **公開時の方針 (現時点の決定)**: `results/` の per-subject 値 (打鍵数・paste 件数・
  セッション数・`ime_shadow` 件数) は **private repo 内限定**。被験者は 5 名しかいないため、
  ロスターを知る者に対しては準識別子として働く。外部公開する場合は被験者 ID を再割当てし、
  打鍵数・paste 件数は範囲値に丸める。
  (粒度は既に追跡済みの `20260731-.../results/metrics_P0*.calib.json` と同水準で、
  本実験で新たに細かくはしていない。)
- 出力は書き出し直前に `assert_no_pii()` で機械検査する (ファイル名・絶対パス・URL・
  1e12 以上の整数=絶対時刻を検出したら非ゼロ終了)。

## 記録精度に由来する制約 (再現時に効く)

`logger.rs` は `feat` を丸めて記録する:

```
f1:{:.2} f3:{:.4} f4:{:.2} f5:{:.1} f6:{:.4} raw_x:{:.4} raw_y:{:.4} ...
```

したがって Python 側で φ を再計算しても **記録値と厳密一致することは原理的に無い**
(丸め後の入力から再計算しているため)。D3 はこの残差を分布として報告する。
