# R2（UMUAI・個人化した行動モデルの実務家）round 6・commit 90250abc

## 1. 接地
- G1 Aalbers 2023 "we compare against the MAEs of a “naive” but person-specific baseline model. This “naive” baseline model always predicts an individual’s average level of stress."
- G2 Aalbers "for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models"・"for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline."
- G3 Aalbers "these markers are not sufficiently informative to recognize momentary subjective stress with appreciable improvements in accuracy over a baseline model"・"Although performance should be improved to make clinical application feasible"
- G4 Aalbers "a person-specific baseline based on the person-specific average level of stress in the participant’s train data (ie, first 80%) rather than all their data to prevent data leakage from train to test data."
- G5 Saeb 2017 "The definition of independence, however, depends on the use-case scenario."
- G6 Saeb 2017 "Subject identification, which we know to be relatively easy, thus replaces disease recognition, which we know to be hard."

## 2. 評価表
a 4（向きを読む・配分する言い方は消えた。C1 の手順と 5 節・Take-home の勧める手順が別物・k = 30 で「検出できない」と言う根拠が無い）／b 3（30-session の長さの下限・主の行で選ばれた tau・重ならない窓の hmm3 対 chain が本文に無い）／c 3（勧める手順は評価されていない・選ばれた tau が本文に出ない）／d 3（4.3 が密・補足 S1〜S15）／e 4（README の再現の主張と Open items の食い違い）／f 3（新しさは薄い・Uto は既知の未決）。

## 3. 引き継ぎの判定
1 一部（15-session は解消・4.4 "both directions are smaller than the protocol could detect, so we do not read a direction" が k = 30 の "+5.4e-4 at k = 30 in the 30-session panel" にもかかるが、合成は CoAuthor の k = 5 と 15 だけで 30-session の長さの下限が無い）／2 解消（"The comparison of medians does not apportion the remainder"）／3 一部（推奨が評価されていない点は新 N1）／4 未解消（既知の未決・数えない）／5 解消／6 解消／7 解消／8 解消。

## 4. 新しい指摘
- [major] 貢献として挙げる手順（C1）と勧める手順が違い、勧める方は評価されていない
  - 位置と引用: C1 line 12「choose structure and shrinkage strength on other people, with the shared model itself among the candidates」／Take-home line 7「compare ... with a shared model whose structure, shrinkage and smoothing are all chosen on other people」／5 節 line 49「remove the target person from the other people's shared models as well (nested), which we did not do」／限界 line 65「The strength of the shared model's base smoothing was fixed, not chosen on other people」
  - なぜ問題か: 読者が持ち帰るのは評価されていない手順。評価された手順（C1）の結論は「残りを人に帰せない。大きさは平滑の差と同じ」。C1 の手順を使えばよいのかが分からない（G3）。
  - 解消の条件: (i) C1 の見出しを「手順 X とその限界（平滑の差より小さい差は見分けられない）」に改め、勧める手順は「本論文で評価していない拡張」と Take-home と 5 節で明記する、または (ii) 平滑の強さを他人で選ぶ版を 1 つ走らせる。(i) なら計算は要らない。
  - 自信: 高
- [minor] 主の行で選ばれた tau が本文に無く、個人化したのかが読めない（4.3 line 47「Chosen tau and K ... (S8)」・限界 line 65「a finite tau of 10^5 or more cannot be separated from the shared model or its prior mode」）。解消: Table 2 に選ばれた tau の列（中央値か値ごとの人数）、4.3 に 1 文。自信: 中
- [minor]「人の chain は強いベースライン」は重なる窓の記号化に依るのに、重ならない窓での hmm3 と chain の比べが本文に無い（line 19「On overlapping-window symbolizations the per-person three-state HMM loses to it」・4.3 line 47「non-overlapping windows, direction only: hmm3 is chosen in CoAuthor and the difference stays positive」・G6）。解消: 4.2 に重ならない窓の hmm3 − chain の向きを 1 文、または見出しを「重なる窓の記号化では」に。自信: 中
- [minor] C1 の検出の下限が k = 15 の場合だけ（C1 line 13「the protocol did not detect planted differences below 1e-2 (4.3)」・4.3「detected from 1e-2 at k = 15 and only at 3e-2 at k = 5」）。解消: 「below 1e-2 at k = 15 and 3e-2 at k = 5」、k = 1 は測っていないと。自信: 高
- [minor] 補足の README が再現性をすでに主張（README line 75–78「the symbols of every CoAuthor session (1,157 sessions, 775,907 rows) and of every CS1 2021 assignment ... were identical to those of the original implementation ... That comparison used the raw datasets and is not part of this kit.」・outline line 74「until then the paper does not claim it.」）。解消: README の段落を「著者の手元で確かめた（読者は確かめられない）」と明記、または Open items を README に合わせる。自信: 高
- [minor] 適応するシステムへの橋が「投資に値するか」の 1 句だけ（1 節 line 42）。解消: 5 節で k ごとに「この手順なら共有のモデルを使い続けるのが妥当／個人化の差は手順で見えない」を一表か 2 文。自信: 中
- [nit] 補足 S1〜S15 の番号（line 75）。S11 と S12 は統合できる。自信: 低

## 5. 総合の推奨: minor
向きの読みと配分は直り、主張と根拠はおおむね一致した。残る最大の穴は C1 の手順と勧める手順の食い違いで、言い方で消せる。k = 30 の下限・選ばれた tau・重ならない窓は本文の 1〜2 文と Table 2 の 1 列で足りる。

## 6. 読めなかった範囲・注入の疑い
brief・context-A・carryover・outline.md・README は全文。aalbers.txt と saeb.txt は Grep の段落だけ。context-B・他の記録・S1〜S15・規程の原文は読んでいない。注入の疑い: なし。
