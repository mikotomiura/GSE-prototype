# paper-reviewer round 4: BRM 査読者（打鍵記録を使う書字研究の利用者・公開の安全に通じた立場）

総合の推奨は **major** です。ただし再査読は §3.4 と §6.7 の 2 か所に絞ってよいと考えます。最も重い新しい穴は、§3.4 の中止の閾値「1 ブロックに 5」が確かめていない前提に立っていることです。凍結の前に、パイロットの参照のログで確かめられます。

対象物: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（`159a2ec8`）。行番号は今の版のもの。

## 1. 接地（文献ごとの逐語と、そこから立てた基準）

**Conijn, Roeser & van Zaanen (2019)**（`...\round-1\tmp\sources\conijn2019.txt`）
- **C1（84–88 行）** "The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."
  - 基準: 指標の定義が、読者の解釈できる単位で 1 通りに決まっていること。
- **C2（807–810 行）** "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task, rather than as a result of the variable of interest"
  - 基準: 指標の値が設計（課題の組成）に依るなら、その依存を切り分けるか、限界として書くこと。
- **C3（124–125 行・137–140 行）** "The interkeystroke interval (IKI, see Fig. 1b) is the most commonly used feature." / "the number of backspaces/deletes"
  - 基準: 公開の形と再重み付けの版が、書字研究の中心の指標（休止・修正）について何を残すかが読者に分かること。
- **C4（356–358 行）** "To account for this positive skew, all time features (except for total time) were log transformed and all values above the 95th percentile were removed."
  - 基準: 長い持続時間を落とす処理が集計量にどう効くかを、読者が自分のデータで判断できる形で示すこと。

**Monaco (2018)**（`...\round-1\tmp\sources\monaco2018.txt`）
- **M1（23–24 行・698–699 行）** "the information gained by different temporal features strongly correlates to typing speed and style." / "These results suggest that temporal side channel information gain is highly user-dependent."
  - 基準: 漏れの評価は、速さと打ち方に依ること・合成の入力の限界を、主張の範囲に反映すること。
- **M2（1295–1297 行）** "doing so may actually compromise anonymity, i.e., enable behavior-based identification, an issue not considered in this work."
  - 基準: 評価していない脅威（同定・結合）は、評価していないと明記すること。

## 2. 引き継ぎの判定（carryover-R2.md）

| 指摘 | 判定 | 理由（1 行）・今の版の位置 |
|---|---|---|
| A [major] 問 3 の主が long の割合に依存 | 部分的に解消 | 件数と時間の割合は範囲の試行の上で定義し直され、偏りは long の割合で動かなくなった（§4.6 L440–445・`l2.py`:306–313）。限界と ICC は、テキストに残る試行の数（設計の long の割合と速さで変わる）にまだ依る（新 2） |
| B [major] 推奨の単位と粒度 | 解消 | §6.8 L743–747・§1.2 L55–58・§7 L865–868・`kit\e2\README.md`:258–263 が「試行の句 1 つの識別」で揃った |
| minor 1 README の逆の記述 | 解消 | README:18–20・258–261・107–110・279–281 |
| minor 2 層 none での重み付けし直し | 解消 | §6.7 L672–676・`match.py`:753・`l2.py`:113–117, 866–868。ただし新しい穴を作った（新 3・nit 6） |
| minor 3 打ち切りの規則を読者のデータに当てる | 部分的に解消 | §6.4 L578–582 に文が入った。§7 L854–859 には無い（既知の入れ漏れ）。どちら向きに効くかも読者任せのまま（新 4） |
| minor 4 §1.2 の問 4 が広い | 解消 | §1.2 L55–58 |
| minor 5 中止の基準が未定 | 解消 | 閉じた規則になった（§3.4 L348–357・`data.md`:25–27, 31–40）。ただし閾値の前提が確かめられていない（新 1） |
| minor 6 合わせ直しを実ログで未試行 | 部分的に解消 | 中身が無いのは既知。約束の文に、どの run・どの印で回すか・結果を何に使うかが無い（新 5）。コードの直し（`closed_set.py`:610–642）は §6.8 L686–692 と合う |
| nit 1 依存の文の自己矛盾 | 解消 | §6.8 L748–752・§7 L860–864・README:108–110 |
| 新 3 | 部分的に解消 | A と同じ |
| 新 4 | 解消 | minor 1 と同じ |
| 新 6 | 解消 | minor 2 と同じ |
| nit 3 冗長さ | 部分的に解消 | 設計効果（§3.3）と打ち切りの規則（§1.1）は 1 か所に寄った。一方で重複が増えた。区間を付けないものの一覧は §1.2 L38–41 と §6.8 を除く §6.1 L487–488 の 2 か所。§6.8 L745–747 と §7 の新しい項 L865–868 はほぼ同文。Wilson と依存の文は §6.8・§7・README の 3 か所。本文は +8% |
| major-3 セッション行の公開の形 | 未解消（採らなかった） | 範囲は明記された（§6.8 L743–745・§7・README）。推奨の形（時刻のない key 行・セッション行なし）では、問 1〜3 の指標も IKI も計算できない。その帰結は書かれていない |
| major-4 | 未解消（採らなかった） | round 3 から変わらない |
| major-5 | 解消 | minor 2 で対応 |
| minor-5 中間の粒度・粒度ごとの書字の指標 | 未解消（採らなかった） | §7 L832–833 の文は実態どおり（"granularities between milliseconds and one-second bins are not evaluated"） |
| minor-7 生ログを預ける基準 | 部分的に解消 | §3.1 L188–190 に「written before the freeze」が入った。中身は未了（既知）。下書きの基準は §3.4 の前提とぶつかりうる（新 1） |

## 3. 評価表 a〜g

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | 問 4 の主張が、攻撃が示せる範囲（試行の句 1 つ・時刻のない 2 つの粒度）に絞られた（M2 を満たす）。問 3 の量の偏りは設計の long の割合で動かなくなった。残る点: §6.4 の読者向けの文が「another source」と言い、同じログで分かることを書いていない（新 4） |
| b 方法の穴 | 3 | 今回の直しが 2 つの穴を作った。(1) §3.4 の閉じた規則の閾値が、確かめていない前提に立つ（新 1）。(2) 範囲の上での再定義により、テキストの実効の大きさが速さで変わる（新 2）。どちらも凍結の前に閉じられる |
| c 持ち帰れるもの | 3 | 試行あたりの率は読者が自分の単位に直せる。再重み付けの版も読者の道具になった。しかし、修正の中心である S6 がその版でほぼ空になる（新 3）。推奨の公開の形で書字の指標が何も残らないことも書かれていない（major-3・minor-5 の帰結） |
| d 簡潔さと構成 | 2 | 12,143 語（+8%）。上の nit 3 のとおり重複が増えた。実務家としては、§7 の新しい項は §6.8 の参照 1 行で足りる |
| e 規程への適合 | 4 | J9（除外・中止を事前に決めて守る）は閉じた規則で満たした。ただし前提が誤っていれば「stick to them」が害になる（新 1）。J6・J7 は §3.3 の精度の記述で満たす。J4 は、中止した run を預けない理由が参加者の機密で、規程の "without breaching participant confidentiality" に合う |
| f 先行研究の位置づけ | 3 | round 3 から変わらない（References は 9 件のまま。§4.6 は 4 つの量が書字の文献の検討から選ばれていないと明記している） |
| g 固定の十分さ | 4 | 中止の規則・問 3 の量の定義・再重み付けの版は 1 通りに決まった。未固定は 2 点。範囲の試行が少ないテキストの扱い（新 2）と、§3.1 の約束の結果の使い方（新 5） |

## 4. 新しい指摘（重い順）

- [severity: major] **§3.4 の閾値「1 ブロックに 5（印 4・かな 1）」は、参照の欄がかなキーの key_down を受けるという、確かめていない前提に立つ。しかも検査の数は、取りこぼしと外からの打鍵が相殺する作りである**
  - 位置と引用:
    - §3.4 L352–354 「its `rows_outside_trials` exceeds the five presses made outside the trials in each block (four marker presses and one kana press). No other reason and no explanation is admitted.」
    - `data.md`:33–35 「exceeds five per block (four marker presses and one kana press)」
    - §4.5 L414–415 「It also models what the oracle does not record: the kana key that the runner presses at the start of every block」
    - `pilot-macos.md`:182–183 「the pilot's reach count (`kit/pilot/reach.py`) checked only the direction from the executor to the observation」
    - `delivery.py`:372–373（`excess_rows` は試行ごとの `max(0, received - sent)` の和、`rows_outside_trials` は run 全体の 1 つの数）
  - なぜ問題か:
    - かなキーは `focus_cmd` が押す（`kit\run\README.md`:88）。oracle に記録されないので、参照が受けたかを確かめた記録が、読んだ範囲のどこにも無い。パイロットで試行の外の行を数えたのは観測の側だけ（`pilot-macos.md`:143–144「the 18 rows outside the trials equal the number of marker presses」）。
    - 参照がかなキーを受けない場合: 余裕が 1 ブロックに 1 でき、on のセルでは 42 打鍵ぶんの外からの打鍵が通る。
    - ブロックの外で 5 を超える key_down が正当に出る場合: 説明を認めない規則なので、3 回とも機械的に中止になり、セルは "not measured" になる。
    - 「in each block」と書きながら、検査の道具はブロックごとの数を出さない。合計と比べるなら、ブロックの間で過不足が相殺する。
    - `excess_rows` は試行の中で差し引くので、S14 のモードキーを参照が受けなければ、その試行の外からの 1 打鍵は消える。
    - 預ける基準の下書き（`pilot-macos.md`:179–180「every `key_down` of the reference log is matched ... by a press the executor recorded as sent」）は、参照がかなキーを受けるならパイロットの全 run を落とす。§3.4 と逆の前提に立ちうる。
    - 規程 J9 "set inclusion/exclusion criteria in advance ... and stick to them" は、前提が正しいときに限って守る価値がある。
  - 解消の条件:
    - 凍結の前に、パイロットの run（印 3 打鍵）で `delivery.py` を回す。参照の `rows_outside_trials` のブロックあたりの値と、S14 のモードキーへの参照の到達を §3.1 に書き、閾値をその観測から決める。
    - ブロックごとに数えるか、run の合計を「5 × ブロック数」と比べるかを明記する。ブロックごとなら `delivery.py` にその出力を足す。
    - 試行の中での相殺を、限界として書くか、取りこぼしと余分を別々に数える。
    - 預ける基準の下書きを、同じ前提に揃える。
  - 自信: 中（前提が確かめられていないことは高い。前提が実際に誤っているかは分からない）

- [severity: minor] **問 3: テキストに残る範囲の試行の数が速さで系統的に違うのに、主の限界と ICC は大きさを問わずテキストを等しく並べる**
  - 位置と引用:
    - §4.6 L440–441 「computed for every text on both sides, over the trials of the text that are in the scope」
    - §6.7 L661–662 「The number of a text's trials in the scope is reported per speed」
    - §3.3 L285–286 「a speed level holds 603 (slow), 852 (mid) and 940 (fast) trials」
    - `l2.py`:310–313・588–590（テキストごとの率を等しい重みで平均）
  - なぜ問題か:
    - on では範囲に残る試行の割合が、遅い 57%・中 81%・速い 90%（1,050 試行あたり）。8 試行のテキストに残る数は、遅いで平均約 4.6、速いで約 7.2。
    - 率の量のテキストごとのばらつきは、ほぼ 1/n で効く。遅い速さの一致の限界は、テキストの大きさだけで広がり（試行が独立なら約 1.25 倍。私の概算）、ICC は下がる。
    - そのため、速さのあいだの限界・ICC の比較に、設計の long の割合が持ち込まれる。round 3 の A の残りである。
    - 読者は「1 テキスト（8 句）の観測値がどれだけずれうるか」として限界を読むが、実際には 1〜8 試行の混合になる。
    - 速さごとの偏り（`mixture_bias`）は、テキストの率の平均（テキストに等しい重み）か、試行あたりの差（試行に等しい重み）かが、選択として書かれていない。
    - 接地: Conijn C1 "crucial for the interpretation of the results"・C2 "might differ merely as a result of the task"。
  - 解消の条件（次のどれかを固定する）:
    - (a) 主の一致を、範囲の試行が m 以上のテキストに限る。m を今決め、§3.1 の予測から速さごとのテキストの数を書く。
    - (b) 限界と ICC を n_trials_in_scope の階級ごとにも報告する。
    - (c) 少なくとも §6.7・§7 に、限界と ICC がこの設計の「範囲の試行の数の分布」についての値で、速さの比較には使えないと書く。
    - あわせて、偏りがテキストの平均か試行の平均かを書く。
  - 自信: 中

- [severity: minor] **再重み付けの版では、S6（読みの中の Backspace による直し）が遅い・中くらいの速さでほぼ空になる。しかもコードは空の層を null にせず出力から落とす**
  - 位置と引用:
    - §6.7 L673–675 「over the trials of the scope that are in neither the carried-out nor the received-carry layer of section 6.4, for which reweighting to another mix of scenarios is meant」
    - §3.1 L229–230 「in 188 trials (all S6) a session runs on into a later trial; in 184 trials presses went into a session carried over」
    - §3.3 表 「S6 | 3 / 27 / 61」
    - `l2.py`:665–688（`groups` は試行のある層だけ作る）
    - §6.11 L806–807 「reported as null with the reason, never as zero」
  - なぜ問題か:
    - on で S6 の 225 試行のうち 188 が carried out なので、汚染のない版に残る S6 は多くて 37。おそらく大半は速い速さで、続く 184 試行も外れる。
    - 書字研究の中心である修正（C3 "the number of backspaces/deletes"）を含む場面を、読者は再重み付けで表せない。
    - この版は句のあいだの持ち越しの不一致も外す。自然な書字で S6 のような直しがあれば、持ち越しは起きる。そのぶんを含まない値であることが、読者に伝わらない。
    - 空の層は出力から消えるだけで、§6.11 の「null with the reason」と合わない。
  - 解消の条件:
    - §6.7 に、§3.1 の予測から汚染のない版の場面と速さごとの試行の数を書く（少なくとも S6・S13）。
    - そこで空の層は重み付けし直せないこと、再重み付けの値が句のあいだの持ち越しを含まないこと（その場面は全試行の版と並べて読むこと）を書く。
    - `per_trial` は空の層を null と理由で出すか、§6.11 に例外として書く。
  - 自信: 中（188・184 は予測値。汚染のない版での S6 の速さごとの数は推定）

- [severity: minor] **§6.4 の読者向けの文は、打ち切りが 4 つの量をどちら向きに動かすかを書かず、同じログの key 行で分かることも書かない**
  - 位置と引用:
    - §6.4 L578–582 「The effect of the cut-off on a researcher's aggregates follows from the rule stated in section 1.1. An observer's log does not show which sessions were cut off, because they have no row, so a reader who wants to apply the rule to their own data has to estimate from another source how often a conversion lasts 20 seconds or more」
    - §1.1 L25–27 「that press then starts afresh, so a letter or digit opens a new session」
  - なぜ問題か:
    - 規則からは次のことが言える。20 秒以上の変換は行を残さないが、打ち切った打鍵から短い断片の行が出うる。平均の変換時間と時間の割合は下がり、件数は減るとも変わらないとも言えない。この導出を読者に任せている。
    - 書字研究者は長い時間を刈り込むことに慣れている（C4 "all values above the 95th percentile were removed"）。打ち切りが刈り込みと違うのは、件数からも消え、断片を足しうる点で、読者が要るのはまさにこの差である。
    - 同じログの key 行には、全打鍵の分類と時刻がある。どのセッション行にも覆われない文字の連なりの後に 20 秒以上の空きがあれば、打ち切りの候補になる。macOS ではモードの切り替えが key 行に残らないので近似にとどまるが、それでも「another source」でしか分からない、というのは言い過ぎである。
    - §7 L854–859 には同じ文が入っていない（既知の入れ漏れ）。
  - 解消の条件:
    - 4 つの量ごとに、打ち切りが動かす向きを 1 文ずつ書く。
    - key 行からの近似の手がかりと、その限界（モードの切り替えが見えない）を書くか、使えない理由を書く。
    - §7 にも参照を足す。
  - 自信: 中（key 行から近似できるという点は低め）

- [severity: minor] **§3.1 の合わせ直しの約束は、どの run を・どの印で回し・結果を何に使うかを書いていない**
  - 位置と引用:
    - §3.1 L220–222 「Before the freeze, the assignment of observed key presses to trials that both attacks of question 4 use (section 6.8) is run, without any attack, on the key rows of the pilot's observation logs, and the fraction of blocks it scores is reported here.」
    - §3.1 L194–195 「(F13, F14, F13 in the first pilot and `left`, `right`, `left` from then on)」
    - `pilot-macos.md`:162–163 「The three-key marker of the pilot cannot be told apart from the three arrow presses in a row that scenario S7 may make.」
  - なぜ問題か:
    - 最初のパイロットの印（F13/F14）は macOS で行を残さないので錨が無く、全ブロックが採点されない（README:171–173）。この結果はコードについて何も言わない。
    - その後のパイロットの 3 打鍵の矢印の印は S7 と紛れるので、測定（4 打鍵）とは違う条件での値になる。
    - 結果の使い方（診断だけか、ある割合を下回れば凍結の前にコードを直すのか）が無いと、数を見てから意味づけることになる。
  - 解消の条件:
    - 対象の run（例: pilot2-on/off）と、渡す印（3 打鍵の矢印）を名指す。
    - その数が、パイロットの印の下でのコードの診断であることを書く。
    - 凍結までにその数から何が決まるか（決まらないなら、そう書く）を書く。
  - 自信: 中

- [severity: nit] **§6.7 の「none of the four layers」は §6.4 の層の定義と矛盾する**
  - 位置と引用:
    - §6.7 L676 「As a diagnostic, they are also reported over the trials in none of the four layers.」
    - §6.4 L603–605 「four layers from the prediction: carried out, received carry, closing key in reading, and the trials in none of the three」
  - なぜ問題か: 4 つ目の層が「3 つのどれでもない試行」なので、4 つのどれでもない試行は定義上存在しない。コード（`l2.py`:116–117）は「3 つの印のどれも無い試行」を意味している。
  - 解消の条件: 「the trials in none of the three marks (the fourth layer of section 6.4)」に直す。
  - 自信: 高

- [severity: nit] **§6.8 の「Presses outside every block are counted」と、出力の数が指すものが違う**
  - 位置と引用:
    - §6.8 L692 「Presses outside every block are counted.」
    - `closed_set.py`:620–621 「n_unassigned is the number of presses that no placed block covers (stray presses, the presses of unscored blocks, presses after the last block)」
  - なぜ問題か: 出力の数には、採点しなかったブロックの打鍵も入る。§6.8 の文だけでは、それが分からない。
  - 解消の条件: 「Presses that no scored block covers (including those of unscored blocks) are counted.」に直す。
  - 自信: 高

- [severity: nit] **§3.3 の「usually near 1」は、ブロック内の相関 ρ が小さいことを根拠なしに仮定している**
  - 位置と引用: §3.3 L324–325 「D is therefore at most about 3.4 and usually near 1」
  - なぜ問題か: Σm²/Σm が 2.4〜3.4 なので、D が 1 に近いのは ρ が小さいときだけである。その根拠（パイロットでは一致を計算していない）が無い。
  - 解消の条件: 「near 1 when rho is small」とする。
  - 自信: 中

## 5. 総合の推奨: **major**（再査読は §3.4 と §6.7 に絞ってよい）

1. round 3 の 2 つの major のうち、B は解消した。A は偏りの側で解消し、ばらつきの側（テキストの実効の大きさ）に残った。
2. 新しい §3.4 の閉じた中止の規則は、閾値が確かめていない前提に立つ。外れれば、3 晩とも機械的に中止になるか、外からの打鍵を通すかのどちらかになる。パイロットの参照のログで、凍結の前に確かめられる。
3. 残りは文の直しで足りる。再査読は、§3.4 の閾値（と §3.1 に足す観測値）と、§6.7 のテキストの大きさの規則に絞ってよい。

## 6. 読めなかった範囲と、注入の疑い

**読んでいない（この 25 分で開いていない）もの**
- 事前登録の §2（L82–183。round 3 から変わっていない節）。
- 第 1 群のうち次のファイル: `gt_rules.json`・`SEED`・`run.sh`・`env.md`・`kit\gen\README.md`・`recipes*.json`・`keymap_macos.json`・`kit\e3`・`kit\pilot`・`kit\logger`・`kit\emit` の README。`kit\refinput-macos\README.md` は grep だけ。
- 第 2 群のうち、次のファイル全体: `pipeline.py`（`_focus_loss` の周辺を grep しただけ）・`gt_sessions.py`・`l1.py`・`stats.py`・`spec_predict.py`・`generate_plan.py`（grep だけ）・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・`open_set.py`・Rust の 3 本。
- 第 2 群のうち、次のファイルの一部: `l2.py` の 335–553 行・889 行以降（selftest）、`match.py` の 700–756 行より外、`delivery.py` の 80–260 行・449 行以降、`closed_set.py` の 560–720 行より外。
- 接地の 2 本は、上に引いた範囲だけ。

**注入の疑い:** なし。読んだ範囲に、査読者や LLM に向けた指示は無かった。
