# 3 つの検査の今のコードの棚卸し（2026-11-16）

サブエージェント 3 本（Explore・sonnet・読むだけ）の報告を、要の箇所だけメインが一次で照合した（照合済みの行に「照合」と書く）。スクリプトは実行していない。記録の中身は開いていない。

## 予測（論文 1・枝 `docs/public-data-findings-paper`）

- 帯の判定の核: `experiments/20261105-findings-paper1-prefreeze/scripts/confirm_p1.py:138` `branch(ci)`（幅 > WIDTH_MAX は精度不足・区間が帯の内なら同等・上／下に外れる・帯の端をまたぐ）。値は同 :45 `BAND_LO, BAND_HI, WIDTH_MAX = 0.45, 0.55, 0.10` の直書き（照合）。ε は :38 `EPS_SET = (0.001, 0.0)`。退化の扱い `h1_branch` :153。
- 18 量 `feats18` :248・停滞の錨 `stall_anchors` :260・対照の条件 `control_ok` :308・学習器 `models`（logreg・hgb）:660・人をまたぐ OOF の AUC `oof_auc` :716・`boot_oof` :721。全 1,509 行の 1 ファイル。
- 推定器（床）: 論文 kit の Rust `papers/public-data-findings/kit/estimator/`（`gse-replay --features`・`Cargo.lock`・provenance の 3 重の照合）。定義の値は `prereg/p1-episode.json`（v1.2.0）。
- 変換（実験ごとに複製）: KLiCKe `experiments/20261101-klicke-early-stall-trigger/scripts/convert_klicke.py`・CoAuthor `20261031-coauthor-pre-request-signal/scripts/convert.py`・CS1 `20261104-cs1-landscape/scripts/build_cs1.py`。どれも GSE の NDJSON の key 行に寄せて gse-replay に渡す。
- holdout: CS1 は `holdout.json` の SHA-256 を run.sh で照合し、`build_cs1.py` `read_units` が holdout の書き手を読み飛ばす。
- O1 の人の中の学習器: `experiments/20261116-o1-conduct-record/auc.py`（`matched_auc` :253・`fit_logistic` :234・打鍵 18 量 `feat_k` :184・打鍵以外 `feat_n` :199・止まりの最中 `early=True`）。帯は置かない探索（conditions.md R5.5）。
- Python の lockfile は無い（`requirements-confirm.txt` は版のピン）。

## 定義（論文 2・コードは公開 repo `/Users/johnd/stall-shape-multiverse`・1 コミット `8e4890b`）

- 論文 2 の枝 `docs/gse-paper2-stall-shape` は原稿と集計だけで、コードは公開 repo にある。
- 定義の族: `experiments/20261107-stall-shape-multiverse/scripts/core.py:24-28`（W 3 × θ 5 × 規則 2 × 区間 3 = 90・B0 は :29）の直書き（照合）。休止 36 通りは `round5_pause.py:29-31`。
- `detect`（core.py:62-111）は始まり s・確定 t0 = s + θ・再開を返す（停滞の始まりと確定の時刻を区別している）。
- 中間形式 `unit_record`（prep.py:54-61・t は int64 の ms・ins/dele の bool 配列・観測区間）。
- 向きの判定（区間が 0 の上・下・含む）は `round3_speed.py:51-53` 等にラウンドごとに散在。規則の値 `analyze.py:24-26`（N_BOOT=2000・PHI_CUT=1.5・SHARE_CUT=0.25）の直書き（照合）。結果の変数は KLiCKe の作文の点だけ（`round1_extra.load_scores`）。
- 推定器の停滞の検出の Rust 本体は `src-tauri/src/analysis/feat_offline/stall_onset.rs`、Python はその写し（K1 で照合）。
- lockfile は無い（env.md に版の文章）。

## 漏れ（IME 論文 1 `papers/ime-observation/`・照合の論文は読むだけ）

- 照合の値 0.9019（K=10・counts_only・Windows の合成入力）: `experiments/20261009-matching-attack-prototype/results/summary.md:46`（照合）。`values.tex` の q4x 系は別の特徴集合で 0.90 ではない（取り違えに注意）。
- 攻撃: `papers/ime-observation/kit/e2/closed_set.py`（`_tokens` :156・`_distance` :183・`attack` :261・`coarser_or_equal` :114・定数 `PAUSE_MS=600` :122）（照合）。時刻の除去・丸めは `simulate_obs.py` `apply_features` :83。標準ライブラリだけ。
- 「偶然に近い」の規則: `manuscript/tools/results_tables.py:518` `near_chance_at`（Wilson 95% の上端 ≤ 2/K を直書き）（照合）。規則はプライバシーの基準から導いたものではないと README が明記。
- 最大の障害: 候補の打鍵列を、合成入力の計画（plan）から生成器で作り直す設計。利用者の記録に当てるには、候補を「キーの種類の列」か「候補の本文からキーの種類の列を作る関数」で受ける口が要る。
- キーの種類の体系が 2 つある: GSE の `KeyCategory` 14 種（IME 論文の kit は逐語の抜粋）と、照合の論文の KLiCKe 側 16 種。対応表は無い。
- 検査していない脅威の記述: IME README L276-287（上界を主張しない・言語モデル・同一人物の複数試行・最終本文との照合は未評価）。照合の論文 threat-model.tex（同定・属性は主張しない）。
- Python の lockfile は無い（requirements.txt の版のピン）。

## 横断して分かったこと

1. 3 つとも分析は Python（予測の床だけ Rust の gse-replay）。
2. 規則の値はどれも直書き。「値は利用者が事前に決めて入れる」には引数化が要る。
3. 入力の共通の形は、実態として「GSE の NDJSON の key 行（ms の整数・KeyCategory）」に寄せる形が予測と定義で既にある。漏れは別形式（obs/1）。
4. どれも Python の lockfile を持たない（reproducibility-discipline ルール 2 の穴）。
