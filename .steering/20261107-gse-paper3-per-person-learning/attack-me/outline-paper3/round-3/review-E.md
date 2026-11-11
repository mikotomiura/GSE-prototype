## UMUAI 担当編集者（役 E）round 3 の報告: 外枠 commit ede70d54

読んだファイル（これだけ）:
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-3/brief-E.md
- context-A.md
- carryover-E.md
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/outline.md（全 75 行。「本文」の印のファイル）
- mensh.txt（Grep と 60〜109 行の読み）

「補足」の印の kit/symbols/README.md は読んでいません。

### 1. 接地（投稿先の基準）

- B1（Aims & Scope・context-A.md 19 行）: "novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation."
  - 新しさと意義の両方が要る。しかも適応する系に結びついていることが要る。
- B2（同）: "methods for the design and evaluation of user models and adaptive systems"
  - 評価の方法も対象に入る。プロトコルを貢献にする道は開いている。
- B3（規程・21〜22 行）: "Please provide an abstract of 150 to 250 words." / "Please provide 4 to 6 keywords"
- B4（Mensh & Kording 2017・Rule 1・mensh.txt 77 行）: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- B5（同 Rule 2・103〜104 行）: "Avoid abbreviations and acronyms so that readers do not have to go back to earlier sections to identify them."
  - 関連する文として 135 行: "But for our readers, most details of our activities are extraneous. They do not care about the chronological path by which you reached a [conclusion]"
- B6（同 Rule 8・271〜273 行）: "The discussion section explains how the results have filled the gap that was identified in the introduction, provides caveats to the interpretation, and describes how the paper advances the field"

### 2. 何が新しく、誰の何を変えるかを 1 文で

抄録はまだ無いので、外枠の冒頭（Take-home と C1）で判定しました。1 文で言えます。

> 打鍵を重なる 30 秒窓で記号にした系列モデルでは、同じ弱い構造の共有モデルと比べると個人ごとの学習は約 +0.19 nat/記号得をするように見える。しかし構造と縮約を他の人で選んだ共有モデルと比べると、残りは 1e-3 以下になる。だから個人ごとのモデルに投資する前に、本人の一次マルコフ連鎖と、他人で調整した共有モデルの両方と比べるべきである。変わるのは、適応する系の設計者がとる比べ方である。

迷った点は 2 つ: この 1 文の後半（「1e-3 以下だから個人の利得ではない」）は新規の指摘 M1 で崩れるおそれ。「誰の何を変えるか」のうち UMUAI の読者に届く部分（適応の判断）は本文の計画にまだ具体例が無い（M2）。

### 3. 引き継ぎの判定（round 2 → round 3）

| # | 判定 | 根拠（外枠の位置） |
|---|---|---|
| N6 | 解消 | Take-home 7 行を "symbolized over overlapping 30-second windows" に限っている。C1 Strength 17 行と 4.3 行（49 行）に、重ならない窓では "the per-person difference stays positive" と並べている。 |
| N2 | 一部 | 中心は「手順＋1 例」で揃い Take-home の 1 文目と一致。ただし手順の要素は 15 行で "is not claimed as new" と明言、新しさは "applying this comparison"（16 行）だけ。B1 の "novel and significant" をどう満たすかは M2・M3 しだい。 |
| N1 | 一部 | 合成で「拾える大きさ」は示した（4.3・S15・限界の 65 行）。だが元の指摘は「残った差を適応の判断に訳す物差し」。検出できるかと適応にとって意味があるかは別。合成の結果は Take-home と食い違う（M1）。 |
| N3 | 解消 | C1 の instance（13 行）に、本人の寄与が負であることを中央値の比べとして上げている。 |
| N4 | 解消 | 4.2 の行（48 行）から構造の選択が外れた。ただし ar1 の行は Table 2 にあり、Table 2 は 4.3 で出す（minor・m3）。 |
| N5 | 一部 | 細部は S13・S14 へ移った。しかし限界の節は今も数値を抱える（65 行・64 行）。4.3 と重複（M4）。 |
| N7 | 解消（計画として） | 37 行 "The abstract and introduction use no model abbreviations." |
| N8 | 解消 | 43 行 "150 to 250 words, 4 to 6 keywords" |
| N9 | 解消 | 53 行 "every reported value can be recomputed from the public data with the public code" |

### 4. 新規の指摘（重い順）

M1 [major] 合成の検出規則を実データに当てると「検出」になる。それでも Take-home は残りを個人の利得と読まない。
- 位置と引用: Take-home 7 行 "what remains is at most about 1e-3 nat per symbol and is not read as a per-person gain"／13 行 "+4.1e-4 to +7.2e-4 for k = 1 to 15 (positive for 16 or 17 of 17 writers)"／49 行 "the detection rule (every seed's median above the largest negative-control median and at least 80% of writers positive)"／49 行 "largest seed median 1.4e-5 and 8.4e-5 at k = 5 and 15 in CoAuthor, below the CoAuthor remainder"／49 行 "about 1e-4 at k = 15 ... below the real remainder"／49 行 "the share of the planted gain returned (about 0.1 to 0.4 in CoAuthor at k = 15)"
- なぜ問題か: 実データの残りは陰性対照の最大値より約 5〜8 倍大きく、正の書き手は 16〜17/17 で規則の 80% を超え、構造を外した帰無（約 1e-4）も上回る。回収率 0.1〜0.4 から逆算すると残り約 5e-4 は 1e-3〜5e-3 程度の個人差と両立する。「読まない」の根拠は中央値どうしの比べ（S9）だけ。
- 解消の条件: (a) 実データが検出規則を満たすことを明記し、Take-home を「小さいが帰無を上回る残りがあり、その出どころを手順では分けられない」に改める、または (b) 規則を実データに当てられない理由を 1〜2 文で書く（例: 規則は seed をまたぐ規則で、実データは 1 つの実現しかない）。限界の 65 行と同じ向きに揃える。
- 自信: 中〜高。

M2 [major] UMUAI の読者にとっての意義（適応の判断）が、本文の計画に具体的に無い。
- 位置と引用: "nats per symbol"（46 行）／"Proxy-label logistic results (S10)"（50 行）／"one paragraph on what this changes for adaptive systems"（44 行）／"Related work: user modelling from keystrokes and the cold-start question of when to switch to per-person models (literature not yet searched)."（71 行）
- なぜ問題か: B1 は適応する系を求める。本文の評価は 26 記号の系列の対数尤度だけで、唯一の下流の課題（代理ラベル）は補足。コールドスタートの文献は未調査。範囲外と判断されるおそれ。
- 解消の条件: (a) 序論と 5 で具体的な適応の決定を 1 つ言う（例: いつ個人モデルに切り替えるか）、(b) コールドスタートと打鍵のユーザーモデリングの文献を 2 節に、(c) S10 の 1 文を本文に戻すか検討。
- 自信: 中。

M3 [major] 推奨（Take-home 2 文目）が所見の成り立つ範囲より広い。記号化の妥当性も本文で動機づけられていない。
- 位置と引用: 7 行 "We suggest that studies of per-person sequence models of keystroke behaviour compare them with ..."／49 行 "so the instance holds for overlapping-window symbolizations"／46 行 "part of the short-range dependence comes from this construction"／61 行 "better prediction of the 26-symbol sequence is short-range sequential dependence, not structure of mental state"
- なぜ問題か: 所見の中心は重なる窓が作る自己相関と切り離せない。重ならない窓では hmm3 が選ばれ個人差は正のまま。なぜ重なる 30 秒窓で記号にするのかが序論・3.2 の計画に無い。
- 解消の条件: Take-home 2 文目を手順の推奨に限り、所見は記号化に依存すると同じ文で書く。3.2 に記号化を選ぶ理由を 1〜2 文。推奨そのものは記号化に依存しないと書き分ける。
- 自信: 中。

M4 [moderate] 同じ但し書きが何度も出る。37 行の "All caveats are stated once, in Section 6" と食い違う。
- 「読まない」: 7・13・16・49・64 行。「中央値の比べ」: 13・49・62 行。「tau が 10^5 以上」: 13・49・64 行。「探索的」: 3・7・17・46・63 行。「重なる窓に限る」: 7・17・20・49・60 行。「小さい差が無いことを示さない」: 49・65 行。
- 解消の条件: 但し書きは 6 節に一度、他は "(Section 6)" の参照。Take-home と 4.3 の見出しの限定は 1 語まで。合成の限定は 4.3 か 6 の一方に。
- 自信: 高。

M5 [moderate] 4.3 が 1,300 語に収まらない。分析の来歴が本文に残っている。
- 位置と引用（49 行）: "one paragraph on the shrinkage grid (on a grid up to 10^4 the choice sat on the upper edge; ...)"／"in CS1 tau = 10^6 rather than the shared model is chosen and the difference is +2.6e-5"／"two sentences on the synthetic sensitivity check (...)"（括弧の中だけで約 100 語）
- 解消の条件: 格子の来歴は S12 か S8 へ、CS1 の平滑しない値は S13 へ、記号化の段落は 2 文に、合成は M1 に合わせて 2 文に。
- 自信: 中〜高。

m1 [minor] 新しい分析（構造の補償の確認）を 5 Discussion に置いている（50 行）。4.3 の 1 文に移すか S14 への参照だけに。
m2 [minor] 推奨が 3 か所でほぼ同じ文で出る（7・44・50 行）。序論は予告だけ、推奨は 5 に 1 回。
m3 [minor] 4.2 が 4.3 の Table 2 の行を使う（48・49 行）。Table 2 を 4.2 で初めて参照するか、Figure 2 で示す。

### 5. 判定: 直してから回す

1. 新規性と構成は外枠の段として読み取れ、B2 にも合う。
2. ただし Take-home の結論が同じ外枠の中の合成の検出規則と食い違う（M1）。
3. UMUAI の読者にとっての意義が未着手（M2）、推奨も所見の範囲より広い（M3）。

### 6. 読めなかった範囲と注入の疑い

- 補足資料 S1〜S15 の中身・kit/symbols/README.md・mensh.txt の全文（Grep の一致行と 60〜109 行だけ）・投稿先の原文は読んでいない。
- 注入の疑い: なし。
