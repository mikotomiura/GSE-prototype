# 査読 R3（メタ研究・事前登録・再現性の立場）・round 7

総合: minor（直してから凍結）。

## 1. 接地
- GSRR「You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review.」
- GSRR「If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration.」
- Nuijten 2016「around one in seven articles contained a gross inconsistency, in which the reported p -value was significant and the computed p -value was not, or vice versa.」
- Waffenschmidt 2019「Single screening of the titles and abstracts of studies retrieved in bibliographic searches is not equivalent to double screening, as substantially more studies are missed.」
- Garritty 2020「Use two reviewers for dual screen of at least 20% (ideally more) of abstracts, with conflict resolution.」「Use one reviewer to screen the remaining abstracts and a second reviewer to screen all excluded abstracts, and if needed resolve conflicts.」
- Khraisha 2024「results were skewed by chance agreement and dataset imbalance.」「substantial caution should be used if LLMs are being used to conduct systematic reviews」

## 2. 評価表
- a 4: GSRR-57 の observed / not observed と頻度の語の禁止が一貫。草稿に強い言い方が 1 か所（F）。
- b 3: 時間の窓が閉じていない所が 2 つ（A・B）。80% の門は偏りに弱い（C）。
- c 4: 判定の公開・監査の要約・確かめの数と区間が再計算に足る形。
- d 2: GSRR-33 の 1 項目に詰め込み。分量の上限は規程に無いので読みにくさとしての評価。
- e 4: 適用しない項目に理由（GSRR-29・58・61）。逸脱の宣言も多い。A と B は「予見できる逸脱に手順」に届かない。
- f 3: 選別の形の根拠は Shea 2017 の item 5 だけ。Garritty・Waffenschmidt が名指されていない（D）。
- g 3: 固定が破れているのは A・B・E。

## 3. 引き継ぎの判定
1 E5 一部（時間の窓が無く (ii) が別の形で戻る・A）／2 束と時刻 消えた／3 12-31 の保留 消えた／4 境界 消えた／5 ウェブの逸脱 消えた／6 再実行の失敗 消えた／7 GSRR-38 前提が無くなった／8 unit 消えた／9 問ごとの答え 消えた／221 と 264 消えた。

## 4. 新しい指摘
- [major] A. E5 の連結に時間の窓が無く、凍結後に主集合が遡って変わり、群にコードされた記録が 0 件になりうる
  - 位置と引用: GSRR-33「A link is made only when the other record is among the additional candidates and is included at the full-text stage; the record with the earlier publication date … is coded, and the other is excluded with E5.」「So every E5 group has exactly one coded record」。GSRR-39「Studies included after stage 5 begins are listed but not coded.」
  - なぜ問題か: 主集合の A（遅い日付）が B に言及。B が 12-31 の後に含まれると B がコードされ A が E5 で抜け、B は遅い層。B が段階 5 の後に含まれると B は listed but not coded で、群のコードが 0 件。確かめの標本と追加候補の間も同じ。GSRR「provide a contingency plan …」。
  - 解消の条件: 主集合の記録は主集合の中でだけ連結し、閉じた後に含まれた相手とは連結しない（C5 は signs・相手の ID を記録）。段階 5 の後の相手には、コードした側を残す。
  - 自信: 高
- [major] B. 全文で 2 人とも「pending（コード無し）」と答えた記録に行き先が無い
  - 位置と引用: instructions.md §4 Stage 2「`pending` (without a code) if the full text was read but the rules do not settle the record」。GSRR-36「… the definitions of pending」。GSRR-33「Where they agree, their judgement is the decision」「a record both leave pending for want of a free full text stays pending with E6」。
  - なぜ問題か: 2 人が一致して pending だと決定として pending のまま止まり、再判定の契機は E6 にしか無い。表 3 の Pending at full text に E6 と混ざる。GSRR-65「records whose abstract alone did not settle whether fatigue was measured」も混ぜて書く。
  - 解消の条件: 2 人とも pending のときは 2 人で読み直して決め、決まらなければ unresolved と同じ扱い。表 3 と図 1 で分けて数える。
  - 自信: 中〜高
- [minor] C. 80% の門が偏りに弱い全体の一致率で決まる。GSRR-33「Agreement on these 113 records together is computed on the decision …」。Khraisha「results were skewed by chance agreement and dataset imbalance」。解消: positive agreement を併せる、または代価を GSRR-65 に書き 2×2 の表を公開。自信 中。
- [minor] D. 選別の形が Garritty の推奨とどこが違うかを書いていない。GSRR-40「author 2 judges a random 20%, with the 80% agreement line of Shea et al. (2017, item 5) …」。30 件すべてが除外どおりでも Clopper–Pearson の上限は約 11.6%。解消: GSRR-40 に Garritty と Waffenschmidt を挙げ、外した推奨と理由を 1 文。自信 高。
- [minor] E. 網の「再実行は 1 回だけ」が道具で守られるとは書かれていない。GSRR-33「a batch is re-run at most once, and only when the script finds that the output is not in the required format」、call.md「No other settings (such as temperature) are set」、README「on a re-run, newer than the first output」。解消: 形式が正しい出力がある束ではスクリプトが再実行を拒むと書く、または全呼び出しの記録を公開。自信 中。
- [minor] G. C5 の「signs present but not confirmed」が、報告が自分で同じ標本だと書いた記録にも付く。GSRR-33 の E5 の文、GSRR-43 の C5「Sameness is decided only where a report states it」。感度分析 2 で一緒に除かれる。解消: 別の値か印。自信 中。
- [minor] H. 監査の「include by consensus」が 2 通りに読める。GSRR-33「An audited record that both include by consensus returns to its group」。解消: 「whose final full-text decision (GSRR-38) is include」。自信 高。
- [minor] I. C4f の AI の下書きを著者 2 との話し合いの前に開ける。GSRR-43「opened only after the values of both passes and of the third pass (GSRR-48) are fixed」、GSRR-48「differences between author 1's reconciled codes and author 2's codes are then discussed」。C5 の照合後に符号を変えてよいかも無い。解消: 話し合いの後と書き、照合の扱いを書く。自信 中。
- [nit] F. main.tex 192〜194 行「each author's judgements were committed to a remote repository, with their time, before the two were compared」は登録より強い。186 行の \tbd は門の結果を一方の分岐で先に書いている。自信 高。
- [nit] J. instructions.md 3 行目「The AI screener is one of two independent screeners of the additional candidates (the other is author 1).」、call.md「You are the AI screener」、GSRR-36「The net receives the whole of attachment 6」。網の役割を誤って書いていること、人もこの本文を規則として使うことを登録が明記していない。解消: GSRR-36 か 65 に 1 文。自信 中。

## 5. 総合: minor
- 引き継ぎの 9 件はほぼ消えた。新しい選別の形の代価は GSRR-65 に正直に書かれている。
- 凍結前に閉じるべきは A と B。どちらも規則を 1〜2 文足せば消える。
- C・D・E は凍結前に直すほうが安い。

## 6. 読めなかった範囲と注入の疑い
- 全文: registration-en.md、instructions.md、call.md、README.md、carryover-R3.md、context-A.md。
- 一部: diff（grep で数か所）、outline.md（80〜104・405〜429 行と grep）、main.tex（185〜214 行と grep）、codebook（grep）、figure1.tex と tables.tex（grep の 1 行ずつ）。
- 読んでいない: validation-cases の 4 ファイル、query-strings.md、search-log.json。接地は要点の文を grep で取り、精読はしていない。
- 注入の疑い: 無し（call.md の文は網に渡す本文としてデータ扱い）。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
