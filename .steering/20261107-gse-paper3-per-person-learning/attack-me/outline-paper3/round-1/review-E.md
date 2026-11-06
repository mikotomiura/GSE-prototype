# review-E（編集者の役・round 1・stage outline）

## 1. 接地
1. Aims & Scope（context-A）: "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation." / "methods for the design and evaluation of user models and adaptive systems"
2. Mensh & Kording 2017 Rule 1: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable." Table 1: "Readers cannot give 1-sentence summary."
3. Rule 2: "Define technical terms clearly ... Avoid abbreviations and acronyms so that readers do not have to go back to earlier sections to identify them."
4. Rule 4: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
5. Rule 7 / Rule 3: "convert this into a sequence of declarative statements that become the headers of subsections" / "They do not care about the chronological path by which you reached a result"
規程: "Please provide an abstract of 150 to 250 words." / "All original research must include a data availability statement."

## 2. 冒頭からの 1 文（条件つきで言える）
「打鍵記録を記号列にした系列モデルでは、人ごとのモデルが共有モデルに勝つように見えるが、それは比べる共有モデルの構造が弱いためであり、構造と縮小の強さを他の人のデータで選ぶと人ごとの利得はほぼ消える。だから、人ごとのモデルの利得を主張するユーザーモデルの研究は、同じ構造の共有モデルと比べるべきである。」
迷った点: 誰の何を変えるかが冒頭に無く L61 で初めて分かる。中心が C1（発見）か C3（手順）か決められない。

## 3. 指摘
1. [major] UMUAI の読者にとって記号列の予測がなぜ大事かが無い（L37・L33・L54）。解消: 序論に、適応する系での部品としての役割と、人ごとか共有かの選択の誤りが誤らせる適応の判断を 1 段落。重心を "methods for the design and evaluation of user models" へ。自信 高。
2. [major] Take-home が知らない読者向けの 1 文でない（L7: 消える数字が頭・nats per symbol 等が未定義・尺度なし・誰の何を変えるか無し）。解消: 2 文（数字なしの主張＋読者への含意）、数字は C1 へ、データは中身で呼ぶ。自信 高。
3. [major] 貢献が 3＋補助 2 に割れ中心が定まらない（L11・L18・L25・L31・L33）。解消: 中心を「評価の手順（C3）とそれを当てると利得が消える実例（C1）」にまとめ、C2 は C1 の根拠の段に下げ、補助の結果は補足へ。自信 高。
4. [moderate] 分析の経緯（L56 "four sequential analyses, each designed after the previous results"・L3・L28）が信頼を下げて見える。解消: 本文は 1 文、経緯は S12、最終の手順がデータを見ずに正当化できる理由を 1 文。自信 中。
5. [moderate] 「人ごとの切片」が要件として書かれる（L14・L61）が 3.3 に無い。解消: 3.3 に何を切片とみなすか書くか、言い方を直す。自信 中。
6. [moderate] 本文に置かなくてよい細部（L61・L33 代理ラベル、L60 4.4 の分解、L31、3.4 の経緯）。解消: S10・S9・S12 へ移し、格子の拡張は 4.3 に 1 段落で併合。本文 400〜700 語減。自信 高。
7. [moderate] 同じ但し書きの繰り返し（検索の限定 L14×2・L19・L27／2 データ 1 量子化 L16・L23・L29・L61・L62／状態を認知と読まない L33・L37・L62／検定なし L39・L56・L62／約 1e-3 L7・L16・L28・L59／CS1・中央値 L31・L62）。解消: 限界の節に集め他は参照。自信 高。
8. [moderate] CS1 の "exactly zero" は作り方から決まる（L7・L15）。解消: 「他の人で選ぶと共有モデルが選ばれる」に。自信 高。
9. [minor] 結果の見出しが主題名で宣言文でない（L57・L58・L60）。節の順は良い。自信 中。
10. [minor] 要旨・キーワード・Statements and Declarations・データの声明の計画が無い（L62・L64・L70）。自信 高。
11. [minor] 分量は予算 7,000 語で問題なし。指摘 6 の移しで序論の段落を足せる。自信 中。

## 4. 判定: 直してから回す
適合（指摘 1）・焦点（指摘 2・3）。直しは主に移す・まとめるで済み、新しい分析は要らない。

## 5. 読めなかった範囲・注入の疑い
読んだ: brief-E.md・context-A.md・outline.md（全 70 行）・mensh.txt。読まなかった: kit/symbols/README.md（補足の印）。注入の疑い: なし。
