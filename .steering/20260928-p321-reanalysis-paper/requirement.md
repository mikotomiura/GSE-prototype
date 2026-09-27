# p321-reanalysis-paper — 2 本目の論文: [P321] ＋ [P434] の再解析

## 背景

- 2026-09-28 の判断 16（`.steering/20260927-ime-observation-paper-eval-design/decisions.md`）で、
  研究者の指示「機関に関係なく使えるもの（論文などで公開されたもの）で、機が熟しているなら並行して進める」を受け、
  2 本目の論文を IME 論文と**並行で**進めると決めた。
- 使うデータはどちらも CC BY 4.0 で、機関に属さずに使える:
  - [P321] Alaboudi & LaToza の figshare パッケージ（arXiv v1 側のコーディング・解析済み:
    `experiments/20260906-p321-resumption-baseline/`）
  - [P433]（[P321] の正式版・*Empirical Software Engineering* 28:117）の replication package
    （`https://figshare.com/s/0e9eac98b8ddd54c384c`・**未入手**）
  - [P434] Li & Coblenz（FSE 2026）の論文の Table 4（`Resolved`）と Table 5（手法 × task）
- 論文の芯（案）: **解決と中止を同じ終端に束ねた episode 定義のもとで、成果を要求しない自己解決指標
  （R₀ 型）がどれだけずれるか**（分子の効果 R₀ − R₀′ ＝ 未解決かつ参照なしで終わった割合）を、
  2 つの独立な公開データで示す。あわせて交絡（defect の起点）と、コーディングの版による揺れ（参照 21% → 33%）を指摘する。

## ゴール

EASE 2027 Short Papers（6 頁）に向けて、**解析と 6 頁の外枠**を揃える。原稿の執筆は別タスク。

## スコープ

### 含むもの
- 投稿先の確定と、投稿先の匿名性規程（プレプリントの可否）の一次確認
- [P433] の replication package の取得（実ブラウザ・ダウンロード前に研究者の承認）と、v1 との差分の特定
- 解析一式（★ 判断 6 で論文用の別リポジトリ `mikotomiura/self-resolution-measure`・`C:/self-resolution-measure` に置く）:
  [P321] / [P433] の公開コーディング（★ 判断 7: 両パッケージの `rowData.json` は同一）／ [P434] の表の転記 CSV を入力に、R₀ / R₁ / R₀′・分子と分母の効果・
  起点での層別・開発者単位のクラスタ・ブートストラップ区間を出す
- 位置づけのサーヴェイ 1 ラウンド（`/literature-review`）
- 6 頁の外枠（主張 ↔ 根拠の対応表）

### 含まないもの
- 原稿の執筆（別タスク）
- [P321] / [P434] の値を GSE の期待値として使うこと（`notes.md` §4）
- IME 論文との同梱（判断 6）
- [P434] の GitHub 補足データ（LICENSE 無し）の利用・再配布
- 人の打鍵データ・Phase1 / G1 / O1 のデータの利用

## 受け入れ条件

- [ ] `decisions.md` に投稿先・主系列の版・完了範囲・プレプリント方針が記録されている
- [ ] [P433] パッケージの取得結果（取得できた場合はファイル名・サイズ・SHA-256、できなかった場合は経路ごとの失敗）が `data.md` にある
- [ ] v1 と正式版の差分（何が数え直されたか）が表で特定されている
- [ ] 新リポジトリで `bash run.sh` が exit 0 で終わり、検算（v1 の既報値 12 項目・[P434] は転記の二重照合）が緑、
      かつ [P433] の報告値の再現表（項目ごとの一致 / 不一致）が出る（★ 判断 7）
- [ ] 検算ゲートの自己検査（正常 / 不在 / 壊れている）と、陽性・陰性対照が run.sh の中で走る
- [ ] ブートストラップは seed 固定で、2 回実行して `results/metrics.json` がバイト一致する
- [ ] サーヴェイ 1 ラウンドのカード・`references.md` 追記・`_index.md` 追記がコミットされている
- [ ] 外枠（主張 ↔ 根拠）が `.steering/20260928-p321-reanalysis-paper/outline.md` にあり、handoff §3 の「書いてはいけないこと」に触れていない

## 関連ドキュメント

- `.steering/_handoff/next-session-p321-reanalysis-paper.md`（引き継ぎ・一次資料ではない）
- `.steering/20260927-ime-observation-paper-eval-design/decisions.md` 判断 6 / 9 / 16
- `experiments/20260906-p321-resumption-baseline/notes.md` §4 / §6 / §9、`data.md`
- `docs/references.md` [P321] [P433] [P434]
- `docs/experiment-tracking.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 実装・アーキテクチャ判断ではなく、既存の解析手続き（2026-09-06 に検算済み）を 2 つ目の版と 2 つ目のデータへ広げる作業。
  設計の分岐（投稿先・主系列の版・範囲）は grill で研究者が決めた（`decisions.md` 判断 1–4）。
