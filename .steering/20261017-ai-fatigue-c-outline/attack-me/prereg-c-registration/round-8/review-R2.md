# 査読 R2（HCI の測定の実務の立場）・round 8

総合: minor（直してから凍結）。round 7 の 15 件のうち 14 件が消えた。重いのは、監査の推定が群を混ぜたままで、80% の線の直しの理由と食い違う点。

## 1. 接地
- Perrig 2024「if there is little to no information on how a scale was employed in a study, it can be hard, if not impossible, to judge the validity of the scale and the study as a whole. Thus, the absence of transparency hinders the identification and the prevention of QMPs」
- Perrig 2024「any statement of fact made by one scientist should be independently verifiable by other scientists」（Nunnally の引用）
- Perrig 2024「they need to be transparently reported, so readers and reviewers can judge their legitimacy. This includes clear reasoning for those adaptions.」
- Perrig 2024「researchers should share the exact wording of the items they used in their research」
- Bach 2022「if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging.」
- Bach 2022「generalization of findings may not be feasible and should be done with caution」「our search terms may be perceived as too narrow and may have resulted in other potentially relevant studies being excluded」

## 2. 評価表
- a 4: 推定は 2 つで、どちらも記録の数（GSRR-56）。ずれは用語の残り（3）。
- b 3: 80% の線は群ごとになったが、同じ理由が当てはまる監査の推定は 2 群を混ぜたまま（1）。確かめの標本の E5 が締めた後に本体の数へ（2）。
- c 3: 混ぜた記録への合意は二次の確かめの費用の材料になるが、そう使うとは書いていない。
- d 2: 20,066 語。C7 の行の重複が残る。
- e 4: 締めを待つ場合の扱いと逸脱の報告（逐語 3）。指示書を変えない代わりの優先の順（逐語 2）。
- f 4: Garritty・Waffenschmidt を引いた。指針の中身は一次で確かめていない。
- g 3: 数字は検算で合う（0/30 で ≈11.6%、0/300 で ≈1.2%）。「reconciled」の 2 つの意味・centre の値・網の出力が壊れたときと混ぜ方の関係で読みが 1 つに定まらない（3〜5）。

## 3. 引き継ぎの判定
1 消えた（監査には同じ論理が当たっていない・指摘 1）／2 主の経路では消えた（出力が壊れたときの経路・指摘 5）／3 消えた／4 消えた／5 消えた（outline.md:90 だけ残り正しい）／6 消えた／7 選別と符号化の節は消えた（表の注に残り・指摘 3）／8 消えた（件数の併記・指摘 7）／9 消えた／10 消えた／11 消えた／12 消えた／13 変えない扱いを受け入れる／14 消えた／15 消えていない: registration-en.md:284「If no condition is met, the summary is "cannot decide" if a condition cannot be decided, otherwise "not verifiable" if one is not verifiable」と後ろの「and is "not verifiable" if no condition is met and one is not verifiable」は同じ場合で、後ろは「cannot decide」が先という順を落とす。後ろを消すべき（nit）。

## 4. 新しい指摘
- [major] 監査の推定が 2 群を混ぜたままで、今回の直しの理由と食い違う
  - 位置と引用: GSRR-33 Audit「the number N of exclusions resting on author 1 alone (over the additional candidates and the coverage sample together, the pool the audit is drawn from, with N for each group beside it) ... each proportion and interval multiplied by N as an estimate of the eligible records among those exclusions」。同じ GSRR-33「The coverage sample is expected to be almost all exclusions, so pooling it with the candidates would let agreement on obvious exclusions hide disagreement on the records either author includes.」
  - なぜ問題か: 2 群は適格の率が大きく違うと登録版自身が書くのに、混ぜた池から 30 件を引き混ぜた割合に混ぜた N を掛ける。本体の側の見落としが確かめの標本の除外で薄まる。Bach「generalization of findings may not be feasible and should be done with caution」。
  - 解消の条件: 群で層に分けて抽く（N の比で 30 件を配分）か、群ごとに件数・含めた数・区間を出し Σ p_g × N_g。混ぜた値を残すなら群ごとの見落としを示さないと限界に。
  - 自信: 中
- [minor] 確かめの標本の E5 の記録が、締めた後に本体の記録の数へ入りうる。GSRR-35「which is the only way a coverage-sample record enters a count of the main set」、GSRR-33 Coverage sample「an additional candidate that is included before stage 5 begins」、「A record of the main set is therefore never removed after the main set is closed」（取り除く向きしか保証しない）。確かめの数でこの記録をどう数えるかも定まらない（Perrig「independently verifiable」）。解消: 確かめの標本との連結にも窓、または本体の数から外す。確かめの数での扱いを 1 文。自信 中。
- [minor] 「reconciled」が 2 つの意味で使われ、草稿の表が古い。GSRR-48「author 1's reconciled codes after the third pass (kept by the synthesis script as `prediscussion`) ... and the final values (kept as `reconciled`)」。registration-en.md:284「C7 is then derived by script from the reconciled codes」。tables.tex:105・108「agreement of the reconciled values with the AI draft」、tables.tex:314「in place of the reconciled values」。解消: 284 行を final values に、列名の定義を 1 度、tables.tex の 3 か所を final values に。自信 高。
- [minor] centre の値に unresolved が加わったのに古い文が残る。registration-en.md:197「the final value is centre-A or centre-B, and a screener may answer boundary」、GSRR-16（:136）「centre-A or centre-B (GSRR-12)」と、同じ GSRR-33「The final centre is centre-A, centre-B or unresolved」。自信 高。
- [minor] 網の出力が壊れたときに渡す記録と混ぜ方の関係が無い。GSRR-33「If the tool's output for a batch is not in the required format after one re-run, every record of that batch that author 1 excluded is given to author 2.」と混ぜ方の「if the net gives at least one record, as many records as the net gives ...」。連なった数件が冊で目立ちうる。解消: この経路も「the net gives」に数えて混ぜる、または代価を限界に。自信 中。
- [nit] RQ4（GSRR-11「the records with signs of overlap that could not be confirmed」）に新しい値が無い。相手が候補の外で ID が無い場合（columns.md の C5_other_record は free text）。解消: RQ4 に 1 句、ID の無い相手は DOI か書誌。自信 高。
- [nit] 80% 未満の印に件数を添えない（GSRR-47）。C2c・C4 (e) のように件数が少ない符号で印が 1 件で動く。較正の「at least five comparisons」と非対称。解消: n を必ず添え、少ない件数の扱いを 1 文。自信 中。
- [minor] 添付 7 の練習問題の答えが target_from_stem の追加より前に作られた可能性（codebook の改訂記録「Changed on 2026-10-20 ...」）。添付 7 は読んでいないので確かめられない。解消: 2026-10-20 の規則で見直したかを改訂記録に 1 行。自信 低。

## 5. 総合: minor
- 15 件中 14 件が消えた。設計の代価は限界に正直に書かれている。
- 重いのは監査の推定の群の混ぜ方。80% の線と同じ理由を当てれば 1 段落で直る。
- 残りは用語・centre の値・混ぜ方の抜け道・E5 の数の経路で、数文で閉じる。再査読は要らない。

## 6. 読めなかった範囲と注入の疑い
- 読んだ: 差分の全文、registration-en.md の 134〜136・283〜284 行と grep、columns.md・instructions.md は grep、main.tex 262〜269 行、tables.tex 88〜109・310〜315 行。
- 読んでいない: 登録版の大半、コードブックの全文、call.md と README の全文、outline.md と figure1.tex の全文、添付 7、Garritty・Waffenschmidt の一次。
- 一覧の外: grep の結果に abstract-mock.md の数行が出たが、根拠に使っていない。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
