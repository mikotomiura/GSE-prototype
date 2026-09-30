# 設計 —— サーヴェイ B 群: S-11 語の用法・S-09 理論の節

★ 各サーヴェイの手順（入力・取得・ふるい・抜き出し・書き分け）は、**抄録の取得を 1 本も回す前に**本書へ固定する
（A 群 `../20260929-ai-fatigue-surveys/design.md` と同じ作法）。固定した節は書き換えない。変えるときは `decisions.md` に「逸脱」として理由つきで書く。

## 0. 共通の方針（2026-09-30 18:05・抄録の取得の前に固定）

### 0.1 A 群から引き継ぐもの（変えない）

- 3 つのファイルへの書き分け・`-ai-judgments.md` の冒頭の注意・完了報告には件数だけ: A 群 design.md §0.2。
- 取得と保存（メールアドレスを送らない・1 秒に 1 回程度・429 は「使えなかった」と記録・抄録と本文は repo の外・逐語は 1 引用 40 語〈日本語 80 字〉以内）: 同 §0.4。
- 本文の入手（オープンアクセスだけ。有料は `researcher-requests` 相当の節に書く）: 同 §0.5。
- サブエージェント（抽出だけ・model: sonnet を明示・同時 3 本まで・戻った主張はメインが一次で確かめる）: 同 §0.6。
- 共通の関数: `../20260929-ai-fatigue-surveys/evidence/common.py`（空の抄録で上書きしない `merge_abstract`・repo の外の確認・対の書き出し `write_pair`・URL の柵 `guarded_opener`）を import して使う。★ 抄録の置き場は本セッションの scratchpad（git の外）にする（`../20260930-ai-fatigue-judge-file/evidence/README.md` の流用の注意 (1)）。
- 検査: 前タスクの検査器 `check_survey_files.py` の `run()` を本タスクのディレクトリに当てる（`scripts/check_surveys_here.py`。語の一覧を複製しない）。

### 0.2 入力（259 件）

- `../20260930-ai-fatigue-judge-file/archive/judge/AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx`（SHA-256 `6984472edeef3794a9ed075076568aaca8373c4fb675afba608cdba280e6c883`・Downloads の写しと同じ）の『判定シート』34 行（DB・`ID`・`論文タイトル`・`DOI`）と『追加候補』225 行（`候補番号`・`題名（書誌の記録）`・`DOI`）。★ 読むだけ（書き換えない）。取得の前に SHA-256 を確かめ、違えば止まる。
- ★ DOI の無い 4 件（AF017・S04-30・S12-23・S12-24）: 題名で Europe PMC を 1 回ずつ引き（S12-24 は Europe PMC の `PPR268625`）、題名が一致したときだけ抄録を使う。一致しなければ「題名だけ」と記録する。
- ★ 同じ研究の記録（前刷りと雑誌の版・AF004 と AF034 の訂正通知）も記録ごとに数える（前タスクの判断 13）。

### 0.3 抄録の取得（S-11・S-09 で共通・`evidence/fetch_abstracts.py`）

| 順 | 情報源 | 経路 | 取る欄 |
|---|---|---|---|
| 1 | Europe PMC | `search?query=DOI:"<doi>"&resultType=core&format=json` | `abstractText` |
| 2 | Semantic Scholar | `graph/v1/paper/DOI:<doi>?fields=title,abstract` | `abstract` |
| 3 | OpenAlex | `works/doi:<doi>`（匿名） | `abstract_inverted_index` を語順に戻す |
| 4 | Crossref | `works/<doi>` | `abstract`（JATS のタグを名前を限って除く・A 群の判断 11） |

- 4 つすべてに問い合わせ、`merge_abstract` で**最も長い抄録**を残す。取れた情報源の名前を書誌の JSON に残す。
- 許す URL の接頭辞は上の 4 つの API の根だけ（`guarded_opener`）。User-Agent に連絡先・GSE の名を入れない。
- 書誌の JSON（repo・`evidence/S-xx/`）: 鍵・DOI・題名・年・どの情報源で抄録が取れたか・抄録の文字数・`run_id`。★ 抄録の本文は持たない。
- 抄録の JSON（scratchpad）: 鍵ごとの抄録。`write_pair` で書誌と対にする（既にあれば上書きしない）。

## 1. S-11 語の用法（2026-09-30 18:05・抄録の取得の前に固定）

### 1.1 問い

DB 34 件と追加候補 225 件で、(a) AI に向けた疲労を一つの名で呼ぶ語（「AI 疲労」とその変種）は、どの語形で、どの記録が使っているか。(b) 語を使う記録は、語にどのような意味を与えているか（定義・言い換え・構成要素）。(c) 語を使わず、一般の構成概念（燃え尽き・情動的消耗・認知的疲労・テクノストレス 等）で書く記録はどれだけあるか。

### 1.2 語形の機械のふるい（★ 判定ではない。題名＋抄録に当てる。大文字小文字を区別しない）

AI の語 `AIW`:

```
(?:gen(?:erative)?[\s-]*AI|GenAI|(?<![A-Za-z])AI(?![A-Za-z])|artificial[\s-]+intelligence|ChatGPT|(?<![A-Za-z])GPT(?![A-Za-z])|
   (?<![A-Za-z])LLMs?(?![A-Za-z])|large[\s-]+language[\s-]+models?|chat[\s-]?bots?|conversational[\s-]+agents?)
```

| 記号 | 何を拾うか | 正規表現（`AIW` は上） |
|---|---|---|
| N1 | AI の語 ＋ 疲労の名（間に修飾語 1 つまで） | `AIW(?:[\s-]+(?:induced|related|driven|based|use|usage|interaction|assisted|tools?|technology))?[\s-]+(?:fatigue|burn-?out|exhaustion|weariness|tiredness)` |
| N2 | 疲労の名 ＋ 前置詞 ＋ AI の語 | `(?:fatigue|burn-?out|exhaustion|weariness|tiredness)[\s-]+(?:from|with|of|toward|towards|to|caused[\s-]+by|due[\s-]+to|related[\s-]+to|induced[\s-]+by|associated[\s-]+with)[\s-]+(?:(?:the|using|interacting[\s-]+with)[\s-]+)?(?:(?:use|usage|overuse)[\s-]+of[\s-]+)?AIW` |
| N3 | プロンプト疲れ | `prompt(?:ing)?[\s-]+fatigue` |
| N4 | 日本語 | `(?:AI|ＡＩ|生成\s*AI|人工知能|ChatGPT|LLM|チャットボット)\s*(?:による|への|の)?\s*(?:疲れ|疲労|燃え尽き|バーンアウト|疲弊)|プロンプト疲れ` |
| N5 | 近接の語（★ 数えるだけ。意味の抜き出しはしない） | `AIW(?:[\s-]+(?:induced|related))?[\s-]+(?:techno-?stress|stressors?|stress|anxiety|overload)` |

- **語を使う記録** ＝ N1〜N4 のどれかが題名か抄録に当たる記録。N5 だけの記録は「語を使う記録」に入れない。
- 一般の構成概念の語 G（★ 数えるだけ・語を使う記録にも当てる）: `burn-?out`（燃え尽き）・`emotional[\s-]+exhaustion`（情動的消耗）・`exhaust(?:ion|ed)`（消耗）・`(?:mental|cognitive)[\s-]+fatigue`（精神的・認知的疲労）・`decision[\s-]+fatigue`（決定疲れ）・`fatigued?`（疲労）・`techno-?stress`（テクノストレス）・`cognitive[\s-]+(?:load|overload)`（認知負荷）・`information[\s-]+overload`（情報過多）・`(?<![A-Za-z])strain(?![A-Za-z])`（負担・strain）・`workload|NASA[\s-]*TLX`（作業負荷）・`tired(?:ness)?`（疲れ）。
- ★ 陽性・陰性の例文で正規表現を検査する（`evidence/test_screen.py`）。陽性: `AI fatigue`・`AI-induced fatigue`・`generative AI fatigue`・`GenAI fatigue`・`ChatGPT fatigue`・`LLM burnout`・`fatigue from using ChatGPT`・`burnout caused by generative AI`・`prompt fatigue`・`AI 疲れ`・`生成AIによる疲労`。陰性: `said fatigue`（ai が語の中）・`fatigue assessment`・`Thai fatigue`・`AI adoption and burnout`（間に 2 語以上）・`fatigue of workers`・`promptly fatigued`。

### 1.3 意味を与える文の抜き出し（語を使う記録のすべて）

- メイン（Opus）が、語を使う記録の抄録を 1 件ずつ全文で読み、**語に意味を与える最初の文**を探す。意味を与える文とは、(a) 定義（defined as・refers to・we define・conceptualized as・is a state 等）、(b) 同格の言い換え（「AI fatigue, a state of …」）、(c) 構成要素・次元の列挙、のどれか。
- 機械の補助: 語を含む文のうち、上の手がかりの語を含む文に印をつけて渡す（印は目安で、決めるのはメイン）。
- 記録するもの（事実のファイル）: 鍵・当たった語形（N1〜N4 の記号と文字列）・意味を与える文の逐語（40 語以内。長ければ語を含む節だけ）と (a)(b)(c) の別・出どころ（題名／抄録／本文）。見つからなければ「抄録に意味を与える文なし（語が出るだけ）」。
- **本文**: 抄録に意味を与える文が無く、判定者用ファイルの「本文の入手（OpenAlex）」が「無料の版あり」の記録は、無料の本文（出版社の HTML・PMC・機関リポジトリ・前刷り）で、語に意味を与える最初の文を探す。本文の抜き出しはサブエージェント（Sonnet）に渡してよく、戻った逐語はメインが本文で 1 件ずつ確かめる。無料の本文が無い・取れないものは「本文未読（入手不可）」と書く。
- ★ 語が別の意味（系の性能・材料・人の疲労を検知する対象 等）で使われていても、事実のファイルには文をそのまま載せる（意味の区分は判定案のファイルで行う）。

### 1.4 サーヴェイで記録した用法の例・プロンプト疲れの概念分析

- A 群・前タスクの事実のファイルに記録した用法の例（`survey-S-08.md` §6 の Synthetonia・GenAI Fatigue の制御理論、`survey-S-12.md` の「精査疲れ」「それっぽい嘘に疲弊」「評価疲れ」）は、出どころの節を示して表に写す。逐語を載せるものは一次（抄録・記録のページ）で読み直す。
- プロンプト疲れの概念分析（検索漏れ候補 No.128・129・Zenodo `10.5281/zenodo.21384564`・`21384565`）: Zenodo の記録の API（`https://zenodo.org/api/records/<id>`）で関連の識別子（本体の論文）を見る。無ければ題名の語（`Concept Analysis of Prompt Fatigue`）で Crossref・Semantic Scholar を 1 回ずつ引く。本体が見つかれば書誌・抄録を読み、259 件に無ければ「DB と候補に無い記録」として事実のファイルに書く（候補には足さない・requirement のスコープ外）。

### 1.5 用法の区分（判定案のファイル・メインが行う）

- 区分（issue の 4 つ ＋ そのほか。1 記録に複数可）: **U1** 利用の疲労（AI を使う・対話する・出力を確かめることに伴う疲労）／**U2** 話題・導入・言説への疲れ（AI の宣伝・急速な変化・導入の繰り返しに疲れる）／**U3** AI による仕事の変化・増加で燃え尽きる（職務の要求・雇用の不安）／**U4** プロンプト疲れ（プロンプトの作り直し・対話の繰り返し）／**U5** そのほか（系の性能の劣化の名・人の疲労を検知・予測する AI の対象の名 等）。
- 区分の根拠は、1.3 で抜き出した文（無ければ抄録の該当の箇所）に限る。意味を与える文が無い記録は「区分できない」に数える（推測で区分しない）。
- 出すもの: 区分ごとの定義の表（区分・件数・代表の定義文と出どころ）・語形 × 区分の表・サーベイの定義文の案（2〜3 案と、それぞれが含む区分・外す区分）。★ 定義文は研究者が決める。

### 1.6 出すもの

- `survey-S-11.md`（事実）: 取得の記録（情報源ごとに抄録が取れた件数・取れなかった cid）／語形の件数表（N1〜N5）／語を使う記録の一覧（1.3 の欄）／一般の構成概念の語の件数表（語を使う記録とそれ以外に分けて）／用法の例（1.4）／プロンプト疲れの概念分析の書誌と抄録に書いてあること。
- `survey-S-11-ai-judgments.md`: 1.5 の区分・表・定義文の案。
- `survey-S-11-gse.md`: 生成的返権論の負担の区別（interaction burden・verification burden）との関係（検討するまで）。
- `evidence/S-11/`: ふるいの結果（鍵・当たった語形の文字列・G の区分・抄録の有無。抄録の文は持たない）。

## 2. S-09 理論の節（2026-09-30 18:05・抄録の取得の前に固定）

### 2.1 問い

(a) 疲労が生じる仕組みについて、一般の理論（機会費用・補償的制御・能動／受動的疲労・自我消耗とその再現性）は何を言うか。(b) 259 件の記録は、抄録でどの理論的枠組みに依拠しているか。(c) 件数の多い枠組みの原著は何を言うか。

### 2.2 issue の 4 本の原典（固定の一覧・DOI で抄録を取る。無料の本文があれば本文も読む）

| 柱 | 文献 | DOI |
|---|---|---|
| 機会費用 | Kurzban ほか 2013（*Behav Brain Sci*） | 10.1017/S0140525X12003196 |
| 機会費用 | Agrawal ほか 2022（*Psychol Rev*） | 10.1037/rev0000309 |
| 補償的制御 | Hockey 1997（*Biol Psychol*） | 10.1016/S0301-0511(96)05223-4 |
| 能動／受動的疲労 | Desmond & Hancock 2000（書籍の章） | 10.1201/b12791-3.1 |
| 能動／受動的疲労 | Saxby ほか 2013（*J Exp Psychol Appl*） | 10.1037/a0034386 |
| 能動／受動的疲労 | Matthews ほか 2019（*Accid Anal Prev*） | 10.1016/j.aap.2018.04.004 |
| 自我消耗（原典） | Baumeister ほか 1998（*J Pers Soc Psychol*） | 10.1037/0022-3514.74.5.1252 |
| 自我消耗（追試・メタ分析） | Hagger ほか 2016（*Perspect Psychol Sci*） | 10.1177/1745691616652873 |
| 同 | Carter ほか 2015（*J Exp Psychol Gen*） | 10.1037/xge0000083 |
| 同 | Friese ほか 2019（*Pers Soc Psychol Rev*） | 10.1177/1088868318762183 |
| 同 | Vohs ほか 2021（*Psychol Sci*） | 10.1177/0956797621989733 |
| 同 | Dang ほか 2021（*Soc Psychol Personal Sci*） | 10.1177/1948550619887702 |
| 自我消耗（グルコース説） | Vadillo ほか 2016（*Psychol Sci*） | 10.1177/0956797616654911 |
| 同 | Finley ほか 2019（*Soc Psychol*） | 10.1027/1864-9335/a000376 |
| 関与の低下と可逆性 | Hopstaken ほか 2015（*Psychophysiology*） | 10.1111/psyp.12339 |
| 同 | Lin ほか 2020（*Psychol Sci*） | 10.1177/0956797620904990 |

- ★ 書誌・要点の出どころは各文献の一次（抄録・本文）だけ。ほかの文書の要約を根拠にしない。
- 能動／受動的疲労の 3 件は A 群の `survey-S-05.md` §2 に要点がある。取り直した抄録で確かめてから写す。

### 2.3 枠組みの機械のふるい（★ 判定ではない。259 件の題名＋抄録に当てる。大文字小文字を区別しない）

| 記号 | 枠組み | 正規表現 |
|---|---|---|
| F-JDR | 仕事の要求－資源モデル | `job[\s-]+demands?[\s-]*(?:and[\s-]*|[-–]\s*)?resources?|(?<![A-Za-z])JD-?R(?![A-Za-z])` |
| F-COR | 資源保存理論 | `conservation[\s-]+of[\s-]+resources?|(?<![A-Za-z])COR[\s-]+(?:theory|model)` |
| F-TS | テクノストレス | `techno-?stress|techno-?stressors?|techno-?(?:overload|invasion|complexity|insecurity|uncertainty)` |
| F-CLT | 認知負荷理論 | `cognitive[\s-]+load[\s-]+theory|(?<![A-Za-z])CLT(?![A-Za-z])` |
| F-SSO | ストレッサー－ストレイン－結果 | `stressor[\s-]*[-–]?[\s-]*strain[\s-]*[-–]?[\s-]*outcomes?|(?<![A-Za-z])SSO(?![A-Za-z])` |
| F-TMS | ストレスの交流モデル・認知的評価 | `transactional[\s-]+(?:model|theory)|Lazarus|cognitive[\s-]+appraisal|challenge[\s-]*[-–]?[\s-]*hindrance` |
| F-SDT | 自己決定理論 | `self-determination[\s-]+theory|(?<![A-Za-z])SDT(?![A-Za-z])` |
| F-EGO | 自我消耗・強度モデル | `ego[\s-]*depletion|strength[\s-]+model|self-control[\s-]+resources?|limited[\s-]+resources?` |
| F-SOR | 刺激－生体－反応 | `stimulus[\s-]*[-–]?[\s-]*organism[\s-]*[-–]?[\s-]*response|(?<![A-Za-z])S-?O-?R(?![A-Za-z])` |
| F-ER | 努力－回復・努力－報酬の不均衡 | `effort[\s-]*[-–]?[\s-]*recovery|effort[\s-]*[-–]?[\s-]*reward[\s-]+imbalance` |
| F-PEF | 個人－環境の適合 | `person[\s-]*[-–]?[\s-]*(?:environment|job|technology)[\s-]+fit|(?<![A-Za-z])P-?E[\s-]+fit` |
| F-OC | 機会費用・動機づけの制御・補償的制御 | `opportunity[\s-]+costs?|motivational[\s-]+control|compensatory[\s-]+control` |
| F-AP | 能動／受動的疲労・覚醒の低下 | `passive[\s-]+fatigue|active[\s-]+fatigue|underload|vigilance[\s-]+decrement` |
| F-AUT | 自動化への慢心・自動化バイアス | `automation[\s-]+(?:bias|complacency)|complacency` |
| F-ACC | 技術受容のモデル（★ 疲労の理論ではないが、数える） | `technology[\s-]+acceptance[\s-]+model|(?<![A-Za-z])TAM(?![A-Za-z])|UTAUT|uses[\s-]+and[\s-]+gratifications?` |
| F-IO | 情報過多 | `information[\s-]+overload` |

- 陽性・陰性の例文で検査する（`evidence/test_screen.py`）。陰性の例: `COR`（語だけ）・`TAMPA`・`self-organizing response`（S-O-R の語でない）・`clt`（語の中）・`limited resource`を含まない`resourceful`。
- ⚠️ 抄録に枠組みの名が無くても本文で依拠している研究はある。件数は「抄録で名を挙げた記録の数」で、依拠している記録の数ではない（事実のファイルの限界に書く）。

### 2.4 件数の多い枠組みの原著（固定の対応表・2.3 で 5 件以上の枠組みだけ読む）

| 枠組み | 原著 | DOI |
|---|---|---|
| F-JDR | Demerouti ほか 2001（*J Appl Psychol*）・Bakker & Demerouti 2007（*J Manag Psychol*） | 10.1037/0021-9010.86.3.499・10.1108/02683940710733115 |
| F-COR | Hobfoll 1989（*Am Psychol*） | 10.1037/0003-066X.44.3.513 |
| F-TS | Tarafdar ほか 2007（*J Manag Inf Syst*）・Ragu-Nathan ほか 2008（*Inf Syst Res*・DB の AF027） | 10.2753/MIS0742-1222240109・10.1287/isre.1070.0165 |
| F-CLT | Sweller 1988（*Cogn Sci*） | 10.1207/s15516709cog1202_4 |
| F-SSO | Koeske & Koeske 1993（*J Soc Serv Res*） | 10.1300/J079v17n03_06 |
| F-TMS | Lazarus & Folkman 1984（書籍・DOI なし）・Cavanaugh ほか 2000（*J Appl Psychol*・挑戦／妨害） | —・10.1037/0021-9010.85.1.65 |
| F-SDT | Ryan & Deci 2000（*Am Psychol*） | 10.1037/0003-066X.55.1.68 |
| F-EGO | 2.2 の自我消耗の一覧 | — |
| F-SOR | Mehrabian & Russell 1974（書籍・DOI なし） | — |
| F-ER | Siegrist 1996（*J Occup Health Psychol*） | 10.1037/1076-8998.1.1.27 |
| F-PEF | Edwards 1991（書籍の章・*Int Rev Ind Organ Psychol*） | — |
| F-OC・F-AP・F-AUT | 2.2 の一覧・A 群の `survey-S-05.md` | — |
| F-ACC・F-IO | 読まない（疲労の仕組みの理論でない。件数だけ） | — |

- 書籍・DOI の無い原著は書誌だけを載せ、「本文未読（書籍）」と書く（有料の本文は使わない）。
- ★ 5 件以上で対応表に原著が無い枠組みが出たら、`decisions.md` に逸脱として原著を足す。

### 2.5 出すもの

- `survey-S-09.md`（事実）: 取得の記録／2.2 の各文献の要点（抄録・本文に書いてあること・逐語 40 語以内・読んだ範囲）／枠組みの件数表（記録の鍵の一覧つき）／2.4 の原著の要点／限界（抄録に名が出た数であること）。
- `survey-S-09-ai-judgments.md`: 理論の節の草稿（1〜2 頁・出典は DOI で示す）／DB の『尺度・理論』に足す理論の文献の提案（DB は書き換えない）／枠組みの使われ方の見立て（疲労の仕組みの理論か、ストレスの一般の枠組みか、受容のモデルか）。
- `survey-S-09-gse.md`: GSE の既存の精読カード・中央書誌との対応（どの文献が既にあるか・新しく引く候補）と、関与の再開・生成的返権論との関係（検討するまで）。
- `evidence/S-09/`: 2.2・2.4 の書誌の JSON（抄録の文は持たない）・枠組みのふるいの結果。

## 3. 進め方

1. `evidence/test_screen.py`（正規表現の陽性・陰性）を先に書いて緑にする（取得の前）。
2. `fetch_abstracts.py` で 259 件 ＋ 2.2・2.4 の原典の抄録を取る（書誌は repo・抄録は scratchpad）。
3. ふるい（S-11 の語形・G、S-09 の枠組み）を回し、件数と一覧を出す。
4. S-11: 語を使う記録の抄録を読み、意味を与える文を抜き出す → 本文の要るものを読む → 事実のファイル → 判定案のファイル → GSE のファイル。
5. S-09: 原典・原著を読む → 事実のファイル → 判定案のファイル（理論の節の草稿） → GSE のファイル。
6. 検査（`check_surveys_here.py`・`test_screen.py`）→ レビュー（code-reviewer・security-checker 並列 → `/cross-review` 2 巡）→ 出荷。
