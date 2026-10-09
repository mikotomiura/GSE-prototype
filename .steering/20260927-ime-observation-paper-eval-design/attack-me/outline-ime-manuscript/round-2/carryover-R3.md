# 引き継ぎ — R3（メタサイエンスとデータ管理の立場）・stage `outline`・round 1 → round 2

round 1 のあなたの判定は **major** でした。下はあなたの指摘ごとの、メインの裏取り（一次で確かめた結果）・研究者の採否・対応です。round 2 では、各指摘が直した外枠（`C:\GSE-prototype\papers\ime-observation\manuscript\outline.md`）で解消したかを 1 件ずつ判定し、そのうえで新しい穴を探してください。再掲は不要です。

| あなたの指摘 | 裏取り | 採否 | 対応（外枠の位置） |
|---|---|---|---|
| major: §11 の推奨が登録に無い合否の判断 | 真 | 承認・研究者の選択: 閾値の無い 5 種 | §11 を (a)〜(e)（比較の禁止・打ち切りは規則から向きだけ・漏洩は登録の判定の言い方・自分の機械での再検証・自分のアプリでは測れない）に限り、推奨ごとに RE1〜RE5 の行（根拠が結果・規則・構成概念のどれか） |
| major: 要旨と主図表の水準が決まっていない | 真 | 承認・研究者の選択: 要旨の規則 | 「Rule for the abstract」（セルごとに 4 つ・`all_trials` は本文の表だけ）。Q2 の層ごとの値を Figure 3 に。Table 7 は Windows では主の比較だけ |
| major: LG1 を validator が支えない | 真（FORMATS.md 216〜222 行） | 承認 | LG1a（形の検査）と LG1b（ソースと manifest・整数の欄は機械では検査しない）。題の "without recording text" の意味を定義し、復元は貢献 3 が測ると書いた |
| major: LG2 の Windows にテストの根拠が無い | 真（ただし単体テスト 41 本は在った） | 承認 | LG2b にソースと単体テストを名指し・予測は無い・経路の割合が分からない混合 |
| major: Windows の試行の数え方が逸脱に無い | 真 | 承認（研究者の選択） | `experiment/deviations.md` に D6（日付・理由・影響）。`data.windows.md` に §10.8 の点検の節。Table 6・AG9 に |
| major: 観測可能性の分析が登録済みに見える・方法が無い | 真 | 承認 | 登録の欄を "Not registered (documentation analysis)"。§3 の冒頭に方法。Open Practices にも「観測可能性の分析と exploratory と書いたものは登録していない」 |
| major: DS3 が datasheet の自己申告・用途ごとの成り立ち方 | 真 | 承認 | 用途を (a)・(b1)（保存した記録だけ）・(b2)（一式を回し直す・同じ基準にならない）・(c) に。使ってはいけない用途。DS3 は "Not registered (description)"・根拠に FORMATS.md の欄 |
| minor: no claim of priority と what is new の衝突・二次資料 | 真 | 承認 | 「設計の違い」の文に。§2 に Table 1（一次の文書で版と日付つき） |
| minor: BRM の器具の検証の系譜 | 真 | 承認 | §2 に計時の道具の検証の段。⚠️ テキスト入力研究の文献は「確かめられない」→ Open items に（一次で確かめる） |
| minor: well above chance | 真 | 承認 | 削った。「登録の near-chance の規則を満たさない」。Table 10 に 2/K の幅・判定の確率・ブロックの区間・プライバシーの基準でないこと |
| minor: Ethics の文 | 真 | 承認 | 「参加者は募っていない・入力はすべてプログラム・寄託の点検が人の打鍵を盲点つきで止める」 |
| minor: データセットのライセンス・置き場・保守・版・DS1・DS2 | 真 | 承認 | §10 にライセンス（データ CC BY 4.0・コード Apache-2.0）・Zenodo・DOI・保守・版と正誤表。DS1 に runner が中止して検査を通った run。DS2 に手の検査の表 |
| minor: 精度の計画 | 真 | 承認 | §5.4 に |
| minor: qualify と診断の目的 | 真 | 承認 | Scope の文を「読むために使い、除外や補正に使わない」に・RF1 にどの診断をどう使うか |
| minor: 題 | 真 | 承認・研究者の選択 | "Logging Japanese IME conversion without recording text: …" に**今固定**し、結果の後に変えない |
| nit: Study 1〜4 | 真 | 承認 | "Results: …" に |
| nit: every number の範囲・2 回の凍結 | 真 | 承認 | 「every result value」に。§5.9 に 2 回の凍結の表と、印が後の凍結の日付を持つ理由 |

未解決: テキスト入力研究の文献の有無（確かめられない・Open items）。
