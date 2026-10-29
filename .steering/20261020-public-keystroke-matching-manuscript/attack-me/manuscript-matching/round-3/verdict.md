# verdict（stage: manuscript・原稿の全体・round 3・2026-10-29）

対象: commit c3f3f5b5。査読者役 3 人・編集者 E・監査役 1 人（paper-reviewer・Opus）。Codex は加えない。

## 1. 編集者の判定: major revision

- R1 major（minor に近い）・R2 minor（major に近い）・R3 major・E「直してから回す」。E が「直してから回す」なので major 以上（Skill の 4b）。
- 凍結した計算をやり直す指摘は無い。どれも本文の言い換え・付録への移動・まとめで直せる。新しい計算の提案（R1: λ = 4 の A1′ と R7・正規化した開いた世界の診断）は任意。
- 有効な査読 4/4（R1・R2・R3・E がそれぞれ 2 本以上〔E は一次＋1 本〕の文献から基準を逐語で抜き出した）。

## 2. 一致（分母 = 有効な査読 4。監査は別に書く）

| 指摘 | R1 | R2 | R3 | E | 監査 | 裏取り |
|---|---|---|---|---|---|---|
| A C2 の要約（抄録・序論・§7.3 の「10 個の指標を元に近く残した形は 70% 以上」）が事後の 0.84 と中央値に依り、修正の指標の喪失を隠す | major | major | major | major | 2-A・2-B・3-C | 真。0.84 は preregistration.en.md に 0 件（登録は 231 行でパレート前線の記述だけ）。utility-r0.tex の R3: R-burst 0.28・insertion length 0.48・insertion proportion 0.19。R3 の中央値 0.92 は R0 と同じ式の 5 個（1.00）で決まる。R7(0.25)（14.3%・0.81）が二分の間に落ちる |
| B 但し書き（試した攻撃者・上限ではない ほか）の繰り返し | nit | minor | （d） | major | — | 真（位置は review-E.md・review-R1.md の一覧） |
| C 抄録の退化した区間「100.0 to 100.0」 | minor | — | major | nit | — | 真（main.tex:46） |
| D 本文が付録に頼る・本文から移せる細部（KeyTAR・§7.7・予測・A3 の細部・規則の誤差・逸脱の詳細） | minor（KeyTAR） | （e） | major | major | — | 真（results.tex §7.7 は付録でしか定義されない R-DP・一意性を引く。KeyTAR は脅威モデルの外で全形で A0 未満） |
| E 1 頁目にプライバシーとの関係（誰が何を失うか）が無い | — | — | major | major | — | 真（抄録と序論に "privacy" は 0 件。本文は threat-model.tex:146 の否定の 1 件だけ） |
| F 粗い形（R4(w ≥ 4)・R7）の「長さを超えない」は全文の攻撃者の弱さ（λ = 8・端から端の整列）に依る | major（λ の感度） | minor（R7 の条件） | major（窓との食い違い） | — | — | 真。windows.tex で N = 1,000 の窓は R4(4) 13.1〜43.3%・R4(2) 44.2〜58.1%（全文は 0.35%・4.4%）。λ = 4 で A2 は R4(4) 4.5% |
| G N = 10（教室）の床（長さだけで 57〜62%）と少数の書き手への集中が持ち帰りに無い | major | major | — | — | 2-B | 真（main-10.tex・explore-tail.tex の R7(0.5) 1.6%） |
| H 結論・§8 の一般化（"hiding the characters did not keep the logs apart"） | — | — | minor | — | 2-C | 真（conclusion.tex:7–8。R4(4)・R4(8)・R7(0.5) も文字を隠す） |

1 人だけ（＋監査）・すべて真（偽陽性なし）:
- R1: 開いた世界の AUC は長さで大きさの変わる素の費用をまとめた量（protocol.tex §6.5 の定義どおり・影響の大きさは未測定）／窓のおとりが 1 窓（appendix-attackers.tex:43・§3.5 は向きだけ）／攻撃者の非対称は C2 には保守的（提案）／N = 10 の R4 は組み合わせた攻撃者なら A0 を上回る／Rocher の correctness（nit）。
- R2: 近似した指標で得点との関係が変わる（−0.11→−0.50）ことが §8 に無い／R2 の挿入の近似（R2 と R3 の効用が同じ値）／R7 の結果に「抑制を戻す攻撃者は試していない」の条件が §8.3 に無い／統計的開示制御の語彙と文献（round 1 から未解消）／結論の「matching low」が未定義（nit）。
- R3: protocol.tex:17「Everything in Sections 3 to 6 … was fixed」が §3.3 の登録後の情報まで含む／予測の「すべて当たった」に構成上の一致（R4(1)）を含み、KeyTAR の外れに「the intervals include 10 times」を添える（results.tex:171）／探索の時刻の証拠がリポジトリだけ／新規性の主張（related.tex:46）が検索の記録に対して強い・C3 が先行の候補選択の攻撃と重なる／効用の近似の規則が図を悲観側へ寄せる／倫理: 審査を頼む他の手段の検討と、個人的な連絡を公表する許諾（判断 72 の追記: 明示の許諾ではない）／ENJA の抄録に値が無い（nit）／図 1 の支配が 0.0025 の差に依る（nit）。
- E: 考察が公開する側への含意を出し切っていない／序論の出どころの文が流れを切る／ENJA が抄録の焦点をぼかす／§7.4 が雑多で図 1 の注が結論を言わない。
- 監査: §8.3 に「区間には有用さの軸が無い」が無い（round 1 の 1-1 が組み直しで落ちた）／§1 に問いが 2 つしか無いのに §6.6・§7.6 は「4 つの問い」／open-science.tex の 19:22 と 19:29（19:22 は ENJA15 の取得・説明が無い）／害 (a) の言い換え（登録は "Learning the content of a hidden text"・原稿は「記録と本文が結び付くこと」）が逸脱の一覧に無い／§7.7 の得点の帯の要約が表と合わない（R3-u のほかに区間が 0 をまたがない行が 8 つ・粗い形では得点の高い書き手ほど結び付く）／抄録が目的の読みを著者のものと書かない／序論の「only at a cost」が因果に寄る／§7.6 の R3j-t と R4(1) は作りの上で R3j と同じ値。

## 3. 裏取り

- 接地の引用: 5 本とも、各役 1 件以上を本文で確かめた（空白を正規化して照合）。narayanan "declares there is no match if and only if"・stadler "outliers or members of minorities largely remain vulnerable" と "under any potential privacy adversary"・rocher "can be accurately estimated, and is often high"・borgman "depending on the time, purpose, or entity requesting access"・hanisch "implies a weak adversary and must be improved"・arp "calibrating thresholds on the test data" と "threat models should be defined precisely"・kohno "beyond consenting participants" と "accept that sometimes the answer is"・mensh "each subject should be covered in only one place"・"advances the field by providing new opportunities"・"title of the figure should communicate the conclusion"。捏造なし。
- 原稿側: 0.84 の不在（grep）・privacy の不在（grep）・窓の R4 の値（windows.tex）・得点の帯（explore-band.tex）・取得の時刻（open-science.tex:4 と 29）・害 (a) の登録の文（preregistration.en.md:41）・§8.3 の窓の文（discussion.tex:68–70）・protocol.tex:17・related.tex:46・results.tex:171 を開いて確かめた。

## 4. 直す順（案）

本文は余白 0 なので、まず移して空け、空いた分で足す。

移す・まとめる（紙面を空ける）
1. KeyTAR を本文から付録 E へ（表 4 の A4 の 2 行・§7.4 と §7.5 の文・attackers.tex の細部・data.tex の取得の段）。本文は 1 文。
2. §7.7（探索）を付録 D への 1〜2 文の参照に。§6.7 の手順も付録 D へ（判断 78 で一部移し済み）。
3. 予測と結果（§7.5）と逸脱の詳細（§6.8）を付録へ移し、本文は 1 文ずつ。
4. attackers.tex の規則の誤差・同じ費用の選び方・A3 の推定の細部を付録 C へ。
5. 但し書きを §3.5 に 1 か所（抄録と結論に 1 回ずつ）、他は参照。

書き直す・足す
6. C2 の要約（A）: 0.84 を外し、パレート前線の点と、処理した形はどれも修正の指標（R-burst・挿入）を失うことで述べる。設計の判断。
7. 1 頁目のプライバシー（E）: 抄録と序論に、書き手が失うもの（作文に結び付いた過程・得点・修正の履歴、教室では名前つき）を 1〜2 文。
8. 粗い形（F）: 全文の攻撃者の弱さ（窓の値・λ）を 2 文、§8.3 の「w ≥ 4 left no gain」に条件。設計の判断。
9. N = 10 の床と少数の書き手への集中（G）を §8.3 に 1 文。
10. 結論と §8 の一般化を 1 つの公開に戻す（H）。
11. 抄録: 退化した区間を外し、目的の読みが著者のもの、ENJA に値を添える。

小さな直し（判断不要）
12. §8.3 の窓に有用さの軸が無いこと・§1 の 4 つの問い・19:22 の説明・害 (a) の言い換えを §6.8 か §3 に 1 文・得点の帯の要約を表に合わせる・protocol.tex:17 の範囲・予測の R4(1) の注と KeyTAR の句・新規性の主張を検索の範囲に限る・効用の近似が下限側に寄りうる・近似した指標で得点との関係が変わる（§8.3）・R7 の条件・R2 の効用は位置を使わない・結論の「matching low」・図 1 の注（λ = 8・効用軸に区間なし・注の頭を結論に）・倫理（審査の他の手段・個人的な連絡の公表の許諾を角括弧で）・探索の時刻の証拠・§7.6 の R3j-t と R4(1) の注・序論の出どころの文を短く。

任意（新しい計算）
13. λ = 4 の A1′ と R7 の A2・正規化した開いた世界の診断を探索として付録に（G-GEAR）。結果を見た後に足す探索になる。

## 4b. 編集者 E の判定: 直してから回す

1 頁目に書き手が失うものが無い（範囲外と読まれる余地）・C2 が事後の閾値に依る・本文が上限ちょうどで直す余地が無い。

## 4c. 本文の分量

本文の語数 11,086（texcount を本文の 9 節に当てた和・commit c3f3f5b5）。前の round の版（commit 92c0cadb）は同じ数え方で 11,046（+40）。直した後に測り直し、次の round に書く。

## 5. 逸脱・注入の疑い

- 投稿規程と CfP をこの round で取り直せなかった（petsymposium.org の名前を curl・WebFetch・Chrome のどれでも引けず、研究者のブラウザでも開けなかった・2026-10-29）。round 1（2026-10-21）に照合した抜粋を使った。規程に依る指摘（E の 1 頁目・付録への依存）は、その抜粋で確かめた。
- 保存の形: 5 本の応答は、tmp/*.raw.md に写すときにメインが言い回しを縮めた（指摘・位置・逐語・解消の条件・自信は残した）。保存の検査（secrets-filter rc=0・応答の中の絶対パスなし）は 5 本とも通った。
- 注入の疑い: 5 本とも「なし」。メインも保存の際に見つけていない。
- 失敗した役: なし（5 本とも初回で返った）。
- 編集者 E はこの round から（枝 chore/paper-write-skill の attack-me の版・判断 77 の試し）。

## 6. 研究者に問うこと

- C2 の要約の書き直しの方向（6）
- 粗い形の扱い（8）と、新しい計算をするか（13）
- 本文から移す範囲（1〜5）
- 小さな直し（12）と書き直し 7・9・10・11 の一括の承認
