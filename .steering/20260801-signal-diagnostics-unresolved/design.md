# 設計 — 未解決 3 件の原因特定

## アプローチ

**候補定義の総当たり (exhaustive enumeration)**。
`.idea` 側に式・前処理が書かれていない以上、「なぜ違うか」は推測でなく
**有限の候補空間を全部計算して、記載値を再現する組み合わせを探す**ことで決着させる。

見つかれば「定義の違い」として確定 (✅)。見つからなければ
**「候補 N 通りを総当たりして再現不能」**という強い形で閉じる (前回の
「式が書かれていないので不明」より一段強い結論)。

## 変更対象

| ファイル | 変更 |
|---|---|
| `experiments/20260801-signal-diagnostics/probe_variants.py` | **新規**。総当たり本体 |
| `experiments/20260801-signal-diagnostics/results/probe_variants.txt` | **新規**。総当たり結果 |
| `experiments/20260801-signal-diagnostics/acceptance.sh` | **新規**。受け入れゲート |
| `experiments/20260801-signal-diagnostics/check_notes.py` | **新規**。notes ⇔ diagnostics.json 整合 |
| `experiments/20260801-signal-diagnostics/notes.md` | §1 表 3 行 + §2-A1/§2-C を更新 |
| `experiments/20260801-signal-diagnostics/diagnostics.py` | **結論次第**。`.idea` が正と判明した場合のみ |
| `experiments/20260801-signal-diagnostics/metrics.json` | 本体が変われば再生成 |
| `.idea/...§1` | 結果を追記 (gitignore・コミットに乗らない) |

**`diagnostics.py` は結論が出るまで触らない**。総当たりは `probe_variants.py` に隔離し、
`import diagnostics as D` で `load` / `make_phi` / `window_rows` / `_icc1` などを再利用する
(定義の二重化を避ける = 前タスク D2 と同じ方針)。

## 候補空間

### ① 「並べ替え検定 68 件」— セル数の定義

数える集合の直積を総当たりする:

- **特徴量セット**: 5 (φ のみ) / 7 (現行 `FEATS`) / 12 (`per_feature_cindex.py` の
  ewma_x,y・p_stuck,flow,inc を含む) / 12 (現行 FEATS+extra5) / 17 (12+extra5) /
  X 系 (f1,f3,f5,f6,raw_x) など
- **被験者**: 5 名 / 4 名 (P013 除外 — `.idea` §1.1 の表は P013 列が無い)
- **ターゲット**: Q1 のみ / Q2 のみ / 両方
- **数え方**: 全セル / 算出可能セルのみ
- **pooled 列**: 含む / 含まない

**先行仮説**: `.idea` §1.1 は Q1 (摩擦) の節。17 特徴量 × 4 被験者 (P013 除外) = **68**。
総当たりで裏を取る。

### ② r=0.78 — 相関の取り方

- 相手を `raw_x` (現行) / `ewma_x` / **再計算 X (β_writing 基準)** に替える
  ← `.idea` は「実 X」としか書いていない。§1.3 全体が β_writing 基準の再計算なので、
  再計算 X 同士の相関だった可能性がある
- 重み 0.25 の有無 (スケール不変なので同値のはず — 確認のため計算する)
- 被験者ごとに計算して平均 (プールでなく) / セッション単位
- ラベル窓集約 (n=200) 上で計算
- Spearman (順位相関)
- 丸めの有無

### ③ ICC — 式 × 前処理

- **式**: ICC(1)+k0 補正 (現行) / ICC(1)+単純平均群サイズ (N/k) / η²=SSB/SST /
  MSB/(MSB+MSW) / ICC(1,k)=(MSB−MSW)/MSB / 分散成分比 σ²b/(σ²b+σ²w)
- **前処理**: feat 全件 (現行 124,517) / **ラベル窓集約 (n=200)** / セッション平均 /
  外れ値除去 (IQR・percentile clip)
- **被験者**: 5 名 / 4 名 (P013 除外)

**先行観察**: `.idea`/再現の比は f1=0.750 f3=0.753 f4=0.779 f5=0.780 と
**4 特徴量で系統的にほぼ一定**。前処理差なら特徴量ごとにばらつくはずなので、
**式の違い**が第一候補。特に η²=SSB/SST は大 N 極限で ICC(1) の 4/5 倍に近づく
(k=5 群のとき) ので符合する。

## テスト戦略

`experiments/` は Rust を触らないので `cargo test` / lint は無条件に緑になる。
検証は `acceptance.sh` に集約する:

1. `run.sh` が exit 0
2. 同一 seed で 2 回実行し `results/diagnostics.json` が **byte-equal** (決定性)
3. φ 等価性検査 PASS (run.sh 内で fail-closed 済み・二重確認)
4. `check_notes.py`: `notes.md` の数値 ⇔ `results/diagnostics.json` の整合
5. `assert_no_pii` (run.sh 内・`probe_variants.py` の出力にも適用)
6. `metrics.json` が `diagnostics.json` と整合

## リスク

- **総当たりで「たまたま一致」を掴む**: 特に ① は 68 という 1 つの整数に当てるので
  偽陽性が出やすい。→ **一致した組み合わせは 1 つに絞らず全部列挙**し、
  意味的に妥当か (`.idea` の文脈と整合するか) を別途論じる。
- **③ で `.idea` が正と判明した場合**: `diagnostics.py` の `d4_icc` を直すと
  `results/` と `notes.md` §2-C・§3・`metrics.json` が連動する。整合チェックを
  先に用意してから直す。
</content>
