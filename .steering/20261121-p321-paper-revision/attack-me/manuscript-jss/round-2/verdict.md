# verdict — attack-me・stage `manuscript`・round 2（JSS へ投稿する前の改訂版・`revision-jss` の `75e8e76`）

作成: 2026-11-22（Surface・メイン）。査読の結果は研究の証拠ではない。裏取りの判定はメインが、対応の採否は研究者が決める。

## 1. 編集者の判定: **major revision**（ただし直すのは文と小さな作業が中心）

- 有効な査読は 3 本（R1・R2・R3）。推奨は R1 が major（minor に近い）、R2 が minor、R3 が minor（major に近い）。
- 3 人とも、round 1 の重い指摘（DF3 と打ち切り・RQ4・凍結の開示・名前）は実質的に解消したと判定した。凍結した部分をハッシュで守る作りは R3 が「模範的」と書いた。
- それでも major とするのは、**検証の主張が事実より強い**所が複数の査読者で一致しているからである。JSS の水準で甘くしない。
  - 2 つ目の実装は、照合の的になる値を入力の本文から受け取っていた（3 人一致）。
  - §7.3 の Hellas の例は、原典の数で計算すると向きが逆になる（2 人）。
  - D2 の打ち切りは P4TA だけに当て、4 件とする原典の逐語と食い違う（R3 と監査役）。
  - Data availability の DOI が旧い版を指している（R3 と監査役）。
- どれも新しいデータは要らない。文を直す作業と、小さな作業（手での数え直し・D2 で 4 件を打ち切りにした値・新しい版の寄託）で消える。

## 2. 一致した指摘（分母 = 有効な査読 3 本。監査役は別の列）

| # | 指摘 | R1 | R2 | R3 | 監査役 | 裏取り |
|---|---|---|---|---|---|---|
| A | 2 つ目の実装は、渡された §4.1 の本文から照合の的の値（89・2,136・11・15・DF の内訳・10/79）を受け取っていた。"without access to … the results" は事実と違う。指示文も残っていない。一致を事後に選んだ所もある（duration の sum と span・時刻の順） | major | minor | major | 3.2 | **真**（body 115・117・121 に値がある。`audit/independent-recount/README.md` に指示文が無い。`output.txt` に span と sum の両方がある） |
| B | 「セッションの最後の DF3」の理屈が §3.1 と食い違う（"Neither dataset links a unit to later work" なら、最後でなくても戻りは記録されない）。しかも 2 つの実装で唯一合わなかった数 | minor | minor | minor | — | **真**（body 69・189） |
| C | D1 の duration の定義（block の和か、始まりから終わりまでか）と、block を時刻の順に並べる規則が本文に無い | minor | minor（順序） | minor（duration） | 3.2 | **真**（body 162 は "seconds of the episode" だけ。§4.1 に by time / chronological の語が無い） |
| D | 要旨の "raised the measure by only 3.5 points" は、どの量からどの量かが分からない（A から A\|R なら 14.8）。序論 21 行の "barely moves the measure" も同じ | minor | nit | — | A | **真** |
| E | 本文が長く、同じ但し書き（区間は符号の検定ではない・DF3 は打ち切り）を 4〜5 か所で繰り返す。凍結の開示の段落（140 行）が長い。189 行に数値が詰まりすぎ | 評価表 d | major | 評価表 d | — | **真**（評価の判断。約 11,100 語・26 頁） |
| F | 要旨 249 語は上限 250 語に余裕が無い（素朴な数えで 250） | nit | 評価表 e | 評価表 e | — | **真**（context-A の測った値） |
| G | 要旨と序論の「誤読の実例は見つからなかった」が §2.5 だけに頼る | M5 の注 | #1 の注 | minor | 3.4 | **真**（構成の指摘。§2.5 を書き直すときに要旨の文も範囲つきにする） |
| H | §7.3 の Hellas et al. の例: "consists mostly of submissions that passed" は逆。原典の 120,583 件・合格 56,855 件・不合格 63,728 件（依頼 1.3%）から、依頼の無い提出の約 52.5% は不合格 | — | major | nit | — | **真**（`hellas2023.txt` 858・861・863 行で 3 つの数を確かめ、算術を再現した） |
| I | 解析のコードと D2 の本文中の相談を人が確かめていない。D2 は 17 件で手で数え直せると書きながら、数え直していない。JSS の "reflects their own analysis" に照らして編集者が問題にしうる | 評価表 e | — | major | — | **真**（body 176・381、declarations 18） |

## 3. 1 人（または査読者 1 人と監査役）だけの指摘（裏取り済み）

| 指摘 | 誰 | 裏取り |
|---|---|---|
| 「unaided resolution」が、観察した単位の中の解決（定義）と最終的な解決（[A, U]・要旨の "not a loss"）の間で滑る。表 1 に第 2 の概念を足し、要旨は両面を書く | R1 major・監査役 2.2 | **真**（body 69・158・189・324、abstract） |
| 主の結論を担う 2 つのコード（DF3/DF1 と、相談のコード）に、コードごとの一致度も再コードの標本も無い。原典の κ が何の一致かを本文が書かない。単一コーダーの限界を Consultation の側にも置く | R1 major | **真**（原典の逐語は "75% for episodes and 84% for activities" だけ） |
| D2 の打ち切りの感度分析が P4TA だけ。原典は 4 件（P4TA, S3TA, S4TB, S5TA）を "within the study period" と書き、本文 127 行も NOTES.md 10 行もそう読んでいる。4 件とすると D2 の差は 0 | R3 major・監査役 3.1 | **真**（`config.json` 112 行 `"study_period_end_ids": ["P4TA"]`・body 156 行・`li2026.txt` 344 行） |
| Data availability の DOI `10.5281/zenodo.23029603` は旧い版（`submission-2026-09-29`）で、派生表・post_review・数え直しが入っていない | R3 major・監査役 2.3 | **真**（declarations 15・README 75）。S9 で新しい版の DOI に替える予定だった。いまの文は事実と合わない |
| §7.3 の "11 and 12 developers who agreed to be observed" は、D1（公開の配信の二次利用）に当たらない。§8 の倫理に、元の当事者の同意と研究利用の範囲が無い | R3 minor・監査役 2.1 | **真**（body 334・373・385） |
| 区間の読み方が節ごとに違う（不確かさの下限／開発者のばらつきの記述）。結論 390 行の区間に但し書きが無い。MacKinnon et al. の言い換え "no method is known to be reliable" は原文より強い。CV3・WCR を使わない理由が無い。クラスタの大きさの中央値と最大を書く | R3 minor・監査役 C | **真**（`mackinnon2023.txt` に "no method" の趣旨の文が無いことを grep で確かめた。§6.1 の逐語 "primarily to confirm" は在る） |
| Highlight 4 "Restricting to resolved episodes hides the gap because two differences cancel." は D1 に限らない書き方。D2 では打ち消さない（body 260） | R3 minor | **真** |
| Highlight 2 "unconsulted exceeded unaided resolution by 11.2 points" に「観察した単位の中で」も「上限」も無い | 監査役 1.4 | **真**（評価の判断） |
| 再利用する人への提言に、公表値が相談率だけのときに言えること（U だけ／U と u／2×2 表）の表が無い | R2 major | **真**（評価の判断・新しい表の提案） |
| 道具を評価する人への提言が 2 文で、時間制限の例（Shihab 2025）と結びついていない | R2 minor | **真**（評価の判断） |
| debugging の観察研究の文献が D1・D2 の原典に偏る（IDE のログで数える研究が無い） | R2 minor | **真**（refs.bib 28 件） |
| 表 1 の概念の行が指標の繰り返しで、formative と書いていない。help の範囲（AI・同僚・事前の知識）の定義が無い | R1 minor | **真** |
| 派生表から計算し直せると言うが、それを読むスクリプトが無い | R3 minor | **真**（declarations 15 "can be recomputed"・NOTES 46 "not an input to any result"） |
| 序論 21 行に "with one command" が残る（実際は `run.sh` と `paper/build.sh` の 2 つ） | 監査役 L | **真** |
| 古い言い方の残り: body 10 行の参照先が `sec:related`（`sec:search` のはず）・48 行 "resolved without help"・140 行 "the approximate effect"・README 22 行と 31–33 行の旧い名前（outcome-agnostic・numerator effect など） | 監査役 S | **真** |
| §8 の "only the direction of the difference between U and A" は、U − A が定義から 0 以上なので言い方がずれる | 監査役 3.3 | **真** |
| RQ4 の D2 の段落の末尾 "Here the omission doubles the unresolved-unconsulted share" が断定 | 監査役 I | **真**（評価の判断） |
| 要旨の D2 の「観察の終わり」がどちらのデータかを示さない／結論に D2 の「一人を除くと消える」が無い／持ち帰り 3 の後半（操作的定義・コーディングの版）が要旨と Highlights に無い | 監査役 E・C・1.2・1.3 | **真**（評価の判断） |
| nit: 表 3 の duration の行の "/" の読み方・要旨の "Its complement"・189 行の "every definition" の範囲・pp と % の揺れ・所属が都市と国だけ | R1・R2・R3 | 真（nit） |
| 監査役 R「著者が journal 版の値を PDF と照合した記録が無い」 | 監査役 | **偽陽性**: 判断 24（監査役には読ませていない）に、研究者が 8 つの値を NSF PAR の PDF と照合して一致したと記録がある |
| 監査役 2.4「生成 AI の申告に『読んで直した』を足す許可の記録が無い」 | 監査役 | **偽陽性**: 判断 24 に研究者の許可がある |

### 接地の引用の確かめ（査読者ごとに 1 件以上）

- R1: "CV requires an unambiguous" が `sjoberg2022.txt` に在る。"a single coder codes the majority" が `oconnor2020.txt` に在る。
- R2: Hellas の 3 つの数（120,583・56,855・63,728）が `hellas2023.txt` 858〜863 行に在る。
- R3: "primarily to con[firm]" が `mackinnon2023.txt` 1595 行に在る。"human validation should always be employed" が `wagner2024.txt` に在る。
- 捏造は見つからなかった。

## 4. 直す順（各 1 行・位置つき）

- **fatal**: なし。
- **major**
  1. 2 つ目の実装（A・I）: §5「Use of large language models」・§8 Reliability・`audit/independent-recount/README.md`。一致を「入力の本文に在った値」と「無かった値」に分ける。指示文が残っていないと書く。duration の span と sum を両方書く。§8 で「独立の検証」でなく「実装の誤りを見つける手段」に下げる。★ 人の確かめ（D2 の 17 件の手での数え直し・D1 の数件）をするかは研究者の判断。
  2. Hellas の例（H）: §7.3 334 行を原典の数どおりに直し、提出は単位の終わりでなく多くが再提出に続く（DF3 の型）ことを書く。
  3. D2 の打ち切り（L）: §5.4・RQ1・§8・`config.json`。★ 4 件すべてを打ち切りにした値（差 0）を足すか、P4TA だけにする理由を書くか、研究者の判断。結論と要旨の "positive in both" を観察の中の解決に限った言い方にする。
  4. 構成概念の滑り（R1）: 表 1・§5.4・§7.1・要旨。「観察した単位の中」と「最終的」の 2 つを分けて書く。"not a loss" を両面に。
  5. Data availability の DOI（K）: S9 で新しい版の DOI に替える（すでに予定）。それまでは文に「改訂版の DOI は投稿の前に入れる」の印を付けるか、S9 の作業の順で必ず替える。
  6. 長さと繰り返し（E）: 但し書きを方法の節で 1 回にし、結果と考察は参照にする。凍結の開示を短くし、詳細は NOTES へ。★ どこまで削るか（R2 の目安は 8,000 語）は研究者の判断。
- **minor**: 要旨の 3.5 の言い方（D）と語数の余裕（F）・最後の DF3 の理屈（B）・duration と順序の定義（C）・"agreed to be observed" と倫理・区間の読み方と MacKinnon の言い換え・クラスタの大きさの中央値と最大・Highlight 4 と Highlight 2 の限定・κ が何の一致かと単一コーダーの限界を Consultation にも・表 1 の formative と help の範囲・派生表を読むスクリプトか「手で」・"with one command"・古い言い方の残り（sec:related・"resolved without help"・"effect"・README の旧い名前）・§8 の "direction"・"doubles" の断定・要旨の D2 と持ち帰り 3・再利用する人の表（R2）・道具を評価する人の提言・debugging のログ研究の文献。
- **nit**: 表 3 の duration の行・"Its complement"・"every definition" の範囲・pp と %・所属の書き方。
- **§2.5 と一緒に直す**: G（要旨と序論の「実例は見つからなかった」に検索の範囲を付ける）。

## 5. 意図の監査役

- **意図にあって対象物に無いもの**: 持ち帰り 2（A\|R は差を解消しない）が要旨に警告として無い／持ち帰り 3 の後半が要旨と Highlights に無い／D2 の限界（一人を除くと消える）が要旨と結論に無い／Highlight 2 に但し書きが無い。
- **対象物にあって意図に無いもの（漂流）**: "agreed to be observed"／要旨の "not a loss" が意図（上限として読む）より強い／旧い DOI。
- **矛盾**: D2 の打ち切りの集合（P4TA だけ 対 4 件）／2 つ目の実装に渡した本文と順序の規則／§8 の "direction"。
- 監査役の 2 件（R・2.4）は判断 24 で解決済み（偽陽性）。context-B に判断 24 を入れなかったのはメインの漏れ（round 3 では入れる）。

## 6. 逸脱・失敗・注入の疑い

- 失敗した役: なし（4 本とも締切の内に返った: R2 約 3 分・監査役 約 4 分・R1 約 4 分・R3 約 6 分）。
- 注入の疑い: なし（4 本とも）。
- 保存の検査: `secrets-filter.sh` は 4 本とも 0。一覧の外の絶対パスは 4 本とも 0。
- 依頼の渡し方: 依頼文の本文を Agent の prompt に貼らず、「最初にこのファイルを Read せよ」として `brief-*.md` の絶対パスを渡した（4 本とも依頼文を読んで従ったことを応答の「読んだもの」で確かめた）。
- 起動の前に知らせたこと: この機械に Zenodo のトークンと age の鍵があること（査読者役の道具は Read・Grep・Glob だけ。応答のパスは機械で検査した）。
- Codex（5 人目）は加えていない（既定）。

## 7. 研究者に問うこと

1. 直す一覧（§4）の承認。
2. 2 つ目の実装と人の確かめ: (a) 文を直すだけ（一致を 2 つに分け、§8 で格を下げる）、(b) それに加えて研究者が D2 の 17 件を手で数え直す、(c) さらに D1 の数件を研究者が確かめる。
3. D2 の打ち切り: (a) 4 件すべてを打ち切りにした値（差 0）を足す、(b) P4TA だけの理由を書く。
4. 長さ: どこまで削るか（但し書きの重複を消すだけ／8,000 語前後まで削る）。
5. 新しく足すかどうか: 再利用する人の表（R2）・debugging のログ研究の文献（R2）・CV3 か WCR の区間（R3）・D1 の標本の再コード（R1）。
