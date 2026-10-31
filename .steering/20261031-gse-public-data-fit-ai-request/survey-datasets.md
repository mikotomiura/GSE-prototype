# 3 データの利用条件と出来事の種類（2026-10-31・サブエージェント 3 本の並列＋メインの抜き取り照合）

データ本体は取っていない。メインが一次で照合した主張には【照合済】を付けた。それ以外はサブエージェントの報告（WebFetch の要約を含む）で、逐語は原文と未照合のものがある。

## CoAuthor（Lee, Liang & Yang, CHI 2022・arXiv:2201.06796）

- セッション数は 1,445（創作 830・論述 615）・書き手 63（論文 Table 3）。引き継ぎの「1,447」は誤り。
- 利用条件: データのライセンスの記載が公式サイト（https://coauthor.stanford.edu）に無い【照合済: "licen" の出現 0 件】。コード（https://github.com/minalee-research/coauthor-interface）は MIT でデータには及ばない。同意書（論文の付録）逐語 "Your textual interaction (e.g. insert, delete, select) can be recorded and released for research purposes."。審査機関名と承認番号は匿名化されている。参加者は MTurk。
- 入手: Google Drive の単一ファイル。形式・サイズは未確認。
- 出来事（論文 Table 1）: text-insert（User/API）・text-delete・cursor-forward/backward/select・suggestion-get（User・Tab）・suggestion-open（API）・suggestion-reopen・suggestion-up/down・suggestion-select（Enter・マウスも可）・suggestion-close（User/API）。各イベントは名前・時刻・エディタのスナップショット。
- 提案は利用者の要求（Tab）でだけ出る。教示文 逐語 "Whenever you feel stuck or just want some inspiration, press the tab key"。
- 要求は平均 11.8 回/セッション・約 11 分。受け入れ 72.3%。
- 未確認: 時刻の単位と精度・貼り付けの扱い・マウスのクリックの記録。
- 注意: 受け入れた提案の本文は source=API の text-insert として入るので打鍵から除く。教示文が Tab を「詰まったとき」に結び付けている。1 分放置の規則がある。

## RealHumanEval（Mozannar et al., arXiv:2404.02806・[V340]）

- 利用条件: Hugging Face（hsseinmz/realhumaneval）は "License: CC"（版は不明）、GitHub は CC0-1.0。IRB 承認の記載あり。
- 出来事: チャット（request・response・copy_events・timestamp）とオートコンプリート（suggestion・accepted・requested・timestamp）。コードは 15 秒ごとの全文の保存【照合済: 論文 HTML 逐語 "every 15 seconds, the interface saves the entire code the user has written"】。打鍵ごとの時刻は確認できなかった。
- 所見: GSE の特徴量（打鍵間隔・2 秒の休止・バースト・修正率）は作れない。差分を取るには本文を一度使う必要があり、本文を捨てる規約とも合わない。

## CS1 打鍵データ（Edwards, Hart & Shrestha, JEDM 2023・[V243]）

- 2019 年版 doi:10.7910/DVN/6BPCXN（505 名・5 課題・約 500 万イベント・ブラウザの自作 IDE・補完なし）／2021 年版 doi:10.7910/DVN/BVOF7S（44 名・8 課題・PyCharm）。
- 利用条件: CC0 1.0【照合済: 2019 年版の API】。ただし termsOfAccess 逐語 "Contact john.edwards@usu.edu for access to files. Access is restricted because some of the assignment descriptions are still in active use…"・fileAccessRequest=True【照合済】。ファイルごとの restricted は False（サブエージェントの報告）。論文 逐語 "Ethical use of this dataset includes avoiding attempts at reconstructing identities."。2019 年版の同意書は公開共有に触れない（サブエージェント・先頭と grep のみ）。2019 年版の students.csv は 2025 年 7 月に除去。
- 出来事: ClientTimestamp（ミリ秒・Unix epoch）・EventType・InsertText/DeleteText・X-Keystroke（2019）・X-Action/X-Metadata（2021）・実行の成否。助けを求めた出来事は無い。
- 所見: 打鍵の時刻とキーの種類から GSE の特徴量は作れる見込み。AI を求める出来事が無いので、項目 1 では「出来事の無い対照」にしか使えない。
