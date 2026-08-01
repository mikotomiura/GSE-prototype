# phase1-signal-diagnostics-repro — `.idea` の設計根拠を再現可能な実測値に落とし込む

## 背景

`.idea/20260801-architecture-signal-and-online-learning.md` §1 は「実測でわかった現状の故障
(推測でなく数字)」として、以降の設計判断 (ADR-008/009 候補) の根拠となる数値を並べている。
しかし **追跡下にある再現可能な出力は §1.1/§1.2 の C-index 表だけ**だった。

| `.idea` の主張 | 追跡下の裏づけ | その主張が支える設計判断 |
|---|---|---|
| §1.1 特徴量→Q1 C-index | ✅ `exploratory/per_feature_cindex.txt` | X 軸が主観摩擦を予測できていない |
| §1.1 並べ替え検定 68 件・名目有意ゼロ | ❌ 無い | 同上 (偶然でないことの担保) |
| §1.3 φ レール飽和率 (74.3 / 92.1 / 63.5 / 90.4%) | ❌ 無い | **「正規化が壊れている」= 具体的な故障箇所** |
| §1.3 実 X と 0.25·φ(F1) の r=0.78 | ❌ 無い | 「f1 項が支配的だが完全な崩壊ではない」 |
| §1.4 ICC 0.060〜0.159 | ❌ 無い | **「個人適応すべきは β でなく写像係数」= 最重要の設計分岐** |
| §1.5 未使用信号 (paste/ime_dwell/keys) が既存特徴量を上回る | ❌ 無い | 収集シグナル拡張 (案 A) の根拠 |
| §1.6 paste の被験者間 97 倍 | ❌ 無い | **「paste を単独の目的変数にする案」の棄却根拠** |

`exploratory/per_feature_cindex.py` は 61 行で C-index しか計算していない
(`paste` / `icc` / `phi` / `perm` のいずれの語も現れない)。

このまま ADR / docs へ昇格すると、**再現手段の無い数字が SSOT の主張になる**。
`reproducibility-discipline` (SSOT: `docs/experiment-tracking.md`) のルール 4
「1 コマンド再現できないなら実験は未完了」に反する。

## ゴール

`.idea` §1 の数値をすべて **追跡下のスクリプトから再生成できる**状態にし、
再現結果と `.idea` の記載を突き合わせて **一致 / 不一致 / 再現不能** を明示する。

その上で「ADR に載せてよい主張」と「温度を下げる / 載せない主張」を仕分ける。
**数値が再現できなければ、その主張は設計判断の根拠として採用しない。**

## スコープ

### 含むもの

新規実験ディレクトリ `experiments/20260801-signal-diagnostics/` (探索的) を作り、
以下の診断を再現可能な形で実装する。入力は Phase1 確証カットと同一
(`gse-dataset` `raw/P010–P014`、`calibration_blind` 40 セッション)。

| ID | 診断 | `.idea` の対応箇所 |
|---|---|---|
| D1 | 特徴量 → Q1/Q2 の C-index に**並べ替え検定**を付す (名目有意 / Bonferroni) | §1.1 |
| D2 | **φ レール飽和率** — 各項が 0 / 1.0 に張り付く割合。β_writing 固定と ime_state 由来の実 β 両方 | §1.3 |
| D3 | 実 X と 0.25·φ(F1) の相関 (r) | §1.3 |
| D4 | **ICC** — f1/f3/f4/f5 の個人差割合 (被験者間分散 / 全分散) | §1.4 |
| D5 | **未使用信号** — `paste` / `ime_shadow.dwell_ms` / `key` 数 を窓内集計し C-index を算出 | §1.5 |
| D6 | `ime_shadow.nav` / `.abandon` が全件ゼロか (死んだフィールドの確認) | §1.5 |
| D7 | **paste/1000打鍵** の被験者間比と paste=0 セッション比率 | §1.6 |

### 含まないもの

- **ADR-008/009 の起票と docs/ への昇格** — 本タスクの成果 (数値の可否) を前提にする別タスク。
- 新規データ収集・被験者募集。既存 40 セッションのみ。
- **凍結対象コードの変更** — `engine.rs` / `features.rs` / `probe_scheduler.rs` /
  `schema_dto.rs` には一切触れない。診断は Python 側で φ を**再実装**して行う
  (Rust 実装と定数が一致することを別途アサートする)。
- HMM の再チューニング。`notes.md` §5③「現時点で着手する根拠は無い」に従う。
- 生 NDJSON / `.age` のコミット、外部 LLM への送信。集計値のみを追跡下に置く。

## 受け入れ条件

- [ ] `experiments/20260801-signal-diagnostics/` が `reproducibility-discipline` の
      ディレクトリ規約 (config / data.md / env.md / run.sh / results/ / notes.md) を満たす
- [ ] D1–D7 がすべてスクリプト化され、**1 コマンドで再走**できる
- [ ] Python 側 φ 実装が Rust (`features.rs::phi` / `engine.rs` の β と重み) と
      一致することを機械的に確認する (定数の二重定義を検知できる形にする)
- [ ] 入力を gse-dataset の commit hash + セッション数 + HMM_VERSION で固定 (`data.md`)
- [ ] 各診断について `.idea` の記載値と再現値を並べた突合表を `notes.md` に作る
- [ ] 不一致・再現不能があれば**それも結果として記録**する (隠さない)
- [ ] 生ログ・PII が `experiments/` に混入していないことを確認する

## 関連ドキュメント

- `.idea/20260801-architecture-signal-and-online-learning.md` §1 (再現対象の主張)
- `.idea/20260801-behavioral-context-online-latent-ml-design.md` (後続 ADR の設計案)
- `experiments/20260731-phase1-calibration-analysis/` (確証判定・入力カットの来歴)
- `docs/experiment-tracking.md` (再現性規約の SSOT) / Skill `reproducibility-discipline`
- `docs/research-positioning.md` §5 H-X1 (検証中の仮説)
- `src-tauri/src/analysis/features.rs::phi` / `engine.rs::calculate_latent_axes` (φ と β の定義元)

## 運用メモ

- /reimagine 適用: **No**
- 理由: 再現対象の数値と計算式が `.idea` と既存コードで確定しており、設計の選択肢が開いていない。
  実装は「既に主張されている数字を検証可能にする」作業。
