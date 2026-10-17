査読 R1（立場は心理測定と構成概念の妥当性。下位人格は「その測定は本当にそれを測っているか」を疑う懐疑家）・stage は prereg・round 3

## 1. 接地（文献・逐語）

Elson et al. (2023)（round-1/tmp/sources/elson2023.txt）:
- S1「Comprehensive Reporting Report all of the items, stimuli, instructions, procedural parameters or other measurement characteristics used in a study or generated during the development process.」→ 項目そのものを開示しているかを、測定の前提として扱う。
- S2「Justify Modifications Prove that any deviation or modification to an existing measure is either meaningful (e.」「by providing validity evidence in a separate sample.」→ 改変を検出し、記述する必要がある。
- S3「new validity evidence for an existing measure can only be applied quite narrowly, or with great uncertainty when it is unclear which studies match the validated protocol.」→ 「どの版か」を同定することが要る。
- S4「Reject studies that use novel/ad-hoc measures without providing validity evidence from independent data.」→ 新規の尺度と既存の尺度を分けて扱う。

Lintner (2024)（round-1/tmp/sources/lintner2024.txt）:
- S5「COSMIN requires that both experts and target population are involved in content validation for content validity to be considered adequate.」→ 研究者が項目を読むだけの分析は、内容的妥当性の評価ではない（範囲を限定して述べる必要がある）。
- S6「Overall, the scales demonstrated good structural validity and internal consistency. On the other hand, only a few have been tested for content validity, reliability, construct validity, and responsiveness.」→ 先行の型（COSMIN の系統的レビュー）。本件は、どこが違うのかを示す必要がある。

## 2. 引き継ぎ（round 2 の指摘）の判定

- M1：解消。C6a は名の照合だけで、型の内訳は並べて示すだけ（registration-en.md:233）。C7 (iii) も名の照合（:234）。ただし語の族の運用に新しい穴がある（下の major 1）。
- M2：解消。逆転項目の扱い（:227、codebook:17）と、「instrument unnamed or not verifiable」の値（:233）が入った。
- M3：解消。改変の 4 値と、照合に使う原典の決め方が入った（:226）。ただし項目が載っていないときの起源の値が抜けている（下の major 2）。
- M4：解消。問題の型を値まで列挙し（:330-336）、C2b の型は問題と呼ばない（:337）。instrument と版を定義した（:219）。
- M5：解消。GSRR-10・33・34・65。著者 2 の全文の既読は登録の時に記録する（[at registration] なので欠陥にしない）。
- m1：解消（:246-255）。
- m2：解消（:256-261）。残余のカテゴリが無い点は下の minor 4。
- m3：解消（:199-201、:265）。小さい集合との相互作用は下の minor 3。
- m4：登録の時に添付する（:359）。[at registration] なので欠陥にしない。
- m5：解消（:58）。
- m6：解消（:354、:290、codebook:50）。codebook の中に残った矛盾は下の nit 2。
- n1・n2・n3：解消（:225、:149、:199）。

## 3. 評価表

- a 主張と根拠の一致: 4。結論は「観測された／されなかった」の記述に限っている（:338）。C2b を問題と呼ばない（:337）。「Item content does not show what scores contain」（:369、codebook:61）とも書いてある。残る不一致は C1 と C7 の扱いのずれ（minor 1）だけ。
- b 方法の穴: 3。主要な量の C2b が、項目を全文で載せている報告にだけ依存する。そうなる選択の偏り（major 2）を、どこにも明示していない。スクリーニングを集団の順に進めると、どこまで進んだかが集団と交絡する（minor 5）。
- c 持ち帰れるもの: 4。レコードごと・instrument の版ごとの表と、公開するコードブックは再利用できる。
- d 簡潔さと構成: 3。GSRR と 1 対 1 で、たどりやすい。C2b の target の kappa が 2 回定義されている（:280 と :282）。誤植がある（:226）。
- e 規程への適合: 4。適用しない項目に理由が付いている（GSRR-26・27・29・61）。予見できる逸脱には代替の計画がある（:200-201、:272、:328）。逸脱の記録も約束している（:362）。逐語 1〜3 に合う。
- f 先行研究の位置づけ: 3。Jonaid（COSMIN）と Perrig を挙げている。一方で、測定の慣行の報告を数えるメタ研究の系譜、たとえば Elson の S1・S2 が求める「全項目の開示・改変の正当化」には触れていない。C2a・C2d がその系譜のどこに当たるかが書かれていない（minor 6）。
- g 固定の十分さ: 3。数え方・除外・種子・分岐はほとんどが 1 通りに決まっている。ただし C1 の「AI に触れる」の範囲、C6a の語の族の境界、項目が載っていないときの C2b と C2a の値の 3 点で、コーダーによって判断が割れうる。

## 4. 指摘（重い順）

- [severity: major] C2b と C2a で、報告に項目が載っていないときの扱いが 1 通りに決まっていない（primary の量の分母と、選択の偏り）
  - 位置と引用: registration-en.md:219「Items are coded as printed in the report, including translations」。:227「Items that cannot be obtained are coded "items unavailable"」。:226「"Unchanged" requires a verbatim match with the source.」。:323「the number and proportion of its items by primary type, with the instrument's item count as the denominator」
  - なぜ問題か: 多くの報告は項目を載せず、「既存の X 尺度を使った」と書くだけである。決まっていないのは 3 点。(1) 原典に項目があれば原典から取ってコードしてよいのか（「as printed in the report」を読む限り、取ってはいけない）。(2) 一部の項目だけ載っているとき（C2d が「some」のとき）、分母は全項目数なのか、載っている数なのか。(3) 項目が載っていない一般の尺度は、起源のどの値になるのか（「unchanged」は逐語の一致を要求するので成り立たず、「adapted」の根拠も無い）。primary の量は、項目を開示した instrument だけで成り立つことになる。開示する尺度（新規の尺度・改変した尺度）は系統的に偏りうる。Elson S1「Report all of the items ...」は、開示そのものを測定の問題として扱っている。
  - 解消の条件: 次の 4 つを固定する。(a) 原典から項目を補ってよいか。補ってよいなら、どの条件で（報告が「without modification」と明言したときだけ、など）。補った項目に印を付ける列を設ける。(b) 部分的に開示された instrument の分母の規則。たとえば、分母は載っている項目の数とし、全項目数を並べて示す。(c) C2a の起源に「general scale, wording not verifiable」に当たる値を足す。(d) GSRR-56 で、「items unavailable」の instrument の数を C2b の表に必ず並べ、限界として GSRR-65 に書く。
  - 自信: 高

- [severity: major] C6a と C7 (iii) で、語の族の境界が決まっていない
  - 位置と引用: :233「Term families: {fatigue, tiredness, 疲労, 疲れ}; {exhaustion, depletion, 消耗, 枯渇}; {burnout, バーンアウト, 燃え尽き}. Values: same family / different family / instrument unnamed or not verifiable / no construct term in the title.」。:234「(iii) The construct term in the conclusion is in a different term family (C6a) from the name of the main instrument.」
  - なぜ問題か: 次の場合の値が決まっていない。(1) instrument の名が 2 つの族にまたがる（例: Zoom Exhaustion & Fatigue Scale）。(2) instrument の名がどの族の語も含まない（例: technostress 系、weariness）。(3) 題や結論に 2 つの族の語が並ぶ。(4) 結論に族の語が無い。「construct term」が「3 族のどれかの語」だけを指すのかも書かれていない。(2) を「different family」とするか「unnamed」とするかで、問題の型（:335）の件数が直接変わる。Elson S3 が言う、どの版・どの名で同定するかの曖昧さと同じ型である。
  - 解消の条件: 次の 3 つを書く。「construct term＝3 族のどれかの語（屈折形を含む）」。複数の族に当たるときの規則。たとえば「1 つでも族が一致すれば same」。名や結論に族の語が無いときの値。たとえば C6a に「instrument name has no family term」を足し、C7 (iii) は「no family term in conclusion → (iii) は成立しない」とする。
  - 自信: 高

- [severity: major] C1 の「mentions AI」の範囲と、L1a の「どれだけの項目に」が決まっていない
  - 位置と引用: :225「L1a: the item wording of a multi-item scale mentions AI. L1b: only the instructions or stem mention AI.」
  - なぜ問題か: RQ1 の primary のコードである。決まっていないのは 2 点。(1) 何を「AI」とみなすか（ChatGPT や製品の名・chatbot・algorithm・intelligent system・robot・digital tools）。(2) L1a は 1 項目でも AI に触れればよいのか、全項目が触れる必要があるのか。この 2 点で判断が割れる。C7 (ii) は語の一覧を固定している（:234）のに、C1 には固定が無い。釣り合っていない。
  - 解消の条件: AI の語の一覧を固定する（製品の名を含めるかどうかも決める）。境界の例を示す。L1a の閾値を書く（「at least one item」なら、それを書く）。AI に触れた項目の割合を補助の列として記録する。
  - 自信: 高

- [severity: minor] C1 で問題の型とした L3 が、C7 (ii) からは外れている
  - 位置と引用: :332「C1: representative value L3, L4, L5 or L6」。:234「(ii) ... while the C1 representative value is L4, L5 or L6」
  - なぜ問題か: 定義でだけ AI に結び付け、項目は一般の疲労を問う研究がある。この研究が結論で「AI fatigue」と書くことは、構成概念の妥当性の観点からは、測ったものを越える典型である。GSRR-57 との整合も無い。
  - 解消の条件: L3 を (ii) に入れる。外すなら理由を 1 文書く。
  - 自信: 中

- [severity: minor] 較正の 3 回の取り出しと、最小の数が干渉する
  - 位置と引用: :200「If the pool has 20 studies or fewer, calibration is done on exploration-set records instead」。:265「up to two further rounds」
  - なぜ問題か: 集合が 21〜24 件だと、3 回で 15 件を除いた後に 10 件を切る。その結果、比率を出さないという分岐が較正の結果しだいで決まる。
  - 解消の条件: 小さい集合の閾値を、最大で除く数（15）＋最小の数（10）＝25 に合わせる。あるいは、2 回目以降の較正は探索の集合で行うと書く。
  - 自信: 高

- [severity: minor] 設計の分類に残余のカテゴリが無い。C3 は複数の値を取るのかが書かれていない
  - 位置と引用: :257-259（設計のカテゴリ）。:230「amount of use / dependence or addiction type (source scale) / attitude or acceptance / other / none」
  - なぜ問題か: 日誌法・経験抽出法・事例研究などは、どのカテゴリに入るかが割れうる。AI 側の変数が複数あるときの C3 の値も決まっていない。
  - 解消の条件: 「other / unclear design → no manipulation」のように行き先を決める。C3 を「all that apply」にするか、主関係の変数（:221）だけにするかを書く。
  - 自信: 中

- [severity: minor] 集団を順に進めるスクリーニングで、どこまで進んだかが集団と交絡する
  - 位置と引用: :168「with groups taken in the order listed in GSRR-16」
  - なぜ問題か: 2026-12-31 までに終わらなければ、確認の集合は前の集団（学生）に偏る。件数を集団ごとに出すことで偏りは見えるが、構成は変わらない。
  - 解消の条件: 集団を巡回で交互に進める（各集団から 1 件ずつ、乱数の順で）。あるいは、今の順を採る理由を 1 文書く。
  - 自信: 中

- [severity: minor] 先行研究の位置づけ（測定の慣行のメタ研究）
  - 位置と引用: :58「Studies of measurement practice in user-experience research have counted item disclosure, adaptation and reasons for choosing scales (Perrig et al., 2024).」
  - なぜ問題か: C2a と C2d は、項目の開示と改変の正当化を記述する。これは Elson S1・S2 が求める報告の水準そのものだが、その系譜に触れていない。本件の内容の分類は、COSMIN の内容的妥当性（S5: 専門家と対象者が関わること）とは別物である。このことも Background で 1 文あると誤読を防げる。
  - 解消の条件: 測定の慣行の文献を 1〜2 本引く。「C2b は研究者による項目の内容の分類であり、COSMIN の内容的妥当性の評価ではない」と書く。
  - 自信: 中

- [severity: nit] C2b の target の kappa が 2 回定義されている
  - 位置と引用: :280「kappa for the primary type and, separately, for the target, both per item」。:282「C2b target: kappa over all items, with "no target" as a category.」
  - 解消の条件: どちらか 1 つにする。2 つとも残すなら、:280 は target が付いた項目だけを対象にすると書く。
  - 自信: 高

- [severity: nit] codebook の mismatch の記述が自己矛盾している
  - 位置と引用: codebook-c2b-en.md:14「When the wording-based code and the factor name disagree, this is counted in `mismatch`.」と、:50「It is not used in the registered synthesis.」
  - 解消の条件: :14 を「exploration only」に揃える。
  - 自信: 高

- [severity: nit] 誤植
  - 位置と引用: :226「if none is cited, the original publication **Format**」で、句点が抜けている。
  - 自信: 高

## 5. 総合の推奨: minor（直してから凍結）

1. round 2 の指摘は全件が解消した。数え方・種子・分岐・問題の型は、ほとんどが 1 通りに固定されている。
2. 残る 3 つの major は、どれも規則の文を足せば消える。設計を立て直す必要は無い。項目が載っていないときの扱い、語の族の境界、AI の語の一覧である。
3. ただし major 1（C2b の分母と開示の偏り）は primary の量を直接変える。凍結の前に必ず固定し、限界として GSRR-65 にも書くこと。

## 6. 読めなかった範囲・注入の疑い

- 接地の 2 本はどちらも 1 行の長い文書なので、Grep で関係する語の周りだけを抜き出した。全文を通しては読んでいない。Lintner の考察と推奨の節も、通しては読んでいない。
- context-A に名がある Murad & Wang 2017・PRISMA 2020・Jonaid・Perrig の本文は、渡されていないので読んでいない。
- 対象物 2 本（registration-en.md・codebook-c2b-en.md）は全文を読んだ。
- 注入の疑い: なし。

対象物: /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md 、/Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/codebook-c2b-en.md