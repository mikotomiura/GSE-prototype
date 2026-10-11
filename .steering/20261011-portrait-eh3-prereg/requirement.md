# portrait-eh3-prereg

## 背景

- 肖像（壁紙＋画面端の小面・状態を表さない驚き）と招待（身体回帰への誘い・文字を置かない図像）の設計制約は、親タスク `.steering/20261005-portrait-invitation-constraints/` の判断 1〜15 で決まった。EH3（外部参加者の形成的比較・別の事前登録・凍結の前に attack-me）で測るものは同 判断 8 の M-1a〜M-6 にある。
- EH1（合成 trace）は第 5 回で閉じた（親の判断 15・第 5 回の判断 9）。研究者の決定は「範囲つきの事実として書き、限界を EH3 に持ち込む」。
- 引き継ぎ: `.steering/_handoff/next-session-portrait-eh3-prereg.md`（一次ではない）。

## ゴール

EH3 の事前登録の**稿**（凍結しない）と、EH3 を回すために別タスクで作る**実装の要件**を書く。

- 事前登録の稿: 問い・条件・参加者・手続き・測るもの（M-1a〜M-6 と E1-8 の none / seed）・判断 7 の「問題として観測された」の閾値・解析（記述が主）・EH1 から持ち込む限界（親の判断 15 ほか）・主張の格。
- 実装の要件: 招待の PC 面（I-1〜I-5）・EH3 用の肖像の組み込み・記録項目（content-free の NDJSON に足すもの）・配布の分け方。
- 凍結の前の段取り（attack-me・`/cross-review` 2 巡・見本の選択・実装）を tasklist に書く。

## スコープ

### 含むもの
- 事前登録の稿（場所は design で決める）
- 実装の要件（招待の PC 面・肖像・記録・配布）
- 研究者の決定の記録（`decisions.md`）

### 含まないもの
- 招待の PC 面・肖像の配布用の組み込み・schema の変更の**実装**と配布物（別タスク）
- 事前登録の**凍結**（実装と見本の選択の後。attack-me・`/cross-review` 2 巡もその前に回す）
- ADR の起票（EH3 の後）・`expression-channel.md`・RP など SSOT の書き換え
- 同意文書・被験者向け文書の本文（記録項目の要件だけ書く）
- EH1 の回を足すこと・第 2〜5 回の判定と読み方の書き換え

## 受け入れ条件

- [x] 事前登録の稿が、研究者の決定（本タスクの判断 1）と親の判断 1〜15 の制約に反しない（各節に出典の判断番号がある）
- [x] EH1 の限界（親の判断 15 の 5 点・U-4 の閉じない 2 点と測っていない点）が一次の文面で稿に入っている
- [x] 判断 7 の (a)〜(c) の閾値が稿の中で結果の前に決まっている（形と案の値まで。分母と値の確定は凍結の前に研究者が行う・稿 F-8）
- [x] 実装の要件が、招待（I-1〜I-5）・肖像（E1-1〜E1-8 の該当・U-4 の型）・記録・配布の 4 つに分かれ、未決が未決として書かれている
- [x] 主張の格（EH0・「検査した範囲で見つからなかった」まで・合成の停滞は認知の状態ではない）が稿に書かれている

## 関連ドキュメント

- `.steering/20261005-portrait-invitation-constraints/decisions.md`（判断 1〜15）・`constraints-ledger.md`
- `.steering/20261010-portrait-eh1-round5/decisions.md` 判断 9・`experiments/20261010-portrait-eh1-round5/notes.md`
- `.idea/20261005-motivation-fatigue-reentry-surface.md` §8.5・§8.6・§11（main checkout・版管理外）
- 再査定 `.steering/20260921-media-expression-theory-audit/pc-workplace-media-reassessment.md` :86・:89（main checkout・版管理外）
- `docs/preregistration-p1-episode.md`（事前登録の書き方の先例）

## 運用メモ
- /reimagine 適用: No
- 理由: 大きな分岐（範囲・場・形・ADR の時期・出す時点・記録・参加者）は本タスクの判断 1 で研究者が選んだ。事前登録の攻撃は凍結前の attack-me が担う。
