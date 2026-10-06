# 意図の監査役・原稿 round 2（対象 `b8849a6a`）

全体として、Discussion は研究者の方向性（判断 196・198・200・201）の範囲に収まっています。仮説と事実も分けて書かれています。ただし次の 3 つは直す必要があります。
- **D11・D12 の開示の強さが原稿とdeviations.mdで揃っていない**（3-a）
- **事後に足した D12 の「層ごとの変化」の数が、原稿の D12 の定義にも Results にも無く、Discussion にだけある**（2-e・3-a）
- **AI 宣言の「the author checked and approved it」が、研究者が採った後にメインが入れた直しを覆っていない**（3-b）

## 0. 引き継ぎの判定

| # | 判定 | 根拠（位置と逐語） |
|---|---|---|
| 0-10 | 一部 | 写し元は 2 つに揃った（method.tex:363-365「copied from the result files by a script …, and the figures of the records … from the records of the runs」）。ただし、値から手で書いた語と数はどちらの写し元にも入らない。例は results-text.tex:13-14「in six of the nine strata of speed and cell」（`\rv` でない結果の数）、recoverability.tex:116-117「equal those of the macOS cell with live conversion off to the reported precision」、results-agreement.tex:170-180 の層の名前。外枠 outline.md:478-479 は「no result value is typed or rounded by hand」と書く。手で書くことの開示は main.tex:113-117 の `%` コメントにしか無い |
| 0-14 | 解消 | method.tex:13-15「The study estimates and tests no hypothesis; the only rule that turns an estimate into a decision is the near-chance rule」 |
| 0-15 | 解消 | 引き継ぎの「推奨には足していない」より進んでいる。recommendations.tex:16-19「the minus, comma and period keys in Romaji input, and every kana typed with a symbol key in the kana layout, close a session」 |
| 0-16 | 解消 | limitations.tex:15-16（焦点を自分で失う）・25（S15）・26-27（短い会話）・28-29 と 50-51（キーの経路）・46-49（時計） |
| 0-19 | 一部 | method.tex:13「The registrations call the logger the observer.」は入った。しかし dataset.tex:89「Evaluating an observer that needs other signals」が、"observer" を別のロガーの意味で使ったまま残る |
| 1-1 | 解消 | 0-14 と同じ |
| 1-2 | 解消 | method.tex:44-49、results-agreement.tex:15-21・32-40、declarations.tex:52-55 |
| 1-3 | 解消 | results-agreement.tex:180-183「A miss can come from the timing of a row or from a difference between the lengths of the two constructs」 |
| 1-4 | 未解消（著者の決定どおり） | main.tex:119-122 の「何をしたか」に実行コストとデータセットが無い |
| 1-5 | 解消 | recommendations.tex:37-38「so it is not an independent judgement」 |
| 1-6 | 一部 | 列は足されていない。related.tex:41 の列は 6 つのまま。この次元は「Input-method conversion」のセルに入った（:49 hybrid「inter-key intervals before a candidate is confirmed and after a conversion told apart」、:50 本ロガー「the time of a commit is approximated」）。ほかのロガーのセルには、この次元が書かれていない |
| 1-7 | 未解消（後で） | method.tex:374-376 は「the SHA-256 of the list of files exported」と書くが、表 tab:freezes（:389）には「Files exported 98 / 108」しか無い |
| 1-8 | 一部 | results-text.tex:32「The supplement gives the same measures over all trials」。本文は method.tex:311-313「always given with … the estimate over all trials」と約束している |
| 2-1 | 解消 | main.tex:142-143（キーワード）、conclusions.tex:55-59、recoverability.tex:110-113 |
| 2-2 | 解消 | main.tex:128・132-133、results-agreement.tex:170-178、conclusions.tex:30-36 |
| 2-3 | 解消 | limitations.tex:37-39「so how those sets would fare on human typing is not known」 |
| 2-4 | 解消 | results-agreement.tex:107-108「so this loss of focus gave no false positive of detection」 |
| 2-5 | 解消 | dataset.tex:9-12 |
| 2-6 | 解消 | related.tex:50「Any application, system-wide; the application is not recorded」 |
| 2-7 | 解消 | introduction.tex:34-35、conclusions.tex:10-12「Which of the two Windows routes drove the measured input method was not determined」 |
| 2-8 | 未解消（著者の決定どおり） | main.tex:139-140「nor did either on Windows」に、独立でないことの断りが無い |
| 2-9 | 解消 | recommendations.tex:42「shows whether」 |
| 3-1 | 解消 | results-agreement.tex:202-203 |
| 3-2 | 解消 | results-agreement.tex:28-29「No person pressed a key during it: the 11 presses that the executor sent in it did not reach the reference field」 |
| 3-3 | 解消 | results-agreement.tex:43-45、cost.tex:41-42 |
| 3-4 | 解消 | declarations.tex:16-20 |
| 3-5 | 解消 | introduction.tex:30-32、observability.tex:131-132 |
| 3-6 | 解消 | method.tex:340-344、declarations.tex:86-87 |
| 3-7 | 解消（軽い注あり） | dataset.tex:100-102「released with it \tbd{written at deposit}」。ただし declarations.tex:29「with its datasheet … is deposited」は現在形で `\tbd` が無い |
| 3-8 / 3-9 | 解消（context-B 側） | 原稿も method.tex:409-410「reported next to the registered one for every cell」 |
| 3-10 | 一部 | declarations.tex:59-60 に Discussion の書き方が足された。しかし :66「The interpretation of the results is the author's」は、Results・推奨・結論の解釈も覆う言い方のまま。それらは Claude が下書きし、研究者は §A を「今のまま残す」とした（判断 200-7）。採った後の直しは 3-b を参照 |

## 1. 意図にあって原稿に無いもの

**1-a. D10・D11・D12 が限界の節に無い**
- context-B の「既知の限界」には「凍結のコードの欠陥（D10）…全セルで報告」と「D11 と D12 は…結果を見た後の報告の変更」がある。
- §13（limitations.tex 全体）には D10〜D12 が 1 つも無く、置き場所は method.tex:395-410 と declarations.tex:87-88 だけ。
- 外枠 §12 にも無いので、意図の側の分類（限界に書く）の誤りの可能性もある。どちらかに揃えてほしい。

**1-b. near-chance が甘くなることが限界の節に無い**
- context-B の「ブロック内の依存で near-chance が甘くなりうる」は recoverability.tex:57-59 にある（外枠 outline.md:364-366 も §8 に置く）。
- §13 の Scopes and intervals（:70-73）と Recoverability（:82-85）には無い。§13 の「what else it does not evaluate … is stated in Section …」から辿れるのは "What is not evaluated" の段落で、この断りがある "The near-chance rule" の段落ではない。

**1-c. 持ち帰り 4 の芯が結論に無い**
- 持ち帰り 4 の芯（macOS の一致は実装より規則で決まっていた）は conclusions.tex に無い。:69-70 はデータセットで別の規則を評価できることだけを書く。
- 結論は §6.1 の規則で書くので、足さない判断もありうる。任意の指摘。

## 2. 原稿にあって意図に無いもの（漂流）

**2-a. ¶1「almost exactly … almost the same durations」（discussion.tex:12-13）**
- 自分の規則とぶつかる。method.tex:352-353「the estimates are described without evaluative words」、outline.md:56-57「no estimate is described with evaluative words」。
- 範囲が無い。最初の文に「In the primary scope」が無い（範囲は次の文から）。
- 根拠はプールの値だけ。Results の層ごとの区間（results-agreement.tex:190-193）は主の範囲で 0.845–1.000（off）・0.815–1.000（on）、全試行で 0.301・0.207 から（`predobs.all.recall.range`）。長い試行のプールは 0.920（:239）。登録 §6.1 は「The primary estimates are given per stratum」。
- 直し方の案: 程度の語を外し、範囲を付けた数で書く。

**2-b. ¶4「set mainly by its rules rather than by their implementation」（discussion.tex:71-72）は片側だけを言う**
- ¶1 の根拠は「where the sessions that its rules define differ from the sessions of the reference」（:32-34）。参照の側の規則も一致を決める（limitations.tex:9-11「The ground truth depends on the rules that assemble sessions … a rule that did not fold them would define a conversion differently」）。
- ¶4 は差の片方（ロガーの規則）だけを主語にしている。読者は「ロガーの規則を変えれば一致が上がる」と読みうる。
- 研究者が採った「決まっていた」の向きは保てる。例: 「set mainly by how its rules define a session relative to the reference」。

**2-c. 尺度の段落（discussion.tex:111-116）が両 OS の値を 1 つの列挙に並べる**
- 100 ms 以内の割合を macOS 2 セルと Windows（37.1%–37.5%）で、同じ文の中に並べている。
- 直前の :77-78「the values of the two systems are therefore not compared」と外枠 outline.md:122-123「not set against the macOS values」に対し、断りは「each as its logger defines a session」の 1 句しか無い。

**2-e. Discussion が Results に無い値を初めて出している**
- 該当する値: 予測との比較のプールの取り逃しと誤検出の率、`predobs`・`gtpred` の長さの一致の限界の幅と中央絶対差、`layer.none` の値、`gtpred` の最低の層、D12 の層ごとの変化の数（:90-95）。
- 外枠は AG6 を「Section 6; Table 8」に置く（outline.md:501）。Discussion の中心の主張の根拠が、結果の節には補遺への参照としてしか無い（results-agreement.tex:278-279）。
- D12 の変化の数は補遺の表（detection-definitions.tex）にも無い。読者は Discussion でしか見つけられない。
- 判断 200-4 で研究者が採った置き方だが、外枠の置き場所とは食い違う。

## 3. 矛盾

**3-a. D11・D12 の開示の強さが揃っていない**
- deviations.md:3-5・271-272・298-303 は 3 つのことを書いている。
  - 何が引き金か（「when a simulated review of the article before its submission pointed out these values」）
  - D12 の段階（区間の範囲は「recorded that they would be reported whatever their values before they were computed」、変化の数は「added after the ranges had been seen, when a review of the discussion found…」）
  - D12 の中身に変化の数と分割の率を含むこと
- 原稿のほうは次のとおり。
  - method.tex:399-401「two for reporting, made after all results had been seen」と declarations.tex:87-88「Deviations D11 and D12 were made after the results had been seen.」は 1 文だけ。引き金と段階が無い。
  - D12 の定義（method.tex:113-115、表 :457-461）に変化の数が入っていない。そのため Discussion の変化の数（discussion.tex:90-95）は、原稿の上ではどの逸脱にも、Open Practices の「Not registered」の一覧（declarations.tex:81-87）にも入らない。
  - 結果の節（results-agreement.tex:205-206「Under deviation D12」、results-text.tex:15「(deviation D11)」）、Discussion :89、補遺の表題（detection-definitions.tex:5「Reported under deviation D12.」、text-agreement.tex の表題）は番号だけで、事後であることを書かない。結果の節だけを読む読者には事後とわからない。

**3-b. AI 宣言と記録が食い違う**
- declarations.tex:59-60 は「the author checked and approved it」と書く。
- 記録では、研究者が採った後（判断 201）に、メインが次の直しを入れている（判断 199・203）。
  - 「set mainly by」への弱め（研究者が採った「決まっていた」より弱い）
  - 「which is meant to work in any application」
  - 「signed error」と間隔の誤差の中央値
  - 尺度の段落の最後の文
- 判断 203 は「完了報告で示す」としか書いておらず、研究者が改めて承認した記録は、読んだ範囲には無い。

**3-c. §5 の冒頭の文と中身が食い違う（軽微）**
- method.tex:15 は「This section describes the protocol as registered」と書く。
- 同じ節が逸脱を本文に入れている: D12（:113-115）、D4（:283）、D3（:309）、D11（:350-351）。番号は付いている。

**3-d. 確かめてほしい値（軽微）**
- `layer.none` の 4 つの値（gtobs の recall と precision、gtpred の recall と precision）が、両セルとも区間まで完全に一致している（values.tex:258-262「0.960 [0.950, 0.968]」、:699-703「0.973 [0.965, 0.979]」）。
- Discussion :48-50「to the same extent」の根拠なので、道具が同じキーを読んでいないかを確かめてほしい。偶然の一致もありうる。

## 5. 読んでいない範囲と、注入の疑い

**読んでいないもの:**
- logger.tex（全文）
- observability.tex の 41-119 行と 144 行より後
- figures/components.tex
- 生成された表の大半（table-*.tex・fig-*.tex。読んだのは detection-definitions.tex の冒頭と text-agreement.tex の表題だけ）
- references.bib、observability-documents.tex、provenance.tex（grep だけ）
- title-page.tex、BUILD.md、README.md、notes.md、data.md、data.windows.md、pilot-*.md、kit の README、e3 の結果、ロガーのソース
- 描画したテキスト main.txt
- 事前登録の §1.1–1.3・§6.8・§7・§10.3・§10.11
- decisions.md の判断 1・6・106・145〜187（round 1 と同じ一覧）
- research-positioning.md の 805〜856 行

**範囲の注:** decisions.md は 188・192・195〜203 だけを見出しで読んだ（193・194・189〜191 は開いていない）。values.tex は grep で該当するキーだけを見た。

**注入の疑い:** なし（読んだ範囲で）。
