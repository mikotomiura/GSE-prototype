# 判断

## 判断 1: CS1 は著者へ連絡してから使う（研究者の回答・2026-11-02）

- 一次で確かめたこと（Harvard Dataverse の API・2026-11-02）: 2019 年版 doi:10.7910/DVN/6BPCXN・2021 年版 doi:10.7910/DVN/BVOF7S とも、ライセンスは CC0 1.0、各ファイルの `restricted` は False、`fileAccessRequest` は True。termsOfAccess 逐語 "Contact john.edwards@usu.edu for access to files. Access is restricted because some of the assignment descriptions are still in active use, so we want to make sure that files are only used by researchers and not students looking for assignment solutions."。2019 年版の `keystrokes.csv` は 455,078,162 バイト。
- 研究者の選択: 先に著者へ連絡する（推奨どおり）。連絡の文案は Claude が作り、送るのは研究者。返事が来るまで、俯瞰は KLiCKe と CoAuthor の 2 つで進める。

## 判断 2: レビュー 2 系統の指摘をすべて採り、集計を回し直す（2026-11-02）

- code-reviewer と /cross-review（Claude と Codex）の指摘を一次で確かめ、すべて採った。両系統の一致は 2 件（CoAuthor の受領を種類ごとに出していない・取っておく書き手の照合が CoAuthor の解析側に無い）。
- コードの直し（`0e61de28`）: 条件どおりに直したもの 3 つ（受領を種類ごと・受領の頻度を観測時間で割る・CoAuthor の照合）と、足した記述（判定に使わない）。直す前と後の集計値を比べ、変わったのは受領の 1 時間あたりの値だけだった。
- notes の直し: CoAuthor の L2・L3 を条件どおりふつうの区間を主にした（最初は断らずに全体を主にしていた）。L5 は「書き手の中の揺れは数え上げの揺れと同じ大きさ」に、L3 は削除（停滞の定義から出る）を除いた量で読むように、L1 は再開した停滞に限ると改めた。
- positioning.md の信号の一覧に `starve_window`・`recording_pause` を足した。
- CS1 の文案にある連絡先は Dataverse の termsOfAccess に公開されている管理者の宛先で、参加者の情報ではないので残す。
- 採らなかった指摘: なし。CoAuthor のふつうの区間の頻度に最小の時間を置く案（LOW）は、条件に無いので値は変えず、notes に「ふつうの区間は薄い・長い出来事ほど入りにくい」と書いた。

## 判断 3: CS1 は 2019 年版と 2021 年版の打鍵ファイルだけを頼む（研究者の回答・2026-11-02）

- 研究者の問い: 2021 年版も使うか、もらえる分の全部をもらうか。
- 研究者の選択: 両版の `keystrokes.csv` だけ（推奨どおり）。理由: 2021 年版は同じ学生の 8 課題で、1 人の中の長い単位を何回も見られる（L5 で足りなかった材料）。課題文は制限の理由そのもの、調査票と `students.csv` は取らないと決めた人口統計、2021 年版の実行の記録は計約 2.4 GB で使わない。
- 文案（`cs1-contact-draft.md`）を両版に改めた。送るのは研究者。
- 返事の後の注意: PyCharm の補完で入る複数の文字は、受領の数え方を濁すので別に数える。
