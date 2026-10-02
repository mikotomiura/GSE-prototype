# R1 査読（BRM・打鍵の時刻を外部の基準で検証してきた方法論の立場）round 4: 事前登録の下書き `preregistration.md`（`159a2ec8`）

**総合: major。ただし再査読は狭い範囲で足ります。** round 3 の 7 件はすべて解消しました。一方で、今回新しく閉じた中止の規則（§3.4）が、実行器自身のかなキーで発火しうる構造になっています。これは凍結の前に、手元にあるパイロットのログで確かめられます。

## 1. 接地（この立場が求める基準）

- **G1 道具は自分のログでは自分の誤りを知れない**（Plant, 2016, p.410）:「The common thread being that the software or script being run can know nothing of the errors introduced by the hardware, rendering engine, or plug-in. It, just like the experimenter, will blindly act on and report the timings given without question.」／「Worryingly the log files suggested that the test had run normally imbuing an unwarranted confidence in the experiment, equipment, and software used.」
- **G2 その場で、その装置で検証する**（Plant, 2016, p.410–411）:「The only way to be sure of timing accuracy is to check it when paradigms are running in-situ, on the experimenter's own equipment, at the time a given study is carried out.」／（Bridges et al., 2020）「We would like to stress, once again, the importance of testing timing for every study, with the particular combination of stimuli, operating system and hardware used in that study.」「Papers such as this one, which report "best case" timing performance, should not be used in lieu of study-specific validation and testing.」
- **G3 基準は測定から独立している**（Bridges et al., 2020）:「Probably most importantly, however, by validating the timing independently with dedicated hardware, we could detect when timing was not as good as expected (whether because of hardware or software settings).」
- **G4 合成入力は実際の課題を代表する**（Pinet et al., 2017, p.1164）:「A limitation of this approach is that their manipulation involved fixed intervals and a single button. A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production.」／（Bridges et al., 2020）「A study like this can only show what performance it is possible to achieve in a given setting rather than what is likely to occur in a standard experiment.」
- **G5 OS の層が打鍵の解釈に入り込む**（Pinet et al., 2017, p.1163）:「operating systems may interpret successive or concomitant keyboard events according to both automatic and user-based settings」
- **G6 自分の誤差を最初に知る**（Plant, 2016, p.410）:「Knowing one's error at the outset is something that the vast majority of researchers cannot currently attest to.」

## 2. 引き継ぎの判定

| 指摘 | 判定 | 理由（1 行）・今の版の位置 |
|---|---|---|
| N-1 中止の規則の裁量 | **解消** | 閉じた規則になった。観測の余分な行は中止の理由にならない。「No other reason and no explanation is admitted」。§3.4 L349–357・`data.md` L31–40。ただし規則そのものに新しい穴があります（下の新-1・新-2）。 |
| N-2 4 つの矢印で以後が全滅 | **解消** | `align_blocks` が次のブロックを試してから飛ばす形になった（closed_set.py L626–642）。§6.8 L686–692・README L198–203。端の場合が 1 つ残ります（新-4）。 |
| N-3 焦点の喪失の区間 | **解消** | `_loss_intervals`（delivery.py L265–279）。区間は focus_out から次の focus_in まで。S15 は試行の中で戻るときだけ外す（L282–292）。selftest で戻らない場合・試行の間の場合・続く focus_out を確かめている（L599–626）。§6.2 L522–529 と一致。 |
| N-4 設計効果のばらつき | **解消** | §3.3 L317–326 に式と計画から計算した値。√3.4≈1.84 で「1.8 倍」、§6.1 L481–482 と合う。nit が 1 つ（新-7）。 |
| N-5 速さごとの 1.4〜1.8 点 | **解消** | §3.3 L286–288（「if the trials are treated as independent」）。n=940 と 553 で Wilson の半幅 1.39 と 1.82 を確かめた。 |
| N-6 §6.6 と §6.9 の相互参照 | **解消** | §6.6 L645–647・§6.9 L788–791。 |
| N-7 `carried out` の定義 | **解消** | §4.5 L424–425。§1.1 では矢印は会話を閉じないので、「cut off by a press outside the trials」は 20 秒の打ち切りの意味でだけ成り立ち、整合する。 |
| N2 の条件 3（要旨の規則） | **解消** | §6.1 L493–494。 |
| N8 `log_truncated` | **解消** | §6.2 L505。 |
| m1 | **解消** | N-4 で。 |
| m5 | **解消** | N-3 で（pipeline.py `_focus_loss` L647–678 が合計と速さごとを出す）。 |
| m11 生ログを預ける基準 | **部分的に解消** | 中身が無いのは既知なので指摘にしません。ただ約束の文が 2 通りに読めます。§3.1 L189–190 の「which are written before the freeze」は、生ログ（凍結の前に書かれたのは自明）にもかかれる。また `pilot-macos.md` L172–173 は「Before they are [deposited] … will be written here」のままで、§3.1 の「凍結の前」と時点が食い違う（新-6）。 |
| n3 解析コードの同一性 | **部分的に解消（変わらない）** | 研究者の選択（§5・§9 の 40 桁の識別子、コミットは `notes.md` に手で書く）として受け入れます。新しい指摘にはしません。 |

## 3. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | §6.8 と `kit/e2/README.md` の「a difference loses one block only」は言い過ぎ（新-4）。§6.3 の最後から 2 文目は §3.4 より広く書いている（新-3）。ほかは round 3 から変わらない。 |
| b 方法の穴 | 3 | 閉じた中止の規則は、実行器自身のかなキー（oracle に行が無く、block_begin より前に押される）を「実行器の外からの打鍵」と数えうる（新-1）。規則の特異度が、凍結の前に手元のパイロットで確かめられていない（G2・G6）。 |
| c 持ち帰れるもの | 4 | round 3 から変わらない。§7 に「judges one phrase at a time」が加わり、問 4 の結論の範囲がはっきりした。 |
| d 簡潔さと構成 | 3 | 本文は 12,143 語で +8%。「four layers」の語の衝突（新-5）のように、直しが増えた所で語の揺れが出ている。 |
| e 規程への適合 | 4 | J9（除外と規則を事前に決めて守る）に沿って閉じた規則にした点は前進。ただし規則は凍結する解析のコードでは機械的に強制されず、手で埋める表だけで守られる（新-2）。 |
| f 先行研究の位置づけ | 3 | round 3 から変わらない（外部の時計を使わない理由は §7 L818–821・L844–846 に限界として書かれている）。 |
| g 固定の十分さ | 4 | 中止・合わせ直し・焦点の喪失・要旨の規則が 1 通りに決まった。残る揺れは 3 つ: 中止の検査の窓の幅（`tail_ms` = 300 の既定値）を規則の文が名指していない（新-1）。「in each block」の閾値は実装上は合計でしか判定できない（新-2）。§3.2 の「each run」に問 5 の `idle` が入る（新-8）。 |

## 4. 新しい指摘

**新-1 [major] 閉じた中止の規則が、実行器自身のかなキーで発火しうる（規則の特異度をパイロットで確かめていない）**

- **位置と引用**
  - §3.4 L350–354「the reference's `excess_rows` over all presses is greater than zero, or its `rows_outside_trials` exceeds the five presses made outside the trials in each block (four marker presses and one kana press). No other reason and no explanation is admitted.」
  - §6.3 L551–552「outside them, where the block markers and the runner's kana presses fall」
  - `delivery.py` L82 `CUT_KINDS = ("reset", "block_begin", "marker")`（`block_end` を含まない）と L26–28「A trial's interval runs from the trial_begin wall time minus pre_ms (default 20) to the trial_end wall time plus tail_ms (default 300). The tail end is also cut at the next oracle row (reset, block_begin, marker or the next trial_begin)」
  - `run_cell.py` L585–595: `focus_cmd` が走り、その後に `em.run_block`（`block_begin` を書く）が来る。`kit/run/README.md` L108–111 も同じ順序。
  - `pilot-macos.md` L21「`focus_cmd` … presses the kana key (key code 104)」
- **なぜ問題か**
  - かなキーは oracle に行が無く、前のブロックの最後の `trial_end` の後、次の `block_begin` より前に押されます。計画は reset を求めないので reset の行もありません。
  - したがって、`focus_cmd`（System Events を動かす外部コマンド）が 300 ms 以内にかなキーを押し、参照の入力欄が `keyDown(with:)` でそれを `key_down` に残すと（refinput README L94）、その行は前の試行の `excess_rows` に入ります。規則上、その run は「実行器の外からの打鍵」として中止になります。
  - これは構造的な原因なので 3 回の試みで繰り返しえます。説明は認められないため、結果は「not measured」か凍結後の逸脱です。
  - 逆に参照がかなキーを残さないなら、閾値に 1 ブロック 1 打鍵の余裕が生まれ、外からの打鍵を見逃します。
  - どちらであるかは、パイロットの参照のログ（測定機にある・同じ `focus_cmd` の構造）で今わかります。ところが `pilot-macos.md` L182–183 は「the pilot's reach count … checked only the direction from the executor to the observation」と書くだけで、参照側の `excess_rows` と `rows_outside_trials` は報告されていません。
  - 道具の判定規則を、道具の想定（「かなキーは試行の外に落ちる」）だけで閉じています。G1「the log files suggested that the test had run normally imbuing an unwarranted confidence」・G2「check it … in-situ, on the experimenter's own equipment」・G6「Knowing one's error at the outset」に照らして、規則の特異度を手元の装置で先に知るべきです。
- **解消の条件**（(a) か (b)、そのうえで (c)）
  - (a) 凍結の前に、パイロットの各 run（`pilot2-on`・`pilot2-off`・`verify-off`）に `delivery.py` を規則と同じ引数で流し、次を §3.1 に書く:
    - 参照の `excess_rows`（all presses）と `rows_outside_trials`
    - 参照がかなキーと S14 のモードキーを `key_down` に残したか
    - 各ブロックのかなキーが前の試行の窓（+300 ms）の内か外か
    - パイロットの印は 3 打鍵なので、そこでの上限は 4/ブロック
  - (b) かなキーの時刻を実行器の記録に入れる。例: `focus_cmd` の前後の時刻を oracle に `prep` 行として書き、`CUT_KINDS` に入れる。そのうえで、規則が数える「外からの打鍵」から既知の実行器の打鍵を時刻で外す。selftest に「`trial_end` の 100 ms 後のかなキー」の対照を足す。
  - (c) 規則の文に `pre_ms`／`tail_ms` の値（20／300）を明記する。
- **自信: 中**。コードの経路は確かです。不確かなのは、参照がかなキーを `key_down` に残すかと、`focus_cmd` の所要時間の 2 点です。

**新-2 [minor] 閉じた規則は、凍結する解析のコードでは強制されない（手で埋める表だけ）**

- **位置と引用**
  - `pipeline.py` L805「`used = sorted((r for r in runs if not r["aborted"]), …)`」。L829–833 で `delivery.evaluate` を計算するのに、規則での拒否はしていない。`check_run`（L560–589）にも無い。`run.sh` には SHA や中止の検査が無い。
  - `data.md` L23–27 の Run checks の表は「(to be filled in)」。
  - §2.4 L170–171「a run whose plan has a different SHA-256 is not analysed」も、どのコードが確かめるかが書かれていない。
- **なぜ問題か**
  - 凍結の印・ログのハッシュなど、ほかの約束は機械で止める設計です。中止の規則だけは、人が表を正しく埋め、該当の run を `data.md` の一覧に載せないことに依存します。
  - 規則に引っかかった run を誤って載せても、解析はそのまま進みます。読者が確かめられるのは手書きの表だけです（G1: 判定を人の注意に預けない）。
  - 加えて、閾値の「five … in each block」は、`delivery.py` が合計しか出さないので、実際には合計 > 5 × ブロック数（630／585）でしか判定できません。文はブロックごとの判定とも読めます。
- **解消の条件**
  - `pipeline.py` が、一覧の中止でない run に §3.4 の 2 条件（計画の SHA-256 が §2.4 の値と一致すること・参照の数字）を当て、満たさなければ拒否する。
  - 閾値を「5 × the number of blocks of the plan（630 / 585）」と合計で書く。
- **自信: 高**

**新-3 [minor] §6.3 の最後から 2 文目が §3.4 より広い**

- **位置と引用**: §6.3 L555–556「rows of the reference without one show input from outside the executor and make the run count as aborted (section 3.4)」
- **なぜ問題か**: 文の通りに読むと、送った打鍵の無い参照の行すべて、つまり印 4 打鍵とかなキーも中止の理由になります。§3.4 の閾値（`excess_rows` > 0、または外の行が 5/ブロックを超える）と食い違います。中止の規則を 2 か所で違う言葉で書いています。
- **解消の条件**: §6.3 を「the reference's figures decide whether a run counts as aborted, by the rule of section 3.4」とし、規則の本文を §3.4 の 1 か所に置く。
- **自信: 高**

**新-4 [minor] 「1 つの違いで失うのは 1 ブロック」が、矢印で終わる試行の後の欠けで破れる**

- **位置と引用**
  - §6.8 L691–692「so a difference loses one block only (the block that holds it, or the next block when an added arrow press joins that block's marker)」
  - `kit/e2/README.md` L200–201「so one dropped press in some 100,000 loses one block and shifts no other」
  - `closed_set.py` `_is_anchor` L580–590（ちょうどその長さの列だけを錨とする）
  - `recipes.macos-live-off.json` L39 の S7: `{"repeat": "right", "times": "nav_count"}, {"pause": "think"}, {"key": "enter"}`
- **なぜ問題か**
  - ブロック i の最後の試行が S7（ライブ変換オフ）で、最後の Enter が観測から 1 つ欠けると、1〜3 の矢印が次のブロックの 4 打鍵の印とつながり、5〜7 の列になります。
  - コードを追った結果:
    1. ブロック i は合わない（欠け）。
    2. ブロック i+1 の印はちょうど 4 ではないので錨にならない。
    3. ブロック i の走査は i+2 の錨で `seqs[i+1]` と照らしても合わず、終わりまで何も置けない（カーソルは動かない）。
    4. ブロック i+1 は i+2 の錨で飛ばされる。
  - つまり 1 つの欠けで 2 ブロックを失います。ライブ変換オンでも、Enter 2 つがともに欠けると同じです。
  - 頻度は低いと見ます（パイロットで欠けは 0）。それでも §6.8 と README は保証として書いており、§3.1 のパイロットでの検査では見つかりません（G6）。
- **解消の条件**（次のどちらか）
  - 錨の左端の条件をやめる。ブロックの置き場所は列全体の一致で確かめているので、錨は「直後が矢印でない 4 打鍵」（右に揃える）で足りる。selftest に「ブロック末の S7 の Enter の欠け」の対照を足す。
  - または §6.8 と README の保証の文に、この例外を書く。
- **自信: 高**（コードの論理）。頻度は低い。

**新-5 [nit] §6.7 の「none of the four layers」は定義上空になる**

- **位置と引用**: §6.7 L676「As a diagnostic, they are also reported over the trials in none of the four layers.」。§6.4 L604–605「four layers from the prediction: carried out, received carry, closing key in reading, and the trials in none of the three」。`match.py` L156 `PREDICTION_LAYERS = ("carried_out", "received_carry", "closing_key_in_reading", "none")`
- **なぜ問題か**: 4 つ目の層が「3 つのどれでもない」なので、「4 つのどれでもない試行」は空です。実装（`per_trial_layer_none`）が指しているのは layer `none` です。
- **解消の条件**: 「over the trials of the layer none (section 6.4)」と書く。
- **自信: 高**

**新-6 [nit] §3.1 の 2 つの約束の書き方**

- **位置と引用**
  - L189–190「The raw logs of its runs that meet the criteria set out there, which are written before the freeze, are deposited」
  - L220–222「the assignment … is run, without any attack, on the key rows of the pilot's observation logs, and the fraction of blocks it scores is reported here」
  - `pilot-macos.md` L172–173「Before they are, the criteria … will be written here」
- **なぜ問題か**
  - 1 つ目: 関係節が「生ログ」にもかかり、時点の約束として読めません。また `pilot-macos.md` は「預ける前」と書いており、§3.1 の「凍結の前」と食い違います。
  - 2 つ目は対象の run を特定していません。最初のパイロットの印 F13・F14 は macOS の観測器が記録しない（§1.1 L16–17）ので、合わせ直しはできません。結果がどうであれ規則を変えるのか（凍結との順序）、記述だけなのかも書かれていません。
- **解消の条件**
  - 「The criteria are written in `pilot-macos.md` before the freeze; the raw logs of the runs that meet them are deposited」と分けて書き、`pilot-macos.md` 側も「before the freeze」にそろえる。
  - 2 つ目の約束に、対象の run（`pilot2-on`・`pilot2-off`・`verify-off`）・`--markers-in-obs`・パイロットの 3 打鍵の印を書く。割合が 1 未満のとき規則を変えるかどうかも書く。
- **自信: 中**

**新-7 [nit] 「D は … usually near 1」に根拠が無い。また範囲の層には当てはまらない**

- **位置と引用**: §3.3 L324–325「D is therefore at most about 3.4 and usually near 1」
- **なぜ問題か**
  - rho はブロックの中の入力メソッドの状態や学習に依存し、ここでは推定されていません。上限の文だけで足ります。
  - 3.4 は計画した 75 試行の上の値です。主の範囲（打ち切りで外した後）の層の Σm²/Σm は、外れ方によっては上がりえます（上限は最大の m_j）。
- **解消の条件**: 「usually near 1」を消す。範囲の層の Σm²/Σm を結果と一緒に報告するか、「computed on the planned strata」と明記する。
- **自信: 中**

**新-8 [nit] §3.2 の「each run」の検査に問 5 の `idle` が入る**

- **位置と引用**: §3.2 L250–251「The check of section 3.4 is made right after each run, before the next item of this order.」（この順序には `idle` と `working` が入る）
- **なぜ問題か**: `idle` には計画も oracle も無く、`delivery.py` を流せません。`working`（計画を流し、参照も起動する）に参照の規則を当てるかも書かれていません。
- **解消の条件**: 「the check of the delivery report applies to the runs of the two cells (and to `working` / not to `working`)」と範囲を書く。
- **自信: 中**

## 5. 総合の推奨: **major（範囲を絞った再査読）**

- round 3 の 7 件と前の 4 件は解消しました。合わせ直し・焦点の喪失・設計効果・要旨の規則は、文とコードが 1 通りに合っています。
- 新しく閉じた中止の規則（§3.4）は、実行器自身のかなキー（oracle に無く、`block_begin` より前、+300 ms の窓の中に落ちうる）で発火しえます。説明を認めないため、凍結の後では逸脱でしか直せません。しかも凍結の前に手元のパイロットのログで確かめられます（G2・G6）。
- 再査読は §3.4・§6.3・`delivery.py`（と、その対照）・パイロットの参照の数字に限ってよいです。新-2〜8 は minor 以下で、直してから凍結すれば足ります。

## 6. 読めなかった範囲・注入の疑い

**読んでいない:**
- `config.json`・`gt_rules.json`・`SEED`・`plan_config.macos.json`・`notes.md`・`env.md`
- README: `kit/gen/README.md`・`kit/e3/README.md`・`kit/pilot/README.md`・`kit/logger/README.md`。`kit/emit/README.md` は grep した行だけ。
- `keymap_macos.json`・`recipes.json` の S7 以外。
- コード:
  - 一部だけ読んだもの: `l2.py`（`aggregate`・`text_layout`・`mixture_bias`・`_outside_report` は読んでいない）・`match.py`（`parse_prediction`・`evaluate` は読んでいない）・`closed_set.py`（`align_blocks` の周りと selftest の有無だけ）・`run_cell.py`（L1–70 と L530–640 だけ）。
  - 開いていないもの: `gt_sessions.py`・`l1.py`・`stats.py`・`spec_predict.py`・`generate_plan.py`・`clock_sync.py`・`seal_obs.py`・`open_set.py`・Rust の 3 本。
- 事前登録の変わっていない節: §2.1–2.3・§4.1–4.3 と References（指示どおり round 3 の判定のまま）。
- 接地: Pinet の L261 以降と、Bridges の grep で当たらなかった部分。

かなキーが参照の `keyDown(with:)` に届くかは、どのファイルでも確かめられませんでした（新-1 の自信が「中」の理由）。

**注入の疑い: なし。** 読んだ範囲に、査読者や LLM に向けた指示はありませんでした。

**関係するファイル:**
- `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\delivery.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\run_cell.py`
- `C:\GSE-prototype\papers\ime-observation\kit\run\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\pipeline.py`
- `C:\GSE-prototype\papers\ime-observation\experiment\data.md`
- `C:\GSE-prototype\papers\ime-observation\experiment\pilot-macos.md`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\closed_set.py`
- `C:\GSE-prototype\papers\ime-observation\kit\e2\README.md`
- `C:\GSE-prototype\papers\ime-observation\kit\gen\recipes.macos-live-off.json`
- `C:\GSE-prototype\papers\ime-observation\kit\analysis\match.py`
- `C:\GSE-prototype\papers\ime-observation\kit\refinput-macos\README.md`
