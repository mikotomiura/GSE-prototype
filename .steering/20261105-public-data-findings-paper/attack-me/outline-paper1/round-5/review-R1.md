# review-R1（outline round 5・paper-reviewer・打鍵の記録と作文の過程の測定の伝統）

推奨: minor（直して書き進める）。

## 1. 接地
- 基準 1 Roeser et al. 2025（roeser2025.txt:162-164）"“Pause” in the written-production literature is used to refer to a break in output with duration that exceeds an a priori threshold. In the present study “hesitation” is operationalised within the statistical models that we used to interpret our data."
- 基準 2（:519-523）"interkey intervals between adjacent keys at locations that have been identified repeatedly in previous research as locations where observed mean interkey intervals ... have tended to vary substantially"
- 基準 3（:1189-1192）"We found that the two-distribution mixture model was successful at uncovering the parameter values of the data generated with a two-distributions mixture process"
- 基準 4（:1210-1213）"one concern might be, perhaps, that mixture models show better performance because they capture distributions in the data that are related to off-task activities"
- 基準 5 Guo et al. 2020（guo2020.txt:1049-1052）"we used relatively simple heuristics to define our writing states ... Further research that combines think-aloud protocols and other sources of evidence with keystroke logging might enable us to build even more effective classification procedures" ／（:240）"Such a personalized threshold was larger than the 95th percentile of within-word pauses"
- 基準 6（:1056-1059）"both our data and our methods impose important limitations on the conclusions that we can draw. ... results may not necessarily generalize to a broader population or to different conditions"

## 引き継ぎの判定
1 含意 → 解消（:27・:60・:34）／2 問い → 解消（:7・:85。「型の」の nit）／3 θ → 解消（:75）／4 計器の動き → 一部（:101 に置き場と手順。confirm_holdout.json の床の割合は停滞と対照の集合の値〔`level_floor_ceiling` の `floor_lt_002` 0.607・0.648〕だけで、全時間の床の割合・分散・u の後の値は無い。草稿の前に数えるまで未解消）／5 状態モデル → 解消（:34・:92）／6 上端の 3 桁 → 解消（:38・:111）／7 実効の書き手 → 解消（:102）／8 H3 の桁 → 解消（:111）／9 公開 → 一部（:66・:78。外枠の段では足りるが、推定器を公開しないと決まれば受理に効く穴）

## 2. 評価表
a 4（主の文は notes.md:133・137 と合う。持ち帰りの主語「作文の打鍵で学んだ」の出どころが資料に無い）／b 3（IDE の編集の出来事を打鍵に写す対応が 5 量の意味を保つかが無い・推定器の陽性対照が無い〔:71 で認める〕）／c 3（部品の名指しは "generalizable methodologies" に合うが、利点は「この形で確かめられる」までで重心は陰性の 1 結果）／d 4／e 4（推定器の公開が未決）／f 4（[V157] を個人化の動機に使っていない・ラベルの外部照合の扱いが無い）

## 3. 指摘
- [major] 「作文の打鍵で学んだ」推定器の係数の出どころが外枠と根拠の資料に無い
  - 位置: :17「作文の打鍵で学んだ状態推定器の 2 つの信号」・:7「作文の打鍵で学んだ型の状態推定器」・:34「作文の係数を固定したまま使うこと」
  - なぜ: 「学んだ」は係数を作文の打鍵データから推定したという主張。根拠の資料は「it uses the writing head (coefficients without IME; `heads/writing.rs`)」（prereg-draft.en.md:39）だけで、どのデータからどう推定したか（手で決めたのか）が読んでよいファイルに無い。持ち帰りの主語で、:7 の「持ち出しだけでは説明しにくい」も係数が作文に合うことを前提にする。
  - 解消: 3 節に係数の由来（データ・人数・手続き、または手で決めた値）を 1〜2 文、出どころを S2。もとの領域で Stuck が打鍵の外の何かと照合されたかを 1 文（無ければ無い）。推定で決めた値でなければ「学んだ」を「作文向けに係数を定めた」などに。自信 中（外に記録がある可能性は残る）
- [minor] 推定器の状態「Stuck」とラベル「停滞」が同じ語（:111「停滞の確率の 30 秒の差」・:83「文字の産出の停滞」）。「停滞の確率が停滞を識別しない」が自己矛盾に見える。「摩擦の量」も合成に解釈を乗せた名前。Roeser の "operationalised within the statistical models"。解消: 推定器の状態には別の語（例「推定器の Stuck 状態の確率」）、語を分ける規則を :111 に 1 行、`ewma_x` は中身が分かる語に。自信 高
- [minor] CS1 の入力から作った 5 量が作文の量と同じものを測るかの記述が飛行時間だけ（:76・:101）。訂正の比・バーストの長さ・削除の後の休止の割合は、複数の文字の挿入（補完・貼り付け・自動のインデント）や範囲の削除を何打に数えるかで変わる。解消: 3 節か S2 に写す規則の小表と、取り置きで複数の文字の出来事が占める割合。限界に「5 つの量の意味は作文と同じとは限らない」。割合が結果に無ければ条件を先にコミットしてから数える。自信 中
- [minor] 停滞を上位の構成概念の「代理」と書く根拠が無い（:83「停滞はその秒単位の代理の 1 つ」・:44 停滞の 47% は休止の中に出来事）。Roeser の off-task・Guo の外部の照合。解消: 「秒単位で観測できる候補の 1 つ（上位の構成概念との対応はこの研究で確かめていない）」に、限界 :75 にラベルが打鍵の外の証拠と照合されていないことを 1 句。自信 中
- [nit] :7 の問いの「型の」が主語を型にかける。「作文の打鍵向けの状態推定器（HMM・型の 1 例）の信号」に。自信 中
- [nit] 柱 2 の個人化の文（:92）に [V157]（guo2020.txt:240 "Such a personalized threshold"）を。自信 高

## 4. 総合: minor
- round 4 の major は解消し、主の文は確認の値・人数・幅と一致。
- 新しい穴は計器の由来と語の対応に集中し、3 節と書き方の規則への追記で塞げる。
- 引き継ぎ 4（全時間での計器の挙動）は草稿の前に条件をコミットして数えることを書き進める条件にする。

## 5. 読めなかった範囲・注入
接地の 2 本は grep の周辺だけ（roeser2025.txt:150-179・510-534・1184-1222、guo2020.txt:236-255・1035-1069）。prereg-draft.md・prereg-draft.en.md・notes.md 2 本・novelty.md・related-work.md は grep の行だけ。conditions.md・explore_*.json・seed_spread.json・20261101 の notes 2 本は読んでいない。confirm_holdout.json は floor/variance/std/frac の grep だけ。注入の疑いなし。
