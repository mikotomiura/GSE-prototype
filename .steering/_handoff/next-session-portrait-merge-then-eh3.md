# 引き継ぎ — 肖像の 4 本のブランチを merge し、EH3 の事前登録を始める

> 作成: 2026-10-10（EH1 第 2 回の結果を読んだセッション）。研究者の決定: 次は「A → B」＝ 先に 4 本を merge し、その後 main の上で EH3 の事前登録を始める（`.steering/20261009-portrait-eh1-round2/decisions.md` 判断 6〜8 と、その後の AskUserQuestion）。
> このメモを一次資料にしない。結果は `experiments/20261009-portrait-eh1-round2/notes.md`、決定は同 decisions 判断 6、親への還元は `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 13。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-merge-then-eh3.md を読んで、肖像の 4 本のブランチを順に merge し、終わったら EH3 の事前登録の準備を始めてください。
worktree は C:\wt\portrait-eh1-round2（ブランチ docs/portrait-eh1-round2）が最新の積み重ねの先端です。
```

## §1 いまの状態（2026-10-10 に確かめた）

- 4 本は 1 列に積み重なっている（下が上の祖先）。どれも push だけで、PR はまだ無い。

| 順 | ブランチ | main より先 | 中身 |
|---|---|---|---|
| 1 | `docs/motivation-reentry-survey`（S-MR） | 4 | サーヴェイ |
| 2 | `docs/portrait-invitation-constraints`（親） | 11 | 台帳・判断 1〜11 |
| 3 | `docs/portrait-eh1-eh2` | 29 | EH1 第 1 回・EH2・親の判断 12 |
| 4 | `docs/portrait-eh1-round2` | 41（先端） | EH1 第 2 回・親の判断 13 |

- 4 本とも main から **279 コミット遅れている**。共有の文書（`docs/references.md`・`docs/literature/_index.md`・`.codex/budget.json` など）で衝突しうる。
- `.codex/budget.json` はブランチごとに記帳されている。merge では合算する（memory「Codex ledger split by branch」）。
- worktree: `C:\wt\portrait-invitation-constraints`（親）・`C:\wt\portrait-eh1-round2`（先端）。ほかの 2 本の worktree の有無は確かめていない。

## §2 やること（順に）

1. **計測の run と self-hosted CI が重ならないことを確かめる**。PR を出すと Mac と G-GEAR の runner で CI が走る。走っているかは推測せず、runners の API などで確かめる（memory「No PR during measurement」「CI status」）。
2. **merge の進め方を研究者に聞く**（AskUserQuestion・推奨と理由を添える）。候補:
   - (a) 下から 1 本ずつ PR → CI 緑 → merge（4 回）。記録の単位は保たれるが、CI が 4 回走る。
   - (b) 先端（`docs/portrait-eh1-round2`）の PR を 1 本だけ出し、4 本ぶんを一度に merge する。CI は 1 回で済むが、PR の単位が大きい。
   - どちらでも、先に main を取り込んで衝突を解く必要がある。取り込みは、積み重ねの一番下から順に行う。
3. merge の後、main の CI を確かめる（`git-workflow` ルール 6・`/finish-task` Step 5）。
4. **EH3 の事前登録の準備**（新しいタスク・`/start-task` から）。持ち込むもの:
   - E1-3 の限界: 実際の組は判定不能（2 回）。既定・`recent` の経路は神託で狭い（目安・証明ではない）。親の判断 8 は満たしていないと明記したうえで進む、という研究者の判断（判断 6 の決定 3・親の判断 13）。
   - U-4 は `recent` で確定した。閉じない点として、次の 3 つを持ち込む。
     - 更新の時刻が「直前の 1 分まで打っていた」を写す。
     - E1-4 が構成上検査できない。
     - 不在の 2 割弱で 1 回更新され、その変化の大きさと不在の長さの関係は測っていない。
   - 形は `raw` か `lattice` か（見本は `experiments/20261009-portrait-eh1-round2/results/v2/samples/`）。研究者が見本で 1 つに絞るか、EH3 で比べる。
   - E1-8 は none が主、seed が比較（親の判断 12）。
   - 親の判断 8 の M-1〜M-5、判断 4・6・7 の制約。U-2・U-3 は未決のまま。
   - ADR をいつ起こすか（EH3 の事前登録の前か後か）は決めていない。親の判断 2 は「ADR は EH1 の後」。

## §3 守ること

- 応答は日本語。AskUserQuestion には推奨と理由を添える。★・⚠️ を多用しない。
- `git add` はファイルを名指しする。main checkout（`C:\GSE-prototype`）の git には触らない。並行セッションのブランチの未コミットの変更がある。
- 生成した NDJSON・`work-*/`・PNG を Codex や外部の LLM に送らない。
- EH0 の主張の格: 「検査した範囲で見つからなかった」まで。合成した停滞は打鍵の統計の型で、認知の状態ではない。

## §4 片付け（任意・研究者の判断）

- `experiments/20261009-portrait-eh1-round2/work-*/`（コミットしない）と `C:/wt/_eh1r2-*.log`・`_eh1r2-*.start`（本番のログ）。
