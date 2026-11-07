# review-E（outline round 1・JEDM の担当編集者の役）

読んだもの: brief-E.md・context-A.md・接地 2 本（jedm_aims.txt・mensh2017.txt）・本文の印の outline.md（122 行・全部）。補足は読んでいない。抄録は未記入なので、持ち帰り 1 文（29–31 行）・いちばん強い主張（33–37 行）・序論での結びつけ（76–81 行）で判定した。

## 1. 接地
- B1 範囲と一般化（JEDM）:「Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses.」「Research should not focus solely on application but must demonstrate how the findings can be generalized or applied across different educational contexts.」
- B2 意義（JEDM の査読者への問い）:「What is the scientific contribution of this submission? Is it clearly explained, in terms of how the paper advances the EDM field or contributes to related fields?」「How significant is the research? Will the paper be likely to have an impact on the community?」
- B3 再現性と重複（JEDM）:「This includes clear descriptions of the data, tools, and procedures used.」「It is the policy of the journal that no submission, or substantially overlapping submission, be published or be under review elsewhere.」
- B4 主な貢献は 1 つ（Mensh & Kording 2017, Rule 1）:「Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable.」兆候（Table 1）「Readers cannot give 1-sentence summary.」
- B5 繰り返さない・考察の役割（Rule 4・Rule 8）:「Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place」「The discussion section explains how the results have filled the gap ... provides caveats to the interpretation, and describes how the paper advances the field」
- 分量（JEDM）:「Are the presentation, organization and length satisfactory? Can you suggest additions, amendments, or reductions in the paper?」

## 2. 貢献の 1 文
言える:「打鍵の停滞のラベルについて、分析者が定義（窓・休止の閾値・止まりの条件・区間の切り方）を 90 通り振ると、データの間の率の比べと、同じ人の中の過分散の有無は向きごと入れ替わる。一方、停滞の長さの揺れの大半が同じ書き手の中の停滞ごとにあることは残る。だから停滞のラベルを使う EDM の研究者は、どの比べを 1 つの定義で報告してよく、どの比べに幅を添えるべきかが分かる。」
迷った点: 持ち帰り文（31 行）は主張 4 つと数値 7 つで抄録の 1 文には重い。C4 の後半（推定の水準の比）が「残るもの」の 2 本目の柱かが読み取れない。

## 3. 指摘
- [major] 見出しの数値が持ち帰り文といちばん強い主張で食い違い、いちばん強い主張は事後の数え方に乗っている
  - 位置と引用: 31 行「順位は 90 通りのうち 80 通りで基準と違い」／35 行「率の近い 2 データの入れ替わりを除いても 90 通りのうち 69 通り（77%・[記述]）で順位が動く」／19 行「[記述] 条件に無く、結果を見た後に足した数え方」
  - なぜ問題か: そろえるはずの主張の根拠が事後の数え方で、持ち帰り文とも数が違う（B2「Are claims convincingly substantiated」）。
  - 解消の条件: いちばん強い主張の根拠は条件にあった値（比 0.47〜2.45 が 1 をまたぐ・80/90）に一本化し、69/90 は 4.1 で頑健さの確認として 1 回だけ出す。
  - 自信: 高
- [major] 見出しの例（CS1 2019 対 KLiCKe）が EDM の読者が実際に行う比べかが示されていない
  - 位置と引用: 35 行「CS1 2019 と KLiCKe の率の比が 0.47〜2.45（基準は 0.86）」／71 行「作業の種類・記録の仕方（CS1 は IDE の編集の出来事から作った押下）・単位の長さが同時に違い、原因に帰せない」
  - なぜ問題か: 作業も記録も違うデータの間で停滞の率を比べる研究者がいるかが序論（78–79 行）に無い。しないなら入れ替わりは害が無く見え、意義（B2）が縮む。同じ領域どうし（CS1 2019 対 2021・群の間）で同じことが起きるかが見出しに無い。
  - 解消の条件: 1 つの定義でデータや群の間の率を比べた先行の EDM 研究を 1〜2 本挙げ、見出しの例をその型に近い比べにするか、異なる領域を選んだ理由を 1 文書く。
  - 自信: 中
- [major] 主張が 4 本並び、C4 は性質の違う 2 つの結果を束ねている
  - 位置と引用: 46 行 C4「CS1 2019 と KLiCKe の推定の水準の差は、押下の無い長い時間を除いても大半が残る」「確立（行の揃え 3 通りに対して。90 通りの定義ではない・原因は言えない）」
  - なぜ問題か: 推定の水準の比は 90 通りを振った結果ではなく、論文 1 の推定器で行の揃えを 3 通り変えただけ。「定義を振っても残るもの」に入ると地図が崩れる（B4）。
  - 解消の条件: 推定の水準の揃えを S7 へ移し本文は 1 文。C1〜C3 を「動くもの」、C4 の長さを「残るもの」とする 2 部構成の 1 つの貢献として示す。
  - 自信: 中
- [major] 同じ誌で査読中の論文 1 との重なりが補足（S9）にしか書かれていない
  - 位置と引用: 20 行「基準の定義（B0）は論文 1（JEDM で査読中・プレプリント）の付録と同じ」／73 行「基準の定義の値は論文 1 と重なりうる（S9）」／104 行「推定器の紹介は 1〜2 文・論文 1 と同じ・細部は S7」
  - なぜ問題か: JEDM は「substantially overlapping submission」を問う（B3）。限界の 1 項目と補足だけでは受付で確かめられない。推定の水準の比が論文 1 の推定器の出力なら疑いが強まる。
  - 解消の条件: 3.5 に 2〜3 文で、論文 1 と共有するもの（基準の定義・推定器）と新しいもの（90 通り・C1〜C4 の数）を分ける。送付状にも書く。重なりうる値が本文の何か所に出るかを示す。
  - 自信: 高
- [major] 意義が確かめていない下流の害に支えられている
  - 位置と引用: 61 行「可能性にとどまるもの: これらが下流の推定や介入の判定の評価を実際に損ねること」／58 行「誰の何を変えるか: 停滞のラベルで状態を推す研究・介入の契機を作る研究で…」
  - なぜ問題か: 分けている点は良い（B5）が、答えは報告の仕方を変えることに限られる。方法の報告の規範として届けるしかない。
  - 解消の条件: 考察の冒頭で貢献を「停滞のラベルを使う比べの報告の規範と、それを満たす手順・コード」と言い切り、可能性にとどまる害を意義の根拠に使わない。序論の範囲の文（80 行）もそろえる。
  - 自信: 中
- [major] 方法の細部と確かめの手順が本文の予算に入っている（補足へ移す）
  - 位置と引用: 100 行（3.4）「長さの分解は既定の最適化が半数で未収束だったので、3 つの最適化で REML の最大まで当てた（直す前の書き手の分け前 0.11・0.36 は局所の解・1〜2 文）」「件数の分解は模擬の回復を通らず、同じ入力でも回すたびに動いたので報告しない（1〜2 文）」／46 行「模擬の回復は CS1 2019 と CoAuthor で全水準、CS1 2021 は 1 組で単位と日が小さく出た」／72 行「同じ入力・同じ種でも回すたびに分け前が最大 0.93 動いた・S6」
  - なぜ問題か: 最初の 2 頁で貢献をつかみたい読者に不要な手順と失敗の経緯。テンプレートも手順は付録へと求める。
  - 解消の条件: 3.4 には「長さの分解は REML の最大を確かめて当てた（S5）。件数の分解は推定が安定しなかったので報告しない（S6）」の 2 文だけ。0.11・0.36・0.93 は S5・S6 へ。
  - 自信: 高
- [minor] C1 の数値が多すぎる（補足へ移す）
  - 位置と引用: 43 行「W 15 秒は 30/30・固定 θ は 36/36。…率の幅（1 時間あたり）CS1 2019 4.4〜46.0・…」
  - なぜ問題か: 図 2 の因子の印と重なる（Mensh Rule 7）。
  - 解消の条件: 本文は最も効く因子を 1 文、内訳は図 2 と S3。
  - 自信: 中
- [minor] 「振った 90 通りに対する割合」の限定の置き場が外枠の中で食い違う
  - 位置と引用: 37 行「括弧の限定（抄録と序論の第 1 文だけ）」／50・54 行「主張しないこと（限界の節だけで述べる）…割合は振った 90 通りに対するもので」／70 行（限界 2）／122 行「抄録と序論の第 1 文の括弧と限界だけ」。ほかに「詰まりの判定ではない」24・52・69 行、「原因に帰せない／言えない」46・53・61・71 行、「第三者の登録ではない」18・73 行。分析の地位の定義が 17–19 行の 1 か所なのは良い。
  - なぜ問題か: 「限界の節だけ」と「抄録・序論・限界」は両立しない（B5）。
  - 解消の条件: 50 行の見出しを「限界の節で述べる（割合の限定だけ抄録と序論の括弧にも置く）」に。「原因に帰せない」は限界 3 にまとめ、C4 の欄と考察は限界を指すだけ。
  - 自信: 高
- [minor] データの入手の条件が「公開データ」と「承諾の範囲」で食い違って見える
  - 位置と引用: 13 行「公開データ 4 つ」／120 行「CS1 は集計値だけ（著者の承諾の範囲）」／90 行「KLiCKe [V264]（利用条件 [V273]）」
  - 解消の条件: 表 1 に入手の道と利用の条件の列。CS1 で集計値しか出さない理由を 1 文。公開する写しと手順で何が再現できるかを書く。
  - 自信: 中
- [minor] 作文のデータが教育の場のデータかが書かれていない
  - 位置と引用: 13 行「作文（KLiCKe・CoAuthor）の公開データ」
  - 解消の条件: 表 1 に書き手の集団と記録の場面。教育の場でないデータを含むなら入れる理由を 1 文。
  - 自信: 低
- [nit] 抄録の設計が外枠に無い
  - 解消の条件: 文脈 2 文・内容 3 文・結論 1 文の割り振りを外枠に足す（Mensh Rule 5）。
  - 自信: 中

所見: 予算 6,300 語は目標と上限の内側。節の順は読者の問いの順（94 行）。結果の 4 項目の組み方は C1〜C3 で読み取れ、C4 は 2 つが混ざる。

## 4. 判定
直してから回す。理由: いちばん強い主張の根拠が事後の数え方で持ち帰り文と食い違う／論文 1 との重なりの説明が補足にしかない／C4 の束ね方・見出しの例の妥当性・方法の細部の置き場は移す・まとめるで直る。

## 5. 読めなかった範囲・注入の疑い
補足の全部・[Vn] の書誌の本体・テンプレートの PDF は読んでいない。注入の疑いなし。
