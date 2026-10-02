# 意図の監査（stage `prereg`・round 2）

対象物は `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（下書き。以下「PR」）です。意図は context-B が指す資料だけから読みました（requirement.md、design.md の §0〜§3 と §6、decisions.md の判断 85〜107、handoff §2）。

## 0. round 1 の指摘の判定

| # | 判定 | 理由（1 行）と今の版の位置 |
|---|---|---|
| 1-1 | 解消 | §7 "The input method's learning is not reset" と、§3.2 の実行の順とその理由がある。 |
| 1-2 | 部分的に解消 | 予測の行と 2 段の報告は §4.5・§6.4 に入った。付随の指摘は残っている。§6.9 "a session is still paired as long as the offset … stays at or below a third of its length" は、2 つの区間の長さが同じときにしか成り立たない。同じ文が `notes.md` "Analysis settings" と `pilot-macos.md` "Clocks" にもある。 |
| 1-3 | 解消 | §2.3 Think time "Its role in the design is to place sessions on both sides of the observer's 20-second cut-off"、§6.6 Cut-off。 |
| 1-4 | 部分的に解消 | 割合と平均差は §3.3 の表と式で埋まった。一方、§3.3 "The width of an interval for the limits of agreement, for kappa and for the ICC depends on the values estimated and is reported as estimated" の 3 量には、判断 103 の「各量に『その幅で言えること』を 1 文」が無い。`notes.md` は "the precision expected at the planned numbers of trials are stated in `preregistration.md`" と書いている。 |
| 1-5 | 部分的に解消 | §6.2 の最後の項 "The run of the `working` condition of question 5 is not used for questions 1 to 4" は入った。8 時間でサンプラーを止めた後、11.9 時間の計画の残り約 3.9 時間をどうするかは、まだどこにも無い。§6.10 は "for eight hours" だけで、`kit/e3/README.md` は "Run it as one long plan that covers the whole window" と書く。 |
| 1-6 | 解消 | 判断 104 のとおり、§6.7 第 2 段落に試行ごとの差が入った。言い方の小さな点は 3-g に書いた。 |
| 1-7 | 解消 | §6.2 Other contingencies "If the input method stops responding or restarts …"。 |
| 1-8 | 解消 | §2.4 "a run whose plan has a different SHA-256 is not analysed"。 |
| 1-9 | 解消 | §1.3、§8。 |
| 2-1 | 解消 | 題から content-free が消えた。題の言い方の残りは 2-f に書いた。 |
| 2-2 | 解消 | §3.3 "The number was chosen for the precision … It was then checked that a run fits in one night"。 |
| 2-3 | 解消 | §2.5 "the blinding withheld the observer's output, not its input"。 |
| 2-4 | 解消 | §6.8 Open set（K0 は unigram、K1 は作品を除いた trigram）。 |
| 2-5 | 解消 | §3.1 "In addition, outside the runs, …"。 |
| 3-1 | 解消 | §6.8 の表。二項分布で 0.210・0.067、K = 100 で c = 1.5 のときの 0.487 を計算し直し、合っていた。 |
| 3-2 | 部分的に解消 | §1.3・§8・`notes.md` で、追補の範囲と新しいファイルの追加は読めるようになった。ただし Windows の手順書の直し方と矛盾する（3-d）。 |
| 3-3 | 解消 | 両方の `_note` が段階凍結に合った。小さな食い違いが 1 つ残る（3-h）。 |
| 3-4 | 解消 | §1.2 → "section 6.8"。本文の "section N" はすべて確かめ、参照先はすべて合っていた。 |
| 3-5 | 解消 | §4.2 "the key code of each key-down it receives, and each change of its focus"。 |
| 3-6 | 解消 | §6.2 "two carry-overs … excluded four trials"。 |
| 3-7 | 解消 | §6.2、§6.6 "A row with `dwell_ms` equal to zero never enters a pair"。 |
| 3-8 | 部分的に解消 | §1.2 "Every proportion and every continuous estimate is reported with an interval" はまだ言い過ぎ。区間の無い連続量がある。§6.10 の CPU の平均・中央値・95 パーセンタイル・最大と RSS の傾き、§6.8 の "the mean rank"、§6.9 の "median, range, drift per hour"、§6.7 の 3 つの混合の下での偏り、§6.3 の配送の遅れ（"reported descriptively"）。 |
| 3-9 | 解消 | `pilot-macos.md` "Time per trial"。 |
| 3-10 | 解消 | `pilot-macos.md` Setup "Learning"。 |
| 3-11 | 解消 | `kit/run/README.md` の最後の段落 "The runner does not align them, and the analysis does not correct them either"。 |
| 3-12 | 解消 | `notes.md` の表。問いの言い方の残りは 2-e に書いた。 |
| 3-13 | 解消 | `kit/gen/README.md` Configuration keys。 |

## 1. 意図にあって対象物に無いもの

- **1-a パイロットの生ログを公開するという約束が、PR から消えている**（carryover の「未解決」をメインが自分で書いているが、ここで確定させる）。
  - 意図: design §1.1a「★ preregistration に『正解の定義の根拠』として載せ、パイロットの生ログも公開物に含める」。判断 99〜107 に、これを取り消す判断は無い。
  - PR: §3.1 には公開するとも、公開しないとも書いていない。
  - 公開物どうしもずれている。`pilot-macos.md` "Raw logs" は "are not yet deposited. Before they are, the criteria … will be written here" と書き、公開する前提に立つ。
  - 封印した観測ファイルの扱いも登録されていない。`kit/pilot/README.md` は "`--unseal` is for the post-freeze analysis pipeline only" と書くのに、PR は封印した行を凍結の後に開けるのか、預けるのか、開けないのかを登録していない。§2.5 が言うのは "the sealed files were not opened" だけ。
- **1-b §7 に、E2 の区間の限界が無い**。
  - §6.8 は "judging by the upper end allows for part of this, and the remainder is stated as a limitation" と、§7 に書くことを約束している。
  - context-B の既知の限界（判断 97・101「残りは限界に書く」）と handoff §2 の 2 も、同じものを限界に挙げている。
  - しかし §7 Threats and limitations に、この項が無い。プールした割合の区間が下限として読まれること（§3.3・§6.1）も、§7 に無い。
- **1-c 判断 106 の「限界と今後の課題に回す」が、§7 に届いていない**。
  - 他の IME については、§7 に "One machine, one system version, one input-method version" の版の話しか無い。「標準 IME だけで、他の IME は評価していない」という項が無い。§1.3 には範囲外と書いてある。
  - 持ち帰り 3（他の IME の精度は主張しない）は、§1.3 にしか無い。
- **1-d 判断 107 の 1「予測のセッションは、正解と同じく重なり最大で試行に割り当てる」が、PR に無い**。
  - §4.5 は試行ごとの印を "a session that the trial started" で定義している。そのため読者は、割り当ても「始まった試行」で行うと読みうる。
  - また判断 107 の 1 の「試行ごとの表（判断 104）は範囲の外の試行を除く」と「`dwell_fraction` の分母は変えない」が、§6.4・§6.7 に無い。

## 2. 対象物にあって意図に無いもの（言い過ぎ）

- **2-a §7 "The primary estimates of questions 1 and 2 describe the sessions the observer is specified to report"**。これは同じ PR の §6.4 と合わない。
  - §6.4 は、規則から予測できる食い違い（S6・S10・読みの中の終端キー・Return 2 回）を "they are not removed from `gt_obs`" と書く。
  - "long" は "a session that the trial started is cut off"（§4.5）で決まる。このため、S6 から持ち越したセッションを受けた試行は、主の範囲 `under_limit` に入る。§3.1 では "113 trials start no session of their own"。このセッションが 20 秒で打ち切られれば、観測器はその試行に行を出さないと仕様で決まっている。
  - つまり主の範囲には、仕様上の欠落と分割が含まれる。判断 99 の意図（20 秒の打ち切りを主の分母から外す）よりも、§7 の文は強い。
- **2-b §1.1 "For every key press it writes one of fourteen key categories and a time"**。全部の打鍵に行が出るわけではない。
  - §3.1 は "the missing presses were the input-mode keys, which the observer does not record by design" と書き、§6.8 は "input-mode switches are not recorded on macOS" と書く。
  - `pilot-macos.md` は F13〜F19 が記録されないと書く（"The logger observes F1 to F12 on macOS, not F13 to F19"）。
  - `spec_predict.py` は修飾キーについて "Modifier keys are not delivered to the observer's event tap" と書く。
- **2-c §7 "a conversion exists only as the calls between the input method and an application"**。判断 107 の 8 が §7 に許したのは「基準をソフトの層に置く理由」で、これは存在についての強い主張になっている。同じ項の見出し "not the input method's internal state" は、内部状態が別にあることを前提にしており、それとも張り合う。
- **2-d `kit/refinput-macos/README.md` "The input method is therefore given no left context, so that trials are independent of one another"**。PR §6.1 は "trials in one block share the state of the input method" と書き、§7 は学習をリセットしないことを書く（判断 91）。README の「独立」は言い過ぎ。
- **2-e `notes.md` の問いが、はい／いいえの形に戻っている**。
  - 表の行は "Does the observer detect the compositions the input method performs?"、"Do the per-text aggregates a writing researcher might compute agree?"、"Did the scripted presses arrive as planned?"。
  - 判断 103 は「Q3 は how closely に改める」とした。判断 105 は比較の相手を「参照入力欄が受けた呼び出しから組み立てたセッション」にした。PR §1.2 は直っているが、公開物の `notes.md` だけ旧い枠のまま。
- **2-f 題 "agreement between an observer … and the input method's own calls"**（小さな点）。比べる相手は「呼び出し」ではない。§1.1 のとおり "the sessions assembled, by the rule of section 4.3, from the calls that a reference input field received" で、これが判断 105 の X5 の言い方。

新しい節（§4.5、§6.3 の配送、§6.4、§7）は、上の 2-a と 2-c を除けば判断 99〜107 の範囲に収まっていました。

## 3. 矛盾

- **3-a §6.4 と §6.6・コードの食い違い（範囲の数）**。
  - §6.4: "Each analysis of questions 1 and 2 is computed under three scopes"。
  - §6.6 は Q2 を "under `under_limit` (primary) and `all_trials`" で、範囲は 2 つ。
  - `pipeline.py:179` は `L1_SCOPES = ("under_limit", "all_trials")`。判断 107 の 1 も「L1 は 3 つの比較 × `under_limit`（主）・`all_trials`」。
  - `notes.md` は "the scopes are `under_limit`, `all_trials` and `over_limit`" と一括で書いている。
- **3-b §6.4 "Each scope is computed for three comparisons, with the same matching and the same measures"**。直前の段落は Q3 の範囲を述べているので、Q3 にも 3 つの比較が当たると読める。しかし判断 107 の 1（「L2 は `gt_obs` だけ」）と `pipeline.py:180, 659` では、Q3 は `gt_obs` だけ。PR の §6.4・§6.7 のどこにも、Q3 が `gt_obs` だけだとは書いていない。
- **3-c 「読みの中の終端キー」の層の説明が、手順書と合わない**。
  - §4.5 "**closing key in reading**: the trial types a long-vowel mark, a comma or a full stop"、§3.1 "113 trials type a long-vowel mark, comma or full stop"、§6.4 "a reading split by a long-vowel mark, comma or full stop"。
  - 一方、`recipes.macos-live-off.json` の `kana_layout` は `"minus": "ほ", "comma": "ね", "period": "る"`。S12（かな配列）ではこれらのキーが ほ・ね・る を打つ。
  - 判断 100 によれば、113 試行のうち 76（OFF では 99 のうち 64）が S12。層の大半は「ー・、・。を打つ試行」ではない。
  - 判断 100 自身も「読みに『ー』『、』『。』を含む試行（… うち S12 のかな配列が ON 76）」と書いており、意図の側も同じ誤り。`spec_predict.py:87` のコメント "in Romaji and in kana input alike" も同じ。
- **3-d 追補の縛りと、Windows の手順書の直し方が食い違う**。
  - PR §8: "it may add new files that only the Windows cells use …; it may not change any other existing file"。`notes.md` も同じ。
  - しかし Windows の手順は既存の `kit/gen/recipes.json` の `os.windows` にある。このファイルはライブ変換 ON のセルが使う。
  - `kit/gen/README.md` は "The Windows procedures … are still **hypotheses** … to be revised after a calibration pilot" と書き、"**Only this data should be edited after a calibration pilot**" と recipes.json を直すよう指示する。さらに Return と Escape の回数を変えるときは "must be made there as well"（`generate_plan.py` の `_PROFILES`）とも書く。
  - 同じ README には "Its Windows section is identical to `recipes.json`"（OFF のファイル。selftest が同一を検査する）ともある。
  - README の手順に従えば §8 に反する。新しい Windows の手順書を作る道は §8 の例示にも README にも無い。
- **3-e 時計のずれで対にならなくなる長さが、公開物どうしで違う**。
  - PR §6.9（読み取りの遅れ約 100 ms を足す）: "a session shorter than about 370 ms could fail to pair"。
  - `pilot-macos.md` Clocks: "the largest difference seen here (22 ms) could affect only sessions shorter than about 66 ms"。読み取りの遅れ（PR §4.4）を入れていない。
- **3-f 意図（context-B）と対象物の数の食い違い**。
  - context-B の既知の限界は「slow では試行の約 3 割が 20 秒の打ち切りに当たる（判断 99）」と書き、判断 99 は「mid 約 11%」と書く。
  - PR §3.1 の予測は ON で 423 / 1,050（40%）、OFF で 398 / 975（41%）、mid は 158 / 1,050（15%）。§3.3 の表の合計とも合っていて、計算し直した。
  - 判断 99 の値は持ち越しを数えていない旧い数え方で、意図の側が古い。
- **3-g §6.7 "A text mixes the scenarios of its block about equally"**。`kit/gen/README.md` によれば、ブロックは seed で並べた試行を切っただけで、シナリオを均等にそろえる操作は無い（"Trials for each speed are ordered by the seed and cut into chunks"）。8 試行の文に入るシナリオは 14 のうち多くても 8 で、均等なのは期待値の上だけ。
- **3-h `gt_rules.json` の `_note`（凍結のハッシュに入る）**: "excluded … as carry_over, together with both trials"。PR §6.2 は "every trial it overlaps is excluded" で、判断 88 は 3 試行にまたがる場合を試験に足した。"both" は狭い。
- **3-i §6.4 over_limit**: "the rows that the observer writes after a cut-off … are rows of these trials"。行は重なり最大で試行に割り当てる（§6.2 "Observation rows are assigned to the trial they overlap most"）。そのため、打ち切りの後の断片が次の試行に入れば、`under_limit` 側に入る。断片は常に long の試行に入るとは限らない。

## 4. 位置と逐語

各項目の中に書きました。

## 5. 読んでいない範囲と注入の疑い

- **読んでいない**（一部は Grep の該当行だけ見た）:
  - `recipes.json`（S 番号の位置だけ grep）と `keymap_macos.json`、`SEED`。
  - `kit/emit/README.md`・`kit/logger/README.md`・`kit/refinput-macos/README.md`（grep の該当行だけ）。
  - `match.py`・`stats.py`・`gt_sessions.py`・`generate_plan.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・`closed_set.py`・`open_set.py`・`keymap.rs`。
  - `pipeline.py`・`l1.py`・`l2.py`・`delivery.py`・`driver_macos.rs` は grep の該当行と一部だけ。`spec_predict.py` は 1〜100 行と grep。`ime_compose.rs` は 160〜349 行と grep。
- **一覧の外を 1 行見た**: `kit\**\README.md` に Grep をかけたとき、一覧に無い `C:\GSE-prototype\papers\ime-observation\kit\refinput-windows\README.md:135` の 1 行が出力に出ました。中身は指摘にも根拠にも使っていません。
- **注入の疑い**: ありません。読んだ範囲に、LLM に向けた指示は見当たりませんでした（`ime_compose.rs` の日本語のコメントは開発者向けの注記）。
