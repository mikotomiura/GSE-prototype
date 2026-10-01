# 査読 round 4（立場: BRM の方法論の査読者・メタサイエンスと統計／対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md` の版 159a2ec8）

結論は **minor（直してから凍結）**。round 3 の指摘は、テキストの量の定義（1）を除いて解消した。今回の直しで、中止の規則と問 3 の定義に新しい穴が開いた。どれも局所的で、計画を立て直す必要は無い。

## 1. 接地（この立場が求める基準・逐語）

- **S1 事前登録は具体・精密・網羅的であること**（Wicherts et al., 2016, l.90–98）: "each described step should allow only one interpretation or implementation (it should be precise). Finally, a preregistration should exclude the possibility that other steps may also be taken (it should be exhaustive)."
- **S2 停止の規則**（Wicherts et al., 2016, l.610–613）: "C4: Determining the data collection stopping rule on the basis of desired results or intermediate significance testing. A specific and precise a priori sampling plan could ameliorate this"
- **S3 除外は網羅的に書くこと**（Wicherts et al., 2016, l.465–472）: "an ideal preregistration specifically and precisely describes which types of participants will be excluded from the analyses, and also explicates that the stated rules of exclusion will be the only ones that will be used"。得点の付け方を後から選ばないこと（l.221）: "A6 Trying out different ways to score the chosen primary dependent variable"
- **S4 精度による n の根拠**（Lakens, 2022, l.692–697）: "The only aspect a researcher needs to justify for a sample size justification based on accuracy is the desired width of the confidence interval with respect to their inferential goal, and their assumption about the population standard deviation of the measure."
- **S5 計算は再現できること**（Lakens, 2022, 表 l.680–681）: "Make sure the power analysis is reproducible. Include the code used to run the power analysis, or print a report containing the details"
- **S6 ICC は形と区間で報告し、区間で読むこと**（Koo & Li, 2016）: l.52 "researchers should explicitly specify the ICC form they used in their calculation"、l.543 "the 95% confident interval of the ICC estimate (not the ICC estimate itself) should be used as the basis to evaluate the level of reliability"、l.483 "researchers should try to obtain at least 30 heterogeneous samples"

## 2. 引き継ぎ（carryover-R3）の判定

| 指摘 | 判定 | 理由（1 行）・今の版の位置 |
|---|---|---|
| 1 [major] 問 3 の量に、抜いた試行の数が混ざる | **部分的に解消** | 量を範囲の試行の上の比にしたので、試行の数が値を拡大・縮小する経路は消えた（§4.6 l.440–445、`l2.py` `aggregate` l.306–313 の `n / nt`・`total / span`）。ただし 1 つのテキストの範囲の試行の数 k が 1〜8 でばらつき、その平均が速さで違う。そのため一致の限界と ICC が k の混合になる。新 3 で扱う（round 3 で (b) を採らなかった理由は、この点では成り立たない） |
| 2 [minor] 設計効果の上限が割り付けと合わない | **解消** | 式 D = 1 + (Σm²/Σm − 1)ρ は不等クラスタの設計効果として正しい。1.96/√75 ≈ 0.23、√3.4 ≈ 1.8 の算術も合う（§3.3 l.317–326、§6.1 l.481–483）。残る小さい点（"usually near 1"・計算のコードが無い）は新 5 |
| 3 [minor] run の関門の「説明できる」に基準が無い | **解消** | 「説明」の裁量は消えた（§3.4 l.350–357 "No other reason and no explanation is admitted"、data.md l.31–40、§3.2 l.250–251）。ただし新しい規則の入力（窓・単位・道具が拒んだとき）が 1 通りに決まっていない。新 1・新 2 で扱う |
| 4 [minor] 速さごとの偏りに区間が 2 つ出る | **解消** | §6.7 l.664–665 "the interval of a single speed's bias is the one reported with that speed's agreement"。`l2.py` docstring l.90–92 と `mixture_bias` も同じ |
| nit a 問 4 の場面ごと・速さごとの正解率の区間 | **解消** | §1.2 l.38–41・§6.1 l.487–488・§6.8 l.709–711 が揃った |
| nit b §3.3 の残る試行は除外の前の数 | **解消** | §3.3 l.290–293 "before the exclusions of section 6.2, which can only reduce them" |
| N6 run の関門 | **解消** | 3 と同じ。新しい穴は新 1・新 2 |
| M2 2/K と K の根拠 | **解消** | 設計の選択として開示されている。`kit\e2\README.md` l.107–110・l.279–282 が §7 l.863–864 と同じ言い方になった |
| M3 一致の限界の幅 | **解消** | §3.3 l.328–330 の 1.96·SD·√(3/75) ≈ 0.39·SD は Bland–Altman の近似と合う。D を一致の限界の分散にそのまま掛けるのは近似で、n = 75 は計画の層の値（新 5 に含める） |

## 3. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | 区間を付けるもの・付けないものの一覧が §1.2・§6.1・§6.8 で揃った。§6.1 l.493–494 で、主の範囲の推定に「外す割合」と `all_trials` の値を並べる規則ができ、§7 の新しい項（句 1 つずつの判定）で主張の範囲も絞られた。残る過剰な主張: §3.3 "usually near 1" には根拠が無い（新 5）。§3.4 の "a key press from outside the executor" は、規則が実際に数えるもの（余りの行）より強い（新 8） |
| b 方法の穴 | 3 | 中止の規則の入力が 1 通りでない（新 1）。閾値をパイロットで確かめていない（新 2）。問 3 の k が不均一（新 3）。§6.6 の「読む」に計算が無い（新 4） |
| c 持ち帰れるもの | 4 | round 3 から変わらない。data.md の "Run checks" の表は、他の検証研究でもそのまま使える形 |
| d 簡潔さと構成 | 3 | 12,143 語（+8%）。§3.3 の設計効果の段落は、式・2 つの計画の値・例・一致の限界を 1 段落に詰めていて、追いにくい。節の構成は変わらない |
| e 規程への適合 | 4 | J6・J7: 75 の根拠（比率の精度）と、連続量・一致の限界の精度が §3.3 にある。J9: 除外は事前に決まり、"These are the only exclusions" と書かれている。J2: 設計効果の値を出すコードが公開物に無い（新 5、S5） |
| f 先行研究の位置づけ | 3 | round 3 から実質変わらない。設計効果の式に出典が無いのは著者の選択で、事前登録としては許容する（原稿では出典を勧める） |
| g 固定の十分さ | 3 | 除外・範囲・テキストの定義・区間の一覧は 1 通りに近づいた。しかし中止の規則の窓・単位・拒否の分岐（新 1）と、§6.6 の読み（新 4）が 1 通りでない。新 1 と新 4 を直せば 4 |

## 4. 新しい指摘

- [severity: minor] **§3.4 の閉じた規則が、道具の引数・限界の単位・道具が入力を拒んだ場合で 1 通りに決まっていない**
  - 位置と引用: §3.4 l.350–354 「in the delivery report of `kit/analysis/delivery.py`, run on the run directory alone … the reference's `excess_rows` over all presses is greater than zero, or its `rows_outside_trials` exceeds the five presses made outside the trials in each block (four marker presses and one kana press). No other reason and no explanation is admitted.」／`delivery.py` l.7 「[--pre-ms N] [--tail-ms N]」、l.25–28（試行の窓は既定で 20 ms 前・300 ms 後）、`_reach` l.365–376（合計しか出さない）、l.54 「Refused (exit 2): …」／data.md l.25 「Reference `rows_outside_trials` / limit」／`pipeline.py` l.805 `used = sorted((r for r in runs if not r["aborted"]) …`
  - なぜ問題か:
    - (i) 2 つの数は試行の窓で決まる。窓を変えれば、同じログで判定が変わる。§3.4 にも data.md にも、窓の値と命令行が無い。
    - (ii) "in each block" は「各ブロックで 5 以下」とも「合計が 5 × ブロック数以下」とも読める。道具は合計しか出さないので、前者は道具では計算できない。後者の読みでは、あるブロックの外からの打鍵が、別のブロックで失われた印の行で相殺される。
    - (iii) delivery.py が入力を拒んだ（exit 2）run は、規則のどちらの枝にも当たらない。
    - (iv) pipeline は manifest の `aborted` しか見ず、§3.4 を計算し直さない。規則が守られたかは、手で書いた記録だけで確かめることになる。
    - これは S1 の "only one interpretation or implementation" と "exhaustive" に反する。結果を見る前の判断ではあるが、停止の分岐が残る（S2）。
  - 解消の条件:
    - §3.4 と data.md に命令行を逐語で書く（`--pre-ms 20 --tail-ms 300` を明示）。
    - 限界を「合計 > 5 × 計画のブロック数」か「どれかのブロックで 5 を超える」のどちらかに決める。後者なら delivery.py にブロックごとの数を出させる。
    - 「delivery.py が入力を拒む run は中止と数える」を足す。
    - できれば、pipeline が同じ規則を計算し直し、当たる run を拒む。
  - 自信: 高

- [severity: minor] **中止の規則の閾値（参照の `excess_rows` = 0、ブロックの外の行が 5）を、パイロットの参照ログに当てていない**
  - 位置と引用: §3.4 l.350–354／pilot-macos.md l.180–183 「`kit/analysis/delivery.py` counts both directions for both logs … the pilot's reach count (`kit/pilot/reach.py`) checked only the direction from the executor to the observation.」／l.140–144（数えたのは観測の側だけ）／l.124 「Block 0 | 95 ms and 86 ms | 105 ms and 108 ms」
  - なぜ問題か: 許容 0 の規則で、凍結の後は変えられない。次の 3 つは、パイロットの参照ログに delivery.py を当てれば凍結の前に分かる（§3.1 は参照の側の解析を許している）。
    - 参照の入力欄が、送った打鍵のほかに無害な key_down を受けるか。受けるなら、外からの打鍵が無い run も中止になる。
    - ブロックの頭のかなキーの key_down を受けるか。受けなければブロックごとに 1 の余裕ができ、外からの打鍵を見逃す。
    - 遅れた行が 300 ms の尾を超えて「外」に数えられることがあるか。block 0 の遅れは約 105 ms だった。
    - 当てないまま凍結すると、「3 回とも中止で not measured」になる危険と、余裕のせいで見逃す危険が、どちらも見積もられない。
  - 解消の条件: 凍結の前に、矢印の印を使ったパイロットの run に、同じ命令行の delivery.py を当てる。参照の `excess_rows`・`rows_outside_trials`・ブロックあたりの外の行の数を §3.1 か pilot-macos.md に書き、印が 3 から 4 に増えた分を補正して、規則がそれらの run を中止にしなかったことを示す。中止にするなら、規則を直して再査読に回す。
  - 自信: 中（パイロットの参照ログそのものは読んでいない）

- [severity: minor] **問 3 の主の範囲では、テキストの値が 1〜8 個の試行の上の比になり、一致の限界と ICC がその混合になる。そのため速さのあいだで比べられない**
  - 位置と引用: §4.6 l.440–441 「The four measures are computed for every text on both sides, over the trials of the text that are in the scope of the analysis」／§6.7 l.658–662 「The per-speed values are primary … The number of a text's trials in the scope is reported per speed」／§6.2 l.534–535 「A text whose measure cannot be computed on one side is left out of that measure's figures」／`l2.py` l.431–432（重みを付けずに全テキストを並べる）／§3.3 l.285–286（速さごとの範囲の試行は 603 / 852 / 940、各 1,050 のうち）
  - なぜ問題か:
    - §3.3 の数から計算すると、テキストあたりの範囲の試行の平均 k は、on で slow 約 4.6・mid 約 6.5・fast 約 7.2、off で 4.5・6.4・7.2。
    - テキストの値の分散は k で変わる。Bland–Altman の一致の限界は差の分散が一定であることを前提にしているので、k の違うテキストを等しい重みで並べると、限界は k = 8 のテキストには広すぎ、k が小さいテキストには狭すぎる混合になる。
    - ICC(A,1) は、テキスト間の分散と誤差の分散の両方が k に依存する。速さのあいだの ICC の差の一部は、速さではなく k の差になる（S6: 形と前提が解釈を決める）。
    - k が小さいと、片側だけで値が計算できないテキストが増える。たとえば観測器がテキスト唯一のセッションを見落とすと、`mean_dwell_ms` と `abandon_rate` からそのテキストが落ち、一致が良く見える方向に偏る。これは slow で強く出る。
  - 解消の条件: 凍結の前に次のどれか 1 つを決める。
    - (a) 主の一致を、k = 8（または事前に決めた下限以上）のテキストに限り、残りを数える。
    - (b) k の層（例: 1–4 / 5–7 / 8）でも報告する。
    - (c) §6.7 と §7 に「主の範囲の一致の限界と ICC は k の混合で、速さのあいだでは比べない」と書く。
    - 最小の直しは (c)。
  - 自信: 中〜高（向きは確か。大きさは計算していない）

- [severity: minor] **§6.6 の「仕様の行との一致は試行ごとの行の数で読む」に、統計も計算するコードも無い**
  - 位置と引用: §6.6 l.645–647 「Agreement with the specified rows is read from the numbers of rows per trial; a pair of a short row can fail for timing alone (section 6.9).」／`l1.py` `truncation_check` l.286–325（数えるのは長いセッションの行と 20 秒以上の行だけ）／`match.py` の detection_metrics（層ごとの `n_gt`・`n_obs` だけ）
  - なぜ問題か: 何を「読む」のかが決まっていない（行の数が予測と等しい試行の割合か、層の合計の差か）。凍結したコードが出さない数なので、結果を見てから読み方を選べる（S3 の A6）。
  - 解消の条件: 統計を 1 つに決める。例: `over_limit` の長い試行のうち、観測の行の数が予測の行の数と等しい試行の割合。区間を付けるかどうかを決め、§1.2・§6.1 の一覧にも載せ、pipeline に計算させる。あるいは文を、層ごとの `n_gt`・`n_obs` で読む形に改める。
  - 自信: 高（`l1.py`・`match.py`・`pipeline.py` を grep した範囲で、該当する計算は見つからなかった）

- [severity: minor] **§3.3 の設計効果の段落: "usually near 1" に根拠が無い、計算を再現するコードが無い、数字が主の範囲の層のものでない**
  - 位置と引用: §3.3 l.322–326 「computed from the two measurement plans, sum of m_j squared over sum of m_j is 2.4 to 3.1 (on) and 2.5 to 3.4 (off) across the strata. D is therefore at most about 3.4 and usually near 1: the half-width is about 0.23 x SD」／§6.1 l.481–482 「within a planned stratum the design effect of the blocks is at most about 3.4」／§6.1 l.485–486 「because trials in one block share the state of the input method」
  - なぜ問題か:
    - "usually near 1" は ρ ≈ 0 を仮定している。パイロットでは一致を計算していない（§3.1 l.219–220）ので根拠が無い。しかも §6.1 がブロックで再標本化する理由と、向きが逆になる。
    - Σm²/Σm を出すコードが公開物に無い（"design effect" を grep しても事前登録の外に出てこない）。S5 に反する。
    - 0.23·SD は n = 75 の値。主の範囲の層は 31〜75（§3.3 の表）で、n = 31 なら約 0.35·SD になる（S4: 精度は主の推定の n で示す）。
    - 上限の 3.4 は計画の層の値で、主の範囲の層でも成り立つかは確かめていない。
  - 解消の条件: "usually near 1" を消すか、"when rho is near 0" に改める。Σm²/Σm を計算する命令か表を置く。最小の主の層（31）の半幅を添える。§6.1 の上限が主の範囲の層でも成り立つことを確かめてから書く。
  - 自信: 中

- [severity: nit] **§6.3 の文が §3.4 の許容と食い違う**
  - 位置と引用: §6.3 l.551–552 「the number of rows without a sent press (inside trials, and outside them, where the block markers and the runner's kana presses fall)」と、l.555–556 「rows of the reference without one show input from outside the executor and make the run count as aborted (section 3.4)」
  - なぜ問題か: §6.3 自身の定義では、印とかなの行も「送った打鍵の無い行」に入る。字義どおりに読むと、すべての run が中止になる。
  - 解消の条件: 「rows of the reference beyond the limits of section 3.4 …」のように、§3.4 の限界を参照する形にする。
  - 自信: 高

- [severity: nit] **§3.1 の 2 つの約束の書き方**
  - 位置と引用: §3.1 l.220–222 「Before the freeze, the assignment … is run, without any attack, on the key rows of the pilot's observation logs, and the fraction of blocks it scores is reported here.」／l.194–195 「a three-key block-start marker (F13, F14, F13 in the first pilot and `left`, `right`, `left` from then on)」／pilot-macos.md l.55・l.162–163／§3.1 l.189 「which are written before the freeze」と pilot-macos.md l.172–173 「Before they are [deposited], the criteria … will be written here」
  - なぜ問題か:
    - 最初のパイロットの観測には印の行が無い。後の run の 3 キーの印は、S7 の 3 つの矢印と区別できない。どちらの場合も、パイロットで採点されたブロックの割合は、本番の 4 キーの印での割合の見積もりにならない。
    - どの run に当てるか、どの命令で計算するか、割合を何に使うかが書かれていない。
    - 預ける基準を書く時点が、§3.1 では「凍結の前」、pilot-macos.md では「預ける前」で、揃っていない。
  - 解消の条件: 対象の run（例: `pilot2-on`・`pilot2-off`）と命令を書き、「報告だけに使う。凍結の前に割り当ての規則を変えたら、変えた旨と前後の割合を書く」と添える。pilot-macos.md の時点も「凍結の前」に揃える。
  - 自信: 中

- [severity: nit] **中止の規則は「外からの打鍵」の十分条件でしかない（相殺される）**
  - 位置と引用: `delivery.py` l.30–31 「excess_rows = sum of max(0, received - sent)」／data.md l.35–36 「since its reference log may hold a person's key presses」
  - なぜ問題か: 同じ試行の中で 1 打鍵が失われ、外から 1 打鍵が入ると、差し引き 0 になって規則に当たらない。規則を通った run の参照ログにも、人の打鍵の key code が残りうる。
  - 解消の条件: §7 か data.md に「規則は余りの行だけを検出し、置き換わった打鍵は検出しない」と一文書く。
  - 自信: 中

## 5. 総合の推奨: **minor（直してから凍結）**

- round 3 の指摘は、問 3 の定義の残り（k の不均一）を除いて解消した。「説明」の裁量が消え、区間の二重も解消した。
- 新しい穴は、中止の規則の入力（窓・単位・拒否の分岐）、§6.6 の読み、問 3 の k の混合の開示で、どれも文と小さいコードの直しで閉じる。
- 中止の閾値をパイロットの参照ログに当てる作業は、凍結の前に必須。当てた結果、規則を変える必要が出たら major として再査読する。

## 6. 読めなかった範囲・注入の疑い・範囲の逸脱

- **読んでいない**: 変わっていない節（§1.1・§1.3・§2・§4.1〜4.4・§5 は一部・§6.5・§6.10・§6.12・§8・§9 は一部）、`config.json`・`gt_rules.json`・`SEED`・`run.sh`・`notes.md`・`env.md`、`kit\e2\README.md` を除く README 全部（e2 も一部だけ）、`spec_predict.py`・`gt_sessions.py`・`stats.py`・`open_set.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・logger の Rust、`match.py` の `parse_prediction` の全体、`l2.py` の `_outside_report`・`mixture_bias` の本体と selftest、`closed_set.py` の selftest。接地の 3 本は該当箇所だけ読み、全文は読んでいない。
- **注入の疑い**: 無し（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。
- **範囲の逸脱（報告）**: `C:\GSE-prototype\papers\ime-observation\kit` を対象に `*.py` を grep したとき、一覧の外の `kit\e2\simulate_obs.py` と `kit\emit\emit.py` の行が出力に含まれた。さらに一覧の外の `kit\emit\emit.py` の l.355–379 を Read で開いた。どちらの中身も、上の指摘の根拠には使っていない（そこから考えた「印の行が最初の試行に入る」という懸念は捨てた）。
