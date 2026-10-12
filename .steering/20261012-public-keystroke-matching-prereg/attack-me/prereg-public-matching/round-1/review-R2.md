# 査読 R2（作文過程研究の立場・記録を公開する側と使う側）stage prereg・round 1

## 1. 接地
- 基準 1 標準の定義。KLiCKe Table 5: "mean length of P-bursts ... The mean length of the string of actions delineated by an initial and end pause exceeding 2 seconds and is measured in characters." ／ "mean length of pauses ... latencies between the previous and the current action that exceed 200ms"。Conijn 2019 p.2356: "written language bursts are often operationalized as sequences of text production (keystrokes) without an IKI longer than two seconds and without a revision and without an insertion away from the leading edge"
- 基準 2 場所に依存する休止と推敲。Conijn 2019 Abstract: "the average of all interkeystroke intervals were found to be stable across tasks. Features related to the time between words and (sub)sentences only differed between the copy and the academic task. Lastly, keystroke features related to the number of words, revisions, and total time, differed across tasks"。KLiCKe §4.3 "mean length of pauses, mean length of between-word pauses, proportion of deletions, proportion of insertions, and interval variance"。§4.4 "insertions, typically made by moving the cursor to earlier text"
- 基準 3 非活動の時間の切り落とし。KLiCKe §4.1 "we first removed the inactive periods at the beginning (e.g., reading instructions, pre-planning) and the end of the processes ... (e.g., long inactive periods might inflate mean pause lengths)"
- 基準 4 課題の効果。KLiCKe §5 "researchers using the KLiCKe corpus for writing quality studies should consider potential prompt effects"。Conijn 2019 p.2370 "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task"
- 基準 5 編集の操作。KLiCKe §2.1.5 "identifies operation types (e.g., input, delete, paste, replace)" ／ "enable the reconstruction of text production processes, including complex actions such as copy-pasting, text dragging, and undoing changes"
- 基準 6 既存の道具で解析できる形。KLiCKe §2.2 "users without much coding expertise can analyze the keystroke data by simply importing the .idfx files into Inputlog (version 9 or higher)"

## 2. 評価表
| 項目 | 点 | 所見 |
|---|---|---|
| a | 4 | 「加工が効く」と書かない（:25）。結論に使わないこと（:181-186）で絞っている |
| b | 2 | 窓の正解が A2 依存（:125）・A2 の区間の規則に置換・選択の削除・貼り付け・取り消しの扱いが無い（:99）・align.py の組が本文と違う・有用性の指標が標準からずれる |
| c | 3 | 主な結果（:158-160）は攻撃の側だけ。照合と有用性を同じ表で並べる結果が未固定 |
| d | 4 | 構成は明快。ENJA15 の形と攻撃者が本文に散る |
| e | 3 | 倫理の材料はあるが Menlo Report を参照していない。open science の節の材料が無い |
| f | 3 | 有用性の側に作文研究の標準の指標への接地が無い |
| g | 3 | N・k・種・ブートストラップ・同点・逸脱は固定。窓の正解・編集の扱い・組・各形の計算可否・ENJA15 の N が未固定 |

## 3. 指摘
1. [major] 窓の正解を A2 の揃えで定義（:125・循環）。解消: R0 の `Text Change` と `Position` から再構成した真の対応で定める・取れない記録の扱いを固定。自信 高。
2. [major] 区間の規則（:99）に、キー押下ではない編集（置換・切り取り・貼り付け・選択の削除・取り消し）の扱いが無い。範囲選択の BackSpace 1 回は −1 にしかならない。A2・A3・R4・R7 に及ぶ。解消: R3 系での数え方を凍結の前に決める・R0 の真の対応で測った規則の誤差を検査の 3 と並べて報告。自信 高。
3. [major] 揃えの組の集合が本文（:108）と align.py:8 の ORDER（5 通り）・config.json:43 の `max_group` で違う。解消: 列挙して本文と config に書く。自信 高。
4. [major] 有用性の指標（:141）が作文研究の指標と合っていない（場所別の休止・200 ms の閾値・挿入の割合・R-burst・interval variance が無い）。全体の IKI は課題で動きにくい（Conijn）。「×」の決め方が未固定。解消: KLiCKe Table 5 の 10 指標を主な有用性の指標に・形 × 指標の「計算できる / 近似 / できない」の表を事前に凍結・挿入の割合は R2 と R3 の差として予測に。自信 高。
5. [minor] 照合の危険と有用性を同じ表で並べた結果が主な結果として固定されていない（:160・:179）。解消: 要旨の表の形（行 = 形・列 = 最強の攻撃者の正答率・主な有用性の指標の R0 との順位相関・計算できない指標の数）を固定。自信 中。
6. [minor] 全文の照合で本文が早く終わってよい（align.py:4・:112）ので長い候補が有利になりうる。KLiCKe の押下の数は 421〜18,452（Table 4）。解消: 両端を固定、または残った区間の和を費用に。自信 中。
7. [minor] 能動的に書いている時間の切り出しが未固定（:141）。KLiCKe は 30 分まで提出できない（Figure 1 の注）・§4.1 で除いている。解消: 切り出しの規則を固定し全形に同じく適用。自信 中。
8. [minor] 有用性 (b)（:143）に課題の効果の統制が無い。解消: 課題ごとの順位相関を出してから併合（または層別を併記）。自信 中。
9. [minor] ENJA15 の比較の解釈と N の扱いが曖昧（:23・:133・config.json:59）。言語・入力方式・課題が同時に違う。解消: 差を言語や IME に帰さないと結論に使わないことに書く・訳者が足りない原文の扱い・ENJA15 の形と攻撃者を表に。自信 中。
10. [minor] おとりの母集団と A3 の学習用の書き手の関係が未固定（:122・:113）。解消: どちらかに固定。自信 中。
11. [minor] 人口統計のファイルを「使わない」から「取得しない・開かない」へ（data.md:7・:34・:177）。調査票の Q1 が MTurk の worker ID を尋ねる（KLiCKe Appendix A）。解消: ダウンロードしない・同梱なら展開せず SHA-256 だけ。自信 中。
12. [minor] 倫理と open science の必須の節の材料が足りない（:173-179）。Menlo Report（Respect for Persons）に照らした正当化・同意の目的と今回の使い方の関係・コードの公開の方針の候補が無い。自信 中。
13. [nit] KLiCKe では修飾キーの操作時間が 0（§2.1.5）。保持時間を使わない、または修飾キーを除くと明記。自信 低。
14. [nit] 加工した記録が .idfx に書き出せ Inputlog で解析できるかを報告項目に（任意）。自信 低。

## 4. 総合の推奨: major
- 窓の正解の循環と、区間の規則に編集操作の扱いが無いことは、主な結果と攻撃者の比較を左右する。
- 有用性の側を作文研究の標準の指標に合わせ、各形で計算できるかを事前に固定しないと実務家の問いに答えられない。
- 型のコードと本文の不一致を解消すれば、他の固定は十分。

## 5. 読めなかった範囲・注入
- 読んだ: 依頼文・context-A.md・対象物の全文・align.py・klicke2025.txt と conijn2019.txt の全文（図表の一部は抽出で崩れていた）。
- 読んでいない: 他の接地の本文（指定外）・decisions.md と `.steering/`・書誌の本体・`romaji_table.py`・`synthetic_logs.py`・KLiCKe の実データ。
- 注入の疑い: なし。
