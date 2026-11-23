# handmark-to-main-plan —— 手跡を main に入れる計画（地図 R10）

## 背景

- 段 1 の後期では、手跡を日ごとに無作為で表示する（ADR-043 D4・ADR-048 D1〜D3）。後期が始まるまでに、手跡を main に入れておく必要がある（`docs/architecture/gse-design-map.md` §3.1 の R10）。
- 研究者本人の段 1（R5）は、2026-11-08 0:56 に前期（手跡なし）で始まった。
- 手跡の材料は、どれも main に無い。
  - 試作の実装: 枝 `spike/handmark-stage`（351f94e5）。main より 308 コミット遅れており、main に無い差分は 111 ファイル・+11,923 行ある。
  - 設計の記録: 枝 `docs/tangibility-design`。
- tangibility 枝の ADR-040（手跡の入力を記録しない・Proposed）は、main の ADR-040（`ADR-040-nudge-not-in-core.md`）と番号がぶつかる。
- 研究者の決定（2026-11-08）:
  - 段 1 にメディア表現を混ぜる。前期は手跡なし、後期は日ごとの無作為で手跡を出す。
  - 確認の段は本人を除く 3 名ほどで、手跡を合わせた段 1 で行う。

## ゴール

手跡を main に入れる計画を確定させる。実装は、計画で決めた PR ごとに別のタスクで行う。確定したかどうかは、次の 6 つが記録に揃っていることで判定する。

1. 試作のうち本番に入れる部分と捨てる部分（背景の層・下の縁の帯・ポインタの入力・トレイの試作の項目）
2. ADR-048 D2 の漏れの確かめ方（比べる 2 つの条件、許す上回りの幅、区間推定、データの分け方）
3. 後期の日ごとの無作為の割り付けと記録（割付の上の開始日・初めて表示した日・累積の表示の量）、前期の長さを人ごとにずらす仕組み
4. tangibility 枝の ADR-040 の扱い（ADR-050 以降に振り直すか、新しい ADR にまとめ直すか）
5. 日の終わりの問い（ADR-048 D3）と、既存の `day_question` との関係
6. PR の割り方（試作を rebase するか、main の上に本番の形で書き直すか）

## スコープ

### 含むもの
- `design.md`・`decisions.md`（判断を 1 つずつ研究者に確かめる）
- 新しい ADR（入力を記録しないこと・入れる範囲・漏れの確かめ方・割り付け。束ね方は判断 4 で決める）
- 地図 `docs/architecture/gse-design-map.md` の R10 の更新
- 後に続く実装のタスクへの引き継ぎ

### 含まないもの
- コードの実装と試作の rebase（`src-tauri/`・`src/` を触らない。試作の枝は読むだけ）
- 段 1 の事前登録の本文の改訂（`docs/preregistration-stage1.md` 節 F・S-F3。ADR-048 Migration 3）。計画で決めた値をそこへ渡す
- 動機づけ・同期・共存の尺度の文と、そのための文献のラウンド（ADR-048 決めずに残すもの 1）
- 層 A（スマホ）と段 2（ADR-048 決めずに残すもの 3・4）

## 受け入れ条件

- [ ] ゴールの 1〜6 がそれぞれ、`decisions.md` に「決定 / 理由 / 却下案」の形で記録されている（研究者が AskUserQuestion で選んだもの）
- [ ] 新しい ADR が `docs/adr/` にあり、`docs/adr/README.md` の一覧に載っている
- [ ] 地図の R10 に、計画の在り処と PR の並びが書かれている
- [ ] 後に続く実装の PR ごとの引き継ぎが `.steering/_handoff/` にある
- [ ] code-reviewer と /cross-review（Codex を含む）を通している。Codex に O1・段 1 の記録の本文を送っていない

## 関連ドキュメント

- `.steering/_handoff/next-session-gse-handmark-to-main.md`（入口）
- `docs/adr/ADR-043-next-study-stage1-c4-collection.md` D4、`docs/adr/ADR-048-handmark-as-counterpart-of-abstention.md`、ADR-025 D1
- `docs/architecture/gse-design-map.md` §3.1 R10
- 枝 `spike/handmark-stage` と `docs/tangibility-design` の `.steering/`（引き継ぎ文書の「材料の在り処」）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 決めること 6（PR の割り方。試作の rebase か、main の上での書き直しか）は複数の案が成り立ち、最良の案が自明でない。引き継ぎも対象に挙げている。design.md の初めの案を承認した後、実装のタスクに入る前に回す（2026-11-08 研究者）。
- 作業場所: worktree `/Users/johnd/GSE-prototype-handmark-plan`（枝 `docs/handmark-to-main-plan`・origin/main b9010318 から）。入口の引き継ぎ文書もここに写した。
