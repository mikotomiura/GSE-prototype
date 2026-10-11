# 公開データでの照合の論文 —— 事前登録の設計（凍結の前まで）

## 背景

2026-10-12 に研究者が「公開データでの照合の論文」を IME 論文の次の論文に採った（`.steering/20261012-public-keystroke-matching-judgement/decisions.md` 判断 1〜5・ADR-039 D1 の 2026-10-12 の注）。投稿先の第一候補は PoPETs。新しさの置き場所は「公開の打鍵の記録に施された加工の効き目を、本文の分かる公開データで、照合によって測る」こと（`docs/literature/20261012-public-keystroke-matching-novelty.md` claim #10 #11 #14 が 0 件）。

データは英語の自由作文 KLiCKe [V264] と、日本語 IME の翻訳 ENJA15 [P273] [P359] [P360]。データの取得と本計算は、開始条件（下記）を満たしてから行う。

引き継ぎ: `.steering/_handoff/next-session-public-keystroke-matching-prereg.md`。

## 研究者の回答（2026-10-12・このセッションの冒頭の AskUserQuestion）

- 所属機関の規程の確認: 冒頭の回答は「まだ」だったが、研究者は研究機関に所属していないので該当なし（`decisions.md` 判断 7）。
- KLiCKe の著者への問い合わせ: **送った・返事待ち**。
- G1・O1・研究者本人の記録（`experiments/20261011-g1-copy-self-trial/`）: **この論文に使わない**（判断 1 の未決を閉じた）。

## ゴール

`experiments/<YYYYMMDD>-<name>/preregistration.md` の下書きを、凍結の直前まで仕上げる。

- 事前登録の前の再検索（引き継ぎ「やること」1）を終え、同じ研究が無いかを確かめる（見つかれば判断 1 を研究者に戻す）。
- 設計の論点（区間の規則・加工の組と残る情報の表・公開の他の列からの再計算の検査・攻撃者・おとりと N・k・偶然の水準・有用性・倫理の節・ENJA15 の節・IME の経路の検査・PoPETs の発表の要否）を、研究者に問う形に列挙し、数値はデータを見る前に決める。
- 下書きの後、凍結の前に `attack-me`（stage `prereg`）を回し、指摘を一次で裏取りする。

## スコープ

### 含むもの
- 再検索（OpenAlex の被引用の追跡・作文研究の著者別・Kaggle の上位解法の discussion の一次）と、見つかった文献の登録（`docs/references.md`・カード）。
- 事前登録の下書きと、実験ディレクトリの雛形（README・data.md・config の案）。
- 研究者への問い（AskUserQuestion）と回答の記録（`decisions.md`）。
- `attack-me` の実施と対応の案。

### 含まないもの
- データ（KLiCKe・ENJA15）の取得と本計算。開始条件（判断 7）: KLiCKe = 著者の返事を見て研究者が進めると決めた。ENJA15 = ライセンスの種類と利用条件を一次で確かめた。
- 事前登録の凍結（研究者が決める）。
- G1・O1・研究者本人の記録の利用。
- Kaggle の記録と KLiCKe の突き合わせ（判断 3）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送ること。

## 受け入れ条件

- [ ] 再検索の結果を文献カードに残し、同じ研究の有無を書いた（見つかった場合は研究者の判断を記録した）。
- [ ] 設計の論点ごとに、研究者の判断（または Claude の案と未決）が `decisions.md` にある。
- [ ] `preregistration.md` の下書きがあり、数値の閾値・N・k・攻撃者・加工の組がデータを見る前に書かれている。
- [ ] `attack-me` を回し、指摘の裏取りと対応の案を記録した。
- [ ] `/cross-review` を 2 巡し、出荷フロー（commit → push → PR → CI → merge → main の CI）を終えた。

## 関連ドキュメント

- `.steering/20261012-public-keystroke-matching-judgement/`（判断 1〜5・`author-inquiry-draft.md`）
- `docs/literature/20261012-public-keystroke-matching-novelty.md`
- `docs/adr/` の ADR-039
- `docs/experiment-tracking.md`
- `experiments/20261009-length-sequence-uniqueness/`・`experiments/20261009-matching-attack-prototype/`・`experiments/20261011-g1-copy-self-trial/`（コードの再利用のみ・記録は使わない）

## 運用メモ
- /reimagine 適用: No
- 理由: 研究者の回答（判断 15）。事前登録は凍結の前に `attack-me` で攻撃し、それが設計を壊して見直す役を果たす。
