# carryover-R3 — あなた（R3）の round 1 の指摘と、その後（attack-me・stage `manuscript`・round 2）

round 1 で読んだのは、同じ論文の前の版（EMSE に投稿した版）である。行番号は前の版のもので、いまの原稿とは合わない。いまの原稿では、下の「対応」に書いた節を探して判定すること。
round 1 の総合の推奨: major。

⚠️ この round での変更: 出し先が EMSE から JSS に替わった（規程は context-A の JSS の抜粋で見る）。接地の文献のうち、ブートストラップの教育の文献（Hesterberg 2015）を、クラスタが少ないときのクラスタ頑健な推論の文献（MacKinnon, Nielsen & Webb 2023）に替えた。改訂の原稿が補助の区間として CR2・Bell–McCaffrey を足したためである。

判定のしかた: 各指摘について「解消 / 部分的に解消 / 未解消 / この版では確かめられない」と理由（いまの原稿の位置と逐語）を書く。再掲は求めない。

| # | round 1 の指摘（要約） | 裏取り | 研究者の採否 | 著者の対応（いまの原稿で見る場所） |
|---|---|---|---|---|
| major | DF3 と「観察の終わり」を未解決に数えていて、最も効く選択が 8 つの定義の外にある | 真 | 採る（主の定義は変えず、打ち切りとしての感度分析と区間 [A, U] を足す） | §5.4 Analyses added after the first version ／ RQ1 の "How much of the difference rests on DF3" ／ §8 Internal validity ／ 要旨と結論の言い方 |
| major | 11・12 クラスタでのパーセンタイル区間と、符号が構成で決まる量についての「0 を含まない」 | 真 | 採る（主の区間は凍結のまま・補助の区間を文献で確かめてから足す・「0 を含まない」を検定として書かない） | §5.2 Estimation and intervals ／ §5.4 Clusters（k・開発者ごとの分布・CR2 と Bell–McCaffrey の自由度）／ RQ1（CR2 の区間・D2 で下限が 0 を下回るのは近似の性質と書いた・leave-one-developer-out）／ §8 Statistical conclusion validity |
| major | RQ4（公表済みの数値が再現できないという主張）の検証が足りない | 真 | 採る（原著者に照会する・返事を待たずに出す） | RQ4: 表を「構造の確かめ」と「相談の統計の再現」に分けた ／ short = 22 件の根拠 ／ 報告値どうしの算術（22/89 = 24.7% と 33%）／ 著者が journal 版の値を PDF と照合した ／ 照会は 2026-11-21 に送り投稿の時点で返事が無い ／ 言い切りを検討した 4 つの定義の範囲に絞った |
| major | LLM の利用の記録が Wagner et al. の最低線に届かない | 真 | 採る | §5 の小節 "Use of large language models"（モデルと版・日付・各インスタンスに渡したもの・指示文を一式として保存していないこと・本文の相談の拾い出しの再現率は不明・著者は解析のコードを読んでいない）／ 文献表の前の生成 AI の申告（`declarations.tex`） |
| major | 誤読が実際に起きている証拠が無く、動機が藁人形に近い | 真 | 採る（探して、無ければ主張を予防的な報告の推奨に絞る） | 実例は見つからなかった → 主張を絞った（序論）。⚠️ 検索の範囲を書く §2.5 は、記録付きの検索のやり直しの途中で**この round の対象外**。序論と §7 の主張の強さだけを見ること |
| major | D1 の入力がアーカイブに置かれず、再現一式の主張が私的なリンクに依る | 真 | 採る（元データの CC BY 4.0 を一次で確かめた上で、派生表をアーカイブに入れる） | `results/d1_episodes.csv`（`analysis/derived.py`・名前と URL を含まない）／ `DATA.md` ／ Data availability ／ "every number … one command" の言い方を消した |
| minor | 再現一式に「結果の前に凍結した」という記述が残る | 真 | 採る | `config.json` の `_comment`・`analyze.py` の docstring・`NOTES.md` |
| minor | 合わせ込みの的が「検査」に数えられている | 真 | 採る | §4.1 の段落 "Episodes"（"These figures were targets as well as checks" ―― 抽出の規則を決めるのに使った統計と、検査として数えられるものを分けて書いた） |
| minor | 二次データの倫理を「該当なし」で済ませている | 真 | 採る | §8 Ethics of the secondary analysis |
| minor | 声明の置き場所（EMSE の規程） | 真 | 出し先が替わったので JSS の形にした | `declarations.tex` |
| minor | 先行研究の欠け（部分識別・クラスタが少ないときの推論など） | 真 | 採る | §2.3（打ち切り・競合する事象・部分識別）／ 引用に Imbens & Kolesár 2016・MacKinnon et al. 2023・Manski 2003 などを足した |
| minor | 言い過ぎの細部 | 真 | 採る | 本文の各所 |
| nit | D2 の版が本文に無い | 真 | 採る | §4.2 |
| nit | 名前 | 真 | 採る | U・A・A\|R |

round 1 の後に著者が足したもの（新しい穴が無いかを見る）: 凍結の後に足した解析をすべて `results` の `post_review` の下に出し、凍結した部分と提出版の `metrics.json` の不変をハッシュで検査する仕組み（`analysis/analyze.py`・`NOTES.md` の Deviations 8〜11）／ b/(a+b) ／ leave-one-developer-out ／ D1 の 2 つ目の実装による数え直し（`audit/independent-recount/`。同じ種類の LLM の別のインスタンスが、原稿の記述とコードブックだけから書いた）／ 本文の質的な文を検査する `paper/make_results.py` と、要旨・Highlights・声明を検査する `paper/check_frontmatter.py`。
