# Phase 1 Baseline Metrics（GT 付きセッション集計）

> **記入手順**:
> 1. GT 付きセッションを取ったら `~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson` を特定
> 2. `cd src-tauri && ~/.cargo/bin/cargo run --bin gse-replay -- <session.ndjson> --metrics` で pretty-print 出力を取得
> 3. 下表に 1 行追加（**手作業で良い、10 件未満はスクリプト化不要**）
> 4. 10 件以上溜まった時点で Phase 2a 着手判断（Go/No-Go: Stuck precision が平均 0.6 以上）
> 5. 機械可読形式が必要になったら `--metrics --json` を tee で保存して `jq` で集計

## セッション一覧

| Date | Session file | Labels (F/I/S) | Macro F1 | Micro F1 | Stuck recovery median (s) | Detection lead median (ms) | Warnings | Note |
|---|---|---|---|---|---|---|---|---|
| 2026-04-15 | `gse_20260415_144120.ndjson` | 4/1/1 | 0.722 | 0.667 | n/a | -93 | 0 | 初 Windows セッション (JIS、日本語 IME 混在)。Stuck/Inc 完全一致、Flow 2/4 件正解。`replay-feat-alignment-bug` **fix 後**の値 |

### 再計算待ち (macOS、dataset から削除済み)

`replay-feat-alignment-bug` fix 前に regen feat で計算されていた macOS metrics 2 件を 2026-04-16 に dataset repo から削除 (`gse-dataset` commit で記録)。Mac 端末で fix 後 CLI (`gse-prototype main 293b158+` の `gse-replay --metrics --json`) で再生成して dataset に上書き push するまで、macOS 分は集計対象外。

| Session file (再計算待ち) | pre-fix 値 (参考、信頼性不明) | 備考 |
|---|---|---|
| `gse_20260415_080214.ndjson` | Macro F1 0.000 / Micro F1 0.000 / lead -3119ms | 初回実機検証、F/I ラベリング、HMM 全誤判定。Mac raw NDJSON は Mac 端末の `~/Documents/GSE-sessions/` にのみ存在 |
| `gse_20260415_080921.ndjson` | Macro F1 0.222 / Micro F1 0.500 / lead +2383ms、Stuck P=R=F1 で confusion [[0,0,0],[0,0,0],[0,1,1]] | Stuck 単独検証。IME active が 8s 未満だったと思われ、再計算しても値は近い可能性が高いが未検証 |

### fix 前の参考値 (20260415_144120、regen feat)
`gse-replay --metrics` が step() 再生成 feat を使っていた時期の値。`.steering/20260416-replay-feat-alignment-bug/decisions.md` D1 で clock semantic mismatch と判明したため廃棄。Phase 2a 判定には下行の fix 後値を使う。

| Session | Macro F1 | Micro F1 | Lead median | Warnings | 意味 |
|---|---|---|---|---|---|
| `gse_20260415_144120.ndjson` (fix 前) | 0.000 | 0.000 | +26315 | **6 (全ラベル)** | regen feat が IME pause の auto-reset を再現できず 6 件中 6 件 window 外 → 数値全 0。信頼できない |

## 集計サマリ（Phase 2a Go/No-Go 判断）

> 10 件溜まった時点で更新。Phase 2a 着手可否の根拠として使う。

- セッション件数 (fix 後集計対象): 1 / 10 (Windows 1)
- 再計算待ち (macOS): 2 件 (Mac 端末で上書き push 後に合流)
- Flow ラベル総数 (fix 後): 4
- Incubation ラベル総数 (fix 後): 1
- Stuck ラベル総数 (fix 後): 1
- Stuck precision 平均 (fix 後): 1.0 (n=1、Phase 2a Go 条件: **≥ 0.6**、サンプル不足のため暫定)
- Stuck recall 平均 (fix 後): 1.0 (n=1)
- Stuck recovery median 全体: n/a
- **Phase 2a Go/No-Go 判定は Mac 再計算 + 継続収集で n≧5 まで保留**

## 観察メモ

### 2026-04-15 初回検証
- **Flow/Inc セッション (gse_20260415_080214)**: HMM が Flow/Inc を一度も argmax 選択しなかった。セッション開始直後の均等分布 `[1/3, 1/3, 1/3]` からユーザー自認よりも早く Inc/Stuck 側に振れていた → Phase 2a で Synthetic Friction を「真の摩擦兆候があった沈黙のみ」に再設計する動機として強い
- **Stuck セッション (gse_20260415_080921)**: 2 件中 1 件で HMM も Stuck を当てた。lead +2.4s は妥当な反応時間
- **detection_lead_ms の定義見直し (M1)**: 初版 `find()` で +50s、`min_by_key(abs_diff)` に修正して -3.1s / +2.4s と現実的な値に
- サンプル数 n=2 は Phase 2a Go 判断には不十分、**最低 5 セッション × 3 クラス (F/I/S 各 ≥5 件)** まで運用を続けて収集

### 2026-04-16 Windows 初回検証 (gse_20260415_144120、fix 後)
- **混在セッション (F:4 / I:1 / S:1)**: 日本語 IME が長時間 active → `gse-replay --metrics` の **replay-feat-alignment bug** を顕在化 (`.steering/20260416-replay-feat-alignment-bug/`)。logged feat を直接使う fix 後、warnings 0 で意味ある metrics を得た
- **Stuck 完全一致 (P=R=F1=1.0)**: Windows 実機での Stuck ラベルが lead -93ms (実質同時) で HMM と一致。macOS の +2383ms と比較して応答が早い傾向 (サンプル n=1 なので断言不可)
- **Flow 半分誤判定 (2/4 件 → Inc と予測)**: HMM が Flow と Inc を取り違えやすい傾向が Mac 初回検証と同じ → Phase 2a で Synthetic Friction 再設計の必要性を再確認
- **Detection lead median = -93ms**: 実質同期。Mac の -3119ms や +2383ms より中央に寄っており、日本語入力特有のリズムかサンプリング差か n の増加で見極め
- **clock semantic mismatch 学習**: retrospective の「実機データで算出系をすぐ回す」が正解だった。合成テストでは再現困難な IME pause auto-reset 問題を実データ 1 件で抽出できた
