# verdict（manuscript round 4・対象 草稿 v4＋公開物 0.2.0 の DOI・commit ded7d3e7）

## 1. 判定: major revision（E が「直してから回す」・R1・R2・R3 minor・Codex major）

有効な査読 4 本（R1・R2・R3・E。接地はどれも 2 本以上〔E は一次＋1 本〕から逐語）。Codex major（既知の未決 22 件を添えた）。推移: round 1 major → round 2 major → round 3 major → round 4 major。査読者 3 人は 2 回続けて minor（R1・R3 は評価が上がった: R1 a3→a4・e4→e5、R3 b3→b4）。止め手は 2 回とも E で、今回の中心は「序論が約束する比べの相手の貢献を本文自身が否定する」（R2 の major と一致）と「単なる適用を超える要素が弱い」。round 3 の指摘は大半が解消（R1 9 件中 7、R2 9 件中 5＋一部 3、R3 8 件中 7、E 9 件中 4＋一部 3）。

## 2. 一致した指摘（分母 = 有効な査読 4 本。Codex は別枠）

| # | 指摘 | 一致 | 裏取り |
|---|---|---|---|
| A | 序論 72-73「the result shows which comparison partner exposes a weak run-up signal」と結論 9-10 が、考察 43-45・59（揃え方の効果は示せない）と食い違う。橋の向こう岸が無い | E（major）・R2（major）・R3（c の所見）（3/4）＋監査 2-3 | 真（intro 72-73・discussion 43-45・59 を開いて確かめた） |
| B | 要旨・序論の「simple quantities ... 0.04--0.08 higher than the two signals」で、主体（学習器か単一の量か）と相手（変化か水準か）が混ざる | R1・R2（2/4）＋監査 2-1 | 真（results 197-201: LR は変化を 0.078・0.081、水準を 0.042・0.046、GB は変化を 0.051・0.054 で水準は明確でない。単一の量は 0.446） |
| C | X17 の解釈文（results 205-206「Part of this difference comes from the definition of a stall」・discussion 35）が、事前の読み方「その間は値だけを書く」を越える。s − u > 30 s の停滞（4,554 − 3,426 − 1,057 = 71・JSON の 118 は行の数）を書いていない | R1・R2・R3（3/4）＋監査 3-6 | 真（conditions.md 24・reading_rule "between"。JSON の rows は対の行で、118 は行。停滞 71 は引き算） |
| D | 但し書きの繰り返し（偽同等率 4 回・漏れ 4 回・床 4 回・閾値の表 4 回・陽性対照 6 回・学習器 5 回など） | E（major・位置の一覧）・R2（minor）・R1（nit）（3/4） | 真 |
| E | Materials「three of which (the preregistration text and its English check)」が 2 項目に読める | R1・R2・R3（3/4・nit） | 真（discussion 75-76） |
| F | 陽性対照: 表が条件の水準の一部（×1.05・×1.2・r = 0.02・0.1）を黙って落とす／観測の向き（速く・訂正が少ない）には注入していない／水準（ewma_x）は r = 0.1 で 0.598 と帯を越えるのに変化は 0.530 | R2・R3（落とした行 2/4）・R1（向き 1/4）・R3（水準 1/4） | 真（explore_positive_control_v2.json: C_0.1 ewma_x 0.5985〔branch_form 3〕・d_ewma_x 0.5301・controls_fixed ewma_x 0.6070） |
| G | X16 の記述が片側（φ3・φ5 を天井の側で書くが u で φ5 の床 53.7%・φ3 の床 32.3%）。要旨は「floor」だけ。φ5 は u − 30 s の天井から u の床へ入れ替わる | R1・R3（2/4） | 真（results 189-190・JSON の x16） |
| H | 回し直しのバイト一致は著者の 1 環境（macOS arm64） | R1（nit）・R3（minor）（2/4） | 真（discussion 72-73 は環境を書かない） |

1 人だけ（裏取り）:
- R3（major）結論 4-5・考察 4-5 の主文に偽同等率の但し書きが無いのに、限界 24-25 が「the preregistration requires this qualification in the main sentence wherever it appears」と書く → 真（監査 3-1・1-4 と一致）。
- R2 考察 41-42「What the registration establishes ... including after removing stalls that contain events inside the pause」が [C-D] の感度を確立に含める → 真。
- R2 考察 19-20「a trigger that waits longer in the pause meets a higher base rate」が数値なし → 真。
- R2 学習器と信号の予測の相関（nit）→ 真（無い）。
- R3 推定器の門の初回（並列 7）の 9 件の不一致の原因が確かめられていない（estimator/README 77-80）→ 真（状況だけ）。
- R3 conditions-summary.md の round 3 の確かめの節だけ時刻が日付止まり → 真。
- E M2 「単なる適用を超える」要素が弱い（唯一の比較が 4.5 の 4 段目に埋もれる）→ 真（範囲の要件の判断は研究者）。E m1 抄録の "leak" が未定義（abstract 6）→ 真。E m2 本文の細部（Materials 約 330 語・設計の規則の列挙・照合の件数・換算の数値など）→ 真。E m3 推定器の陽性対照が主の結果の後 → 真。E m4 地位のラベル → 真。E n1 題 25 語・n2 確認の場の理由 → 真。

Codex だけ: 1 学習器は取り置きの中の書き手で 5 分割の交差検証であることが本文から読みにくい → 一部真（引いた design 34「nothing was fitted to the holdout」は信号についての文で読み違い。ただし design 80 は「folds by writer」とだけ書き、取り置きの中であることを言わない）／2 「the latest estimate row at or before $t - 30$~s」に最大の時間差の条件が無く、推定行の切れ目をまたぐと 30 秒の差が別の時間差になりうる → 確かめられない（本文で保証の条件が読めない。監査には取り置きの中間での計算が要る）／3 感度の「q = 0.995」は warmup_count 200 も変えている → 真（事前登録 159 は書くが補足の表 243 は書かない）／4 rerun-holdout.sh の失敗の診断が最後のバイト比較だけ → 真（道具の改善・minor）。

監査だけ: 1-1 抄録に橋の貢献が無い／1-2・3-4 抄録に「旧定義で帯の内側」と「取り置きでは 0.5 のわずかに下」が無い（序論 59-61 にはある）／1-3 X17 の読みが抄録・序論・結論に無い／2-2 design 70-71「In the holdout every interval ended at least 0.025 inside the edges of the band, so the decision does not hinge on the exact level.」が事後の断りなしに 0.025 を論拠に使う／2-4 考察 20「In that sense」が換算を受ける（P10 は閾値の表）／3-2 考察 12-13「nor a firing rule that uses the length of the pause itself」と結果 193-195（対照を 5・10 s 以上に）／3-3 事前登録 P10「writing coefficients as they are (not adapted to individuals or to programming)」と序論 47・補足 104「adjusted for code-like input」（補足は「introduced for alphanumeric input and later kept」と書くが Wording の段が挙げない）／3-5 results 157「0.493--0.499」は対照を固定した ×1.02 の Δx 0.492 を含めると 0.492–0.499。いずれも真（開いて確かめた）。

## 3. 直す順

- 研究者の判断が要る:
  - A と E M2（主の貢献と範囲の要件）: 序論・結論の「比べの相手が弱い信号を露わにする」を下げる（3/4）のは判断が要らない。そのうえで範囲の要件を何で満たすか。(a) 信号と標準の量・学習器を同じ対で比べた結果を、主の結果の直後の小節に「比較の分析（地位は探索）」として上げ、抄録と序論の貢献の段もそれで書く／(b) 手順を一般化できる方法として立て、別の推定器か別のデータで最小限の実演を付ける（計算が要る）／(c) 投稿先を考え直す。
  - Codex 2（t − 30 s の推定行の時間差）: 取り置きの中間で両端の実時刻差と同じ観測区間かを数える計算（条件を先にコミット）を回すか。
  - 次の round（Step 5）: 直した後に round 5 を回すか（推移は major 4 回・査読者 3 人は minor 2 回）。
- 文の直し（判断は要らない）: B 主体と相手を分ける／C X17 を値だけに・71 の停滞を書く（解釈は条件の外と断って考察に 1 回）／D 但し書きを主の文と限界の 1 か所に（他は節番号で参照）／R3 の主文の但し書き（結論・考察の主文に短い形と限界への参照）／E 括弧の書き方／F 補足に陽性対照の全水準 × 4 量 × 2 版の表・本文の表題に「selected rows」・向きの限定・水準と変化の応答の違いを 1 文／G 4 成分の床と天井の表・要旨を「floor or ceiling」／H 環境を 1 句／R2 確立の範囲・基準率の断定を下げる／E m1 抄録の leak を言い換え、旧定義と 0.5 の下を抄録に（監査 1-2）／E m2 細部を補足へ（Materials を縮める）／E m3 陽性対照の位置／E m4 ラベル／監査 2-2・3-2・3-3・3-5／Codex 1・3／公開物: R3 の門の初回の原因（README に「cause not established」）・要約の時刻・Codex 4（失敗の診断）。

## 4. 意図の監査役
- 4a: 1-1（抄録に橋が無い）・2-1・2-3・3-1・3-3 が重い。
- 4b. 編集者 E: 直してから回す（M1 貢献の後半が本文に否定される・M2 範囲の要件・M3 繰り返し。直しが「移す」より「足す」で +257 語）。→ 判定は major 以上。
- 4c. 本文の分量: 7,681 語（前回 7,424・+257）。測った版 ded7d3e7（前回は 7fc19bc6）。

## 5. 逸脱・注入
- 応答 5 本と Codex は secrets-filter を通した（すべて rc 0）。応答に絶対パスは無い。応答はメインが要約して round の dir に置いた（Codex はそのまま）。依頼文はファイルの絶対パスで渡し、エージェントが Read で読む形にした。注入の疑い: なし。
- 投稿規程の JEDM の 2 ページは curl で取り直して照合した。テンプレートの説明は 2026-11-06 の zip で照合（この round では取り直していない）。

## 6. 接地の引用の照合（査読者ごとに 1 件以上）
- 空白を詰めて逐語の一致を確かめた: R1 guo2020「relatively simple heuristics to define our writing states」／R2 pelanek2015「useful to analyze correlations of model predictions」・gardner2018「we use ROPE = 0.01」／R3 lakens2017「Confounds can underlie observed equivalent effects」・kapoor2023「The burden of proof for ensuring the」＋「correctness of these arguments is on the researcher making」（2 段組みの左の列で 472-473 行に分かれる）・「to justify that the test set is drawn from the distribution of」（457 行）／E mensh2017「Only the central idea of the paper should be touched upon multiple times」。捏造は見つからなかった。

## 7. 研究者に問うこと
- 主の貢献と範囲の要件（(a)・(b)・(c)）・Codex 2 の計算を回すか・次の round。

## 8. 対応（2026-11-07・研究者の採否は判断 39）
- A・E M2: 序論と結論の比べの相手の主張を下げ、学習器との同じ対での比べを主の結果の直後の小節 4.2 に「比較の分析（地位は探索）」として上げた。
- Codex 2: X18 を条件を先にコミットして数えた（a28eb877・eff23bdc）。外れた行は停滞 1.5%・対照 1.0%、除くと 0.491・0.487。本文と補足に書いた。
- 3 の「文の直し」は、E m3（陽性対照の位置）・E m4（ラベル）・R2 の予測の相関を除いて草稿 v5（0a98f0fd）で直した。本文 7,652 語（-29）・要旨 294 語。
- 次の round: 研究者の採否で round 5 を回す。
