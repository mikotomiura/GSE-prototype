# 編集者 E の応答（round 4・commit bf0d2450）

判定: 直してから回す。新しい計算は要らない（書き直しと付録への移動で直せる）。
読んだもの: 本文・必須の節・context-A・carryover-E・mensh。付録は読んでいない。references.bib は注入の語を Grep しただけ。

## 1. 接地
- B1 authors-2027.php "The first page must clearly state how the work is relevant to real-world privacy applications. The introduction should give some background and summarize the contributions of the paper at a level appropriate for a non-specialist reader."
- B2 cfp27.php "The core contribution must be relevant to real-world privacy applications." / "Papers that treat privacy as a superficial application domain … are therefore out of scope."
- B3 authors-2027.php "The paper should be complete and self-contained without appendices. PC members are not required to read the appendices during review."
- B4 Mensh Rule 1 "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each" / "Readers cannot give 1-sentence summary."
- B5 Mensh Rule 4・5 "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place" / "the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them."

## 2. 1 文（言えるが C2 で迷った）
伏せ字は同じ課題の作文を持つ者に 1,000 本から全ログの元の作文を当てさせ、より少なく出す加工では照合の下がり分が過程の指標を失う分になり、試した加工のどれも指標を計算できたまま照合を偶然近くまで下げなかった。迷った所: 抄録 13〜17 行が「4 倍以内は w ≥ 4 だけ」と言い、すぐ探索で「どれも 4 倍以内に残らない」と打ち消す。図 1 の注の頭（results.tex:128 "No form evaluated brought matching near chance while computing the process measures."）を C2 と採った。

## 3. 引き継ぎの判定
1 解消（abstract.tex:4-5・introduction.tex:38-42）／2 一部（§7.3 は前線の点。抄録・序論・考察・結論の要約は「within four times chance」のまま）／3 本文は解消、抄録は逆戻り（242→348）／4 未解消（探索の文で増えた）／5 概ね解消（推奨しないの明言は m4）／6 解消／7 解消／8 解消／9 解消／data.tex の点検の段は 6 行で保留のままでよい。

## 4. 指摘
- [major] M1 C2 の要約がプロトコルに無い閾値「4 倍以内」で立ち、探索がそれを打ち消す
  - 位置: abstract.tex:13-17 "only segment values coarsened to four or more brought the full-text attackers, with their main penalty, within four times chance … Exploratory attackers fixed after these results … and no form stayed within four times chance"。同じ枠: introduction.tex:48-50・discussion.tex:10-12・conclusion.tex:6-8・results.tex:153-155。protocol.tex:13 "No pass or fail criterion is set"。他の場当たりの閾値: results.tex:88-90 "within 14 points" "below 40\%"・discussion.tex:67-68 "below 40\%"。
  - 理由: 「4 倍」に定義が無く、事後の切れ目が頭の主張を決めて見える。登録（R4(4)・R4(8) は 4 倍以内）と探索（どれも残らない）を同じ文で並べ主張が 1 つに定まらない。R4(4) は登録の二次 λ = 4 で 4.5%（results.tex:69-71, 91）。"with their main penalty" は λ を知らない読者に通じない。B4。
  - 解消: C2 の要約を図 1 の前線で 1 文に（指標を計算できる形はどれも照合が偶然から遠く、偶然に近い形は指標を計算しない）。粗い形の低い値が攻撃者の弱さに依ることを探索と明示して 1 文。「4 倍」「40%」「14 点」を要約から外すか §5 で定義。
  - 自信: 高
- [major] M2 試していない実際の公開について断定
  - 位置: discussion.tex:12 "In that release, hiding the characters did not hide the text, because the lengths and the editing keys remained."・conclusion.tex:8-9 "In that release, hiding the characters did not keep the logs apart from texts held elsewhere."
  - 理由: 評価は KLiCKe に R1 の伏せ字を当てたもの。競技のデータは使っていない（ethics.tex:27）。抄録・序論・結果は "Against the masking" と限定しているのにここだけ食い違う。
  - 解消: "The masking used in that release, applied to a public corpus of the same kind, …" の形に限る。
  - 自信: 高
- [major] M3 抄録が 348 語に伸び、定義の無い語と登録・二次・探索の 3 段の地位が混ざった
  - 位置: abstract.tex:13-17 "segment values coarsened to four or more" "with their main penalty" "Exploratory attackers fixed after these results, with a lighter penalty or aligning chunks of a log anywhere in a text"
  - 理由: segment values・penalty が抄録で未定義（B5）。後半 5 行が C2 を言い・留保し・打ち消すことに使われる。
  - 解消: 250 語前後へ。C1 1 文・C2 の前線 1 文・探索の留保 1 文（数値は 1 つまで）・ENJA 1 文・但し書き 1 文。ρ = 0.81 などは §7 に任せる。
  - 自信: 高
- [major] M4 同じ但し書きの繰り返し（前 round の 4 が未解消）
  - attackers tried / not bounds: abstract.tex:19・threat-model.tex:196-197・protocol.tex:59・results.tex:87・discussion.tex:8, 22-23, 35, 36-37・conclusion.tex:9-10
  - 攻撃者の差も含む: threat-model.tex:176-179・protocol.tex:65-68・results.tex:91-92
  - 1 窓につき 1 おとり: threat-model.tex:170-171・attackers.tex:131-134・results.tex:166-168・discussion.tex:78
  - 探索・結果の後に決めた: protocol.tex:21, 160・results.tex:75・abstract.tex:15・introduction.tex:49-50・discussion.tex:11-12, 36-37, 68-69, 71・conclusion.tex:8
  - KeyTAR は脅威モデルの外: threat-model.tex:140-141・data.tex:42-43・attackers.tex:62-63, 119-122・results.tex:173・discussion.tex:35
  - 競技のデータは KLiCKe から: introduction.tex:19-21・threat-model.tex:99-110, 148-150・discussion.tex:53-55
  - 理由: B5。余白 0.3 頁なのに同じ限定に合計 1 頁近く。
  - 解消: 各項を §3.5 と §5 の 1 か所に置き、他は参照。§8.1 は新しく言えることだけ。KeyTAR は §4 で 1 回（data.tex:41-43 を削る）。
  - 自信: 高
- [minor] m1 §7.2 が論点を行き来する
  - 位置: results.tex:67-71（λ = 4 の二次・窓 5〜50）、75-79（探索 2 つ）
  - 解消: 窓の値は §7.4 へ。λ = 4 と探索は §7.2 の最後に 1 段落か §7.6 へ。
  - 自信: 中
- [minor] m2 本文に置かなくてよい方法の細部
  - 位置: attackers.tex:22-27（Control/Meta の扱い）・attackers.tex:97-101（A1′ の再生の規則）・data.tex:91-100（ドラッグ・押し続けの長さ）・protocol.tex:83-88（産出速度の分母）・protocol.tex:102-106（Inputlog の照合不能）・protocol.tex:137-141（開いた世界の AUC の集め方）・threat-model.tex:99-110（2 つの公開の対応づけ）
  - 解消: 付録へ移し本文は 1 文と参照。threat-model.tex:99-110 は 2 文にまとめ倫理の節を参照。M1・M3 の余地もここから出る。
  - 自信: 中
- [minor] m3 公開する側の持ち帰りが「推奨しない」で終わる
  - 位置: discussion.tex:61 "The results are material for three choices, and none recommends a form."。考察は Windows の段で終わる（77-79）。
  - 解消: §8 冒頭か結論に、限定つきで行動につながる 1 文（例: 語の長さを残す伏せ字は同じ課題の作文を持つ者に対し本文を隠さない。指標を残す形を選ぶなら照合の残り分を明示し利用規約と組み合わせる）。
  - 自信: 中
- [minor] m4 序論が問い 4（ENJA）の答えを示さない
  - 位置: introduction.tex:24-27 で 4 つの問い、44-53 の要約は C1〜C3 だけ。
  - 解消: 序論の最後に ENJA の結果を 1 文か、問いと貢献の対応を明示。
  - 自信: 中
- [nit] related.tex:46-47 の重複 "In the searches described in the open science section, we found no such evaluation. The searches behind this statement are described in the open science section." → 後ろを削る。自信 高。
- [nit] abstract.tex:14-15 "computing no measure" の掛かりが曖昧 → "which compute no process measure"。自信 高。

## 5. 判定: 直してから回す
C1 は明快で 1 頁目にプライバシーもあり範囲に合う。C2 の要約が定義の無い「4 倍」に依り探索がそれを打ち消し、抄録も伸びた（M1・M3）。試していない実際の公開について断定（M2）。どれも書き直しと移動で直せる。

## 6. 読めなかった範囲・注入の疑い
付録・事前登録は読んでいない。ai-use.tex:9 の \S\ref{sec:data:checks} の定義先は本文の data.tex に見当たらなかった（未定義の参照は 0 なので付録などにあるはず）。注入の疑い: なし。
