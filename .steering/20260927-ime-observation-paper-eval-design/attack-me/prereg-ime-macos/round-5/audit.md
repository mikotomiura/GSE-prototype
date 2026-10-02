# 意図の監査役（stage `prereg`・round 5）の報告

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（`ba89bcbd`）。round 4 から変わった箇所に絞り、判断 116〜124 が事前登録・公開物・コードに同じ形で届いているかを見た。行番号は今の版のもの。

**結論**: 判断 116〜124 の芯は、文とコードの両方に届いている。定数はすべて文と一致した（`pipeline.py` の k = 0・`REFERENCE_RECEIVES_MODE_KEYS = False`・pre 20 / tail 300、`delivery.py` の 500・100）。§3.1 の数も内部で整合した（ブロック 15 = 6 + 6 + 3・282 試行・S14 の 18 / 18 / 6、§6.7 の k の平均）。古い規則の言い方は事前登録には残っていない。ただし `pipeline.py` のモジュール説明に 1 文残っている（3-β）。新しい食い違いは、minor 4 件と nit 10 件ほど。いちばん重いのは次の 2 つ。
- パイロットの喪失についての数の自己矛盾（3-α）
- 余裕 500 ms と送出の遅れ 100 ms が、パイロットで決めた値でないことが書かれていない（1-α）

---

## 0. 引き継ぎの判定

| 指摘 | 判定 | 理由（1 行）と今の版の位置 |
|---|---|---|
| A 1-A | 解消 | §3.4 L446-448「A completed run that counts as aborted for any of these reasons is not deposited」。`data.md` 手順 1 も同じ。 |
| A 1-B | 解消 | §1.2 L58「(Section 6.8 states what is not evaluated.)」。 |
| A 1-C | 解消 | 打鍵の規則の上限は、§3.1 L234-247 のパイロットの結果と §3.4 L415-421 で決まっている。（焦点の規則の 100 ms は実測していない。これは新しい項目の 1-α に書いた） |
| A 1-D | 解消 | context-B が「ms と 1 秒のビンのあいだ」と明記し、§7 L956 と一致する。 |
| A 2-A | 解消 | `data.md` の表に「SHA-256 of the plan」の列があり、手順 1 に照合がある。コードでの照合は判断 118 の 4 の選択で入れていない。 |
| A 2-B | 解消 | §6.4 L683-685「a candidate cannot be confirmed from the log alone」と §7 L985 は、§2.5 L179-180 と矛盾しない。 |
| A 3-A | 解消 | §3.4 L403-421 がブロックごとの区間で数える。`delivery._segments` と `pipeline.reference_abort_segments` が同じ規則を実装している。 |
| A 3-B | 解消 | §6.7 L795-796「the trials of the layer none (section 6.4)」。 |
| A 3-C | 解消 | §3.1 L267-268「186 (all S6; 185 of them run on into a later trial, and the session of the other is cut off by a press outside the trials)」。 |
| A 3-D・3-F | 解消 | §3.1 L190-191 で 2 文に分かれ、L225-233 に対象の run・引数・結果がある。 |
| A 3-E | 解消（残りあり） | `pilot-macos.md` L170-200 は本計測の基準と揃った。ただし盲点の列挙が古い 2 項目のまま（3-δ）。 |
| A 3-G | 解消 | §6.8 L809-814、`kit\e2\README.md` L198-208、`closed_set._is_anchor`（右の端）が同じことを言っている。 |
| A 3-H | 解消 | §6.6 L752-755「Agreement with the specified rows is read from the detection counts of `pred_obs` under `over_limit` per stratum」。 |
| B 1-1 | 解消 | §6.2 L617-619「the trials whose presses went into a session that the observer's rules cut off」。 |
| B 1-2 | 未解消（選択） | 題は変わっていない。任意の nit で、範囲は §1.3 にある。 |
| B 1-a | 解消 | `pilot-macos.md` の Raw logs に基準の中身がある。 |

---

## 1. 意図にあって対象物に無いもの

**1-α（minor）余裕 500 ms と送出の遅れ 100 ms が設計の選択であること、100 ms をパイロットで実測していないことが、どこにも書かれていない**
- 意図: context-B の既知の限界に「余裕 500 ms と送出の遅れ 100 ms はメインの選択…100 ms はパイロットの実測で決めていない」とある（判断 122 の 6・124 の 2）。
- 対象物: §3.4 L415-416 は「Two settings of the rule were fixed before the freeze from the logs of the pilot」と k と版だけを挙げている。500 と 100 は L426-431 に根拠の文があるだけで、選択の値だとは書いていない。§7 は E2 について「design choices」と書いているが（L999-1000）、焦点の規則には同じ開示が無い。
- 重く見る理由: L428 は、500 ms が「the offset between the clocks of the two logs」を覆うと書く。しかし 100 ms の窓は、実行器の時計と観測の時計を比べる。`pilot-macos.md` の Clocks の表（L124）では、ブロック 0 の「observation − executor」が「95 ms and 86 ms」で、送出から行までの遅れに残るのは 5〜14 ms しかない。窓が足りないと、2 つのことが起きる。
  - 区間の直前に送った打鍵が「説明されない」に数えられ、人がいなくても中止になる。判断 123 が避けたかった型である。
  - 区間の終わりの側で、人の打鍵が隠れる。
- 文としては、「100 ms は選択で、パイロットで実測していない」と、この時計の差との関係を書けばよい。

**1-β（nit）喪失の頻度の見積もりの幅**
- 意図: 「焦点の喪失の頻度はパイロットの 1 回（約 87 分）から見積もったもので幅が大きい（判断 123）」。
- 対象物: §3.1 L251-252 は「could therefore abort most runs of about 12 hours」だけで、1 回の観測から出した値で幅が大きいことは書いていない。

**1-γ（要確認・nit）`idle` の観測のログ**
- §3.4 L439-440「the `idle` condition sends no key and has no plan」は、`idle` を規則の外に置いている。
- 判断 119 の根拠（観測器は機械のすべての打鍵を記録し、預ける）からすると、`idle` の観測のログに key 行が 1 つでもあれば、それは人の打鍵である。
- 事前登録は、E3 の何を預けるかを書いていない（"deposit" が出るのは L190-193・219・446-450 だけ）。観測のログを預けるのなら、規則か開示が要る。預けないのなら、そう書けば済む。

**1-δ（nit）`kit\run\README.md` が `--pack` を経ない預け方を案内している**
- L142「Deposit `run.json` and the four logs only.」
- 判断 119 の「`--pack` で全 run に強制」には触れていない。`data.md` の手順を読まずにこの文に従うと、強制を通らずに預けられる。

（判断 120 の 9 の「定数と文の一致を機械で検査しない」は、事前登録に書かれていない。ただし `e1_delivery.json` の `abort_rule` が定数を後から照合できる形で残すので、指摘にはしない。）

---

## 2. 対象物にあって意図に無いもの（範囲を超えた言い方）

直しで足した文に、判断の範囲を超えた主張は見つからなかった。言い方の nit が 1 つある。

**2-α（nit）規則が「送っていない打鍵」を特定するかのような言い方**
- §3.4 L393-394「the observation recorded a key press that the executor did not send」
- `pipeline.py` L837-838「the observation log holds key presses that the executor did not send within a loss of focus」
- 規則は数を比べるだけで、打鍵を特定しない（§7 L986「counts presses, not keys」、判断 123）。L393-394 の要約は余裕 500 ms にも触れていない。

---

## 3. 意図どうしの矛盾・対象物の中の矛盾

**3-α（minor・要確認）パイロットの喪失の「前後 3 秒に key 行 0」が、「最後の送出から 2.7 秒」と両立しない**
- §3.1 L248-249「for 31 ms, in the think time of an S1 trial, 2.7 seconds after the last press sent; the observation holds no key row within 3 seconds of the loss」
- §3.4 L435-436「the pilot had one loss, of 31 ms, with no key row within 3 seconds」
- 2.7 秒前に送った打鍵（判断 121 では Space）は、観測に行を残すはずである。観測は space を記録し、`pilot-macos.md` L142-143 には「Every press of a key the observation records produced a row」とある。その行は前後 3 秒の中に入る。
- 判断 122 の 6 自身も「パイロットの喪失〔直前の行から 2.67 秒〕」と書いている。判断 121 の「前後 3 秒に観測の key 行は 0」とも食い違う。
- 規則の判定は変わらない（行は余裕 500 ms の外にある）。しかし §3.4 が引用する事実の文なので、窓の値か言い方を一次の数で直す必要がある。

**3-β（minor）`pipeline.py` のモジュール説明に古い言い方が残っている**
- L101「Extra rows in the observation log never refuse a run.」
- 直前の文（L94-100）は、喪失の区間で観測の行が送った数を超えたら拒むと書いている。判断 124 の 5 は §3.4 と `data.md` を「喪失の外では」に改めたが、この文は改めていない（§3.4 L455-457 と `data.md` L55-57 は「Outside a loss of focus」になっている）。

**3-γ（nit）§6.3 だけを読むと、観測の行は中止に関わらないように読める**
- L658-660「Rows of the observation without a sent press are a result of the observer and stay in the analysis; whether the rows of the reference make a run count as aborted is decided by the rules of section 3.4 alone」
- 判断 121・123 の後は、観測の行も（喪失の区間で）中止の理由になる。「the rows of either log」とするか、喪失の区間の例外を書く必要がある。

**3-δ（nit〜minor）「§7 が捕まえないものを書く」と言っているのに、列挙が欠けている**
- §2.1 L88 は「(section 7 states what they do not catch)」と書く。
- `delivery._focus_losses`（L385-392）は、計画した S15 の切り替えの間（試行の窓の中で始まって戻る喪失）を区間から丸ごと外す。だから、その間に人が他のアプリへ打った打鍵は、どちらの規則にも掛からない。§7 L986-995 はこれを挙げていない。
- `pilot-macos.md` L187-188 の盲点は、判断 120 のころの 2 項目のままである。「Their blind spots are those of the measurement (section 7 of the pre-registration): a press from outside that replaces a press that was lost, and a shortcut that the system consumes without moving the focus.」には、判断 122・124 で足した 3 つが無い（焦点を動かして戻る人・区間の中の取りこぼしと終わりの直前 100 ms・重複行）。全部を挙げるか、「§7 を見よ」だけにする必要がある。

**3-ε（minor）焦点の規則が、試験している観測器の出力で run を中止にする**
- §3.4 L455-457 と §6.3 L658 は、観測の余分な行を「a result of the observer under test」として扱い、中止の理由にしない原則を立てている（判断 112）。
- 判断 123 の代償で、喪失の区間に観測器の重複行が落ちると run は中止になり、やり直しになる。§7 L994-995 は「makes the run count as aborted without a person」とだけ書く。これが、試験している系の振る舞いで中止を決める（原則の例外）ことだとは書いていない。中止は報告されるので目には見えるが、選択の向きとして一言あった方がよい。

**3-ζ（nit）同じ記号 k が 2 つの意味で使われている**
- §3.4 L412 と §3.1 L245（`data.md` L26 も）では、k はかなキーが残す key-down の数で、「k = 0」。
- §6.7 L768-771 では、k はテキストに残る試行の数で、「their number k」「a k of three or less」。
- どちらも round 5 で入った（判断 116 の Z1 と Z2）。context-B の既知の限界も、2 つの意味で同じ記号を使っている。

**3-η（nit）§3.1 の「(above)」が、後ろの段落を指している**
- L254-255「in the oracles built from the measurement plans (above)」
- 計画から oracle を作る説明は、後ろの L258-260 にある。また 78%（ON 78.1%・OFF 77.0%）を再現する命令がどこにも無い。判断 118 の 7 は、§3.3 の値を `plan_figures` で再現できるようにした。

**3-θ（nit）パイロットで規則を当てた run の数が、文書のあいだで違う**
- §3.1 L250-251 は 6 run（「about 87 minutes in the six runs」）。
- `pilot-macos.md` L197-198 は「the six runs listed above and of a short run made before the first pilot」で 7 run（判断 122 の 8・124 の 5 とも 7 本）。
- さらに L200 は「A dry run that was interrupted before the first pilot is subject to the same criteria」と書き、L39 は「No run was aborted」と書く。この 2 つが同じ run なのか別の run なのか分からない。

**3-ι（nit）S15 の計画した切り替えの定義が、節によって違う**
- §3.4 L424 とコードは「a loss that begins and ends inside the interval of an S15 trial」。
- §6.2 L629 は「an S15 switch is planned only when it returns inside its own trial」で、始まりの条件が無い。

**3-κ（nit）`data.md` の節の参照先がずれている**
- L47「the version of `reference.segments` that section 3.1 selects (`excluding_mode_keys`)」
- `excluding_mode_keys` という名前は事前登録では §3.4 L420 にしか無い（§3.1 は設定を文で書くだけ）。

**3-λ（nit）「観測は機械のすべての打鍵を記録する」が、他の文と合わない**
- 「the observation records every key press on the machine」と書く箇所: §3.4 L433・L447-448、`pilot-macos.md` L175・L186-187。
- これと合わない箇所: §3.1 L213「the input-mode keys, which the observer does not record by design」、§6.3 L657、`pilot-macos.md` L141-142・L55-56（F13〜F19 を観測しない）。
- 規則の論理には影響しない。

**3-μ（nit・意図の中の矛盾）持ち帰り 2 の書き方が、既知の限界と合わない**
- 持ち帰り 2 は「止める規則は…人の打鍵が入りうる run…**だけ**を閉じた規則で中止にし…**その設定はパイロットのログで凍結の前に決めた**」と書く。
- 既知の限界は「500 ms と 100 ms はメインの選択・100 ms は実測で決めていない」と書く。
- 対象物（§3.4 L415-416 は 2 つの設定だけをパイロットから決めたと書く）の方が正確である。また §3.4 は、計画の SHA-256 の違いと `delivery.py` の exit 2 でも中止にする（判断 118 の 3）。持ち帰りの「だけ」「その設定は」は狭めて言い直した方がよい。

**一致を確かめたもの（食い違いなし）**
- 定数と文: k = 0、`REFERENCE_RECEIVES_MODE_KEYS = False` ↔ 版 `excluding_mode_keys`、`FOCUS_MARGIN_MS = 500`、`OBS_SEND_DELAY_MS = 100`、pre 20・tail 300、`abort_rule` の名前 `unplanned_focus_loss_with_unexplained_presses_aborts`。
- 判断 123 の数え方の実装: 擬似キーとモードキーを除く押下と、印の行を、[a − 100, b] で数える。接する区間もまとめる。
- 判断 116・118・120 で消えた名前（`excess_rows` の規則・`rows_outside_trials` の上限・旧 `abort_rule` 名・「usually near 1」・「none of the four layers」・「Presses outside every block」）は、事前登録・`data.md`・`pipeline.py` に残っていない。
- §6.2 は、判断 123 の代償（打っている最中の喪失を含む run も解析に残り、その試行は食い違いとして数える）を書いている。§7 L992-995 は、取りこぼし・終わりの直前 100 ms・重複行を書いている。
- §3.3 の 0.35 × SD（1.96/√31）と、§6.7 の k の平均（§3.3 の主の範囲の表と整合）。
- 変わった節の「section N」の参照先は、3-κ を除いてすべて実在し、内容も合っている。

---

## 4. 位置と逐語

各項目の中に書いた（ファイル・行・逐語）。

---

## 5. 読めなかった範囲・注入の疑い・一覧の外

**読んでいない範囲**
- `requirement.md`（全体）
- `design.md`（§0〜§3・§6）
- `decisions.md` の判断 85〜115（674〜939 行）。今回読んだのは 940〜1035 行だけで、85〜115 は context-B の要約と round 4 までの判定に頼った。
- 事前登録の §1.1（L9-35）と §2.2〜§2.3（L90-152）。変わっていない節なので読み直していない。
- 第 1 群の `plan_config.macos.json`・`config.json`・`gt_rules.json`・`SEED`・`env.md`・`kit\gen\README.md`・recipes の 2 つ・`keymap_macos.json`・`kit\logger\README.md`・`kit\refinput-macos\README.md`・`kit\emit\README.md`
- `kit\pilot\README.md`（Grep の 1 回だけ）
- `kit\e3\README.md`（L95-139 と Grep だけ）
- `kit\run\README.md`（L115-162 と Grep だけ）
- 第 2 群のうち、`delivery.py`（L1-160・L360-610）・`pipeline.py`（L75-234・L805-914・L990-1034 と Grep）・`closed_set.py`（L575-649）・`spec_predict.py`（L570-639）以外。`l2.py` は Grep だけ。selftest の本体は読んでいない。
- パイロットの生ログはこの機械に無く、3-α の数は検証できない。

**注入の疑い**: 無い。読んだ文書とコードの中に、LLM や査読者に向けた指示は見当たらなかった。

**一覧の外**: 開いていない。Grep はすべて一覧のファイルを 1 つずつ指定して行い、出力に一覧の外の行は出なかった。
