# 引き継ぎ — EH3 の実装（招待の PC 面・肖像の組み込み・記録・配布）と凍結までの段取り

> 作成: 2026-10-11（EH3 の事前登録の稿と実装の要件を書いたセッション・G-GEAR）。
> このメモは一次資料にしない。一次は次のとおり。
> - 決定: `.steering/20261011-portrait-eh3-prereg/decisions.md` 判断 1〜4、親 `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 1〜16、台帳 `constraints-ledger.md`。
> - 稿: `experiments/20261011-portrait-eh3/preregistration-draft.md`（未凍結）。
> - 実装の要件: `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`（R-I・R-P・R-L・R-D と未決 R-1〜R-9）。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh3-implementation.md を読んで、EH3 の実装タスクを始めてください。
docs/portrait-eh3-prereg が main に merge 済みであることを先に確かめてください。
```

## §1 いまの状態

- EH3 の外枠は研究者が決めた（子の判断 1・2）。
  - 肖像と招待を両方測る。
  - 参加者の PC で、空・D・A の 3 ブロック × 5 稼働日。A の中で none と seed を日ごとに交互にする。
  - 招待は全ブロックで同じ規則で、契機は推定の停滞。Nudge は出さない。
  - 肖像は壁紙だけ。参加者は 6〜12 人で、O1・G1 とは分ける。
  - 判断 7 の閾値は人数で決める。再着手の遅れは既存の再開で置き換える。ADR は EH3 の後に起こす。
- 稿は `/cross-review` 2 巡を通した（子の判断 3・4）。凍結はまだしない。
- 研究者の決めた記録の案（判断 1 #7）は、判断 3 で狭めた。壁紙を書き込んだ時刻と招待の解除の時刻を記録しない。理由は、肖像への本人の操作が時刻から読めるからである（台帳 肖13 からの導出）。

## §2 次にやること（順に）

1. **実装のタスクを `/start-task` で始める**（`/add-feature`）。要件の R-I・R-P・R-L・R-D をそのまま requirement の材料にする。
   - 未決 R-1（ADR-035 D1 の ④ と「Nudge を出さず招待だけ」の両立）と R-8（同意を opt-in とみなすか）は、研究者に推奨と理由を添えて聞く。ADR-035 は Proposed で、Migration は「実装時に見直し Accepted にする」としているので、実装のタスクが ADR-035 を見直す場になる。
   - 招待の値（R-2: T・上限・間隔・契機の閾値・U-3）は、根拠を書いて決める。
   - `analysis/` に OS API を入れない。壁紙は OS 依存の層に置く（`architecture-rules`）。
   - ADR-026 M11 の検査は、招待面の最初のコードと同じコミットで入れる。
   - schema を変えるので、`/finish-task` の schema parity check が走る。
2. **研究者が見本で `raw` / `lattice` を 1 つに選ぶ**（F-1）。見本は EH1 の `render_e18.py` 系で作れる。実装と並行してよい。
3. **罪悪感の尺度の小さなサーヴェイ**（F-6・`/literature-review`）と、反発の尺度の選択。実装と並行してよい。
4. 稿の §10 の F-1〜F-13 を埋める。
5. 凍結の直前に attack-me（stage `prereg`）と `/cross-review` 2 巡を回す。attack-me で稿を Codex に送るときは `--preview` を通し、研究者の OK を取る（attack-me の規則）。

## §3 守ること

- 応答は日本語にする。★・⚠️ は多用しない。
- `git add` はファイルを名指しする。main checkout（`C:\GSE-prototype`）の git には触らない。
- 生のログ・NDJSON を Codex や外部の LLM に送らない。
- 研究者の決定（子の判断 1・2・親の判断 1〜16）の中身を変えない。変えるべき理由が出たら、研究者に聞く。
- EH1 第 2〜5 回の判定と読み方は書き換えない。

## §4 片付け（任意・研究者の判断）

- worktree `C:\wt\portrait-eh3-prereg`（merge の後）。
- 古い引き継ぎ `next-session-portrait-eh3-prereg.md` と `next-session-portrait-merge-then-eh3.md` は、本タスクで消化した。
