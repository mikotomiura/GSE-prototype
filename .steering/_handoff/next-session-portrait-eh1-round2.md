# 引き継ぎ — 肖像の EH1 第 2 回（新しい固定）

> 作成: 2026-10-09（まとめのセッション）。研究者の決定は `.steering/20261009-portrait-eh1-eh2/decisions.md` 判断 9（AskUserQuestion・推奨どおり「EH1 第 2 回を新しい固定で」）。
> ⚠️ このメモを一次資料にしない。結果の値は `experiments/20261009-portrait-eh1/notes.md`、解釈は判断 9・10・11、親への還元は `.steering/20261005-portrait-invitation-constraints/decisions.md` 判断 12。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh1-round2.md を読んで、肖像の EH1 第 2 回の設計を始めてください。
/start-task で新しいタスクを切り、worktree はブランチ docs/ で作ってください（feature/ は CI が self-hosted で走る）。
```

## §1 なぜ第 2 回か（判断 9 の要約）

- E1-3 は v1・v2 とも全組が判定不能。v2 では材料（`p_stuck`・F の水準）が打鍵の有無を超えて停滞を当てた（探索で +0.17〜+0.24）。それでも、既定の scheduler を通る陽性対照 PC2 は拾えなかった → 時計で更新する形に漏れが無いとは、まだ言えない。
- U-4 は「不在の中では更新しない」（`recent`）を第一候補にした。ただし固定の外の探索なので、E1-3・E1-2 をまだ当てていない。
- 仮の文法はどれも「揺らぎに強く、経路を写す」を満たさなかった。

## §2 第 2 回の設計で決めること（研究者に聞く・推奨と理由を添える）

1. **既定の scheduler のもとで働く陽性対照**（PC2 の作り直し）。候補: 材料の情報を形に強く写す版（更新ごとに全体の色相を `p_stuck` で大きく動かす・累積させない）。⚠️ 陽性対照が働かないと、また全組が判定不能になる。
2. **E1-3 の攻撃者の窓**: 60 s の窓に加えて、更新の間隔に揃えた窓（「前の更新から今までが停滞だったか」）を足すか（notes の限界）。v2 の hgb で B < A になった件（形の特徴を足すと検査器が力を失う）への手当て。
3. **`recent` を固定の組に入れる**: E1-3（更新の時刻が「直前に打っていた」を写す量）・E1-2（回数と打鍵の時間の相関）・E1-6。帯ごとの更新の発生率も記述に足す（判断 10 X4・判断 11）。
4. **揺らしに強く経路を写す文法**への作り直し（ordinal・keyed は ±50 ms で崩れ、raw は v2 で経路を写さない）。
5. world は v2 を主にするか（v1 は天井で E1-3 の問いが立たない）。
6. 基準の値は第 1 回と同じにするか。⚠️ 結果の前に固定する（親の判断 8）。

## §2.5 どの機械で回すか（研究者の確認・2026-10-09）

- **本番は Windows の G-GEAR**（第 1 回と同じ機械・16 コア）。EH1 は OS の入力 API を通らないので Mac では回さない（判断 5 の補記）。
- Surface Pro 8（RAM 8 GB）は `--jobs` を渡せるようにしても遅いので、本番には使わない。
- ⚠️ 本番は 1 world で約 14 分、16 コアを使い切る。計測の run・self-hosted CI と重ならない時間に回す。設計（基準の固定）はどの機械でもよい。

## §3 計器の直し（第 1 回で見つかった・判断 9）

- `run.sh` が Windows で `gse-replay` に `.exe` を補わない（notes 判断 W1）。
- `run.sh` から `checks.py --jobs` を渡せない（RAM 8 GB で `MemoryError`・notes 判断 W2）。
- 探索の `scripts/explore_material_info.py` を、固定の検査に上げるか。

## §4 並行して残っているもの

- EH2: 直した Swift は未コンパイル。Mac で `swiftc -typecheck` → `--quick`、それから notes-macos の 3 ケース。手の確認（仮想デスクトップ / Spaces・画面共有）は両 OS とも未実施で、研究者がその場で回す。
- E1-8: none を主・seed を EH3 の比較に（判断 9）。EH3 の設計で使う。
- PR: 計測の run の後。merge の順は S-MR → 親 → `docs/portrait-eh1-eh2`。

## §5 守ること

- 応答は日本語。AskUserQuestion には推奨と理由を添える。
- `git add` はファイルを名指しする。main checkout（`C:\GSE-prototype`）の git には触らない。
- 生成した NDJSON と `work-*/` はコミットせず、外部の LLM にも送らない。結果の PNG も Codex に送らない。
- Codex の台帳は、回す前に 3 つを足して確かめる: origin/main、このブランチ、main checkout。2026-10-09 は合算で上限を超えた（`.codex/budget.json` のコメント）。
- 「検査した範囲で見つからなかった」より強く書かない。主張の格は EH0。
