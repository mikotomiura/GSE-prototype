# 次のセッション（Mac）: 照合の論文 —— Kaggle のデータが KLiCKe から取られたことを原稿に入れる

作成 2026-10-24（判断 72 の後）。この機械は Mac。本計算と探索的な分析 3〜5 は G-GEAR（`next-session-public-keystroke-matching-exploratory-3-5-ggear.md`）。G-GEAR の作業はこのセッションでしない。前の引き継ぎ `next-session-public-keystroke-matching-manuscript-after-attack-me.md` の「結果が出たら」はそのまま生きている（この作業はその前に済ませる）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-kaggle-source.md を読んで、照合の論文に Kaggle のデータの出どころ（判断 72）を入れて。
```

## 今の状態（2026-10-24）

- worktree `/Users/johnd/GSE-wt-matching-manuscript`・ブランチ `docs/public-keystroke-matching-manuscript`。
- 2026-10-23 に研究者が Dr. Tian へ遅れの知らせ（草稿は 11 月中旬ごろ）と Kaggle の問いを送った（`reply-drafts-20261013.md` の 6）。
- 返事（10-24）: Kaggle のコンペのデータは **KLiCKe を公開する前に KLiCKe のコーパスから取ったもの**。研究者が下書き 7 で論文に personal communication として書いてよいかを尋ね、返事は「最も適切だと思う形で進めてよい・原稿を読んでから考えを伝える」。→ 書く（判断 72 と追記）。この返事への返信は要らない。
- Kaggle のデータは使わないまま（判断 67・72）。下書き 4 の CC に Crossley を入れたまま（判断 72 の追記）。下書き 5（The Learning Agency Lab への通知）も保つ。
- 返事の本文とアドレスは repo に入れない（要旨だけ `decisions.md` の判断 72）。

## やること（順に）

1. `decisions.md` の判断 64・67・72 と、原稿の該当箇所を読む:
   - `papers/keystroke-log-release-matching/manuscript/sections/threat-model.tex` の 95〜107 行目付近（「閉じた世界は隠された作文が手元の本文の中にあるときだけ成り立つ。KLiCKe の中にあれば、照合で分かるのは記録の対応だけ」「二つの公開が作文を共有するかは倫理上の理由で調べなかった」）
   - `introduction.tex` の 12〜13 行目付近（Kaggle の「本文の再現を防ぐため」のマスクを動機の例に使っている）
   - `ethics.tex` の "The competition data" の段落
   - `discussion.tex` の 44 行目付近（利用条件の段落）
2. 直し方を研究者に AskUserQuestion で問う（推奨と理由を添える・日本語）。少なくとも:
   - Kaggle の例の位置づけ: 「本文を隠して公開した記録の本文が、後に本文ごと公開された」例として、加工の保護が後の公開に左右されることを書くか、序論の動機の例を別の形に替えるか。害 (a) の定義（判断 68 の 1）と結論の向きを変えないこと。
   - 書く文の言い方（「KLiCKe の著者によれば」の形・personal communication の日付。投稿版は二重盲検で日付を外す・判断 63）。
   - 「調べなかった」の文は残す（当方は照合も突き合わせもしていない）。そのうえで著者から聞いたことを足す。
3. 決めた形で直す: threat-model・introduction・ethics・必要なら discussion と outline.md の該当行。判断 64 の 2（共通の著者を文で書かない）はこの事実に合わせて改めた（判断 72 の 2）ことを本文の書き方に反映する。
4. 下書き 4 を合わせる: "it does not examine whether the two share essays" の段落を、著者から聞いた事実に合わせて直す。倫理の段落の `Section [n]` を埋める。CC の段落の理由（コンペの記述を見てもらう）はそのまま。
5. 下書き 5（The Learning Agency Lab への通知）の "the paper does not examine whether the competition shares essays with any other release" を直す（照合していないことは保つ）。
6. ビルド（`build.sh`・エラー 0・未定義 0）と文体の門（`_style_check.py`）。
7. 直した節に attack-me（stage: manuscript・変えた箇所に限る）。採否は研究者に問う。
8. 記録（判断 73 以降）・コミット・push（PR は出さない）。

## 気をつけること

- 著者の説明は personal communication。当方が突き合わせて確かめたことにしない（照合も重なりの検査もしていない）。
- 本計算の結果をまだ見ていない（G-GEAR）。結果の向きを先取りする文を書かない。
- 送る下書きは研究者が送る。Claude はメールを送らない。
