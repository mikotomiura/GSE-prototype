# 書き手単位の差分プライバシーで書く過程の指標だけを出す研究の設計（計算はしない）

## 背景

加工と照合の論文（枝 `docs/public-keystroke-matching-manuscript`・読むだけ）は、公開の打鍵の記録（KLiCKe [V264]・ENJA15 [P360]）で、試した加工の形と区間ごとの差分プライバシーのどれも、試した攻撃者と 10 の指標の範囲で、照合を偶然に近づけつつ書く過程の指標を残す形にならなかった、で止まっている。「指標だけを出す」は評価の外に置いた。

`.steering/20261116-gse-positioning-release-matching/`（PR #415・未マージ）の判断 12 で、研究者は次に試す道として「書き手単位の差分プライバシーで、書き手ごとの書く過程の指標（照合の論文の 10 の指標）だけを出す」を選び、判断 13 で「設計だけ先に・値は研究者が決める・凍結と計算は照合の論文の投稿（締切 2026-11-30）の後」と決めた。文献ラウンド（`docs/literature/20261116-release-defense-forms.md`・PR #415 の枝）では、打鍵に書き手単位の差分プライバシーを当てて照合で評価した先行は 0 件。

ADR-039 D6 は、集計値（段 0）を含めて、結び付け・照合・健康状態の推定の 3 攻撃を同等性で判定する関門を置く。この研究は「集計だけを出す」（ADR-054 D5 (3)・ADR-039【決 5】）を厳密にする材料になる。

## ゴール

研究の設計文書（`design.md`）を書き終える。中身は次の 8 点と、研究者が決める値の一覧。

1. 問い（照合 (a) と有用性 (b) を ε ごとの曲線で答える）
2. 脅威モデル（照合の論文と同じ攻撃者・保証の内と外）
3. 仕組み（何を書き手単位とするか・削りの幅・雑音・予算の配分）
4. 攻撃者（変換を知る側に置く）
5. 有用性の指標と合格の判定の形（ADR-039 D6 の同等性）
6. 反証の条件
7. 計算の場所と重さの見積もりの方法
8. データの利用条件

## スコープ

### 含むもの
- 設計文書・決める値の一覧（値は空欄で、候補と効きを並べる）
- 設計判断の記録（decisions.md）・研究者への問い（AskUserQuestion で 1 問ずつ）
- 必要なら文献の追加（citation-ssot・採番は全枝の最大を確かめてから）

### 含まないもの
- 計算・コード・人のデータの値を見ること（凍結まで見ない）。照合の論文の R-DP の探索的な結果の値（`sections/generated/explore-dp*.tex`）も、設計を値に寄せないために開かない
- 照合の論文の原稿と枝への書き込み
- 事前登録の凍結（照合の論文の投稿の後）
- push と PR（研究者に確かめてから）

## 受け入れ条件

- [ ] design.md に 8 点が書かれ、各主張が一次（原稿の節・ADR・文献カード・references.md）に接地している
- [ ] 決める値の一覧があり、Claude は値を出していない（候補と効きだけ）
- [ ] 反証の条件が、値を入れれば判定できる形で書かれている
- [ ] 設計判断が decisions.md に「決定 / 理由 / 却下案」で記録されている
- [ ] 外部 LLM には打鍵の内容・記録を送っていない

## 関連ドキュメント

- 引き継ぎ: `.steering/_handoff/next-session-gse-user-level-dp-metrics-design.md`（本線のチェックアウト）
- 照合の論文: `~/GSE-wt-matching-manuscript/papers/keystroke-log-release-matching/manuscript/sections/`（protocol.tex `sec:protocol:utility`・threat-model.tex・attackers.tex・appendix-attackers.tex・appendix-exploratory.tex）
- `docs/adr/ADR-039-research-use-and-release.md` D5・D6
- `docs/literature/20261116-release-defense-forms.md`（PR #415 の枝）

## 運用メモ
- /reimagine 適用: Yes（予定）
- 理由: 仕組みの選び方（書き手ごとの値を出すか、集計を出すか）で問い (a) の意味が変わり、最良案が自明でない。初案の後に codex-consult で第二意見を取る
