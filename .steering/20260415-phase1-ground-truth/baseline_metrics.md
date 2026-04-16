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
| 2026-04-16 | `gse_20260416_060712.ndjson` | 7/4/1 | 0.000 | 0.000 | 1005 | -1699 | 0 | macOS。Flow 全て Inc に誤判定、Stuck 1件も Flow に。HMM が Flow を選択できない傾向 |
| 2026-04-16 | `gse_20260416_062509.ndjson` | 7/2/2 | 0.061 | 0.091 | n/a | -3583 | 0 | macOS。Flow 1/7 のみ正解、Stuck 0/2。Inc も全 miss |
| 2026-04-16 | `gse_20260416_063443.ndjson` | 2/3/0 | 0.444 | 0.600 | n/a | +184 | 0 | macOS。**最良結果**。Flow 1/2、Inc 2/3 正解。lead +184ms (HMM がわずかに先行) |
| 2026-04-16 | `gse_20260416_064130.ndjson` | 3/5/0 | 0.243 | 0.375 | n/a | -224 | 0 | macOS。Flow 2/3 正解だが Inc 1/5 のみ。Inc→Flow 誤判定が多い |
| 2026-04-16 | `gse_20260416_065241.ndjson` | 4/5/0 | 0.095 | 0.111 | n/a | -696 | 0 | macOS。Flow/Inc とも大半 Stuck に誤判定。HMM の Stuck 偏り傾向が顕著 |

### 除外済みセッション (macOS 初回 2 件)

2026-04-15 の macOS 初回 2 セッション (`gse_20260415_080214`, `gse_20260415_080921`) は fix 後再計算でも F1=0.000 だったため集計対象から除外。gse-dataset からも削除済み (2026-04-16)。観察メモは下記に残す。

### fix 前の参考値 (20260415_144120、regen feat)
`gse-replay --metrics` が step() 再生成 feat を使っていた時期の値。`.steering/20260416-replay-feat-alignment-bug/decisions.md` D1 で clock semantic mismatch と判明したため廃棄。Phase 2a 判定には下行の fix 後値を使う。

| Session | Macro F1 | Micro F1 | Lead median | Warnings | 意味 |
|---|---|---|---|---|---|
| `gse_20260415_144120.ndjson` (fix 前) | 0.000 | 0.000 | +26315 | **6 (全ラベル)** | regen feat が IME pause の auto-reset を再現できず 6 件中 6 件 window 外 → 数値全 0。信頼できない |

## 集計サマリ（Phase 2a Go/No-Go 判断）

> 10 件溜まった時点で更新。Phase 2a 着手可否の根拠として使う。

- セッション件数 (集計対象): 6 / 10 (Windows 1, macOS 5)
- 除外: macOS 初回 2 件 (F1=0.000、gse-dataset から削除済み)
- Flow ラベル総数: 27 (Win 4 + Mac 23)
- Incubation ラベル総数: 19 (Win 1 + Mac 18)
- Stuck ラベル総数: 4 (Win 1 + Mac 3)
- Macro F1 平均: 0.261 (range 0.000–0.722)
- Micro F1 平均: 0.307 (range 0.000–0.667)
- Stuck precision 平均: 0.167 (1/6 セッションで正解、Phase 2a Go 条件: **≥ 0.6**、**未達**)
- Stuck recall 平均: 0.333 (Stuck ラベル 4 件中 HMM 正解 1 件のみ = Windows の 1 件)
- Stuck recovery median 全体: 1005 ms (n=1, macOS session 1 のみ)
- Detection lead median 全体: -696 ms (6 セッション中央値)
- **Phase 2a Go/No-Go: Stuck precision 0.167 で Go 条件 (≥0.6) に大幅未達。HMM チューニングが先に必要**

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
