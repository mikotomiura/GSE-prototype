# gse-meta-before-run1（回 1 の前に行うメタな整理）

## 背景

- 研究全体のメタな整理は、回 1（手跡の机上の確かめ・11-19〜21、遅くとも 11-23）の後に行う予定だった（`.steering/_handoff/next-session-gse-research-meta-after-run1.md`）。
- 11-17 に議題 1b の先行の確かめ S-EA を 2 巡まで終えた（枝 `docs/expression-audit-literature`・`docs/literature/20261117-expression-audit-precedent.md`）。一般の形（表示から推せることを測り、表示を縛る）には先行があり、差として書けるのは 3 点（漏れの対象を系の判断に置く・判断を返さない表現に返さなさの検査を足す・系の判断と表現の検査を同じ観測と道具で行う）に限られ、どれも「見つからなかった」水準。
- 2026-11-18 研究者の選択: 回 1 の結果に左右されない議題（1b と 2）だけを回 1 の前に決める。回 1 を「表現の監査の最初の例」と呼ぶなら、その枠組みを結果を見る前に固める方が後付けと言われにくい。

## ゴール

- 議題 1b（地図を表現の文法にするかの採否・差の 3 点の書き方・道具の設計に表現の監査を足すか・作品の候補の扱い）と議題 2（測定の研究と HCI の系の使い分け）を決め、`decisions.md` に残す。
- 決めたことに合わせて、research-positioning と ADR の改訂の案（反映はしない）を書く。

## スコープ

### 含むもの
- 議題 1b・2 の判断（AskUserQuestion で 1 問ずつ・推奨と理由つき）
- /reimagine で 1b の案を伏せて組み直した案と比べる
- research-positioning・ADR の改訂の案

### 含まないもの
- 議題 3〜6（L0・読める所の量・MhD・律速）。回 1 の後に回す
- research-positioning・ADR の本文への反映（承認の後に別に行う）
- 作品の制作・道具の実装
- 回 1 の結果を読むこと

## 受け入れ条件

- [ ] 議題 1b と 2 の各論点に、採用・理由・却下案が decisions.md にある
- [ ] 回 1 の前に固めた枠組み（回 1 を何の例と呼ぶか）が、回 1 の結果を見ずに書かれ、コミットの時刻が回 1 より前にある
- [ ] 改訂の案が、反映先の節を名指しして書かれている
- [ ] /cross-review（Codex を含む）を通す

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-research-meta-after-run1.md` 議題 1・1b・2
- 枝 `docs/expression-audit-literature` の `docs/literature/20261117-expression-audit-precedent.md`
- `docs/research-positioning.md` §1.1〜1.2・ADR-054・ADR-048・ADR-051
- `.steering/20261116-three-checks-tool-design/`（PR #424）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 議題 1b は研究の物語の設計判断で、11-17 の案に引きずられずに別の組み立てと比べるため（研究者の選択・2026-11-18）
