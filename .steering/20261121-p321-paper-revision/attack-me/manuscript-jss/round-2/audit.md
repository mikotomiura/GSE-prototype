# audit — 意図の監査役の応答（attack-me・stage manuscript・round 2・JSS）

> メインが応答の本文を写した。機械の検査（secrets-filter・一覧の外のパス）を通してから追跡されるファイルにした。

注記: round 2 の意図の監査の結果です（stage manuscript）。行番号は元のファイルの番号で、読んだのは `*.resolved.tex` です（行番号は元と同じ）。

# 0. 引き継ぎの判定（carryover-audit）

19 件のうち、解消 12 件（B, D, F, G, J, K, M, N, O, P, Q, H）、部分的に解消 5 件（A, C, E, I, L）、小さなものの S は部分的に解消、確かめられない 1 件（R）です。主なものは次のとおりです。

- **A 部分的に解消**: 向きは直っています。abstract.tex:1 "restricting to resolved episodes raised the measure by only 3.5 points, because two opposite differences largely cancelled"。
  - 残る問題: 要旨は A と A|R を定義した直後なので、"the measure" は A から A|R への変化とも読めます。その場合の差は +14.8 です。
  - "only 3.5" は、§7.2（body:328）が誤りとして退けている推論 "which might suggest that the outcome hardly matters" を後押しする言い方です。
  - 要旨には、持ち帰り 2 の「A|R はこの差を解消しない」が警告の形で書かれていません。Highlight 8（highlights:8 "hides the gap"）には書かれています。
- **B 解消**: body:140 "one measure was renamed and the denominator difference, with its interval, was added"。NOTES.md の Deviation 1 と、7 件という数も合っています。
- **C 部分的に解消**: 要旨からは区間が外れました。本文の限界は §8（body:377）に書かれています。
  - 残る問題: 結論の body:390 "(developer-level bootstrap interval [6.8, 15.7])" には限界が添えられていません。§5.2 の "likely to be too narrow" や、§8 の "none of these intervals is an interval for developers in general" が結論に届いていません。
  - D2 の「一人を除くと消える」（既知の限界）も、結論と要旨にありません。
- **E 部分的に解消**: 要旨の "and in one of them when observation ends" は、どちらのデータの話かを示していません。D2 の値（"In 17 tasks…11.8 points"）とも結びついておらず、2 つの値を比べないという但し書きも要旨にありません。
- **H 解消**: body:350 "under any of the four definitions we examined"。RQ4（body:288）の "under any definition" も、文脈から 4 定義の範囲と読めます。
- **I 部分的に解消**: body:317 は "may undercount… best read as a lower bound" と弱めて §8（body:363）と合いました。
  - ただし同じ段落の末尾は "Here the omission doubles the unresolved-unconsulted share" と、取りこぼしを断定しています。
- **L 部分的に解消**: Data availability（declarations:15）と README からは「1 コマンド」が消えています。
  - 序論の貢献 body:21 には "a replication package that recomputes the results and rebuilds this manuscript from them with one command once the D1 coding has been downloaded" が残っています。
  - 実際には `run.sh` と `paper/build.sh` の 2 つです（README:53・69）。grep で、`run.sh` は `build.sh` を呼ばず、`build.sh` も `run.sh`／`analyze` を呼ばないことを確かめました。
  - `build.sh` は初回にネットワークから TeX のパッケージを取ります（README:69）。
- **M 解消**: RQ1 body:189 "Relative to resolution within the observed episode it is a shortfall; relative to eventual resolution it is an upper bound"、§5.4（body:158）、§8（body:365）がそろっています。
- **Q 解消**: body:140 の (2) "While identifying which rule might produce the journal version's figures for D1 (RQ4), we computed U and A once…"。
- **R この版では確かめられない**: body:150 は "the author compared each of them with the PDF (2026-11-21)" と書いています。
  - 判断 19 は「研究者はまだ PDF と照合していない（S7 で照合すれば書き換える）」で、判断 21・22 にも、journal 版の値を著者が照合した記録はありません。
  - context-B の既知の限界で「著者が PDF と照合」とあるのは D2 の転記だけです。
  - 記録は、読む許可の無い判断 23・24 にあるのかもしれません。投稿の前に記録を確かめてください。
- **S 部分的に解消**: 残っているのは次のとおりです。
  - body:10 "within the literature search described in Sect.~\ref{sec:related}"。参照先は sec:search が正しいはずです。
  - body:48 "a valid operationalisation of ``resolved without help''"。判断 17 は語を unaided resolution にそろえると決めています。
  - body:140 "the approximate effect of adding"。判断 17 は差を "effect" と呼ばないと決めています。
  - README:22 "an **outcome-agnostic** measure… **resolution-conditional** measure" と、README:31–33 の "numerator effect / denominator-only effect / conditioning effect"。公開物の文が古い名前のままで、原稿の名前と合っていません。metrics.json のキー名を残すことは判断 17 で認められていますが、README の散文はその対象ではありません。
- **D, F, G, J, K, N, O, P 解消**（要点だけ）:
  - D: 2×2 表が body:219–232 に置かれ、§7.4 は受け手別に分かれ、要旨に読み手が入りました。
  - F: body:8 "Its aim is preventive"。
  - G: 題は main-jss.tex:48。
  - J: body:260 は算術を述べるだけです。
  - K: body:21 "an accounting identity, not a finding"。
  - N: body:328 "small whenever few units end unresolved"。
  - O: NOTES:10 と body:127 が一致しています。
  - P: README:74 と data/li-coblenz-2026/README:12 が一致しています。

# 1. 意図にあって対象物に無いもの

1. **持ち帰り 2 が要旨にありません**（A の残り）。abstract:1 "raised the measure by only 3.5 points" は「この補正では差が消えない」を言っていません。
2. **持ち帰り 3 の後半が要旨と Highlights にありません**。要旨の推奨は abstract:1 "we recommend reporting outcome by consultation with the reasons units ended" だけです。相談と解決の操作的定義、どの版のコーディングで数えたかが入っていません。Highlight 9 も 2×2 表だけです。本文（body:342）と結論（body:390 "which coding and which rule"）にはあります。
3. **D2 の既知の限界（一人を除くと消える・0 にかかる）が要旨にありません**。要旨は "resting on 2 and 1 tasks" で止まっています。結論は "with intervals starting at 0" を書きますが、一人を除いた結果は書いていません。
4. **Highlight 6 には但し書きがありません**。highlights:6 "unconsulted exceeded unaided resolution by 11.2 points" には「観察した単位の中で」も「上限」もありません。Highlight 7 と合わせれば補えますが、1 本だけ引用されると持ち帰り 1 の「上限として読む」が落ちます。

# 2. 対象物にあって意図に無いもの（漂流・範囲を超えた言い方）

1. **§7.3 の外部妥当性の言い方**（重点の箇所）: body:334 "in our data they rest on 11 and 12 developers who agreed to be observed"。
   - D1 は、公開の配信を二次利用したデータです。§8 は body:373 "11 developers who chose to stream their open source work" と書いています。
   - D1 のプレプリント（alaboudi2021.txt）を grep した範囲では、同意（consent）の記述はありません。
   - D2 の原典で同意の記述があるのは参加者だけです（li2026.txt:146・151 "we obtained consent" / "obtained informed consent"）。配信者 5 名の記述は見つかりませんでした。
   - "agreed to be observed" は、§8 とも原典とも食い違います。
2. **要旨と議論の "not a loss" が、意図より強い言い方です**。
   - abstract:1 "it is the width of the range of unaided resolution, not a loss"、body:324 "not as an amount of lost resolution"。
   - 本文の RQ1（body:189）は両面を書いています: "Relative to resolution within the observed episode it is a shortfall; relative to eventual resolution it is an upper bound"。
   - 要旨は片面だけです。10 件には DF2（mostly fixed）と DF5 の 2 件も含まれ、これらは「後で戻る」ではありません。
   - 意図（持ち帰り 1）は「最終的な解決に対しては上限として読む」で、「損失ではない」とまでは言っていません。
3. **Data availability の版**: declarations:15 は "all results are part of the replication package… archived at \url{https://doi.org/10.5281/zenodo.23029603}" と書いています。README:75 のとおり、これは `submission-2026-09-29`（EMSE 版）の DOI です。
   - その版には、改訂で足したもの（`post_review`、`results/d1_episodes.csv`、`audit/independent-recount/`）が入っていないはずです。
   - requirement.md は「改訂版の再現一式は新しいタグと Zenodo の新しい版で出し」「Zenodo 23029603 の書き換え（EMSE 版として残す）」は含まないと書いています。
   - 投稿の前に差し替える予定（判断 20 の S9）だとしても、いまの文は事実と合いません。
4. **生成 AI の申告**: declarations:18 "After using this tool, the author reviewed and edited the manuscript as needed" が入っています。
   - 判断 21 は「『読んで直した』の文を足してよいかは、改訂の後に改めて研究者に聞く（まだ聞いていない）」、判断 22 の残りも同じです。
   - 読める範囲の意図には、この文を足す許可の記録がありません（判断 24 にあるのかもしれません。読んでいません）。

# 3. 矛盾

1. **D2 で打ち切りとして除く範囲が、自分で引いた逐語と合いません**（重点）。
   - body:156 は "in D2, the task that ended with the study period (P4TA, a participant's task; for the streamers' tasks the paper does not say which ended with the stream)" と書き、P4TA だけを除いています。
   - ところが body:127 が引く原典は "participants did not resolve the task within the study period (P4TA, S3TA, S4TB, S5TA)" で、4 件すべてです。
   - NOTES:10 は、まさにこの点を "(An earlier version of this note named P4TA only.)" と直しています。
   - body:193 "Removing the task that ended with the study period (P4TA) gives 6.2 and 0.0" と、§8 の body:365 "treat… the end of D2's study period as censoring" は、終わり方の扱いを 4 件の逐語と食い違う形で狭めています。
   - 打ち切りを P4TA だけにする理由（逐語の読み方）を明記するか、4 件で揃えるかのどちらかが要ります。
2. **2 つ目の実装と、原稿が述べる順序**: audit/independent-recount/README:20 は "The analysis's ordering by time is the one the manuscript describes" と書いています。
   - しかし 2 つ目の実装に渡したのは §4.1 です。§4.1（body:115 "the most recent interrupted episode of the same session"）と §5.4（body:158 "the last debugging episode of its session"）は、「最後」を時刻の順で決めると明示していません。
   - 食い違いの原因は、仕様の書き漏れとも読めます。body:176 の "It differed in one count" の説明は、この点に触れていません。
3. **§8 の "direction"**: body:361 "only the direction of the difference between U and A within each"。
   - U − A は定義から 0 以上で（body:76・146 "which a single unresolved, unconsulted unit already shows"）、比べる「向き」はありません。
   - body:195・373 の "positive in both" と合わせると、向きが結果であるかのように読めます。意図（持ち帰り 1 の「定義から 0 以上であり、…両方で正だった」）とも、言い方がずれています。
4. **序論が §2.5 に頼っている箇所**（構成の指摘だけで、§2.5 の中身は見ていません）。
   - abstract:1 "We found no published instance of the misreading" は、検索の範囲の限定を付けずに言い切っています。
   - body:8 と body:10 も、この節を根拠にしています。
   - §2.5 を書き直すと、要旨のこの 1 文も見直しが要ります。

# 4. 位置と逐語

各項目に書きました。

# 5. 読んでいない範囲と注入の疑い

- **読んだもの**:
  - body / abstract / highlights / declarations の resolved 版の全体。
  - main-jss.tex の題とキーワード。
  - NOTES.md の全体、README.md の 1–80 行、audit/independent-recount/README.md、data/li-coblenz-2026/README.md（grep だけ）。
  - context-B、requirement.md、decisions.md の判断 2・3・17–22（判断 1・4–16・23・24 は読んでいません）。
- **読んでいないもの**:
  - 再現一式のファイル: results.tex、results/ の全部（metrics.json、report.md、provenance.txt、d1_episodes.csv）、refs.bib、jss-preview.txt、DATA.md、ENV.md、config.json、SEED、analysis/*.py、recount.py、output.txt、make_results.py、check_frontmatter.py、CSV の 3 本。
  - README.md の 81 行目以降と、design.md §4（任意の資料）。
  - 原典は grep しただけで（同意の語・選択的なコーディング）、精読していません。
- **数値の確かめ**: 本文の数値は results.tex と照らしていません。確かめたのは本文の中の算術だけです（8/89 = 9.0、DF3 を解決に数えると (60+8)/89 = 76.4、2/10 = 20%、[5.9, 16.6] が [6.8, 15.7] より広いこと）。
- **§2.5（body:52–58）**: 指示に従い、中身を指摘の対象にしていません。
- **注入の疑い**: 見つかりませんでした。
