# 上流の文書のずれ（2026-11-05・origin/main で grep）

判断 0 により、直すのは議論の後。ここでは種類を 2 つに分ける。

- **事実**: 既に決まった ADR や実装の状態と食い違う。議論の結果によらず直す。
- **主張**: 位置づけ・headline・問いに関わる。議論の結果を待って直す。

行番号は 2026-11-05 の origin/main。

## 事実のずれ

| ファイル:行 | 今の文 | 食い違う相手 |
|---|---|---|
| `docs/agent-shared.md:11` | 目的は「認知状態 (Flow / Incubation / Stuck) を推定し」 | ADR-046 D1（3 状態の名前を主張と新しい文書で使わない）。同じファイルの 23 行目は「作業上の認知状態」と書いていて、ファイルの中でも食い違う |
| `docs/functional-design.md:249`・`:400` | 「ダッシュボードに Flow/Incubation/Stuck の確率が表示される」「3 状態認知推定（Flow / Incubation / Stuck）の 1Hz 更新」 | ADR-046 D1（画面と主張）。48 行目は「参考スコア」と断ってあるが、249・400 は断りがない |
| `docs/architecture.md:183` | MhD の責務を「Flow / Incubation / Stuck は … Need 判定に使う参考確率」と書く | ADR-044（`p_stuck` の役は固定の baseline と H3 の手がかりに限る）・ADR-046 D1 |
| `docs/architecture/gse-v2-overview.md:64`・`:143` | 「Flow / Incubation / Stuck を正確に分類する」（目標でないもの）・旧三状態の表示の残存 | 書き方は否定の文脈。ADR-046 D1 の注を足すだけでよい見込み（要確認） |
| `docs/wbs-verification-halfyear.md:28`・`:29` | B1「1 段目（統制課題）で招待を 3 腕に割り付ける」・B2「1 段目で効果が見えた人だけ多重ベースライン」 | ADR-043 D1（段 1 は招待なしで C4、段 2 で招待の 3 腕）。設計の地図 §0 が既に挙げているずれ |
| `docs/research-positioning.md:55` | 「詰まる前」の中身を「今の推定の出力から定義する」 | ADR-041 D1（契機の中身を今の推定の上がりで埋めない） |
| `docs/research-positioning.md:91`・`:112`・`:134`・`:834`〜`:840` | 売りの層の主役を「Stuck 検出の妥当性 × 介入タイミング」、核心の差分を「Stuck 検出（L1: p_stuck）× 介入機会の妥当性」と書く | 47〜53 行の 2026-10-31 改訂ブロックが既に headline を改め、「食い違うときは改訂ブロックを優先する」（13 行）としている。ただし ADR-044〜046 の後の形（停滞が主の対象・p_stuck の役の限定）はまだ改訂ブロックにも入っていない |

## 主張のずれ（議論を待つ）

| ファイル:行 | 今の文 | 揺らす分析・決定 |
|---|---|---|
| `docs/research-positioning.md:49`〜`:53` | 位置づけ「作業上の認知状態を推定し、詰まる前に介入を促して、身体回帰の機会を差し出す」・headline「作業上の認知状態の推定 × 詰まる前の招待」 | 俯瞰 §3 の 1（手前の上がりがどのデータでも見えない）・ADR-045 D1（主の対象は停滞）・ADR-045 の「詰まる前に」の見直しの保留 |
| `docs/agent-shared.md:23`・`:24` | 同じ位置づけの写し | 上と同じ。research-positioning を直したら写しを合わせる |
| `docs/architecture/gse-design-map.md:9` | §0 の位置づけ（同じ文と、言い方の見直しは research-positioning §1 の改訂で） | 上と同じ |
| `docs/research-positioning.md` §1 の L0〜L2 の表（38 行ほか） | 確証の核は L0（X 摩擦・Y 前進と Q1・Q2 の順序の一致）・L1 Stuck・L2 Need | ADR-043（段 1 のラベルは C4 の 6 択＋Q1・Q2）・ADR-045（停滞の中身の内訳が H1）。L0 を確証の核に残すかは議論の論点 |
| `docs/architecture/personalization-and-online-learning.md` 全体 | 個人適応を前提にした設計（V3「個人適応の必要性」） | ADR-046 D3（学習は 1 人ごとが既定）と、coauthor-ml-improve（構造を良くすると 1 人ごとの効きは小さい） |
| アウトカム（ADR-024 D1 を引く文書の全体） | 主は `receipt_free_resumption` | stall-decomposition（O1 の停滞の単位で 1b が 99.5% 情報なし）・受領がデータで 0.13%〜81% |

## 確かめたが、ずれではなかったもの

- `docs/glossary.md:13`〜`:18`: 3 状態の名前と Nudge の項は、ADR-046 D1・ADR-040 の注が既に入っている。
- `docs/functional-design.md:48`・`:104` と `docs/architecture.md:488`〜`:499`・`:672`: 参考スコアの断りと、EH3 モードの招待の注が入っている。
- `docs/architecture/personalization-and-online-learning.md:335`: ADR-042 の注が入っている。
