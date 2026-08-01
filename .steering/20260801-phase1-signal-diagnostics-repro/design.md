# 設計

## 実装アプローチ

**確証実験を汚さず、探索的診断として隔離する。**

`experiments/20260731-phase1-calibration-analysis/` は Phase1 の**確証判定の記録**であり、
`notes.md` は凍結された判定文書。そこへ後付けの探索的分析を足すと confirmatory / exploratory の
境界が曖昧になる。新規に `experiments/20260801-signal-diagnostics/` を切り、
**入力カットは 0731 と同一である**ことを `data.md` で来歴として明示的に繋ぐ。

診断は Python で実装する (Rust 側は凍結対象)。ただし φ と β を Python で書き直すと
**定数の二重定義**になり、`engine.rs` を将来変えたときに黙ってずれる。これは本セッションで
繰り返し踏んでいる「静かな不整合」と同じ族なので、**Rust ソースから定数を抽出して照合する**
仕組みを入れる (下記 §定数の同期)。

## 実装単位

`experiments/20260801-signal-diagnostics/` (規約: `reproducibility-discipline`)

```
config.json          入力パス / 対象 PID / 乱数 seed / HMM_VERSION / β と重み
data.md              入力の来歴 (gse-dataset commit・セッション数・カット条件・sha256)
env.md               python バージョン / 依存 (標準ライブラリのみ) / Cargo.lock hash
run.sh               1 コマンド再現エントリ
diagnostics.py       D1–D7 の本体
results/             *.json (機械可読) + *.txt (人間可読)
notes.md             仮説・PreReg 番号・`.idea` との突合表・逸脱
```

## 各診断の計算方法

すべて入力は `raw/P0*/*.ndjson` (匿名化済み・40 セッション)。
`realtime_label` は `source=random_probe` かつ `answered` のみ採用 (PreReg-6 の分母規約)。

### D1 並べ替え検定
既存 `per_feature_cindex.py` の C-index をそのまま使い、**ラベル (q) を被験者内でシャッフル**して
帰無分布を作る。特徴量 × 被験者 × ターゲット (Q1/Q2) の各セルで両側 p 値。
- 被験者内シャッフル = 被験者間の絶対値差を帰無仮説に持ち込まない (pooled の交絡を避ける)
- 反復数と seed は `config.json` に固定。`.idea` の「68 件」は
  **セル数 (特徴量 × 被験者 × ターゲット のうち算出可能なもの)** と解釈して件数も再現・照合する
- 多重比較: 名目 p<0.05 の件数と Bonferroni 閾値 (0.05/セル数) の通過件数を両方出す

### D2 φ レール飽和率
`feat` イベントの f1/f3/f4/f5/f6 に φ を適用し、`==0.0` と `==1.0` の割合を数える。
φ(x,β) = clamp((x−β)/(2β), 0, 1) なので、**x ≤ β で 0、x ≥ 3β で 1**。
2 通り出す:
1. **β_writing 固定** — `.idea` §1.3 の再現条件
2. **ime_state 由来の実 β** — `feat` に `ime_open` が無いため、`ime_state` イベントの
   直近 `on` を feat の `t` に前方補完して β を選ぶ。実運用に近い値
`.idea` は 1 しか書いていないので、2 は**追加の観測**として報告する。

### D3 実 X と φ(F1) 項の相関
`feat.raw_x` (Rust が計算した実値) と Python が再計算した `0.25*φ(F1)` の Pearson r。
併せて 4 項すべての寄与 (各項と raw_x の r) を出し、「f1 項が支配的」の妥当性を見る。
**再計算した X と `feat.raw_x` 自体の一致**も確認する (Python 実装の検算になる)。

### D4 ICC
一元配置変量効果モデルの ICC(1):
`ICC = (MSB − MSW) / (MSB + (k−1)·MSW)`、群 = 被験者、k = 群あたり平均サンプル数。
対象は f1/f3/f4/f5 (`.idea` の表と同じ)。窓集約せず **feat 全件**を使う
(`.idea` は 124,517 件と書いており feat 全件のはず。件数も照合する)。

### D5 未使用信号の C-index
ラベル窓 `[analysis_window_start_ms, analysis_window_end_ms]` 内で:
- `paste_count` = `paste` イベント数 / `paste_chars` = `external_paste_chars` の合計
- `ime_dwell_med` = `ime_shadow.dwell_ms` の中央値
- `keys` = `key` イベント (press=true) の件数
- `bs_rate` = `category=backspace` の比率
これらに既存の C-index を適用し、D1 と同じ並べ替え検定を付ける。

### D6 死んだフィールド
`ime_shadow.nav` / `.abandon` の非ゼロ件数を被験者 × OS 別に数える。全件ゼロなら
「実装バグか仕様か」を切り分ける材料として件数を記録する (`.idea` §8-4 の未解決事項)。

### D7 paste の被験者間分散
被験者ごとの `paste 件数 / (key press 件数 / 1000)` と、paste=0 セッション数 / 全セッション数。
最大 / 最小比を出して `.idea` の「97 倍」と照合する。

## 定数の同期 (二重定義の防止)

`diagnostics.py` は β と重みを**ハードコードしない**。
`src-tauri/src/analysis/engine.rs` / `features.rs` から正規表現で抽出し、`config.json` に
書き出してから使う。抽出に失敗したら**即エラーで停止** (fail-closed)。

これにより:
- Rust 側で β や重みを変えると、次回の再現時に config が変わり差分として見える
- 抽出できない形にリファクタされたら実験が落ちるので、黙ってずれない

`KAPPA=2.0` と重み `0.30/0.25/0.25/0.20` も同様に抽出対象。

## 影響範囲

- **本体コードへの影響ゼロ**。`src-tauri/` / `src/` は読み取りのみ。
- 凍結対象 (`engine.rs` / `features.rs` / `probe_scheduler.rs` / `schema_dto.rs` / prereg) 不変。
- `cargo test` / replay snapshot への影響なし。
- 追加されるのは `experiments/` 配下のみ。

## プライバシー

- 入力は匿名化済み NDJSON (`vk` 生値なし・本文なし・session 相対時刻)。
- `results/` に出すのは**集計値のみ**。セッション単位の生値・タイムスタンプ列は出さない。
- 生 NDJSON / `.age` はコミットしない (`.gitignore` の `*.age` / `gse_*.ndjson` で二重防護)。
- 外部 LLM への送信なし (`data-privacy` Skill)。

## テスト戦略

コード変更が無いので `cargo test` は無関係。代わりに**診断自身の検算**を置く:

1. **Python φ ⇔ Rust φ の一致** — `feat.raw_x` (Rust 出力) と Python 再計算 X の
   最大絶対誤差が浮動小数点誤差の範囲 (< 1e-9) に収まること。ずれたら実装違いを検知できる。
2. **定数抽出の成否** — 抽出できなければ run.sh が非ゼロ終了。
3. **件数の照合** — feat 総数・ラベル総数・セッション数が 0731 実験の記録と一致すること
   (入力カットが同一であることの担保)。
4. **並べ替え検定の seed 固定** — 同一 seed で 2 回走らせて同一 p 値になること。

## `.idea` との突合の扱い

再現値が `.idea` と食い違った場合、**`.idea` を正としない**。
`notes.md` に「記載値 / 再現値 / 判定 (一致・不一致・再現不能)」の 3 列で残し、
不一致は原因 (集計単位の違い・カットの違い・計算式の違い) まで追う。
**追えなければ「再現不能」と書く**。これが次タスク (ADR 起票) の入力になる。

## ロールバック計画

`experiments/` への追加のみなので、ディレクトリごと削除すれば元に戻る。
本体コード・凍結対象には触れないため revert リスクは無い。
