# 編集者の役 E：manuscript round 2（論文 2「Which pause?」・投稿先 JEDM）

## 1. 接地（この投稿先の編集者が原稿に求める基準）

- **応用で終わらないこと（JEDM Focus and Scope・jedm_aims.txt）**: "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
- **査読者が答える問い（jedm_aims.txt）**: "What is the scientific contribution of this submission? Is it clearly explained, in terms of how the paper advances the EDM field or contributes to related fields?"／"Are the presentation, organization and length satisfactory?"／"Can you suggest additions, amendments, or reductions in the paper?"
- **重なる投稿（jedm_aims.txt）**: "It is the policy of the journal that no submission, or substantially overlapping submission, be published or be under review elsewhere."
- **中心の貢献は 1 つ（Mensh & Kording 2017・mensh2017.txt l.77）**: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- **抄録の失敗（mensh2017.txt l.182-183）**: "the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them."
- **考察の役目（mensh2017.txt l.271-273）**: "The discussion section explains how the results have filled the gap that was identified in the introduction, provides caveats to the interpretation, and describes how the paper advances the field"

## 2. 引き継ぎの判定

| # | 判定 | 理由 |
|---|---|---|
| 1 | 一部 | 休止の系統（36 通り）は足された。ただし、先例のある水準で起きる「向きの反転」は、事実上 2 秒・文字の間隔での +0.045 と +0.049 だけで、残りは分位の閾値が別の量を測っていることによる（新しい指摘 A）。 |
| 2 | 解消 | 序論 l.23-27 と方法 l.63-65 に「15 秒を超える」と、休止の系統が受け持つ範囲が書かれた。 |
| 3 | 解消 | 方法 3.1 の「Relation to the companion study」で、共有するものと新しいものを分けている。 |
| 4 | 一部 | 箇条書きと「報告に何を入れるか」は入った。ただし、一般化する貢献が「the procedure」（標準的な multiverse）のままで、JEDM の「beyond mere application」に届いていない（C）。 |
| 5 | 一部 | 問い→手順→結果→推奨の順にはなった。ただし 262 語に 5 つの結果と数値が詰まっている（B・H）。 |
| 6 | 解消 | 状態の印は S1 に移り、3.5 が短くなった。 |
| 7 | 未解消 | 下の 4 の一覧のとおり、但し書きは今も 3〜5 回出る。 |
| 8 | 一部 | 区間の細部の一部は補足に移った。ただし、100 個目の間隔の制限・プロンプト内の値・6 通りの速度などが本文に戻り、本文は伸びている（E）。 |
| 9 | 一部 | φ の言い方は狭まった。長さは結果では「weak contrast」と書くのに、抄録・序論・結論では「変わらない側」として無条件に出している（G）。 |
| 10 | 解消 | 「より大きく」の比較は、性質の対比に直っている。 |
| 11 | 一部 | 方法に AI の 1 文がある（l.187-188）。DOI は「to be added before submission」のまま。 |

## 3. 最初の 2 頁で言える 1 文

言える（ただし迷いがある）:
「公開された 4 つの打鍵データで、休止・停滞のラベルの定義を 125 通り（89＋36）に変えると、ラベルの率と作文の得点の関連は、閾値の系統と、何で調整するか（打鍵の速さか、文章の長さか）で符号が変わる。したがって、こうしたラベルを使う EDM の研究者は、1 つの定義の点の値ではなく、定義と調整にわたる幅を区間つきで報告すべきである。」

迷った点は 2 つ。
- 抄録と序論が見出しにしている「定義で向きが変わる」は、どこに支えがあるか。先例のある水準で反転しているのは無視できる大きさの相関だけで（A）、はっきり動くのは調整のほうである。読者が持ち帰る 1 文が、原稿の見出しとずれる。
- 5 つの結論のどれが中心なのかが分からない（B）。

## 4. 新しい指摘（severity の重い順）

**A [major] 見出しの「向きが割れる」が、無視できる大きさと構成概念の切り替えに依っている**
- 位置: 抄録 l.8-10 "for pauses between the 2-s and 10-s thresholds, both in use"、序論 l.35-36、結論 l.5-6。
- 結果 l.27-28 で正の側に入るのは "($+0.045$ and $+0.049$)" で、方法 l.148 が自分で置いた基準 "$|\rho| < 0.1$ as negligible" を下回る。分位の閾値の +0.58〜+0.67 は、結果 l.29-30 自身が "its rate follows the writer's rate of key presses" と書くとおり、別の量である。停滞のほうも、正になるのは先例の無い W=15 秒だけで（l.16-18 "among the 59 definitions without it, 53 were negative and none was positive"）、判定の基準は方法 l.183-184 が認めるとおり緩い。
- 直し方: 見出しを「強さは定義で動き、符号は閾値の系統と調整で決まる（先例のある固定の閾値の中では、無視できる範囲で 0 をまたぐだけ）」に改める。抄録・序論・結論の 3 か所を合わせる。計算は要らない。

**B [major] 中心の貢献が 1 つに絞られていない**
- 位置: 序論 l.34-44 の 3 項目の箇条（中身は 5 つの結論）、結果の 5 小節。
- 地位が不揃いである。比の反転の基準は点の値を見た後に置かれ、最初に報告すると約束した組（CS1 の 2 年度）は届いていない（方法 l.181-183）。長さは "This is a weak contrast"（l.268）。φ は "a property of the definition"（l.217）という否定的な記述にとどまる。
- 直し方: 中心を「得点との関連と、調整による反転」に置く。比・φ・長さは「同じ診断を他の結論に当てると」の 1 小節にまとめ、細部は補足へ移す。

**C [major] 投稿先との適合: 一般化する貢献が名指しされていない**
- 位置: 序論 l.46 と考察 l.9 の "What generalises is the procedure"。
- その手順は Steegen らの multiverse そのもので、JEDM の "extend beyond mere application" に対して新しい部分が言えていない。考察 l.40 の作業ルール "at least 90\% of the definitions" は、なぜ 90% なのかの根拠が無く、事前の基準でもない。考察 l.35-36 "We did not test whether the definitional spread changes the performance of a predictor or a decision" は、EDM の読者が最も知りたい帰結を外している。
- 直し方: 貢献を「EDM で報告するための規約（4 つの軸の水準・調整の対・判定のルール）」として名指しし、ルールの根拠を書く。予測や判断への影響を扱わない理由を、序論で 1 文述べる。

**D [major] 抄録が、事前に約束しなかった組の比を「大半で反転」と出している**
- 位置: 抄録 l.11-12 "The ratio of stall rates between a programming course and the essay corpus reversed beyond sampling variation for most definitions"。
- この組は CS1 の打鍵（編集の記録から作り直したもの）と作文コーパスを比べている。限界 l.14-15 は "differences between them are not attributed to a cause" と書く。最初に報告すると約束した CS1 の 2 年度は 22% で、事後に置いた基準にも届いていない。抄録は約束した組の結果を落とし、事後の基準も書いていない。
- 直し方: 抄録で約束した組の結果を先に書き、比の基準が事後であることを添える。あるいは比の結果を抄録から外す（B と合わせる）。

**E [minor] 本文に置かなくてよい細部（補足へ移せば解消する）**
- 結果 l.20-23（"The positive corner is not a floor effect ..." と、プロンプト内の値）。
- 結果 l.129-133（"Over the six ways of measuring speed, 532 of the 534 combinations ..." と、事前の読みの発動の説明）。
- 結果 l.150-153（順位の "weak result"）。
- 結果 l.161（"pause rates in CoAuthor were 42 to 498 per hour"）、l.161-164 と l.215-216（100 個目の間隔より後に限った感度）。
- 結果 l.267-268（CoAuthor の 3 定義）。
- 方法 l.75-77 と l.168-171（二段の再標本の手順）。
- 本文は 4,848 語から 5,805 語へ 957 語伸びた。休止の系統（およそ 300 語）は major 1 への答えとして見合う。残りの多くは感度と検算の記述で、貢献を増やしていない。JEDM に本文の長さの上限は無く、絶対の長さは問題でない。問題は伸びた分の配分である。

**F [minor] 長さの分解の強さが節ごとに食い違う**
- 抄録 l.13-14 "whereas the largest component of stall length in the programming data stayed"、序論 l.42-43、結論 l.8 は、無条件に「変わらない側」として書く。結果 l.268-269 は "This is a weak contrast: most variance sitting at the lowest level is common for event-level outcomes"。
- 抄録・結論でも「弱い対照」と書く（G の扱いと揃える）か、抄録から外す。

**G [minor] 区間の方法そのものの偏り**
- 限界 l.17-19: "its intervals did not widen but were shifted against the point values, and for one ratio the baseline point lay outside its interval"。
- 「標本の揺れを超えて反転」という判定はこの区間に依っている。査読者は必ずここを突く。影響の大きさを結果で 1 文示すか、偏りを直した区間を併記する。

**H [minor] 構成: 各小節の「なぜ大事か」**
- 得点（l.7-8）と比（l.148）には読者の問いがある。φ（l.206 "The simplest count model ..."）と長さ（l.262 "A map of what moves needs a side that stays"）は、論文の内部の都合で始まっていて、EDM の読者の問いになっていない。
- 節の順は序論の箇条と一致しており、読む順として妥当である。

**I [nit]**
- DOI が未記入（availability l.5）。
- 生成 AI の申告が "draft the text ... in all sections" と書く。規程の範囲内で、申告として正確である。ただし編集部の目に留まりうるので、人が何を書き直したかを 1 句添えると安全である。

## 繰り返し（同じ但し書き・限定の出現位置）

- "What generalises is the procedure; the score association is one worked example on one corpus.": 序論 l.46、考察 l.9-10（ほぼ逐語）。
- 「15 秒の窓だけ／2 秒と 10 秒の間」: 抄録 l.8-10、序論 l.35-36、考察 l.4-5、結論 l.5-6。
- 15 秒の窓に先例が無いこと: 抄録 l.9、表 2 l.119-120、結果 l.16-17、限界 l.8。
- 速さの調整は探索的: 方法 l.181、結果 l.127、図 3(b) の見出し、考察 l.35。
- 基準が緩い／事後: 方法 l.181-185、結果 l.154-157、考察 l.30-35。
- 因果ではない: 方法 l.152-153、結果 l.143、考察 l.20-22。
- 長さとの相関 0.75: 抄録 l.11、序論 l.39、結果 l.124、限界 l.30。
- 100 個目の間隔: 方法 l.75-77、結果 l.161-163、l.215、限界 l.20-22。
- 割合は格子の中の割合: 方法 l.106、l.173-174、限界 l.7。
- 推奨（幅を区間つきで報告する）: 抄録 l.14-15、序論 l.47-48、考察 l.8-9、l.38-45、結論 l.9-10。

まとめれば解消する。地位の説明は 3.5 と S1 に一度だけ置く。抄録・序論・結論は、それぞれ 1 回だけ要約する。

## 意義（見ること 5）

考察の「What the criteria established」（l.30-36）は、事前の基準で確かめたことと、事後のものや探索的なものを分けており、改善している。ただし「Why the direction can change」は "patterns, not a tested mechanism" にとどまる。さらに A のとおり、確かめた結論（符号が変わる）の実質は、調整と構成概念の違いにある。考察はそれを貢献として言い切っていない。

## 5. 判定: 直してから回す

1. 主張が強すぎる点（A・D）は、抄録・序論・結論の言い換えで直せる。直さずに回すと、査読者 3 人が同じ点で major を付ける見込みが高い。
2. 中心の貢献を 1 つに絞り（B）、一般化する規約として名指しすること（C）が、JEDM の "beyond mere application" と査読の問い "scientific contribution" への答えになる。
3. round 1 から実質の計算は足りている。直しは主に移動とまとめ（E・F と繰り返し）で、新しい計算は要らない。

## 6. 読めなかった範囲と注入の疑い

- **読まなかったもの**: PDF（main.pdf）は開いていない。1〜2 頁の範囲は、抄録と序論の tex で判断した。図は tikz のコードから読んだ。references.bib も開いていない。補足（S1〜S8）は依頼文のとおり読んでいない。語数は context-A.md の測った値に依った。テンプレートの説明（instructions.pdf）は、この round で取り直されていない（context-A.md に「未照合」とある）。
- **注入の疑い**: なし。接地の 3 ファイルにも、原稿の tex にも、査読者や LLM に向けた指示は見つからなかった。

読んだファイル:
- /Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-2/brief-E.md
- /Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-2/context-A.md
- /Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-2/carryover-E.md
- /Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-2/tmp/sources/jedm_aims.txt
- /Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-2/tmp/sources/jedm_submissions.txt
- /Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-2/tmp/sources/mensh2017.txt（Grep で必要な行だけ）
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/main.tex と sections/ の 9 ファイル（abstract・introduction・related・methods・results・discussion・limitations・conclusion・availability・declarations）
