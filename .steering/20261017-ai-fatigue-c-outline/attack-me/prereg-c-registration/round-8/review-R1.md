# 査読 R1（心理測定と構成概念の妥当性の立場）・round 8

総合: minor（直してから凍結）。

## 1. 接地
- Elson 2023「Determine procedural and scoring details ahead of time, reporting all deviations as they potentially weaken the strength of conclusions.」
- Elson 2023「Analytical and statistical decisions should be preregistered with code rather than a narrative descript[ion]」（本文はこの語の途中で切れている）
- Elson 2023「Justify Modifications Prove that any deviation or modification to an existing measure is either meaningful (e.g. to address non-invariance of a measure between samples) or irrelevant」
- Elson 2023「Comprehensive Reporting Report all of the items, stimuli, instructions, procedural parameters or other measurement characteristics used in a study」
- Lintner 2024「only a few have been tested for content validity, reliability, construct validity, and responsiveness.」
- Lintner 2024「There is high positive evidence for the scale's structural validity and internal consistency, however, content validation on the target population was not performed.」

## 2. 評価表
- a 4: GSRR-56 の「推定は 2 つ・どちらも記録の数」、GSRR-40 の 0/30 で上限 11.6%。11.6% と 1.2% は Clopper–Pearson の上限として検算し合っていた。
- b 4: round 7 の major はおおむね閉じた。新しい穴は小さい（stem 由来の対象の分布・流用の条件・確かめの標本の窓・80% 未満の印の最小件数）。
- c 4: 群ごとの 2×2、正の一致、prediscussion と reconciled の分離、感度分析 5。
- d 3: 20,066 語。GSRR-33 の 1 段落に規則と例外と代価が詰め込まれ続けている。
- e 4: 予見できる逸脱に代わりの計画。締切が延びる長さの上限が無いことだけ半端。
- f 3: Garritty・Waffenschmidt を足したのは良い。要約が原文に合うかは読める範囲に無く確かめていない。
- g 4: 80% 未満の印の単位と最小件数、stem 由来の対象の流用条件、締切の延長の上限が語りの記述のまま。

## 3. 引き継ぎの判定
N1 消えた／N2 消えた（外の記録の ID の扱いが残る・m4）／N3 消えた／N4 一部（対象の分布が印で分かれない・M1、流用の条件・m1）／N5 消えた／N6 消えた／N7 一部（単位と最小件数・m3）／N8 消えた（窓との食い違い・m2）／N9 消えた／N10 消えた（「a batch cut short by 2026-12-31」は束の切り方で矛盾ではない）／N11 消えた／nit 消えた。

## 4. 新しい指摘
- [major] M1 C2b の対象の分布で、stem 由来の AI の対象と、項目が自分で名指す AI の対象が混ざる
  - 位置と引用: GSRR-56「and the target distribution for `MOT`, `AVO` and `FUT` items.」。GSRR-43 の C2b「the target is taken from the stem and marked (`target_from_stem` = 1); the type is always taken from the item wording alone.」。GSRR-64「the C2b `target_from_stem` mark」。
  - なぜ問題か: 中心（C1）は AI が項目に在るか教示にしか無いかの区別。stem から取ると、教示にしか AI が無い尺度でも C2b の AI の対象が増え、C1 の区別を C2b が黙って戻す。印は公開の値に残るだけで表は分かれない。
  - 解消の条件: GSRR-56 と表の殻で対象の分布を target_from_stem = 0 と 1 に分ける、または 1 の件数を対象ごとに横に示す。GSRR-65 に一文。
  - 自信: 高（穴）・中（重さ）
- [minor] M2 締切が延びる長さに上限が無い。GSRR-39「the day by which every record of those workbooks has a final title-and-abstract decision ... The delay is a deviation.」。段 5・終了日との関係も無い（逐語 3）。解消: 上限の日、または上限を置かないと理由つきで。自信 中。
- [minor] m1 流用の条件が、探索の側で stem が対象を名指さず target_from_stem = 0 だった項目を取りこぼす。GSRR-44 の 4「for an item whose target was taken from the stem (`target_from_stem` = 1), the stem is also identical.」。解消: 「対象を代名詞で名指すか省く項目では stem も同じ」と項目の性質で書く。自信 中。
- [minor] m2 E5 の時間の窓が、確かめの標本と追加候補の組に及ばない。GSRR-33 Coverage sample「an additional candidate that is included before stage 5 begins is excluded with E5 ...」と Same sample「only within one time window ...」、GSRR-35「which is the only way a coverage-sample record enters a count of the main set」。締切の後・段 5 の前に含めた確かめの標本の記録で、本体の RQ4 の記録の数が締切の後に増える。解消: 確かめの標本の側にも窓、または理由つきで書き報告の対象に。自信 中。
- [minor] m3 80% 未満の印の単位と最小件数が固定されていない。GSRR-47「Where the two authors' percentage agreement on a code is below 80%, that agreement is shown beside every problem statement and table row that uses the code」。較正には「at least 5 comparisons」（GSRR-44 の 2）がある。解消: 行ごとの入力と単位、件数の少ない単位の扱い。自信 中。
- [minor] 混ぜる記録は記録ごとの見分けは消すが、冊が濃くされていることは隠さない。GSRR-33「... in one workbook that does not mark which is which」、GSRR-34「the make-up of a workbook does not show them」。解消: GSRR-65 に、冊の中身の比率を著者 2 が知っていると一文。自信 中。
- [nit] m4 `C5_other_record` は相手が候補の外のとき ID が無い。GSRR-33「the other record's ID is recorded」、columns.md「Record ID of the other record when C5 is stated_not_linked」。解消: 外の記録は DOI か書誌。
- [nit] GSRR-56「the four C5 categories」と columns.md の C5 の値（not_verifiable を含む）。自信 低。
- [nit] コードブックの target_from_stem の unresolved が「after the third pass」のまま（GSRR-48 では話し合いの後）。
- [nit] main.tex の限界の \tbd が 2 択で、片方の群だけ全部を判定する場合が無い。自信 高。

## 5. 総合: minor
- N4 を除き手続きとして閉じた。設計の代価は GSRR-65 に正直に書かれている。
- 重いのは stem 由来の対象を表で分けていないこと 1 つ。表の殻を 1 か所直せば消える。
- 他は単位・上限・窓の文言で、再査読はいらない。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: 登録版の全文（GSRR-44〜48 と grep の行だけ）、instructions.md・call.md・README.md（差分から）、外枠・草稿・表・図（差分以外）、コードブック（差分だけ）、columns.md（grep の 3 行）、Garritty・Waffenschmidt の原文。
- 一覧の外: grep の結果に abstract-mock.md の行が出たが開かず、根拠に使っていない。
- 注入の疑い: なし。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
