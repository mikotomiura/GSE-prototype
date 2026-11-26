# 申告（C4 のプローブ）の聞き方とラベルとしての質を洗う

## 背景

`.steering/20261126-gse-concept-field-companion/decisions.md` 判断 14。研究者は、申告の聞き方（無作為の時刻に割り込むカード）とラベルとしての質を問題と見た。申告は Mh-D を学ぶ正解のラベルの元（判断 13）で、段 1 の事前登録の A〜B の値（A3・A4・B1〜B6）の前提でもある。事前登録は凍結の後に変えられないので、凍結の前に結論を出す（まとめの引き継ぎ `.steering/_handoff/next-session-gse-integrated-before-freeze-then-slides.md` の段 A の A-2）。

## ゴール

割り込みの問題とラベルの質の問題を分けて洗い出し、本人の段 1 の記録で測れるものを測り、同意文書・ADR・事前登録への響きを確かめたうえで、3 名の版に入れるか段 1 の後にするかを研究者が決める。

## スコープ

### 含むもの
- 割り込み（いつ出るか・どう出るか・作業への響き）と、ラベルの質（思い出しのずれ・選択肢の粗さ・未回答の偏り・反応性）の洗い出し
- 本人の段 1 の記録の集計（件数・割合・分位だけ・探索）
- 今日の構想（判断 9〜11）との整合
- 響きの確かめ（3 名の同意文書・ADR-031・043・045・052・055・057・`docs/preregistration-stage1.md`）
- 研究者の判断（AskUserQuestion）と、A-1 の decisions.md に写す結論

### 含まないもの
- コードと同意文書の変更（決まったものは別のタスク）
- 聞く中身と答える形（判断 14 で選ばれていない。答え方は ADR-057 で直っている）
- 頻度の変更（ADR-031 D8・ADR-057 の経緯）
- 本人の段 1 の形の変更（ADR-043 D9）

## 受け入れ条件

- [ ] `analysis.md` に洗い出し 1〜4 と、記録で測れたもの・測れないものがある
- [ ] 研究者が 3 名の版に入れるか・段 1 の後にするかを決め、`decisions.md` にある
- [ ] A-1 の作業記録へ写す文が用意されている
- [ ] 本人の記録の中身・個々の申告・日付を出していない。集計を Codex に送っていない

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-probe-asking-and-label-quality.md`（入口）
- `.steering/20261125-s1-probe-one-tap/decisions.md`・ADR-057（答え方の直し）
- `docs/preregistration-stage1.md`（進行中の枝 `docs/stage1-prereg-values-and-stop-rule` の版）
- `.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md` 注 D
