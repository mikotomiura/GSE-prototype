# audit（意図の監査役・round 1）

読んだもの: context-B・outline.md「Rewrite v2」（1〜23 行）・decisions.md 判断 2〜5・context-A・main.tex 全文・supplement.tex 560〜612 行。読んでいない: supplement 1〜559 行・references.bib・figdata・kit README・判断 1・outline v1・追記 1（b0f5821a）。注入の疑い: 無い。

## 結論
持ち帰り 1・2 は要旨・序論・考察・結論に届く。持ち帰り 3 の届き方が弱い: 本文 325 行は凍結した読みの文の前半（近い順に並んだ）だけを写し、後半（時間の近さと分けていない）と頻度だけの基準線が同じ強さであることが落ちる。そのため「科学の問いは開いたまま」の項の末尾で肯定の方向の証拠として読まれやすい。判断 5 の「差の文を書かない」は S14 で守られるが、なぜ書かないかが伝わらない。

## 1. 意図にあって対象物に無いもの
- 1-1（重要）本文の 1 文に持ち帰り 3 の「ただし」が無い。意図「ただし頻度だけの基準線も同じくらい強く、時間の近さ・機器・作業の仕方と分けていない」。main.tex 325 行の文には、頻度の基準線が同じ強さ（k=5 で 0.982 と 0.982）・drift と分けていない・機器と作業の仕方を含む「本人」のどれも無い。凍結した同じ箇条（supplement 601 行）は "These cells do not separate stable differences from closeness in time (drift)." を含む。576 行 "Synthetic drift between units ($\rho=0.9$) was detected in all four gap cells, so no cell separates stable differences from closeness in time." TMLR は "Looking at the Appendix is at the discretion of the reviewers." なので補足を読まない査読者に届かない。
- 1-2 「予測の得と見分けは別の問い」が本文に無い（572 行 "This is a question of ranking, not of predictive gain."・603 行 "Neither result is used to deny or support the other: one is a ranking and the other a predictive gain" は補足だけ）。1 文の位置が "Whether CoAuthor writers differ in stable ways that per-person models capture is not answered" で始まる項の末尾なので、部分的な答え（差はある側）として読まれやすい。
- 1-3 「頻度の差の文を書かない」理由が見えない。604 行 "The frequency baseline reflects marginal differences such as the pause share; no statement is made about the difference between it and the cross-likelihood." 凍結した規則で書かないという理由が無く、k=1 で基準線の方が高い（0.941 対 0.912）のに書かないと都合の悪い比較を避けたように読まれる。案: "because the reading rules committed before the data were read made no provision for it" のような理由を添える（未決 3 の直してよい範囲と照らして判断を）。

## 2. 対象物にあって意図に無いもの
- 2-1 325 行の "with its reading committed before the data were read" を先頭に置くと確認の響きが強まる。S14 の "The check is exploratory and is not used for confirmatory claims."（572 行）が本文に無い。
- 2-2 S14 603 行 "the main analyses concluded on the same records that the remainder of the strong comparison does not show stable per-person differences." は outline v2 "Not claimed: that per-person differences are absent or present" と本文の "could not be attributed" / "is not answered" より強く読まれうる。本文の言い方に揃えるのが安全。
- 2-3 Code availability（main.tex 351 行 "the code of all later checks (listed in \Sref{8}) and the aggregate and synthetic values are available at …"）は S14 を含む 13 件の公開を約束するが、S14 の公開は未決（3-3）。

## 3. 矛盾
- 3-1 判断 3（基準を満たせば論文 3 に入れ、満たさなければ限界の 1 文と補足の 1 節だけ）と判断 5（基準を満たしたのに限界の 1 文と補足の 1 節）。判断 5 は v2 の入れ方が v1 の追記 3 に代わると書き手続きは説明されるが、判断 3 だけ読むと逆に見える。outline v2 の "its section would go after Results and before Discussion"・"[slot for the weight-eye section]" も古い。
- 3-2 判断 4 の TMLR の根拠（統合すると「本人ごとの差はパラメータのどこにあるか」が加わり範囲の一句に入る）は、実際に入ったのが 1 状態の遷移表の順位の探索なので今の版では成り立たない。venue-fit の当て直しは未了。想定読者も outline v2 "learning analytics, writing research, HCI" と context-B の ML の研究者で食い違い、序論 43 行 "Adaptive systems that read behaviour logs, such as writing assistants, tutoring systems …" と keywords "user modelling" は前者の枠のまま。
- 3-3 main.tex 177 行 "thirteen later checks (\Sref{8})" と 351 行は後からの確かめ全部のコードを公開と書き、S14 の公開が未決であることと食い違う。
- 3-4 関連研究 65 行 "Coarse symbols of typing rhythm may discard part of this individuality"・考察 313 行 "a 26-symbol code of rhythm over overlapping windows may keep too little of this individuality" と、S14 で同じ記号で書き手を近い順に並べられた（T = 0.91〜0.996）ことの両立を本文が述べない。
- 3-5 599 行 "Readings (in the wording committed before the data were read)" の下の 604 行の後半（"no statement is made about the difference …"）が凍結した文の英訳か結果の後に足した文かを追記 1 と照らして確かめてほしい。後から足した文なら見出しの下に置くこと自体が地位の取り違え。

## 4. 特に見てほしい点への答え
1. 補足 S14 では意図どおり限界を補う位置。本文 325 行は意図より強く読まれうる。案: 「frequency-only baseline も同程度・時間の近さ・機器・作業の仕方と分けていない・順位の問いで予測の得の問いではない」の 1 句を足す。2. 守られているが理由が無く「避けた」と見える余地。

参考: context-A の題と main.tex 29 行の題が違う。
