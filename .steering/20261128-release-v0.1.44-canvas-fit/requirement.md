# 手跡の canvas の直しの入った版 v0.1.44 に上げ、本人の段 1 の版を入れ替える

## 背景

PR #443（手跡の帯と背景が半分の大きさで描かれるのを直す・`.steering/20261128-handmark-canvas-half-scale/`）を 2026-11-28 に main へ入れた（00bf1646）。同じ判断 6 で、直した版を作り、本人の段 1 の配布フォルダの gse-next を入れ替えると決めた（研究者の指示・段 1 は本人だけの試行で事前登録は凍結前）。
v0.1.44 には、11-26 に出して段 1 に入れなかった v0.1.43 の変更（起動時の時計の待ち・手跡の表示の数え方など）も入る。研究者はこれを承知で進めると選んだ（2026-11-28・AskUserQuestion）。

## ゴール

v0.1.44 の配布物で本人の段 1 の gse-next.app を入れ替え、帯が全幅に描かれることを画面で確かめる。

## スコープ

### 含むもの
- 版を 0.1.44 に上げる（4 箇所・前例 PR #440・#419）
- タグ `v0.1.44` の push、CI の配布物、配布の門（`--audience self --os-only macos`）
- 入れ替え（`gse-next.app` だけ・`s1-release-tag.txt` を書き換え・表と mode のファイルは残す）と日時の記録
- 入れ替えた版で、帯が全幅に描かれることを画面で見る

### 含まないもの
- Windows の配布（本人の段 1 は macOS）
- supply chain audit の新しい公表（cookie 0.18.1・url 2.5.8）への対応（別のタスク）

## 受け入れ条件

- [ ] 4 箇所が 0.1.44 で、`cargo metadata --locked` が通る
- [ ] CI が緑でマージされ、タグの run で build-macos と release が success
- [ ] 配布の門を通る
- [ ] 入れ替えの後、Measuring・input_monitoring=true・手跡の日の行を確かめる
- [ ] 帯が全幅に描かれることを画面で見る

## 関連ドキュメント

- `.steering/20261128-handmark-canvas-half-scale/`（判断 6）、前例 `.steering/20261116-release-v0.1.42-handmark/`・`.steering/20261126-release-v0.1.43-clock-gate/`

## 運用メモ
- /reimagine 適用: No
- 理由: 版上げと配布の定型。前例どおり。
