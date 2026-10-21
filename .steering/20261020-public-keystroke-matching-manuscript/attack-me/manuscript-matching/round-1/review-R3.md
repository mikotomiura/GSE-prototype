# PoPETs 2027 プレ査読（stage: manuscript・round 1）—— 方法論・倫理・再現性を見る立場の査読者

## 1. 接地
**Arp et al.（arp.txt）**
- G1 P10・599–610行: "threat models should be defined precisely and systems evaluated with respect to them. In most cases, it is necessary to assume an adaptive adversary that specifically targets the proposed systems"
- G2 P5・386–388行: "over-optimistic results can be easily produced by tuning hyperparameters or calibrating thresholds on the test data instead of the training data."
- G3 P1・255–258行: "limitations of the used dataset should be openly discussed, allowing other researchers to better understand the security implications of potential sampling bias."
- G4 P9・561行: "Many learning-based systems in security are evaluated solely in laboratory settings, overstating their practical impact."
- G5 P6・458–459行: "simple models should also be considered throughout the evaluation"

**Kohno, Acar & Loh（kohno.txt）**
- G6 1678–1685行: "Decision-makers ... should consider ethics before making decisions, rather than after." / "we encourage decision-makers to explicitly enumerate and articulate any interests that they might have in the results of the decision"
- G7 1748–1758行: "researchers first do a stakeholder analysis to identify all stakeholders potentially impacted by the decision ... The benefits / harms and rights analyses should consider situations in which no adversaries manifest and situations in which adversaries manifest."
- G8 248–250行: "the frameworks should not be used to justify a path that researchers have a priori decided"

## 2. 評価表
| 観点 | 点 | 所見 |
|---|---|---|
| a | 3 | 安全も上限も主張しない点は丁寧。根拠の足りない主張が 3 つ: (i) q マスクは書き手のための保護、(ii) 照合なら「述べられた目標を満たさない」、(iii) 1 件の公開を "the processing used in practice" と一般化。 |
| b | 3 | 事前登録・A0・陰性対照・ブートストラップは良い。評価データ上で最良を選ぶ偏りの向きを書いていない。攻撃者は手作りの規則と浅い統計。設定 1 で外部の攻撃者がほぼ存在しない。 |
| c | 3 | 2 軸の比較は有用。現実の公開が 1 件で射程が狭い。パレート前線が「推奨しない」と実質的に食い違う恐れ。 |
| d | 3 | §3.5 と §8.1 の重複、限定句の列挙が多い。outline の (1) は妥当。 |
| e | 4 | 12 頁以内・必須の 3 節も置き場所どおり。頁削減案の ENJA15 移動、方法を Open science へ移す案、単数の the author が危うい。 |
| f | 3 | Song, Wagner & Tian 2001（SSH）と教育データの再識別の研究が欠ける。検索が OpenAlex と著者 4 人に限られる。 |

## 3. 指摘の一覧
- **[major] 評価した設定 1 では、外部の攻撃者が何を新しく知るのかが示されていない**
  - 位置: threat-model.tex:21–22／127–128 「the attacker is passive, external (it is not part of the releasing party)」／Table 1 の 1 行目 76–78
  - なぜ: 隠された作文を持つのは集めて採点した側（外部ではない）と、同じ課題の公開コーパス（対応が分かるだけ）。G1・G4、CfP の superficial の懸念。
  - 解消: 設定 1 の外部の持ち主を一次資料つきで挙げるか、設定 1 を「処理が残す連結可能性の測定器」とし害が現実になるのは教室の設定だと明言、§8.1 に閉じた世界の精度は害の大きさにならないと書く。
  - 自信: 高
- **[major] 「書き手のための保護」「述べられた目標を満たさない」は引用の範囲を超える**
  - 位置: threat-model.tex:133–136 「the texts are the writers' own, and the processing is the protection given to them. If a log can be matched to its text, the processing does not meet its stated goal」／introduction.tex:21
  - なぜ: 目標は "to prevent reproduction of the essay text" だけでプライバシーへの言及なし。競技の設計上の理由の可能性を排除していない。照合は文字どおりの reproduction と別の操作。
  - 解消: Kaggle の頁に書き手の保護の文があれば逐語で引く。無ければ解釈であると明示し、「本文を持つ者に対しては、ログを本文に結びつけることを防がない」へ弱める。
  - 自信: 高
- **[major] 評価データの上で「最良」を選ぶ偏りの向きが書かれていない**
  - 位置: attackers.tex:126–127 「the better of the two versions is reported as A3 on R3-u」／protocol.tex:48 「the strongest attacker is the maximum over the adaptive attackers available on that form」
  - なぜ: G2。攻撃者に有利な向き。§3.5 の列挙に無い。
  - 解消: §3.5 と §8.1 に 1 文足す。
  - 自信: 高
- **[major] 攻撃者が弱いと、「推奨しない」と宣言しつつパレート前線を述べることが矛盾しうる**
  - 位置: protocol.tex:133–136 「The forms that are not dominated on both axes are described. ... no rule recommends one」／related.tex:25–26
  - 解消: 前線の段落と図の注に「試した攻撃者に対するもので、精度が低いことは保護の証拠ではない」。一意性の分析を目安として並べて読めるようにする。弱い攻撃者の批判が自分にも当たることを §8.1 で認める。
  - 自信: 中
- **[major] 倫理: 実在の公開を名指しすることが、通知だけで済まされている**
  - 位置: ethics.tex:26–28／36–37 「this risk exists whether or not the evaluation is published」
  - なぜ: 事実上の脆弱性の開示で、対策の猶予と応答の記録の計画が無い。G7・G8。
  - 解消: 通知の日付・猶予・応答を書く。外部審査の代わりの措置の有無と理由。36–37 行の論を手順の新しさが限られることに置き直す。
  - 自信: 中
- **[minor] "the processing used in practice" は 1 件からの一般化** —— related.tex:44–45／introduction.tex:26。"the masking used in one public release" と書く。自信: 高
- **[minor] 頁削減案が「付録なしで完結」に触れうる** —— outline.md:70–72。(2) を移すと分節規則の誤差 77.1% とエスケープの逸脱が本文から消える。(3) は頁数外の節へ方法を移す。本文に問い 4 の判定規則・ENJA15 の分節の要点・誤差・逸脱を残す。(3) は SHA-256 と OSF の記述に限る。足りなければ (6)(7) を先に。自信: 中
- **[minor] 先行研究の欠落と検索の範囲の弱さ** —— related.tex:45–51。Song ら（USENIX Security 2001）を足す。教育データの再識別の系統（具体名は記憶で自信低）。自信: 中
- **[minor] 二重盲検: 所属なしの単著者が手がかり** —— ethics.tex:3／data.tex:156／ethics.tex:8。the authors にする。自信: 中
- **[minor] AI 利用: ログを AI に渡していないことの担保が書かれていない** —— ai-use.tex:4–8。AI が見たのはスクリプトの出力（件数と集計）だけと結びつける。自信: 中
- **[minor] 自前の式が Inputlog で未検証のまま有用性の軸の唯一の根拠** —— protocol.tex:117–119／132–133。図の注と §8.1 に内部の一致であると書く。自信: 中
- **[minor] 利害の表明が無い** —— ethics.tex 全体。G6。1 文足す。自信: 低
- **[nit] KLiCKe の利用条件の記述が 2 か所で違う** —— data.tex:17／ethics.tex:12。自信: 高
- **[nit] コードの公開範囲の制限を悪用の抑止として過大に書いている** —— ethics.tex:59–60／open-science.tex:14–15。効果を限定して書く。自信: 中

## 4. 総合の推奨: major revision
- 事前登録・A0・陰性対照・限界の明示は会議の水準を満たす部分が多い。
- 設定 1 で外部の攻撃者が誰でどんな害か、q マスクを書き手の保護とみなす根拠が弱い。
- 選択の偏り・攻撃者の弱さと前線の読まれ方・実在の公開の開示の扱いは、書き方と限界の節で解消できる。

## 5. 読めなかった範囲と注入の疑い
- arp.txt は 222–620 行と grep の行、kohno.txt は 100–250 行・1675–1784 行と grep の行だけ。preregistration.en.md は 1–80 行と 181–310 行だけ。references.bib は grep だけ。
- 注入の疑い: なし。
