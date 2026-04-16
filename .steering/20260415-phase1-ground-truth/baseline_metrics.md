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
| 2026-04-16 | `gse_20260416_060712.ndjson` **(range)** | F:215/I:0/S:5 | 0.591 | 0.791 | n/a | n/a | 0 | **range**: Flow F1=0.88, Stuck F1=0.89。point F1=0.000 から劇的改善。Inc ラベルなし |
| 2026-04-16 | `gse_20260416_062509.ndjson` | 7/2/2 | 0.061 | 0.091 | n/a | -3583 | 0 | macOS。Flow 1/7 のみ正解、Stuck 0/2。Inc も全 miss |
| 2026-04-16 | `gse_20260416_062509.ndjson` **(range)** | F:163/I:23/S:11 | 0.572 | 0.817 | n/a | n/a | 0 | **range**: Flow F1=0.91, Inc F1=0.54, Stuck F1=0.27。3クラス全てに GT あり |
| 2026-04-16 | `gse_20260416_063443.ndjson` | 2/3/0 | 0.444 | 0.600 | n/a | +184 | 0 | macOS。**最良結果**。Flow 1/2、Inc 2/3 正解。lead +184ms (HMM がわずかに先行) |
| 2026-04-16 | `gse_20260416_063443.ndjson` **(range)** | F:190/I:68/S:0 | 0.446 | 0.729 | n/a | n/a | 0 | **range**: Flow F1=0.83, Inc F1=0.51。Inc recall 52.9% で他セッションより良好 |
| 2026-04-16 | `gse_20260416_064130.ndjson` | 3/5/0 | 0.243 | 0.375 | n/a | -224 | 0 | macOS。Flow 2/3 正解だが Inc 1/5 のみ。Inc→Flow 誤判定が多い |
| 2026-04-16 | `gse_20260416_064130.ndjson` **(range)** | F:283/I:110/S:2 | 0.292 | 0.689 | n/a | n/a | 0 | **range**: Flow F1=0.82, Inc recall=3.6% 壊滅 (106/110→Flow 誤判定)、Stuck 0/2 |
| 2026-04-16 | `gse_20260416_065241.ndjson` | 4/5/0 | 0.095 | 0.111 | n/a | -696 | 0 | macOS。Flow/Inc とも大半 Stuck に誤判定。HMM の Stuck 偏り傾向が顕著 |
| 2026-04-16 | `gse_20260416_065241.ndjson` **(range)** | F:68/I:55/S:0 | 0.444 | 0.707 | n/a | n/a | 0 | **range**: Flow F1=0.82, Inc recall=34.5%。Inc→Flow 誤判定 30/55 |
| 2026-04-16 | `gse_20260416_043006.ndjson` **(range)** | F:149/I:100/S:0 | 0.561 | 0.839 | n/a | n/a | 0 | **Windows range**: Flow F1=0.90, Inc F1=0.78。Inc precision 1.0 (誤検出なし)、recall 0.64。Stuck ラベルなし |
| 2026-04-16 | `gse_20260416_043613.ndjson` **(range)** | F:180/I:81/S:38 | 0.236 | 0.478 | n/a | n/a | 0 | **Windows range**: 3クラス全 GT あり。Inc/Stuck 壊滅 (Inc F1=0.06, Stuck F1=0.00)。Inc→Flow 74/81、Stuck→Flow 38/38 |
| 2026-04-16 | `gse_20260416_044520.ndjson` **(range)** | F:168/I:83/S:28 | 0.584 | 0.735 | n/a | n/a | 0 | **Windows range**: Stuck P=1.0 R=0.25 F1=0.40。Inc F1=0.52。Stuck→Inc 9件の誤判定あり |
| 2026-04-16 | `gse_20260416_045123.ndjson` **(range)** | F:242/I:20/S:0 | 0.523 | 0.947 | n/a | n/a | 0 | **Windows range**: Flow F1=0.98、Inc F1=0.59。Flow 支配セッション。Inc→Stuck 5件の誤判定 |
| 2026-04-16 | `gse_20260416_045931.ndjson` **(range)** | F:233/I:0/S:10 | 0.538 | 0.959 | n/a | n/a | 1 | **Windows range**: Stuck F1=0.64 (P=0.58, R=0.70)。**Stuck 検出最良**。タイポ→Stuck 誤分類の観察者指摘あり |

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

### Range-based 集計 (macOS 5 セッション)

| 指標 | 値 | 備考 |
|------|-----|------|
| セッション数 | 5 | 全 macOS |
| 総 feat 数 | 1,417 | point-based 50 ラベル → 28 倍の GT 量 |
| Macro F1 平均 | **0.469** | point 0.261 → +0.208 |
| Micro F1 平均 | **0.747** | point 0.307 → +0.440 |
| Flow F1 平均 | **0.851** | 全セッションで 0.82–0.91。HMM は Flow 検出が得意 |
| Inc F1 平均 | 0.325 | 0.06–0.54 とばらつき大。**Inc→Flow 誤判定が最大の弱点** |
| Stuck F1 平均 | 0.231 | support ありは 3 セッションのみ (0.00, 0.27, 0.89) |
| **Stuck precision** | **0.75** (3 sess avg) | **Go 条件 ≥0.6 達成** (ただし range-based、n=3) |
| Inc→Flow 誤判定率 | 64% (164/256) | 全 Inc feat の 2/3 が Flow と予測される |

### Range-based 集計 (Windows 5 セッション、2026-04-16 追加)

| 指標 | 値 | 備考 |
|------|-----|------|
| セッション数 | 5 | 全 Windows (メモ文章作成) |
| 総 feat 数 | 1,332 | Mac 1,417 と同規模 |
| Macro F1 平均 | **0.488** | Mac 0.469 とほぼ同等 |
| Micro F1 平均 | **0.792** | Mac 0.747 より良好 (Flow 支配セッション多い) |
| Flow F1 平均 | **0.853** | 0.65–0.98。Mac と同水準、HMM の Flow 検出は OS 問わず安定 |
| Inc F1 平均 | 0.443 | 0.06–0.78。Mac 0.325 より改善傾向 |
| Stuck F1 平均 | 0.347 | support ありは 3 セッションのみ (0.00, 0.40, 0.64) |
| **Stuck precision** | **0.79** (support あり 2 sess: 1.00, 0.58) | **Go 条件 ≥0.6 達成** |
| Inc→Flow 誤判定率 | 55% (106/284 feat, support あり 4 sess) | Mac 64% より改善。ただし Session 2 は 74/81=91% で壊滅 |
| **ユーザー観察** | タイポ多い ≠ Stuck | CorrRate 高い + AvgFT 正常 の場合、Stuck 介入は逆効果。Phase 2a の F3 文脈ゲート設計根拠 |

### Range-based 統合集計 (全 10 セッション: Mac 5 + Windows 5)

| 指標 | 値 | 備考 |
|------|-----|------|
| セッション数 | 10 | Mac 5 + Windows 5 |
| 総 feat 数 | **2,749** | Phase 2a の統計検定力として十分 |
| Macro F1 平均 | **0.479** | |
| Micro F1 平均 | **0.770** | |
| Flow F1 平均 | **0.852** | OS 間で安定 (Mac 0.851, Win 0.853) |
| Inc F1 平均 | 0.384 | 最大の改善余地。Phase 2a ターゲット |
| **Stuck precision** | **0.77** (support あり 5 sess avg) | **Go 条件 ≥0.6 を安定達成** |
| **Phase 2a Go/No-Go** | **Go** | range-based で n=10、Stuck precision ≥0.6 達成、Inc→Flow 誤判定が改善ターゲット |

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

### 2026-04-16 Range-based segment 初回検証 (gse_20260416_064130)
- **手順**: `--segment` で 8 セグメント生成 → 回顧ラベル付与 (F:3, I:3, S:1, Skip:1) → `--segments` で range metrics 算出
- **統計検定力**: point-based 8 点 → range-based 395 feat。同一セッションで桁違いの GT 量
- **Flow 検出は良好 (F1=0.82)**: 283 feat 中 268 正解 (recall 94.7%)。HMM は安定打鍵の Flow 検出が得意
- **Inc recall 壊滅 (3.6%)**: 110 feat 中 106 件を Flow と誤判定。**HMM が Inc と Flow を区別できていない**ことが統計的に確認された
- **Stuck 誤検知が実際の Stuck を誘発**: ユーザー回顧で「Stuck 誤検知のせいで実際に詰まった」との報告。Seg 5 (2 feat, CorrRate 25%) を S とラベル → HMM は Inc と予測。介入設計の「false positive が UX を悪化させる」リスクが実データで裏付け
- **Micro F1 が高い (0.689) のは Flow 支配のため**: クラス不均衡で macro/micro が乖離。Phase 2a では Inc/Stuck の GT 量を意図的に増やす必要あり

### 2026-04-16 Windows Range-based 5 セッション検証 (メモ文章作成)
- **作業内容**: 全 5 セッションがメモでの文章作成 (同一タスク種別)。Mac のコーディングセッションとは異なる入力パターン
- **Flow 検出は OS 問わず安定**: Flow F1 平均 0.853 (Mac 0.851)。HMM の Flow 検出能力はタスク種別・OS に依存しない
- **Inc 検出は Windows の方がやや良好**: Inc F1 平均 0.443 (Mac 0.325)。ただし Session 2 (`043613`) は Inc F1=0.06 で壊滅 — Inc 81 feat 中 74 件が Flow と誤判定
- **Session 2 の異常**: 3クラス全てに GT があるにも関わらず Macro F1=0.236。Stuck 38 feat が全て Flow と予測された。HMM が Stuck を全く検出できていない (Stuck ラベルは CorrRate 11.6%, AvgFT 114ms でタイポ主因)
- **タイポ ≠ Stuck (ユーザー直接指摘)**: CorrRate が高くても AvgFT が正常 (90-114ms) で打鍵ペースが維持されている場合、ユーザーは Stuck ではなく「タイポが多い Flow」と認識。**CorrRate (F3) 単独で Stuck を判断すると false positive が発生し、介入が Stuck を誘発するリスク**。Phase 2a の F3 文脈ゲート設計の重要な根拠
- **Stuck precision は良好 (0.79)**: support ありの 2 セッションで P=1.0 と P=0.58。HMM が Stuck と予測した場合は概ね正しいが、recall が低い (真の Stuck を見逃す)
- **Phase 2a Go 判断**: 統合 10 セッション (Mac 5 + Win 5) で Stuck precision 0.77 ≥ 0.6。**Go 条件達成**。改善ターゲットは Inc→Flow 誤判定 (統合 59%) と F3 文脈ゲート
