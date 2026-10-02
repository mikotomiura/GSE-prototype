# R1 の査読 round 5（BRM・打鍵の時刻を測る道具を外部の基準で検証してきた方法論の立場／下位人格: 懐疑家）

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（`ba89bcbd`・未凍結の下書き）。round 4 から変わった箇所に絞った。変わっていない節は round 4 までの判定のまま。

## 1. 接地（この立場が論文に求める基準）

3 本とも読めた（読んだ範囲は §6 に書く）。

- **S1 基準は測られる系から独立していて、人が介在しない合成の入力で確かめる。**
  - Pinet et al. (2017): "we also measured the objective timing accuracy of the jsPsych interface by using specialized hardware and software"
  - 同: "three response switches from the keyboard could be alternatively and variably triggered without human intervention"
- **S2 OS の中間の層は記録に干渉しうる。その影響は分からないものとして扱う。**
  - Pinet et al. (2017): "operating system (OS) settings, such as accessibility features or keyboard hotkeys, might potentially interfere in a detectable way with the recordings"
  - 同: "The impact of this intermediate layer of software on keyboard chronometry is not known."
- **S3 その場で、自分の機材で、研究を行うその時に確かめる。誤差は最初に知っておく。**
  - Plant (2016): "The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter's own equipment, at the time a given study is carried out."
  - 同: "Knowing one's error at the outset is something that the vast majority of researchers cannot currently attest to."
- **S4 ログ（ソフトウェアの自己申告）が正常に見えても、それは信頼の根拠にならない。**
  - Plant (2016): "Worryingly the log files suggested that the test had run normally imbuing an unwarranted confidence in the experiment, equipment, and software used."
- **S5 研究ごとに、その組み合わせで確かめる。一般的な確認で代えない。**
  - Bridges et al. (2020): "We would like to stress, once again, the importance of testing timing for every study, with the particular combination of stimuli, operating system and hardware used in that study."
  - 同: "Papers such as this one, which report “best case” timing performance, should not be used in lieu of study-specific validation and testing."
- **S6 独立した検証があって初めて、期待どおりでないことを検出できる。**
  - Bridges et al. (2020): "by validating the timing independently with dedicated hardware, we could detect when timing was not as good as expected"

## 2. 引き継ぎの判定（carryover-R1.md）

### A. round 4 の新しい指摘

| 指摘 | 判定 | 理由（1 行） | 今の版の位置 |
|---|---|---|---|
| 新-1 [major] かなキーで規則が発火しうる | **解消** | 区間は `block_begin` で切る半開区間で、試行の窓はそれをまたがない（`_windows` が次の oracle の行で切る）。k はパイロットの直接の観測から決めた（最初の区間 0 行・各区間の余りは印ちょうど・6 run で 27 回）。k = 0 なので、かなキーが残れば必ず中止になる | §3.4「Presses from outside」・§3.1 の 2 つ目の項目・`pipeline.py:219,224`・`delivery.py:_segments` |
| 新-2 [minor] 閉じた規則がコードで強制されない | **部分的に解消** | 2 つの閉じた規則は `analyse`（exit 2）と `--pack` / `--check-deposit` が強制する。計画の SHA-256 は手の照合のまま。「config.json に足すと形式が変わる」という理由は、pipeline が既に事前登録の本文を読んでいる（`check_prereg_text`）ので、§2.4 の 2 つの値をそこから照合する道を塞いでいない | §3.4・§5・`data.md` 手順 1・`pipeline.py:904-907,1027` |
| 新-3 [minor] §6.3 が §3.4 より広い | **解消** | 「decided by the rules of section 3.4 alone」 | §6.3 末尾 |
| 新-4 [minor] 1 つの欠けで 2 ブロックを失う | **解消** | `_is_anchor` が右の端で錨を探す。§6.8・README・selftest が揃っている。実ログで再同期を試していないことも開示した。コードを論理で追った範囲でも、欠け・足し・印の損傷・2 ブロック連続の損傷で、失うのは該当のブロックだけ | §6.8 第 2 段落・`closed_set.py:581-648`・`kit\e2\README.md:202-208` |
| 新-5 [nit] | **解消** | 「the trials of the layer none (section 6.4)」 | §6.7 末尾 |
| 新-6 [nit] | **解消** | 2 文に分けた。対象の run・引数・結果・修正したときの扱いを書いた | §3.1 |
| 新-7 [nit] | **解消** | 主の範囲の Σm²/Σm 3.05 / 3.22 と「near 1 only when rho is small」。表の合計（603/852/940・553/783/876）、k の平均（4.60 等 × テキスト数 ≈ 主の範囲の試行 − ブロックの余り）とも整合した | §3.3・§6.7・`spec_predict.py:plan_figures` |
| 新-8 [nit] | **解消** | `idle` を点検の対象から外すことを明記した（ただし新しい指摘 n-2 を参照） | §3.2・§3.4 |

### B. round 4 で「部分的に解消」とした指摘

- **m11 パイロットの生ログを預ける基準: 解消。** `pilot-macos.md` の Raw logs（178-200 行）に、候補・規則・`--check-deposit`・封印を開ける条件を書いた。凍結の前に 7 run へ当てた結果もある。
- **n3 解析コードの同一性: 部分的に解消（round 4 から変わらない）。** 研究者の選択として扱う。

### C. 共通の変更（引き継ぎに書いた理由が成り立つか）

- **C1（runner が中止した run にも点検を当てる）: 理由は成り立つ。** Ctrl+C は端末へ焦点を移して打つので、喪失の規則に掛かる。ただし、試行の途中で中止した run は、人がいなくても打鍵の規則に当たる。中途の試行を `done` から外すためである（新しい指摘 m-4）。
- **C2（焦点の規則を 2 度改めた）: 改めた理由は 2 つとも成り立つ。**
  - 87 分に 1 回なら、12 時間で約 8 回になる。ただし観測は 1 回なので、率の 95% 区間はおおよそ 0.2〜46 回 / 12 h と広い。
  - 規則の時間の約 78% が送った打鍵の 500 ms 以内にある、という数字も、改めた理由として成り立つ。
  - ただし最後の版は、最初の版の「計画した S15 の喪失は対象の外」という分け方を残した。数で比べる規則にはこの分け方が要らないので、新しい盲点を作った（M-1）。100 ms の定数も、key 行の遅れに錨づけていない（m-2）。

## 3. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | §3.1 のパイロットの数はたがいに整合する（15 ブロック・282 試行 = 126+117+39・15 回のかなキー・届かない 18/18/6 = S14 の試行 × 2・6 run で 27 ブロック・約 87 分 ≈ 468 試行 × 約 11 秒）。数とコードが数えるもの（`_segments` の n_unexplained・`_reach`）も対応する。ただし §2.1 の「section 7 states what they do not catch」は、§7 の盲点の一覧が網羅的だと主張している。実装には一覧に無い盲点が 2 つある（M-1・m-2） |
| b 方法の穴 | 4 | 区間の規則そのものは閉じている。かなキー・モードキー・最初と最後の区間・`block_begin` ちょうどの行も、文とコードが一致する。新しい穴はいずれも狭いが、プライバシーのための規則の網羅性の主張に関わる（M-1・m-2・m-3・m-4） |
| c 持ち帰れるもの | 4 | round 4 から変わらない |
| d 簡潔さと構成 | 3 | 本文は 21% 増えた。§3.1 に規則の改訂の経緯が長く入り、§3.4 は 1 段落が密である。規則の定義（§3.4）と、それをパイロットで決めた経緯（§3.1）の分け方は保たれている |
| e 規程への適合 | 4 | J9（除外と中止を前もって固定する）と J4（生データの公開）は、預ける基準・点検できない run の扱い・パイロットの基準まで書かれ、強まった。runner が中止した run の内容の点検の扱いだけ、文とコードがずれる（n-1） |
| f 先行研究の位置づけ | 3 | round 4 から変わらない（設計効果の式の出典は足さない選択） |
| g 固定の十分さ | 4 | k・版・`--pre-ms 20 --tail-ms 300`・500 ms・100 ms はコードの定数として固定され、`abort_rule` に記録される。計画の SHA-256 は手の照合。100 ms はパイロットで測れた量に錨づけていない（m-2） |

## 4. 新しい指摘（重い順・round 1〜4 の再掲は入れない）

- **[severity: minor] M-1 計画した S15 の窓の中の喪失を数えないので、S15 の試行の窓が丸ごと喪失の規則の盲点になる（§7 に無い）**
  - 位置と引用:
    - §3.4（423-424 行）「within a loss of focus of the reference input field other than a planned switch of S15 (a loss that begins and ends inside the interval of an S15 trial)」
    - `delivery.py:388-392`: `spans` は `planned` でない喪失だけから作る。`planned` は「S15 の試行の窓の中で始まって終わる喪失」すべてで、計画した 1 秒の切り替えに限らない。
    - selftest `delivery.py:1160-1161` は、送っていない観測の行（1300）が計画した切り替えの中にあっても `(0, 0, 0)` になることを期待値として固定している（"unexplained: a planned switch of S15 is not a span"）。
    - §2.1（87-88 行）「(section 7 states what they do not catch)」と比べると、§7 の「The stopping rule counts presses, not keys」の項（986-995 行）にこの盲点が無い。
  - なぜ問題か:
    - 2 度目の改訂で、規則は「観測の行が送った打鍵より多いか」を数えるものになった。計画した切り替えの間、実行器は打鍵を送らない（§4.5「Presses that send no key event (the switch to another application in S15) are skipped」）。だから数える規則を計画した喪失にも当てても、人がいなければ中止にならない。
    - S15 を外す分け方は、最初の版（喪失ごとに中止）の名残で、今は盲点を作るだけである。次の 2 つの場合、人の打鍵の行は観測のログに入って預けられ、どちらの規則にも掛からない。
      - 人が切り替えの 1 秒の間に、前面にあるアプリに打つ場合。
      - 人が S15 の試行の窓（3 計画で 225 試行・run の数 % の時間）の中で、焦点を移して打って戻す場合。
    - 接地: Plant (2016) 「the log files suggested that the test had run normally imbuing an unwarranted confidence」。点検が「当たらなかった」ことを安全の根拠にするには、何を見ていないかが全部書かれている必要がある。
  - 解消の条件: (a) 数える規則（行の数 > 送った打鍵の数）を計画した喪失にも当て、selftest の期待を逆にする（送っていない行が計画した切り替えの中にあれば中止）。または (b) §7 の項に「S15 の試行の窓の中で始まって終わる喪失の中の打鍵は数えない」と書き、§2.1 の網羅の文と揃える。(a) のほうが安く、閉じる。
  - 自信: 高

- **[severity: minor] m-2 「100 ms 前から数える」は、区間の頭で送った打鍵を余分に差し引く。開示した盲点の逆向きの場合が書かれておらず、定数は key 行の遅れで決めていない**
  - 位置と引用:
    - §3.4（427-432 行）「the margin covers the offset between the clocks of the two logs, the delay with which the observation collects a row, … counted from 100 ms before the span to its end, so that a press sent just before the span whose row falls inside it is matched」
    - `delivery.py:145-148`「The expected delay from the sending of a key by the executor to the row of the observation log」
    - §7（993-994 行）「and so does a press sent within the last 100 ms of the span whose row falls after it」
  - なぜ問題か:
    - 行は [a, b] で数え、送った打鍵は [a − 100, b] で数える。[a − 100, a) に送った打鍵の行が a より前に落ちると、送った打鍵だけが数に入る。そのぶん人の打鍵が隠れる。
    - §4.4 の約 100 ms は**セッションの行**の集め方の遅れである（503-504 行「The time `t` is the time at which the row was collected」）。§4.5（533 行）は、key 行が「the time at which the event reached the observer」を持つとしている。
    - パイロットで測った観測と実行器の差は、ブロック 1〜5 で 0〜3 ms、ブロック 0 だけ 86〜95 ms だった（`pilot-macos.md:122-124`）。したがってブロック 0 以外では、[a − 100, a) に送った打鍵の行は、ほぼ必ず区間の外に落ちる。
    - 隠れる数は区間ごとに、その 100 ms に送った打鍵の数になる。fast で約 0.8、印の打鍵（150 ms 間隔）で約 0.7。開示した側（区間の終わりの直前）は、遅れが数 ms ならほぼ起きない。開示していない側のほうが、ふつうに起きる。
    - 逆に、ブロック 0 の差が測定で 100 ms を超えれば、[a − 差, a − 100) に送った打鍵の行が区間に入る。人がいなくても中止になる（起きる確率は小さい）。
    - 引き継ぎは「100 ms はパイロットの実測で決めていない」と認めている。その遅れはパイロットの配送の報告（`delay_ms`）に既にある。
    - 接地: Plant (2016) 「Knowing one's error at the outset」・Bridges et al. (2020) 「testing … with the particular combination … used in that study」。
  - 解消の条件: (a) パイロットの観測の key 行の遅れ（`observation.timing.delay_ms` の最大と、ブロック 0 の差）を §3.1 に書き、100 ms をそれに錨づける。(b) §7 の項に「区間の前の 100 ms に送られて行が区間より前に落ちる打鍵も、人の打鍵を 1 つ隠す（fast で区間あたり約 1 つ）」を足す。(c) §3.4 の余裕の理由から「the delay with which the observation collects a row」（セッションの行の性質）を外すか、key 行の遅れに言い換える。
  - 自信: 高（仕組み）／中（大きさ。生ログは見ていない）

- **[severity: minor] m-3 2 つの規則の感度（人の打鍵を捕まえること）を測定機で一度も確かめていない。パイロットが示したのは特異度だけ**
  - 位置と引用:
    - `pilot-macos.md:185-187`「The rules rest on two facts: a person's typing into the reference input field leaves key-downs that no sent press explains, and typing into any other application takes the focus away from the reference while the observation records every key press.」
    - §3.1（251-256 行）は、7 run で「当たらなかった」ことだけを報告している。
    - 参照の焦点は key window の変化で記録している（`kit\refinput-macos\README.md:95`「the window becoming or ceasing to be the key window」）。
  - なぜ問題か:
    - 2 つの「facts」は macOS の振る舞いについての前提である。陽性の対照は selftest の合成の行だけで、測定機の上で人が打ったときに規則が発火するかは示されていない。
    - 特に後者は、人が打つ先が必ず参照から key window を奪う、という前提に立つ。他のプロセスのパネル（たとえば key window を奪わずに文字を受けるもの）でこれが成り立つかは確かめていない。
    - §7 の「a shortcut that the system consumes without moving the focus」は、「打った先が別のアプリなのに参照に focus_out が出ない」場合を覆わない。
    - 接地: Plant (2016) 「check it when paradigms are running in-situ, on the experimenter's own equipment」・Bridges et al. (2020) 「we could detect when timing was not as good as expected」（独立した確認だけが、期待どおりでないことを見つける）。Pinet et al. (2017) 「keyboard hotkeys, might potentially interfere」も、OS の層の振る舞いを前提にせず確かめることを求める。
  - 解消の条件: 凍結の前に、測定機で runner の短い run を 1 つ行い、意図して人が打つ。(i) 参照に 1 打鍵、(ii) 別のアプリへ移して数打鍵、(iii) 移らずに文字を受けるシステムの入力（たとえば検索の欄）に数打鍵。それぞれで規則が発火するかを、数だけ §3.1 に報告する（その run は預けない）。発火しない場合は §7 に書く。
  - 自信: 中

- **[severity: minor] m-4 runner が試行の途中で中止した run は、人がいなくても打鍵の規則に当たる。報告する数も「外からの打鍵」と区別できない**
  - 位置と引用:
    - §3.4（448-450 行）「The same check is made on a run that the runner aborted: … it is deposited only if the check passes」
    - `delivery.py:585`: `done` は `trial_end` のある試行だけ。`_segments` の `n_reached` は `done` だけから数える（docstring 39-41 行「over the measured trials」）。
    - 一方、喪失の規則の `sent_times` は、始まったすべての試行から数える（`delivery.py:398`。`trials` を使う）。
    - `data.md` の Run checks の表は、runner が中止した試行にも `beyond_markers_last_block` を書く（25-32 行）。
  - なぜ問題か:
    - 試行の途中で中止すると（子プロセスの停止など。Ctrl+C に限らない）、`trial_end` の無い試行で送った打鍵の参照の key-down が「説明されない」に数えられる。最後のブロックの区間が上限を超え、run は「中止に数える」かつ「預けない」になる。
    - 同じ関数の中で 2 つの規則が中途の試行を違って扱っており、この場合を考えていないしるしである。
    - 書いてある預け方（点検が通れば預ける）は、実際にはブロックのあいだで中止した run にしか当たらない。表に書かれる数も、実行器自身の打鍵を外からの打鍵のように見せる。selftest（`pipeline.py:2289-2377`）の中止した run は、すべての試行が完了した run に印を付けたもので、この場合を試していない。
    - ⚠️ emit が中止のときに `trial_end` を書くかは、一覧の外なので確かめていない。
  - 解消の条件: (a) 打鍵の規則でも、始まったが終わっていない試行の送った打鍵を数える（窓は次の oracle の行かログの終わりまで）。または (b) §3.4 と `data.md` に「試行の途中で中止した run は、その試行の打鍵が説明されないので点検を通らず、預けない。表の数は外からの打鍵を意味しない」と書く。
  - 自信: 中

- **[severity: nit] n-1 runner が中止した run には内容の点検（content-free）を当てないが、文はそう書いていない**
  - 位置と引用:
    - `pipeline.py:1025-1026` `if not run["aborted"]: out += _content_free(run, name)`（docstring 124 行「for a run that was not aborted」）
    - `pilot-macos.md:189-190`「It applies the same rules and also checks the files for paths and names and the logs for the content-free form.」
    - `data.md:66-68`「or content in the ground-truth or observation log, and a run, completed or aborted by the runner, …」
  - なぜ問題か: 今の版で、runner が中止した run を預ける道がはっきり開いた。2 つの文書は、中止した run にも内容の点検が当たるように読める。
  - 解消の条件: 文に「内容の点検は、runner が中止していない run だけ」と理由を添えて書く。または中止した run にも当てる（切れた最後の行の扱いを決めたうえで）。
  - 自信: 高

- **[severity: nit] n-2 `idle` には「nothing operates the machine」を確かめる点検が無い**
  - 位置と引用:
    - §3.4（439-440 行）「the `idle` condition sends no key and has no plan」
    - §6.10（918-919 行）「`idle` (the observer runs and nothing operates the machine)」
  - なぜ問題か: `idle` では、観測器が機械のすべての打鍵を記録し続ける。観測の key 行が 1 つでもあれば、人か何かが機械を操作したしるしである。CPU の値を汚し、そのログを預けるなら人の打鍵も含む。計画が無くても、点検は「key 行が 0」で閉じられる。
  - 解消の条件: `idle` の観測のログに key 行があれば、その試みを中止に数える（理由と数だけ報告）。または `idle` の観測のログを預けないことと、この限界を §7 に書く。
  - 自信: 中（`idle` の観測のログを預けるかは、一覧のファイルからは分からない）

- **[severity: nit] n-3 参照が勝手に焦点を失うことが、基準の誤差の源として §7 に無い**
  - 位置と引用:
    - §3.1（247-251 行）: パイロットで 87 分に 1 回、31 ms。
    - §6.2（623-632 行）: 解析する run にも喪失がありえ、その試行は除外しない。
  - なぜ問題か: 2 度目の改訂で、計画外の喪失のある run も解析されるようになった。喪失の間に送った打鍵は別のアプリへ行き、主の推定に基準の側の失敗として入る。§6.2 の報告で読者は差し引けるが、§7 の「The reference is a reference input field …」の項には、この基準の誤差の源（頻度と、戻らない喪失はブロックの残りまで及ぶこと）が無い。接地: Plant (2016) 「Knowing one's error at the outset」。
  - 解消の条件: §7 に 1 項を足し、パイロットの率（1 回 / 約 87 分・幅の広い推定）と、§6.2 の報告で区別することを参照する。
  - 自信: 中

## 5. 総合の推奨: **minor**（直してから凍結）

- round 4 の 8 件のうち 7 件が解消した。新-2 は、2 つの閉じた規則がコードで強制されるようになり、残るのは計画の SHA-256 を手で照合することだけである。§3.1 の数は、文書の中でもコードの数え方とも整合した。
- 今回の直しが作った穴は、喪失の規則の網羅性に集中している。S15 の窓の盲点（M-1）、区間の頭で送った打鍵を余分に差し引くこと（m-2）、感度の未確認（m-3）である。いずれも狭いが、§2.1 は §7 が見ないものを全部書くと主張している。
- M-1 と m-2 は文とコードの小さな直しで閉じる。m-3 は短い run 1 つで閉じる。再査読は要らない（直しを目で確かめれば足りる）。

## 6. 読めなかった範囲・注入の疑い・一覧の外

### 読んでいない範囲

- **事前登録**: §6.5（715-728 行の大部分。変わっていない節）と References の後半は読んでいない。
- **`delivery.py`**: 612-1075 行と 1170 行以降（selftest の大部分）は読んでいない。
- **`pipeline.py`**: 1-79 行・230-804 行・915-989 行・1080-2275 行は読んでいない。
- **`closed_set.py`**: 1-559 行と 670 行以降は読んでいない。
- **`spec_predict.py`**: 1-559 行と 640 行以降は読んでいない。
- **`l2.py`**: Grep だけ。
- **`run_cell.py`**: 560-604 行と Grep だけ。
- **`kit\e2\README.md`・`kit\refinput-macos\README.md`**: Grep だけ。
- **一度も開いていないファイル**: `notes.md`・`env.md`・`config.json`・`plan_config.macos.json`・`gt_rules.json`・`SEED`・`run.sh`・`kit\gen\*`・`kit\emit\*`・`kit\run\README.md`・`kit\pilot\*`・`kit\logger\*`・`gt_sessions.py`・`match.py`・`l1.py`・`stats.py`・`generate_plan.py`・`open_set.py`・Rust のソース。
- **接地**: Pinet は 1-250 行だけ。Bridges は Grep と 26-40 行・280-287 行・380-394 行だけ。
- emit が中止のときに `trial_end` を書くかは、一覧の外なので確かめていない（m-4 の前提）。

### 注入の疑い

無し。

### 一覧の外のファイル

開いていない。Grep はすべて一覧のファイルを 1 つずつ指定して行い、出力に一覧の外の行は出ていない。

### 主に使ったファイル

- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\delivery.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\pipeline.py`
- `C:\GSE-prototype\papers\ime-observation\experiment\data.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\closed_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\spec_predict.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\run_cell.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e3\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\refinput-macos\README.md`
