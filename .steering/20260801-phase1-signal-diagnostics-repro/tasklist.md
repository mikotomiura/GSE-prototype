# タスクリスト

## 準備
- [x] `.idea` 2 本を精読し、再現対象の主張を洗い出す
- [x] 既存 `exploratory/per_feature_cindex.py` が何を計算しているか確認 (C-index のみ・61 行)
- [x] NDJSON のイベント種別とフィールドを確認 (feat / key / paste / ime_shadow / ime_state / realtime_label)
- [x] `features.rs::phi` と `engine.rs` の β・重みを確認
- [x] `reproducibility-discipline` Skill と `docs/experiment-tracking.md` を読む
- [x] 入力データの来歴を固定 (gse-dataset commit hash / セッション数 / sha256)

## 実装 — experiments/20260801-signal-diagnostics/
- [x] ディレクトリと規約ファイル (config.json / data.md / env.md / run.sh / notes.md)
- [x] Rust から β・重み・KAPPA を抽出して config へ書く (抽出失敗は fail-closed)
- [x] 共通ローダ (NDJSON → feat / label / key / paste / ime_* の窓集約)
- [x] **検算**: Python 再計算 X と `feat.raw_x` の一致
      (閾値は < 1e-9 でなく r≥0.999 / 残差中央値≤1e-3 / >0.01 が≤0.5%。
       logger.rs の丸めのため厳密一致は原理的に不可能 — decisions.md D7)
- [x] D1 並べ替え検定 (被験者内シャッフル・seed 固定・名目/Bonferroni)
- [x] D2 φ レール飽和率 (β_writing 固定 / ime_state 由来の実 β の 2 通り)
- [x] D3 実 X と 0.25·φ(F1) の相関 + 4 項それぞれの寄与
- [x] D4 ICC (f1/f3/f4/f5・feat 全件)
- [x] D5 未使用信号 (paste / ime_dwell / keys / bs_rate) の C-index + 並べ替え検定
- [x] D6 `ime_shadow.nav` / `.abandon` の非ゼロ件数
- [x] D7 paste/1000打鍵 の被験者間比・paste=0 セッション比率
- [x] results/ へ JSON + TXT 出力

## テスト (診断自身の検算)
- [x] Python φ ⇔ Rust φ の一致を確認
- [x] 定数抽出に失敗したとき run.sh が非ゼロ終了することを確認
- [x] feat 総数 / ラベル総数 / セッション数が 0731 実験の記録と一致
- [x] 同一 seed で 2 回走らせて結果が byte-equal (決定性)
- [x] `run.sh` の 1 コマンド再現

## 突合
- [x] `.idea` 記載値 vs 再現値の突合表を notes.md に作る (一致 / 不一致 / 再現不能)
- [x] 不一致は原因まで追い、追えなければ「再現不能」と明記
- [x] **ADR に載せてよい主張 / 温度を下げる主張 / 載せない主張**の仕分けを結論として書く

## レビュー
- [x] code-reviewer (統計処理の妥当性・ICC/並べ替えの実装)
- [x] security-checker (生ログ・PII が experiments/ に混入していないか)
- [x] `/cross-review` (Codex 独立レビュー)
- [x] HIGH 指摘への対応

## ドキュメント
- [x] `docs/experiment-tracking.md` の実験一覧へ追記 (必要なら) — 一覧節が無いため不要と判断
- [ ] `.idea` の該当節に「再現済み・出典 experiments/20260801-signal-diagnostics」を追記

## 完了処理
- [ ] design.md の最終化
- [x] decisions.md の作成 (再現不能だった主張の扱い・不一致の解釈)
- [ ] git commit
