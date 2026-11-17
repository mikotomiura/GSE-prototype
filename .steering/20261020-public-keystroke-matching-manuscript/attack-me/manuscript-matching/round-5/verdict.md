# verdict（stage: manuscript・原稿の全体・round 5・2026-11-17）

対象: commit b5493db2。査読者役 3 人・編集者 E・監査役（paper-reviewer・Opus）・Codex（直列・既知の未決 16 件を添えた）。判断 95 で「round 5 は 1 回だけ。major でも直しを 1 回入れて投稿へ（round 6 は回さない）」。

## 1. 編集者の判定: minor revision

- R1 minor・R2 minor・R3 minor・E「査読に回す」。Codex（別枠）major。有効な査読 4/4。偽陽性 0。
- 判定の推移: round 1〜4 major → round 5 minor。Skill の Step 5（manuscript で minor → 直して投稿へ）。
- ただし R1 の major 1 件（登録した λ = 4 の二次の解析を本計算が R7 で回していない・記録の無い逸脱）は一次で真と確かめた（preregistration.en.md:203 は形を限らず、:160 の A2 の形に R7 がある。scripts/evaluate.py の `if b != "R7":` が R7 を飛ばす。付録 D の "The registered secondary analysis did not vary λ under suppression" は登録の文と合わない）。値は分析 6 が同じ関数で計算済み（A2・N = 1,000: λ = 4 で R7(0.1) 75.1%・R7(0.25) 51.2%・R7(0.5) 0.20%、λ = 16 で 5.6・2.8・0.0）。研究者に扱いを問う。

## 2. 一致（分母 = 有効な査読 4）

| 指摘 | R1 | R2 | R3 | E | 監査 | Codex | 裏取り |
|---|---|---|---|---|---|---|---|
| A 「matching fell as the process measures were lost」「no form that no other form dominates lowered matching without losing」は前線の定義から出る／R7 は指標を失わず相関が下がるだけ | minor | — | minor | minor（m6） | — | major（1） | 真（R7 は 0/10/0） |
| B 序論の文が途切れている（were lost が無い） | — | — | — | minor（m1） | 3-C | — | 真（私の直しの誤り・b5493db2） |
| C §7.2 の C2 の段落の全員の 0.65% が λ = 4 の句の後で λ = 4 の値に読める・「a gain」の言い方・全員で R4(8) の N = 10 が変わる | minor（5） | — | minor（m3） | nit | 3-B | minor（5） | 真 |
| D 値の組と但し書きの繰り返し（図 1 の見出しと §7.3 末・§8.3 の探索 4 回など） | — | minor（4） | （d） | minor（m4） | 2-A | — | 真 |
| E §8.3 の「three choices」と見出し 5 つ | — | nit | nit | minor（m6） | — | — | 真 |
| F threat-model.tex:176-178 の未定義の "near chance" | nit | — | minor（m2） | — | — | — | 真 |
| G 抄録の密度（3 層・未定義の segment values が戻った） | minor（4） | minor（5） | （d） | minor（m3） | 1-B | — | 真 |

1 人だけ・すべて真:
- R1: 1 登録の λ = 4 を R7 で回していない（上・major）／3 R7(0.5) の 2.2% は書き手の 1.6% に集中（explore-tail・探索）／6 「not bounds either」の向き。
- R2: 1 探索の本文の列挙に R3・R4(1) の 98.5% が無い（explore-strongest.tex:2-3）／2 探索の下でも前線に残るのは R7(0.5) と R4(8) だけ／3 得点との関係のずれが 2 例だけ（utility-score.tex）／7 threat-model.tex:168 が未定義の R3-u・A3 を参照／8 discussion.tex:31 の KeyTAR の既定値の参照先。
- R3: M1 倫理の節に名指しした公開の側へ知らせたかが無い（理由「処理に頼る当事者は知るべき」と行動が噛み合わない・研究者の判断 91・94 で書かないと決めた事項）／m4 抄録の "remained with others" が本文の留保を落とす／m5 逸脱 4 件の中身が本文に無い／m6 KeyTAR の 1 人を除いた値で書き手ごとの値が分かる例外（除いても各セルの差は高々 0.1 ポイント・a4-full.tex）。
- E: m2 序論の 1 文に 3 つの地位が同居／m5 §6.4・Inputlog の 2 か所・SDC の分類・§3.5 の長い文／m7 1 頁目に書き手に何が知られるか／nit results.tex:49-51 の一般形。
- 監査: 2-B §7.2 の "largely reflected" が意図の「一部」より強い・R7(0.1) は低くない／3-A discussion の "segment values with w ≥ 4 computed no measure"（R4 はどの w でも計算しない）／1-A 結論で R7(0.5) が探索で動かないことが落ちる／2-C 抄録の named student に「そうした公開は知らない」が無い。
- Codex: 2 「no more than the total length alone gave」は A0 を候補に含む最大なので構造的に非負・区間は 1.1 ポイントまで含む → 「A0 が最も強い攻撃者だった」に／3 discussion.tex:50-52 "processing protects a text only while no later release contains that text" は過剰な一般化／4 R7 の抑制は 1 回の抽選に条件づけた区間（protocol.tex:91）／6 ENJA の読みと打鍵数の規則が本文で不足（attackers.tex:137）。

## 3. 裏取り

- 接地の引用: 各役 1 件以上を本文で確かめた（round 4 と同じ本文・同じ文献）。捏造なし。
- 原稿側: preregistration.en.md:160・203、config.json の lambda_sensitivity [4, 16]、scripts/evaluate.py:140、explore-lambda-scan-1000.tex の R7 の行、main-1000.tex の R7 の行（0/10/0・A0 (75)・0.0 [0.0, 1.1]）、introduction.tex:46-47、discussion.tex:50-52, 58, 69-70、protocol.tex:91、a4-full.tex（1 人を除いた差は高々 0.1）を開いて確かめた。

## 4. 直す順（案）

1. 登録の λ = 4 の R7（研究者に問う）。
2. 要約の文（A・B・Codex 2）: 「fell as … were lost」をやめ、前線の形と値だけで書く。R7(0.5) は「A0 が最も強い攻撃者だった」。序論の途切れを直す。
3. §7.2 の C2 の段落（C）: 全員の値と λ = 4 を段落の外へ、λ を明記、R4(8) の N = 10 の全員の変化を半文。
4. 繰り返し（D・E・F）: 図 1 の見出しを読み方に、§7.3 末を図の参照に、§8.3 の探索を 1 文に、three を消す、near chance を値に。
5. 小さな直し: R2 1・2・7・8、監査 2-B・3-A・1-A、Codex 3・4、R3 m4・m5、E m2・nit、R1 6。
6. 倫理の通知（R3 M1）・KeyTAR の例外（R3 m6）は研究者に問う。

## 4c. 本文の分量

本文 10,975 語・抄録 324 語（commit b5493db2）。前の round の版（bf0d2450）は 11,009 語・348 語。

## 7. 研究者の採否（2026-11-17・判断 96）

3 問とも推奨: R7 の λ は逸脱として記録し抄録にも添える／倫理は理由の文を直し通知は書かない／KeyTAR は差だけ書き例外を消す。ほかの直しは §4 の案どおり（判断 96 に一覧）。判断 95 により round 6 は回さず、/cross-review で直しを確かめて閉じる。
