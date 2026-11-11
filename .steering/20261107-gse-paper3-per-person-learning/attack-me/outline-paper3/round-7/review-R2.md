# R2（UMUAI・個人化した行動モデルの実務家）round 7・commit 12e46857

## 1. 接地
- Saeb 2017「The definition of independence, however, depends on the use-case scenario.」
- Saeb 2017「While the subject-wise method mirrors the clinically relevant use-case scenario of diagnosis in newly recruited subjects, the record-wise strategy has no such interpretation.」
- Saeb 2017「record-wise CV often massively overestimates the prediction accuracy of the algorithms.」
- Aalbers 2023「These MAE scores are compared with a person-specific baseline based on the person-specific average level of stress in the participant's train data (ie, first 80%) rather than all their data to prevent data leakage from train to test data.」
- Aalbers 2023「However, these models are not highly accurate, as they often do not outperform a person-specific baseline.」

## 2. 評価表
a 4（推奨は評価した手順にそろった。4.3 の補足の陰性対照の比べと 4.4 の「平滑の差と同じ大きさ」が逆を向くおそれ・指摘 1）／b 3（CS1 の合成で選ばれた tau（10^6）が実データ（共有そのもの）と食い違う・指摘 2）／c 3（「平滑を弱めれば同じだけ得られる」と読まれたとき、その版が 2/17 人に確率 0 を与えることが Take-home に無い・指摘 3）／d 3（3688 → 4001 語・4.3 に数値 10 種以上）／e 4／f 4（Uto 2020 の評価設計は未確認）。

## 3. 引き継ぎの判定
1 解消（7 行「a shared model whose structure and shrinkage are chosen on other people」・49 行「extensions not evaluated here」・12 行）／2 一部（55 行の Table 2 の列に tau が無い）／3 解消（19 行）／4 解消（13・64 行）／5 解消（README 75〜80 行「cannot yet be repeated by readers; per-record hashes ... are planned」）／6 一部のまま／7 予定として妥当。

## 4. 新しい指摘
- [major] 陰性対照の比べと 4.4 の「平滑の差」の読みが逆を向くおそれ
  - 位置と引用: 47 行「the detection rule (defined across seeds and not applied to the one real panel; the real remainder exceeds the largest negative-control median)」・48 行の見出し「The remainder is of the size of the shared model's smoothing gap」
  - なぜ問題か: 陰性対照（差を植えていない合成）の中央値の最大より実データの残りが大きいなら、同じ平滑の共有モデルでも差の無い筆者からは実データほどの残りは出ない、と読め、4.4 と緊張する。合成で平滑の差の大きさが実データと同じかは外枠から分からない。この比べが補足の括弧書きに留まり、主張に有利な証拠だけが本文にあると受け取られる（Saeb「record-wise CV often massively overestimates the prediction accuracy」）。
  - 解消の条件: 4.3 か 4.4 の本文に 1 文（実データの残りと陰性対照の比べ・合成の prior mode と共有の差が実データと同じ大きさか・規則を 1 枠に当てない理由）。両立するか、しないなら Section 6 に。
  - 自信: 中
- [minor] CS1 の合成で選ばれた tau が実データと食い違う（47 行「and from 1e-3 in CS1 (where tau = 10^6 was chosen for every writer)」・14 行「under the protocol the shared model itself is chosen for every writer」）。合成が休止の秒（約 72%）を写していないおそれ。解消: 合成の CS1 の陰性対照で何が選ばれたかを書き、CS1 の感度を実データの解釈に使うかを 1 文で決める。自信: 中
- [minor] Take-home の「平滑を弱めた共有モデル」が使えない版であることが抜けている（7 行「what remains in the 15-session panel is about as large as what a less-smoothed version of the shared model gains without any of the person's data」・48 行「although it gives zero probability to the held-out data of 2 of 17 writers」）。解消: Take-home・要旨・結論に句（例「(a diagnostic, not a usable model: it assigns zero probability to some writers' data)」）。自信: 高
- [minor] 30 セッションの枠で共有モデルに対する残りが本文に無い（47 行・48 行「+5.4e-4 at k = 30 in the 30-session panel (7 of 9 ...)」・21 行の LiKamWa の約 30 日）。解消: 4.3 に k = 30 の本人 − 共有と正の数を 1 句、または置かない理由。自信: 中
- [nit] 使う場面の文が個人の訓練データを落とす（25 行「Use case: predicting a new person's later sessions with a shared model fitted before that person arrived.」）。解消: 「after observing the person's first k units」。自信: 高
- [nit] Table 2 の列の書き方（55 行）。解消: 列に「chosen structure and tau」。自信: 高

## 5. 総合の推奨: minor
引き継ぎの major は解消し、主張・推奨・限界がそろった。一番大きい懸念は陰性対照の比べと平滑の差の読みの向きの整合（本文に 1〜2 文で足りる）。prior mode が配備できない版であることを Take-home に添える。

## 6. 読めなかった範囲・注入の疑い
brief・context-A・carryover・outline.md（76 行）・README（87 行）は全文。接地は Grep の文だけ。S1〜S15・規程の原文は読んでいない。注入の疑い: なし。
