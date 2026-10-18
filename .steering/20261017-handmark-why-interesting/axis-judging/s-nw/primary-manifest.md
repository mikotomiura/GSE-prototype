# 一次テキストの来歴（2026-10-18）

- 一次テキストの本体（pdftotext の抽出・抄録の逐語）は著作物なので repo に入れない。置き場は作業時の scratchpad（`/private/tmp/claude-501/-Users-johnd-GSE-prototype/f99bdc93-3f93-41b7-863c-4ad0bd1f8194/scratchpad/survey/primary/`）で、セッションの後は消える。claims.md の「一次テキスト」の列はこの抽出のファイル名と行番号を指す。
- ファイルごとの取得先（2026-10-18・`/cross-review` 2 巡目の Codex の指摘で作った）。探索役が URL を記録しなかったものは「記録なし」と書いた。取り直すときは DOI から原本を取り、下の SHA-256 で同じ抽出かを確かめる。版が違えば行番号も変わるので、claims.md の行番号は逐語の引用で引き直す。
- 抽出の手段: PDF は `pdftotext`（poppler 26.04.0・オプションなし）。HTML は探索役がテキストにしたが、手段は記録されていない。原本のハッシュは取っていない（原本の PDF は scratchpad に一部しか残っていない）。

| 抽出ファイル | ID | DOI | 取得先 | 抽出 |
|---|---|---|---|---|
| ishii-1998.txt | [P534] | 10.1145/286498.286652 | 記録なし（探索役は「MIT Media Lab publications の PDF」とだけ記録） | PDF→pdftotext |
| marti-2001.txt | [P535] | — | 記録なし | PDF→pdftotext |
| focusbuddy-2026.txt | [P536] | arXiv:2609.00412 | https://arxiv.org/abs/2609.00412（の PDF） | PDF→pdftotext |
| epstein-2016.txt | [P537] | 10.1145/2971648.2971656 | https://homes.cs.washington.edu/~jfogarty/publications/ubicomp2016.pdf | PDF→pdftotext |
| mekler-2017.txt | [P538] | 10.1016/j.chb.2015.08.048 | https://glassmanlab.seas.harvard.edu/annotated_works/mekler17.pdf | PDF→pdftotext |
| ahn-2024.txt | [P539] | 10.1038/s41746-024-01133-5 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11109260/ | HTML→テキスト（探索役の手段・未記録） |
| alt-2010.txt | [P540] | 10.1109/PERCOMW.2010.5470542 | 記録なし | PDF→pdftotext |
| skog-2003.txt | [P541] | 10.1109/INFVIS.2003.1249031 | 記録なし（[P112] の URL の PDF と同じ版かは未照合） | PDF→pdftotext（OCR の崩れあり） |
| vogel-2004.txt | [P542] | 10.1145/1029632.1029656 | 記録なし | PDF→pdftotext |
| hudson-1996.txt | [P543] | 10.1145/240080.240295 | 記録なし | PDF→pdftotext |
| prpa-2018-respire.txt | [P544] | 10.1145/3170427.3180282 | 記録なし（探索役は metacreation.net の PDF と記録・完全な URL なし） | PDF→pdftotext |
| prpa-2018-attending.txt | [P545] | 10.1145/3196709.3196765 | 記録なし | PDF→pdftotext |
| ishii-1997.txt | [P546] | 10.1145/258549.258715 | https://arl.human.cornell.edu/879Readings/HiroshiIshii_Tangible%20Bits.pdf | PDF→pdftotext |
| wisneski-1998.txt | [P547] | 10.1007/3-540-69706-3_4 | https://dam-prod.media.mit.edu/x/files/publishedmedia/Papers/314-Ambient%20Displays%20Turning%20Architectural/Published/PDF | PDF→pdftotext |
| weiser-1996.txt（ファイル名の年は依頼時の仮のもの・書誌は 1995-12-21） | [P548] | — | https://calmtech.com/papers/designing-calm-technology | HTML→テキスト（探索役の手段・未記録） |
| shelton-2017-abstract.txt | [P549・P550] | 10.22496/atct20161230121・10.1145/3014812.3014821 | OpenAlex の abstract_inverted_index から復元 | API→復元 |
| pratt-2010.txt | [P551] | 10.1177/0956797610387440 | https://www.psychologicalscience.org/journals/psychological-science/0956797610387440/ | 抄録の写し |
| volk-1994.txt | [P552] | 10.2466/pms.1994.79.3f.1632 | https://soar.wichita.edu/items/51253e0a-55b4-4ab3-8aa7-293768025c4b | 抄録の写し |
| eich-2023.txt | [P553] | 10.3758/s13414-023-02749-7 | 記録なし（txt の冒頭は DOI のみ） | PDF→pdftotext |
| morrison-smith-2021.txt | [P554] | 10.20380/GI2021.04 | 記録なし（探索役は graphicsinterface.org の PDF と記録） | PDF→pdftotext |
| consolvo-2008.txt | [P100（既登録）] | 10.1145/1357054.1357335 | 記録なし | PDF→pdftotext |
- 検証の規約: 枝 `docs/literature-review-vote-rule` のコミット `41411a8994dce85e5623fdbe9ed15736d402dfe0` の `.claude/commands/literature-review.md` Step 4・Step 5 と `.claude/agents/evidence-axis-judge.md`。
- 取り直したときの照合用に、抽出ファイルの SHA-256 を残す（同じ版・同じ抽出の手段なら一致する）。

```
fb6256736be42dabe36aab180408fbf1b45f7e02b508bd127595ad6a3a8de503  ahn-2024-abstract.txt
a5446291e89bd95421c48897fd34a7c21ef6765085f5f763d489c6fef7060c8a  ahn-2024.txt
d92e66f18b63d6740dd52887d4fb2a3769e00197e009f912ddf7f30552f21c06  alt-2010.txt
8d5155d358739ac65dea5becf737ba58a4fccbccd918431e99ed21437d1d6698  consolvo-2008.txt
7a07efbbf98975531491f99e53654ac5ec6a7e92e16491130ee5764eded0c4b8  eich-2023.txt
b3eb6be6296f0cfaaeab1a4da9c9c080a966a864aeb26c2c7a0de3f227b3253d  epstein-2016.txt
c9f585692a94bf7b07766cc19b84cdc8f9db2b5ec56c2e1682d14c89f935f14f  focusbuddy-2026.txt
335347ea7898db61749b2c5268d44ba53df5eb3ea804d9ca092ae08cd561259e  hanus-2015-secondary.txt
33269066e5cb192bed5168abf3a87dcc9a4e3f99add135f051c0ab7315ca6c48  hudson-1996.txt
f1994d49262a1347241d5e3b6ffc1d25d7aa7578f9bc76cf718f795bcc15a48e  ishii-1997.txt
c23ffdebb2ad2581139f23b4278042750e6fae39fb3199a615c523cb27890c31  ishii-1998.txt
5278649fdcc2dfe2f541cb59dd2de0495a56adc1289d5cc244bad2cbd1a6f432  lewandowska-2022.txt
378fd66a5e72858cc2583b9c5e805fc7dae7b6b84fde0448d244102b8209b3d1  lin-2006-abstract.txt
5939303e8535141154fa9017a9088f398c9eaf060348e2b9d9d049d71b2caad7  liu-2021.txt
6cdd0d9ca54ba7ce49c5639db17cfebc6c79026733cd8b1722fdef91f5ec3c07  marti-2001.txt
cf7bef34ef35f7ab506415e2d4bc82fdc2f7834086e8dae123069a3ea61d1e2c  mekler-2017.txt
fb3eafd70e75e7c946b9662accc5b39da7b4e944e7149e7ebd751726bd5505c8  morrison-smith-2021.txt
07a78346648bfee65d6b509bac8156bcab644f260820f31e9069eda6aabf3dda  omran-2016.txt
d81a6bd19c904686249490cd27ab14b3d1889d747eb469847c55fdf404a069fd  plaue-2007-bluegoo-page.txt
d3b4370488ab5fabdcc5003f1bad569dfc2d08a635066613d5921418cb9ac216  pratt-2010.txt
98e43b2d6474e4c759de9fd95be0090582d78b68b6aad8ce1bed4abe6252b9a1  prpa-2018-attending.txt
1be37397799fbac78e450b9afedea62af255db51d801b57f2024208ad762cd65  prpa-2018-respire.txt
1653baca079fd5a6d54fea22bb9037fc984e3fbe52130107ea19857fe5a02115  shelton-2017-abstract.txt
f3872ed43f4a23091a5de2deee7c1ad6d35c1fc05092bd928d16bfb622b7d024  skog-2003.txt
f4bdb27a7e560483db1ae6f105b89ad33d5d08091bab0b17831dd7bb678e9073  snyder-2015.txt
6c5327cbf4fecfba9486d35814676a87b0f55ddecea137fae0d81e3846690cd8  unknown-2023-pmc.txt
b55e390dd9a2050436e1e11b6bc1f307972625fb4f1e6df0f8340dfe687293b2  vogel-2004.txt
62c11ec9f39a21cb2170b6ab342147b15dd2c1bd4ef5d9bae4afdafa556def5a  volk-1994.txt
6a0493d6e297544dbb9b9e3a8baa11bf5abe955d6aa2ae6192610d634ddb37cd  weiser-1996.txt
17c5bb9d765f176091cde8fdd2760c3b78210689cc4c4662ac65e7dc5043c2df  wisneski-1998.txt
```
