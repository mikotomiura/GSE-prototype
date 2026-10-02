# round 5 査読（BRM・打鍵記録を使う書字研究の利用者／ログの公開のサイドチャネルに通じた立場・stage `prereg`）

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（context-A の SHA-256 `d6e7dbf6…` の版）。round 4 から変わった節・公開物・コードに絞って読んだ。

## 1. 接地（2 本とも逐語で抜き出せたので、査読に入った）

- **C1（指標と問いの対応）** Conijn et al. (2019), conijn2019.txt:84-88: "The selection of the correct keystroke features is crucial for the interpretation of the results and therefore, the derived conclusions."
  → 求めること: 報告する量が、書字研究の読者の問いにどう効くかが分かること。
- **C2（設計の値を一般化しない）** Conijn et al. (2019), :808-811: "caution should be taken when generalizing the effect of these features across tasks, because these features might differ merely as a result of the task, rather than as a result of the variable of interest"
  → 求めること: 設計に固有の値（k や long の割合）を、設計の性質として明示すること。
- **C3（除外の閾値を明示する）** Conijn et al. (2019), :298-299: "seven sessions were excluded where the number of keystrokes was smaller than 600 or the number of words was smaller than 50"
  → 求めること: 除外と中止の規則を、閾値つきで 1 通りに書くこと。
- **C4（多因子性）** Conijn et al. (2019), :80-81: "Keystroke features may be multiply determined, and are sensitive to a variety of factors."
- **M1（時刻が漏らす）** Monaco (2018), monaco2018.txt:17-22: "a temporal side channel leverages key press and release timings" / "nontrivial information gains can be achieved even in the presence of substantial measurement error"
  → 求めること: 公開するログの時刻は、粗くしても漏れうる前提で扱うこと。
- **M2（検出が先）** Monaco (2018), :1143-1145: "Since keystroke detection is a prerequisite for key identiﬁcation, a defense that mitigates the former is also generally effective against the latter."
  → 求めること: 人の打鍵が預けるログに入ること自体（検出の段）を断つ規則の、穴の一覧が正確であること。

## 2. 引き継ぎ（carryover-R2.md）の判定

### A. round 4 の新しい指摘

| 指摘 | 判定 | 理由（1 行） | 今の版の位置 |
|---|---|---|---|
| 新 major（閾値 5 の前提・相殺） | **解消** | ブロックの区間ごとに数えるようになった。k = 0 とモードキーの扱いはパイロットで決め、fail-safe の向き（「it cannot let a press from outside pass」）。相殺は限界として書いた | §3.4「Presses from outside.」・§3.1 2 つ目の項目・§7「The stopping rule counts presses, not keys」・`pipeline.py:812-826` |
| 新 minor-k | **解消** | k の分布を開示し、速さのあいだで比べないこと、テキストに等しい重みを掛けることを書いた。数（603 試行・平均 4.60）は §3.3 の表と整合する | §6.7 第 1 段落・§7 打ち切りの項 |
| 新 minor-S6 | **解消** | S6 と S13 は null と理由で出す。コードは `status: no_trial` と `trials_not_used` を持つ | §6.7 第 2 段落・`l2.py:106-111` |
| 新 minor-§6.4 | **解消** | key 行は候補を示すが確定できないこと、4 つの量が動く向きを書いた | §6.4 Scopes の段落の末尾・§7 |
| 新 minor-§3.1 | **解消** | 対象の run・引数・結果・使い道を書き、「再同期は試されていない」とも書いた。15 ブロック・282 試行（126+117+39）は数が合う | §3.1 1 つ目の項目 |
| nit（none の層） | 解消 | 「the trials of the layer none (section 6.4)」になった | §6.7 末 |
| nit（Presses outside every block） | 解消 | 「Presses that no scored block covers (including those of unscored blocks)」になった | §6.8 |
| nit（usually near 1） | 解消 | 「near 1 only when rho is small」になった | §3.3 |

### B. round 4 で「部分的に解消／未解消」とした前の指摘

| 指摘 | 判定 | 理由（1 行） | 今の版の位置 |
|---|---|---|---|
| A・新 3（問 3 の主が long の割合に依存） | **解消** | 偏りの側は round 4 で解消済み。限界・ICC の側は k の開示で閉じた | §6.7・§7 |
| minor 3（打ち切りの規則を読者のデータに当てる） | **解消** | key 行の候補と、確定できない理由を書いた | §6.4 |
| minor 6（合わせ直しを実ログで試していない） | **部分的に解消** | 実ログに欠けも足しも無く、再同期は selftest でしか試されていないと正直に開示した。パイロットの key 行に欠けや重複を人工的に入れて試すことは、まだしていない | §3.1 1 つ目の項目・§6.8 |
| minor-7（パイロットの生ログを預ける基準） | **解消** | 本計測と揃えた基準を凍結の前に書き、7 run に当てた。ただし穴の一覧が §7 と食い違う（新しい指摘 3） | `pilot-macos.md` Raw logs |
| nit 3（冗長さ） | **部分的に解消** | §7 の 1 項は縮めたが、本文は +21%。増えた分の多くは規則の経緯 | 新しい指摘 6 |
| major-3・major-4・minor-5（セッション行の公開の形・中間の粒度） | 未解消（採らなかった・round 1 から） | round 4 までの判定のまま | §6.8 |

### C. 共通の変更（引き継ぎに書いた理由が成り立つか）

- **C1（runner が中止した run にも点検を当てる）**: 理由は成り立つ。中止は人の介入と相関しうる。
  - ただし、中止した run には、預ける点検の中の content-free の検査が当たらない（`pipeline.py:1025`「if not run["aborted"]」、docstring の (e)「for a run that was not aborted」）。`data.md` の手順 4 はこの但し書きを書いていない（新しい指摘 5）。
- **C2（焦点の規則の 2 度の改訂）**: 理由は成り立つ。
  - 喪失ごとに中止すると、87 分に 1 回の観測から約 12 時間の run の多くが止まる（観測は 1 回なので幅は大きい）。
  - 実行器は喪失の間も打鍵を送るので、2 度目の改訂も必要。
  - ただし、2 度目の改訂で入れた 100 ms の前窓は、区間の始まりの側に系統的な抜けを作り（新しい指摘 1）、パイロットの実測で裏づけられていない（新しい指摘 2）。

## 3. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | §3.1 の数は互いに合う。<br>・S14 の 18・18・6 は S14 の試行の数 × 2。<br>・15 ブロック＝6+6+3。<br>・§3.3 の slow の主の層の和 603 は §6.7 の平均 k 4.60 と合う。<br>ただし §2.1「section 7 states what they do not catch」は、§7 の一覧が欠けているので言い過ぎ（新しい指摘 1・3・4）。 |
| b 方法の穴 | 4（round 4 の major が解消して上がった） | 区間ごとの規則と、喪失の中で送った打鍵を差し引く規則で、人の打鍵の入口はほぼ閉じた。残る穴は 1 区間あたり 1〜2 打鍵の規模か、手順の境界（idle・S15 の計画した 1 秒・中止した run）にある。 |
| c 持ち帰れるもの | 4 | k の開示と §6.4 の読者向けの文は、読者が自分のデータに当てられる形になった。<br>一方、per-text の限界を自分のテキストの長さ（k が数十〜数百）へ持ち帰る道筋は無い（新しい指摘 8）。<br>§3.4 の装置は読者が持ち帰るものではなく、分量に見合わない（d）。 |
| d 簡潔さと構成 | 2 | 14,665 語（+21%）。§3.1 に規則の改訂の経緯（最初の版・78%）が、§3.4 に規則の理由づけが本文として入った。<br>同じ規則を §3.4・`data.md` 手順 1・`pilot-macos.md` Raw logs・`pipeline.py` docstring の 4 か所で言い直しており、すでにずれている（新しい指摘 3）。 |
| e 規程への適合 | 4 | 除外・中止を前もって固定している（J9）。<br>安全を理由に預けない run がある点は、J4 の「without breaching participant confidentiality」と両立する。<br>ただし預けない run の配送の数を報告しても、その根拠を読者が確かめられない（新しい指摘 9・J2）。 |
| f 先行研究の位置づけ | 3 | 今回変わった箇所に、先行研究の位置づけに関わる変更は無い（References は 9 件のまま）。round 4 までの判定のまま。 |
| g 固定の十分さ | 4 | k = 0・版 `excluding_mode_keys`・500 ms・100 ms・pre 20 / tail 300 が、文と定数で 1 通りに決まっている（`pipeline.py:219-226`・`delivery.py:144,148`）。<br>ただし 100 ms は値の根拠が書かれていない（新しい指摘 2）。 |

## 4. 新しい指摘（severity の重い順。round 1〜4 の再掲は無い）

- **[minor] 1. 焦点の規則の 100 ms の前窓が、区間の始まりに系統的な抜けを作るのに、どこにも書かれていない**
  - 位置と引用:
    - §3.4「counted from 100 ms before the span to its end, so that a press sent just before the span whose row falls inside it is matched」
    - `delivery.py:409-410`（行は `within(t, (a, b))`、送った打鍵は `within(t, (a - OBS_SEND_DELAY_MS, b))`）
    - §7「so does a press sent within the last 100 ms of the span whose row falls after it」
  - なぜ問題か:
    - key 行の時刻は tap の受け取りの時刻で（`driver_macos.rs:250` `wall_ms()`・§4.5）、遅れはふつう数 ms。
    - そのため [a−100, a) に送られた打鍵の多くは、行が a より前に落ちる。送った数には入るが行には入らず、区間ごとに人の打鍵をその数だけ隠す。
    - 期待値の目安は、fast で約 0.8、mid で約 0.4、slow で約 0.2 打鍵（区間の始まりが打っている最中のとき）。区間の終わりの側（§7 が書いた側）より、始まりの側の方が頻繁に起きる。
    - §7・`delivery.py` docstring の Blind spots・`pilot-macos.md` は、どれもこれを挙げていない。
    - 隠れるのは 1〜2 打鍵の区分と時刻で中身は小さいが、M2「keystroke detection is a prerequisite」の段で、穴の一覧が不正確になっている。
  - 解消の条件: どちらか。
    - (a) 行と送った打鍵を 1 対 1 で照合する（各行に、[行−100 ms, 行] の中の未使用の送った打鍵を当てる）。対応の無い行を数え、selftest に始まりの側の場合を足す。
    - (b) 今の数え方のまま、§7・docstring・`pilot-macos.md` に「区間の始まりの前 100 ms に送られ、行が区間の外に落ちた打鍵の数だけ人の打鍵が隠れる」と書く。
  - 自信: 高

- **[minor] 2. 100 ms の値がパイロットの実測で裏づけられておらず、遅れが 100 ms を超えたときの誤った中止も §7 に無い**
  - 位置と引用:
    - §3.4「counted from 100 ms before the span」
    - `delivery.py:145-148`「The expected delay from the sending of a key by the executor to the row of the observation log」
    - §3.1 の 2 つ目の項目は、同じ配送の報告から多くの数を引くが、観測の行の遅れ（`observation.timing.delay_ms`・`delivery.py:503-519`）は引いていない
  - なぜ問題か:
    - 100 ms は規則を決める定数なのに、手元にある実測（パイロットの 3 run の delay_ms の p95・最大）が本文に無い。
    - 遅れが 100 ms を超えると、区間の外で送った打鍵の行が区間に入り、人がいなくても中止になる。中止は試行の繰り返しを呼び、その分の学習も残る（§7「also through attempts that are repeated」）。
    - §7 は誤った中止の原因として観測器の重複行しか挙げていない。
  - 解消の条件:
    - §3.1 に、パイロットの観測の行の遅れ（p95・最大）を書き、100 ms がそれを上回ることを示す。
    - §7 に「遅れが 100 ms を超えた行は、人がいなくても中止にしうる」を足す。
  - 自信: 高

- **[minor] 3. 規則が捕まえないものの一覧が §7 で欠け、`pilot-macos.md` とも食い違う（S15 の計画した切り替えの窓）**
  - 位置と引用:
    - §2.1「the rules of section 3.4 set aside a run whose logs show a sign of a person's key presses (section 7 states what they do not catch)」
    - §3.4「other than in the planned switch of S15」
    - `pilot-macos.md:187-188`「Their blind spots are those of the measurement (section 7 of the pre-registration): a press from outside that replaces a press that was lost, and a shortcut that the system consumes without moving the focus.」
  - なぜ問題か:
    - 計画した S15 の喪失（各セルで S15 の試行ごとに約 1 秒・数百回）の中では、人が別のアプリに打っても、どちらの規則にも掛からない。§7 の新しい項はこれを挙げていない。
    - `pilot-macos.md` は穴を 2 つだけ挙げて「those of the measurement」と言う。喪失の区間の中の取りこぼし、終わりの 100 ms、キーを押さずに焦点を移す人、指摘 1 の始まりの側が抜けている。4 か所で言い直した結果、文書のあいだでずれが生じている。
  - 解消の条件:
    - §7 の項に「S15 の計画した切り替えの間の打鍵は、どちらの規則にも掛からない」を足す。
    - `pilot-macos.md` は列挙をやめて「section 7 の項 "The stopping rule counts presses, not keys" に挙げたもの」と参照だけにする。
  - 自信: 高

- **[minor] 4. `idle` の条件の観測のログは、規則の外にあり、人の打鍵を必ず含みうるのに、預けるかどうかが書かれていない**
  - 位置と引用:
    - §3.4「the `idle` condition sends no key and has no plan」
    - `kit\e3\README.md:103-109`「`idle`: start the observer (only one), then `bash run_e3.sh idle 28800 30 runs/e3-idle` and leave the keyboard and the pointer alone.」
  - なぜ問題か:
    - 手順のとおりなら、観測器を起動した後に研究者が `run_e3.sh` の命令を打つ。
    - 観測器は機械のすべての打鍵の区分と時刻を記録する（§3.4「the observation records every key press on the machine」）ので、`idle` の観測のログには人の打鍵が入る。
    - 規則は当たらず、預けるかどうかも書かれていない。§2.1「no person's typing is part of the data」が `idle` の観測のログにも及ぶのかどうかが、閉じていない（M1）。
  - 解消の条件: どちらか。
    - (a) §3.4 か §6.10 に「`idle` の観測のログは預けない（預けるのは標本の `samples.tsv` だけ）」と書く。
    - (b) 預けるなら、採った窓の中に key 行が 0 であることを預ける条件にする（窓の外は切り落とす）。
  - 自信: 中（預けるかどうかを述べた文を、読んだ範囲で見つけられなかった）

- **[minor] 5. 中止した run は預けられるようになったが、content-free の検査が当たらない。`data.md` はそれを書かず、途中で止めた run はほぼ必ず拒まれることも書かない**
  - 位置と引用:
    - `pipeline.py:1025-1026`「if not run["aborted"]: out += _content_free(run, name)」・docstring:123-124「(e) content in the ground-truth or observation log (the content-free validator), for a run that was not aborted」
    - `data.md` 手順 4「The command refuses … content in the ground-truth or observation log, and a run, completed or aborted by the runner, that the rules of section 3.4 … catch」
    - §3.4「it is deposited only if the check passes」
  - なぜ問題か:
    - C1 で中止した run も預ける経路ができたのに、文字を含まないことの検査はその run に当たらない。`data.md` の文は、すべての run に当たるように読める。
    - また `_segments` は trial_end のある試行の押下しか説明に数えない（`delivery.py:534-537`）。試行の途中で止めた run は、参照に届いた押下が「説明されない」に数えられ、ほぼ必ず拒まれる。これは安全の側に倒れているが、読者は「通れば預ける」から、多くの中止した run が預けられると期待しうる。
  - 解消の条件:
    - content-free の検査を、中止した run にも当てる（途中で切れた最後の行だけを許すなど）。そうしないなら、`data.md` 手順 4 と §3.4 にその但し書きを書く。
    - 「試行の途中で止めた run は、届いた押下が説明されず預けない」と 1 文書く。
  - 自信: 高（コード）・中（意図）

- **[minor] 6. 規則の経緯と理由づけが本文を 21% 膨らませ、同じ規則を 4 か所で言い直している**
  - 位置と引用:
    - §3.1「A first version of the change counted every key row within the loss; in the oracles built from the measurement plans (above), about 78% of the time of a run lies within 500 ms of a press sent …」
    - §3.1「The least time between the last key-down of a segment and the start of the next block was 1,582 ms.」（k = 0 の下では、どの決定にも使われない）
    - §3.4 の「Loss of focus.」の段落の後半と、§3.4 末の段落
  - なぜ問題か:
    - 事前登録が固定すべきなのは、規則・設定・その根拠の所在。2 度の改訂の経緯と、決定に効かない数は、パイロットの報告の仕事である。
    - 書字研究の読者にとって、この装置（人が加わらない合成入力の預ける安全）は持ち帰るものではない。
    - 4 か所の言い直しは、指摘 3 のずれをすでに生んでいる（C1「crucial for the interpretation」の対偶として、読者の問いに効かない分量は削る）。
  - 解消の条件:
    - §3.4 は、規則・定数・命令行・k と版の決定の 1 文に絞る。改訂の経緯（喪失 1 回・78%・最初の版）と 1,582 ms・「within 3 seconds」は `pilot-macos.md` へ移す。
    - `data.md` 手順 1 と `pilot-macos.md` Raw logs は、規則を言い直さず §3.4 を参照する（表の列名と閾値だけ残す）。
  - 自信: 中

- **[nit] 7. §3.4 の「the delay with which the observation collects a row」は、key 行には当たらない**
  - 位置と引用: §3.4「the margin covers the offset between the clocks of the two logs, the delay with which the observation collects a row, and a key that moves the focus」
  - なぜ問題か: 「行を集める遅れ（約 100 ms）」はセッション行の `t` の性質（§4.4）。規則が数える key 行の時刻は、tap の受け取りの時刻（§4.5・`driver_macos.rs:244-251`）。指摘 2 の 100 ms と混同されやすい。
  - 解消の条件: 「the delay from the sending of a key to its row in the observation」に直す。
  - 自信: 中

- **[nit] 8. k の開示は限界として正しいが、読者が自分のテキストの長さへ持ち帰る道筋が無い**
  - 位置と引用: §6.7「the limits of agreement and the ICC of the primary scope hold for this design's distribution of k and are not compared between speeds」
  - なぜ問題か: 書字研究のテキストは数十〜数百の変換を持つ。k が 4.6〜7.2 の per-text の限界は、そのままでは使えない（C2）。§6.7 の第 2 段落の per-trial の差は、その換算の材料になりうるが、そうは書かれていない。
  - 解消の条件: どちらか 1 文を書く。
    - 「別の長さのテキストへの換算は per-trial の差から読者が行う（ブロックの中の依存のため下限）」
    - 「この設計の k を超えて外挿しない」
  - 自信: 中

- **[nit] 9. 中止に数えた run の配送の数は報告されるのに、その根拠を確かめる手段を預けない。また、預けない理由の文が計画の SHA-256 の理由に合わない**
  - 位置と引用:
    - §3.4「Aborted runs are reported with their reason and their delivery figures」
    - §3.4「A completed run that counts as aborted for any of these reasons is not deposited, because its reference log records the key code of every key-down …」
  - なぜ問題か:
    - 配送の報告（`delivery.py` の JSON）は数と要約だけで、鍵コードも行ごとの時刻も持たない。代わりに預ければ、報告した数を読者が確かめられる（J2）。
    - 計画の SHA-256 の違いだけで中止になった run には、「人の打鍵を含みうる」という理由が当たらない。また、計画の SHA-256 の照合は `--check-deposit` に無く、`data.md` 手順 1 の目視だけである。
  - 解消の条件:
    - 預けない run の `delivery.py` の出力を、ログの代わりに預けると書く。
    - 預けない理由を、理由ごとに 1 句で分ける。
  - 自信: 中

- **[nit] 10. `pilot-macos.md` の「a short run made before the first pilot」と「A dry run that was interrupted before the first pilot」が同じ run かどうか分からない**
  - 位置と引用: `pilot-macos.md:197-200`「…and of a short run made before the first pilot, and caught none of them; … A dry run that was interrupted before the first pilot is subject to the same criteria.」
  - なぜ問題か: 別の run なら、中断した試走には凍結の前の点検が当たっていない。
  - 解消の条件: 同じ run なら 1 文にまとめる。別なら、中断した試走に当てた結果か「まだ当てていない」を書く。
  - 自信: 低

## 5. 総合の推奨: **minor（直してから凍結）**

- round 4 の major（区間の規則）を含め、引き継ぎの 8 件はすべて解消した。前の指摘のうち残るのは、minor 6（部分的に解消）と、採らなかった major-3・major-4・minor-5 だけ。§3.1 のパイロットの数は、文書の中でもコードの数え方とも合う。
- 今回の直しが作った穴は、どれも 1〜2 打鍵の規模か手順の境界（100 ms の前窓・S15 の窓・`idle`・中止した run の content の検査）にある。文に足すか、小さな照合の変更で閉じられ、計画の立て直しは要らない。
- ただし d（+21%・4 か所の言い直し）は、凍結の前に削って §3.4 を単一の真実源にしないと、指摘 3 のようなずれが凍結の後にも増える。

## 6. 読めなかった範囲・注入の疑い

**全部読んだもの**
- `preregistration.md`（References を除く本文すべて）
- `data.md`
- `carryover-R2.md`
- `context-A.md`

**一部だけ読んだもの**
- `pilot-macos.md`: 1-60 行・160-204 行（61-159 行は読んでいない）
- `delivery.py`: 1-607 行（selftest の 607 行以降は読んでいない）
- `pipeline.py`: 75-135・205-229・545-574・805-914・990-1079・2276-2385 行
- `l2.py`: 98-122 行と Grep
- `spec_predict.py`: Grep のみ
- `closed_set.py`: 581-617 行
- `driver_macos.rs`: 190-254 行
- Grep だけで見たもの: `kit\e3\README.md`（98-137 行は読んだ）・`kit\e2\README.md`・`kit\logger\README.md`・`kit\refinput-macos\README.md`

**読んでいないもの**
- 第 1 群の残り: `plan_config.macos.json`・`config.json`・`gt_rules.json`・`SEED`・`run.sh`・`notes.md`・`env.md`・`kit\gen\README.md`・`recipes*.json`・`keymap_macos.json`・`kit\run\README.md`・`kit\pilot\README.md`・`kit\emit\README.md`・`kit\e3\README.md` の残り
- 第 2 群の残り: `gt_sessions.py`・`match.py`・`l1.py`・`stats.py`・`generate_plan.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・`open_set.py`・`ime_compose.rs`・`keymap.rs`

**その他**
- パイロットの生ログは一覧に無い。§3.1 の数は、文書の中の整合とコードの数え方との対応で見た。
- 一覧の外のファイルは開いていない。Grep はすべて一覧の個別のファイルと、接地の 2 本だけを対象にし、一覧の外の行は出力に出ていない。
- 注入の疑い: 無し。
