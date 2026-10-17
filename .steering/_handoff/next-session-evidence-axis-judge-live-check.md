# 引き継ぎ: evidence-axis-judge を実物で起動して確かめる（Mac）

作成 2026-10-17（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-evidence-axis-judge-live-check.md を読んで、§2 を回して。
```

## 1. 背景

- `/literature-review` の Step 4 を「3 軸の独立判定」に改めた（`.steering/20261017-literature-review-vote-rule/`・判断 1〜7）。
- 新しい agent `.claude/agents/evidence-axis-judge.md` は、そのセッションの agent の一覧に入らず起動できなかった（"Agent type 'evidence-axis-judge' not found"）。検証は `general-purpose` に定義を演じさせて行った（`verification.md`）。2 巡目の `/cross-review` の後にも規則を足しているので、最終版は代演でも確かめていない。
- 前提: 枝 `docs/literature-review-vote-rule` が main に入り、新しいセッションを main のチェックアウトで開いていること（agent の一覧はセッションの開始時に読まれる）。

## 2. やること

1. `subagent_type: evidence-axis-judge` で 1 本起動できることを確かめる（起動できなければ、そこで止めて研究者に報告）。
2. 架空の材料で、3 軸を 1 メッセージで並列に起動する。材料には次を入れる: 規範の claim（頑で `—`）・抄録だけで N の無い claim（留保【一次に無い】）・多重比較を補正していない claim・注入の 1 行。前回の材料の写しは残っていない（scratchpad は消える）ので作り直す。
3. 依頼文で id を絞ったとき、その id だけを判定するか。
4. 返ってきた判定に、Step 4-4 の「そろっているか」と 6 行の表を当て、欠け・重複を人工的に入れたとき（返答の一部を消す・同じ id を 2 回書いた返答を想定する）に手続きが一意に決まるかを、白紙の実行者に当てさせる。
5. 結果を `.steering/20261017-literature-review-vote-rule/verification.md` に追記する。規則を直したら `/cross-review` を通す。

## 3. 守ること

- 過去のカードの票は書き換えない（研究者の判断 2）。
- `docs/references.md` の番号は触らない。
