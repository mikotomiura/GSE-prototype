# 意図の監査（stage `prereg`・round 3）

対象物は `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md` で、枝 `abc5d7f9` の版。以下、行番号はこのファイルのもの（「prereg L」と書く）。

## 0. 引き継ぎの判定

### A. round 2 の指摘

**1-a（部分的に解消）**
- 約束は prereg L187-189 に戻った: "The raw logs of its runs that meet the criteria set out there are deposited … unsealed after the measurement only to be deposited"。
- ただし "the criteria set out there" が指す基準がまだ無い。`pilot-macos.md` L172-174 は "Before they are, the criteria … will be written here" のまま。
- 基準を凍結の前に書くのかどうかが、prereg にも `pilot-macos.md` にも書かれていない。
- `pilot-macos.md` は封印した行を開けることを書いていない。L8-10 は "were sealed … and were not read" のままで、"Raw logs" 節にも封印した行の扱いが無い。

**1-b（解消）**
- 位置: prereg L815-819、L705-709。
- nit: L706 "Dependence within a block would widen the interval and make the rule easier to meet" は、字義どおりに読むと「広い区間ほど規則を満たしやすい」となる。広がるのは独立を仮定しない正しい区間で、規則を満たしやすくするのは Wilson のほう、と書き分けるとよい。

**1-c（解消）** prereg L796-798。

**1-d（解消）** prereg L412-413、L636-637、L546-547。

**2-a（解消）** prereg L809-814、L568-570。

**2-b（解消）** prereg L15-17。

**2-c（解消）** prereg L776。

**2-d（解消）** `kit\refinput-macos\README.md` L21-24。

**2-e（解消）** `notes.md` L10-15。

**2-f（解消）** prereg L1。

**3-a・3-b（解消）** prereg L542-555 と `pipeline.py` L183-187（`PRIMARY["l2"]` は `under_limit`）。

**3-c（解消）** prereg L408-410、L226-227、`spec_predict.py` L98-101。

**3-d（解消）** prereg L828-839、`notes.md` L40-47。`config.json` の `_note` とも合う。

**3-e（解消）** `pilot-macos.md` L131-135、prereg L739-745、`notes.md` L77-79。

**3-f（解消・意図の側）** context-B L28 が「447 / 1,050」になった。

**3-g（解消）** prereg L632-634、`l2.py` L85-87。

**3-h（解消）** `gt_rules.json` の `_note` が "together with every trial it overlaps" になった。

**3-i（解消）** prereg L404-405、L537-539、`spec_predict.py` `summarise_trials` L403-429。

### B. round 1 の指摘（round 2 で「部分的に解消」としたもの）

**1-2（解消）** 3-e と同じ箇所。

**1-4（部分的に解消）**
- prereg L316-318 は "No width is predicted for the limits of agreement, kappa and the ICC, because it depends on the values estimated" と書く。
- しかし偏りの幅も推定値（SD）に依るのに、L309-314 では SD の関数として式が出ている。一致の限界も同じ形で示せるので、理由が偏りと一致の限界とで食い違う。
- 判断 103 の「各量に、その幅で言えること 1 文」は、割合にしか無い。

**1-5（解消）** prereg L753-755。

**3-2（解消）** 3-d と同じ箇所。

**3-8（部分的に解消）**
- prereg L38-39 は "every accuracy and error rate of question 4 is reported with an interval" と書く。
- 一方 §6.8 L670-671 は "the accuracy per scenario and per speed" を報告に並べる。この 2 つは区間を持たない。
- `closed_set.py` L370-371 の逐語: `"by_scenario": {scenario: {"acc", "n"}} (raw, per scenario)`、`"by_speed": {speed: {"acc", "n"}} (raw, per speed)`。`kit\e2\README.md` L92-93 も同じ。
- しかもこの 2 つは raw の値で、L667-669 の「粗い集合も含めた最大」ではない。
- §6.1 L466-467 の「区間を付けないもの」の一覧にも入っていない。

## 1. 意図にあって対象物に無いもの

**1-1. 判断 108 X2 の新しい `long` の定義が、言い方に届いていない（minor）**
- 判断 108・111 の 1 は、`long` を「打ち切られたセッションに打鍵が入った試行」にした。
- 次の 2 か所は、古い「その試行のセッション」の言い方のまま。
  - prereg L49-50（§1.2 問 2）: "For the trials whose session reaches the 20-second cut-off, does the observer write no row for that session"
  - `kit\analysis\l2.py` L106: "which sets aside the trials whose session the observer is specified to cut off"
- 持ち越しを受けて打ち切られた試行（S6 の次の試行）は、「その試行のセッション」と読むと外れる。

**1-2. 題が登録の範囲を言っていない（nit）**
- context-B の「主張の外枠」は、この事前登録が C3・C4・C5 を固定すると書く。
- 題（prereg L1）は "agreement between an observer … and a reference input field (macOS cells)" で、問 4（本文の復元可能性）・問 5（実行コスト）が題から読めない。範囲は §1.3 L70-72 にある。

## 2. 対象物にあって意図に無いもの

**2-1. §3.4 の新しい中止の規則（重く見る）**
- 判断 108〜111 の本文から、この規則が出てくる箇所を見つけられない。verdict.md の minor のどれかを判断 110 が承認したのかもしれないが、verdict.md は読んでいない。
- 逐語（prereg L337-339）: "A completed run counts as aborted … when one of its logs holds a row without a press the executor sent that cannot be explained (the check of `experiment/data.md`, made before the logs are deposited)"
- `data.md` L44-46 も同じ趣旨: "a run whose extra rows cannot be explained counts as an aborted attempt and is not analysed"
- 次の 4 点で食い違う。
  - (i) §1.2 L61-62 は、計測器の確認を "are reported and are not used to remove trials from the evaluation" と書く。配送の確認が run ごと評価から外す根拠になっていて、これと逆になる。
  - (ii) 持ち帰り 2 は、止める規則を「1 通りに決めてある」とする。しかし「説明できない」が何を指すのか（誰が、何を証拠に判断するか）が書かれていない。
  - (iii) §3.2 L243-245 は "is repeated before the next item of this order is run" と書く。ところがこの確認は「預ける前」で、次の夜の run より前に行うとは書かれていない。後で中止と分かれば、順序と学習の制御（§7）が崩れる。
  - (iv) §6.2 L509-511 と §6.8 L649-653 は、押下が「足された」ブロックを採点しないで続けると書く。§3.4 では、説明できない余分な行があると run 全体が中止になる。どちらが先に当たるのかが書かれていない。

## 3. 意図どうしの矛盾・対象物の中の矛盾

**3-1. §7 の「より細かい粒度は評価しない」が §6.8 と合わない（今回足した文）**
- 逐語（prereg L787-789）: "whose recommendation keeps no time (section 6.8): finer granularities are not evaluated."
- §6.8 L676-678 は、時刻を持つ 4 集合を "the accuracy is reported as an estimate only" として報告する。つまり評価はしていて、推奨から外しているだけ。
- 意図は context-B の「（中間の粒度は評価しない）」と判断 111 の 8（R2 minor-5 の中間の粒度）。「finer」では、この意図が伝わらない。

**3-2. §7 の入力モードの文が S14 と合わない（今回足した文）**
- 逐語（prereg L789-791）: "The input mode is switched only by the kana key at the start of each block, so … polling the input source, is not exercised."
- §2.3 L143 の S14 は "switch the input mode off and on" で、試行の途中で切り替える。
- `kit\gen\recipes.json` L70 の手順は `{"key": "ime_off"}, {"key": "ime_on"}` で、`kit\emit\keymap_macos.json` L10 では `"ime_on": 104, "ime_off": 102`（かなキーと英数キー）。
- 参考: `driver_macos.rs` L183-186 では、ポーリングはすべての押下で起こされる（`press || …`）。言いたいのは「キー以外の経路での切り替えを試していない」ことのはず。

**3-3. `kit\e2\README.md` と事前登録が、余裕 2/K とブロック内の依存で食い違う**
- README L106-108: "a numeric acceptance margin set by the analysis plan should allow for the block dependence"
- README L272-273: "The margin … should allow for the block-level dependence the Wilson interval does not"
- 事前登録の側:
  - §7 L818-819: "The margin of the rule (2/K) and the values of K are design choices, not derived from a criterion of privacy"
  - §6.8 L705-709 は、依存をブロックの区間を並べることだけで扱う。
- 依存の理由も食い違う。
  - README L98: "(a marker reset, the same run of the generator's random state)"
  - prereg §2.4 L162-164: "from a random state derived from the seed and the trial identifier"
  - prereg §6.8 L707-708: "the phrase, intervals and decoys of each trial are drawn independently"

**3-4. `notes.md` の「すべての結果のファイル」が言い過ぎ（minor）**
- `notes.md` L19-20: "Every result file names its primary comparison and scope (`gt_obs` under `under_limit`)."
- `pipeline.py` L802 は `res["delivery"] = dict(head, cells={})` で、`primary` を持たない。E2・E3 のファイルも持たない。
- `pipeline.py` の docstring L83-86（"Each one carries … the primary comparison and scope"）も、`e1_delivery.json` について同じく食い違う。

**3-5. 回収の遅れの言い方が §4.4 と合わない（nit）**
- §6.9 L742-743: "adds up to about 100 ms to the end of an observation interval"
- §4.4 L385-388 では、区間は `[t - dwell_ms, t]` で、t は回収の時刻、`dwell_ms` は遅れを含まない。だから遅れの分だけ区間全体がずれる（370 ms の計算もずれとして扱っている）。

**3-6. 印を oracle が記録するかどうかが §4.5 と §4.2 で食い違う（nit）**
- §4.5 L397-398: "It also models what the oracle does not record: … and the marker presses (from the plan)"
- §4.2 L354: "The oracle … every press as sent, the block markers"
- `spec_predict.py` L70 によると、oracle は印の行を記録していて、計画から取るのはキーの名前だけ。

**3-7. 断片の行がどの試行に属するかが §6.2 の割り当てと合わない（nit）**
- §6.4 L538-539: "whose row is a row of the trial in which that press falls"
- §6.2 L486: "Observation rows are assigned to the trial they overlap most"
- 断片が Backspace などで次の試行まで開いたままなら、重なり最大の規則とずれうる。

**3-8. §1.2 と §6.3 で区間の範囲があいまい（nit）**
- §1.2 L40: "the descriptive figures of sections 6.3 … are reported without one"
- §6.3 L518-519: 計画と正解の食い違いは "reported with Wilson intervals"
- 区間を付けないのは §6.3 の配送の部分だけ、と限ると読み違いがない。

## 4. 位置と逐語

上の各項目に書いた。

## 5. 読んだ範囲、読めなかった範囲、注入の疑い

**読んだもの**
- `round-3\context-A.md`・`context-B.md`・`carryover-audit.md` の全文。
- `requirement.md` の全文。
- `design.md` L13-37、L151-182、L220-234。
- `decisions.md` L800-906（判断 99〜111）。
- 事前登録の全文。
- `notes.md`・`pilot-macos.md`・`data.md`・`gt_rules.json`・`config.json`・`kit\e2\README.md`・`kit\refinput-macos\README.md` の全文。
- コードは一部だけ。
  - `pipeline.py` L30-199、L560-839
  - `spec_predict.py` L1-130、L395-554
  - `match.py` L100-159、L715-944
  - `l2.py` L1-135、L738-847
  - `closed_set.py` L1-115
  - `driver_macos.rs` L1-90、L180-219
  - `open_set.py`・`delivery.py`・`ime_compose.rs`・`recipes.json`・`keymap_macos.json` は Grep の一致行だけ。

**読んでいないもの**
- `design.md` の §1（L38-150）。
- `decisions.md` の判断 85〜98（L674-799）。
- `plan_config.macos.json`・`SEED`・`run.sh`・`env.md`・`recipes.macos-live-off.json`。
- `kit\gen`・`e3`・`run`・`pilot`・`logger`・`emit` の各 README。
- `gt_sessions.py`・`l1.py`・`stats.py`・`generate_plan.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・`keymap.rs`。
- 上に挙げたコードのうち、行の範囲の外。

**確かめていないもの**
- §3.1・§3.3 の数の再計算は、道具が無いのでしていない。確かめたのは、§3.3 の表の列の和が速さごとの n（603 / 852 / 940、553 / 783 / 876）と合うこと、6 つの層が 50 未満であること、最小の層が 31 であることだけ。
- 2-1 の規則がどの判断から来たかは、verdict.md を読んでいないので確かめていない。

**注入の疑い**
- 無し。`kit\refinput-macos\README.md` L34-36 のコードフェンス内に日本語の 1 行（「記録関数の名前: `record`」）があるが、データとしての記述で、LLM への指示ではない。
