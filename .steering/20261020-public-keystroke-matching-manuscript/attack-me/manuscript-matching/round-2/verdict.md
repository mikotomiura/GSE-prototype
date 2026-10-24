# verdict（stage: manuscript・round 2・変更箇所だけ・2026-10-24）

対象: commit 92c0cadb の変更箇所（Kaggle のデータの出どころ・判断 72 / 74）。査読者役 3 人（paper-reviewer・Opus）・監査役 1 人。Codex は加えない。

## 1. 編集者の判定（変更箇所について）: major revision

R1 major・R2 minor・R3 major。§3.3 の条件文と「確かめていない」は 3 人とも適切とした。直す芯は倫理の節で、新しい事実で前提（同意の区分・名指すことの害）が変わったのに論が古いまま。凍結した手順を変える指摘は無い。有効な査読 3/3（各役 2 本以上の文献から逐語の基準を抜き出した。接地の引用は各役 1 件以上を本文で確かめた: narayanan "cross-correlation with publicly available databases"・rocher "release-and-forget"（PDF の抽出で "releaseand-forget"）・arp "threat models should be defined precisely"・kohno "microcosm of ethical considerations"・borgman "depending on the time, purpose, or entity requesting access"・hanisch "attacker models should be made explicit and common"）。

## 2. 一致（分母 = 有効な査読 3）

| 指摘 | R1 | R2 | R3 | 監査 | 判定 |
|---|---|---|---|---|---|
| A threat-model.tex:95 "We do not know who held the texts" が同じ段落の新しい文と食い違う | major | major | minor | 3-1 | 真 |
| B 序論 19–20 に条件と「確かめていない」が無い（§3.3 より強い） | major | major | minor | 1-2 | 真 |
| C 倫理の名指しの害: "report only"・"lose nothing new"・「既知の手順だからこの論文だけの危険ではない」がこの事実に効かない。論文が対応を公にする | major×2 | major | major | 3-4 | 真（下の裏取り 1） |
| D "drawn from … before it was released" の範囲（全部か一部か・公開版か選別前か）が不明。倫理の節で "before it was released" が落ちる | major | major | major | 1-3・2-3 | 真（判断 72 の要旨に範囲の言及は無い） |
| E "another log of the same writing"・"scores are already public"・"only which records correspond" が確かめていない前提 | major | minor | minor | 2-1・2-2 | 真 |
| F 義務の理由「参加者が同意していない」（ethics.tex 27・48–49）と関係者の区分（33–34）が、KLiCKe の参加者の同意（8–11）と同じ人について並ぶ | — | major | major | 3-2 | 真 |
| G 公開元への知らせ（ethics.tex 28–30）の中身にこの事実が無い・KLiCKe の著者を当事者として扱わない | major | major | major | — | 真（原稿は真。下書き 5 は今回出どころを入れて直してある） |
| H 説明を載せることの著者の了承と、ethics.tex 17–18 "will receive the paper when it is complete"（完成前に読んでもらう予定と時期が合わない） | major | major | minor | 4 | 真 |
| I 公開する側への持ち帰り（後の公開が前の加工を無効にする・出どころを追う）が一般形で無い | （c の所見） | minor | （c の所見） | 1-1 | 真 |

1 人だけ:
- R1: この場合に有利な攻撃はログどうしの対応づけで §3.4（threat-model.tex 137–138 "links across several releases"）の範囲外、閉じた世界の正答率はこの事例のリスクの上限でも下限でもない（真）／「結びつけられる状態」と「起きた害」（96 行）の区別（真・A と一緒に直せる）。
- R2: 掲げた目標がコンペの期間に限ったものだった可能性（threat-model.tex 148 の解釈に影響）（真・設計の判断は小）／「data」と「essays」の言い方のずれ（真・nit）／尋ねることは照合ではない（真）。
- R3: "collected in the same way"（ethics 41・43）が §3.3 の "names the same platform, the same kind of prompts and the same sequence of tasks" より強い（真・元からある文）／優勝解法の "external data" が KLiCKe か（下の裏取り 2 で偽陽性）／outline.md:109 が範囲の限定を落とす（真・nit）。

## 3. 裏取り（メインが一次で）

1. 「この関係は既に公か」（R3 major 2 の (1)）: KLiCKe の論文（JoWR 17(1), OpenAlex の oa_url の PDF を 2026-10-24 に取得し pdftotext で全文検索）に "Kaggle"・"Learning Agency"・"Linking Writing" は 0 件（"Competition" は課題名と所属だけ）。優勝解法の writeup（Chrome で 2026-10-24 に本文を読んだ）は外部データとして CommonLit・ASAP-AES・ASAP-SAS・Feedback Prize ELL・IELTS・Persuade 2.0 へのリンクを挙げ、KLiCKe の語は無い。内部の 2026-09-03 のカードに「KLICKE 由来」の注記があるが出どころ不明（novelty カード #5 のとおり）。→ 調べた範囲では、二つの公開の関係を公に書くのはこの論文が初めてになる。C と G はこの事実のもとで真。
2. R3 minor「external data が KLiCKe かもしれない」: 偽陽性（上の 1）。
3. 引用の位置: 査読者が引いた原稿の行（intro 19–20・threat-model 95–96・104–110・137–138・143–149・表 1 の 79–80・ethics 8–11・17–18・27・28–30・33–34・35–37・40–44・48–49・63–66・outline 109・151）はすべて逐語で在ることを確かめた。

## 4. 直す順

major（設計の判断が要る: 研究者に問う）
1. 倫理の節の名指しの害（C・G・H）: 出どころを書くこと自体を害として名指しし、書く理由と量る。"only"・"lose nothing new" を直す。知らせの中身に出どころを入れる。著者に完成前に読んでもらう（了承を確かめる）ことを書く。
2. 照合しない理由（F）: 同意の区分ではなく、別の当事者が別の条件で出した公開で、その条件と意図を確かめておらず、照合は掲げた目標をこちらの行為で破る、という形へ。関係者の段落で重なる書き手を 1 文。
3. ログどうしの対応づけ（R1）: §3.3 か §3.5 に 1 文（範囲外・正答率はこの事例のリスクを示さない）。
4. 公開する側への持ち帰り（I・R2-6）: §8 に条件つきの 1 文を足すか。

minor・nit（書き方だけ）
5. threat-model.tex 95–96 を説明と整合させ、「結びつけられる状態」と「起きた害」を分ける（A・R1）。
6. 序論に条件と「確かめていない」（B）。言い方を "the competition data" にそろえる（R2 nit）。
7. 範囲: 著者は全部か一部か・公開版に入るかを言っていないと書く（D）。倫理の節にも "before it was released" を入れる。
8. "another log" → 同じ記録か別かは分からない形・得点の条件・"only" の前提（E）。
9. "collected in the same way" を §3.3 の言い方にそろえる（R3）。outline.md の行を本文の範囲にそろえる。

## 5. 逸脱・注入の疑い

- 注入の疑い: 4 本とも「なし」。メインも保存の際に見つけていない。保存の検査（secrets-filter rc=0・一覧の外の絶対パスなし）は 4 本とも通った。
- 逸脱: なし（4 本とも初回で返った）。

## 6. 研究者に問うこと

上の 1〜4（設計の判断）と、5〜9 の承認。

## 7. 研究者の採否（2026-10-24・判断 75）

1〜4（設計の判断）は 4 問とも推奨を選んだ。5〜9 は全部承認。直した内容は判断 75。round 3 は未実施。
