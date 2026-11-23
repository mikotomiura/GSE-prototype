# review-R3（round 2・paper-reviewer・opus）
接地: Wicherts ら "a specific, precise, and exhaustive plan"・"the word "only" is key"・"clearly distinguish between these very different types of analyses"・"the evidence should be seen in the context of the size and breadth of the explorations"。Lakens "based on the smallest effect size of interest"・"(Scenario D) when the 90% CI includes one of the equivalence bounds"。
carryover: 1 一部（帯が 139 人の登録より前に凍結なら外れうる検定で「確認」と矛盾・M2）／2 一部（KLiCKe・CoAuthor に区間が無い・m1）／3 解消（面の名前と食い違い・M3）／4 一部（M3）／5 解消（割付で何を測るか・m3）／6 解消（読みに新しい穴・M4）／7 一部（m2）／8 一部（漏れの系譜・m4）／9〜13 解消。
評価: a3 b3 c3 d4 e4 f3。
- [major] M1 尖りの「同じ観測の上で測る」が材料（公開データの打鍵の記録と自前のロガーの合成入力）と合わない。解消: 「同じ種類の観測の上で、別々のデータで」か、1 つのデータに 3 検査を当てることを §4 の今後に。自信 高。
- [major] M2 帯の根拠（SESOI）と、登録で凍結したもの（帯・主の信号・90% か 95% か）が書かれていない。学習器が 0.55 付近なので帯の幅で面の割り当てが変わる。解消: 帯の幅の根拠を 1 文・登録に入ったものと入っていないものを 1 行で分ける・凍結の時点で「確認」か「検定」かを書き直す。自信 中。
- [major] M3 「読めない所」「読める所は今は無い」が学習器の結果より強い（検査の列は「観測の量」を問うのに根拠は推定器 1 つ）。解消: 「この推定器では読めない／観測としては未決（探索では弱い信号）」に分ける。自信 高。
- [major] M4 定義しだいの所の材料に、長さで調整すると負の定義が消える（＝長さの交絡とも読める）結果が入っているのに、どちらの読みを採るか・何通りのうち何通りかが無い。解消: 調整の前後で正・負・不定の数・「調整のありなしという分析の選択で向きが動く」か「調整後は残る」かを 1 文で。自信 中。
- [minor] m1 KLiCKe・CoAuthor に区間と帯の判定が無い。CS1 の上端 0.4995 は 0.5 を外す（偶然をわずかに下回るが帯の内）。自信 高。
- [minor] m2 n=3 の判定の規則が無い（凍結の時に決める・今は草案、と 1 句）。自信 中。
- [minor] m3 無作為の割付で何を測るか。自信 中。
- [minor] m4 漏れの先行に、打鍵の列や時刻から内容を推す攻撃の系譜が無い。自信 中。
- [nit] n1 3 検査と 4 つ目の検査の数え方。「対応」を道具の範囲の外と明記するか 4 検査にそろえる。自信 高。
総合: major（書き直しで消せる）。
読めなかった範囲: 接地は検索での抜き出し・§7 のパス。注入の疑いは無い。
