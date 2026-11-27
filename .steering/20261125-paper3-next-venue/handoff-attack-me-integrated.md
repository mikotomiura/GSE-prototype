# 次のセッション: S14 を入れた論文 3 に attack-me をかける

> 作成: 2026-11-27。worktree `~/GSE-prototype-paper3`、枝 `docs/gse-paper3-per-person-learning`（fbef3f75 まで push 済み・PR なし）。研究者の選択（次のタスク = 論文 3 の attack-me）。

## 入口の文

```
~/GSE-prototype-paper3 の .steering/20261125-paper3-next-venue/handoff-attack-me-integrated.md を読んで、その手順を行って。
```

## ここまで

- 判断 5（fbef3f75）で、重みを見る目 v2 の実データの結果を補足 S14 と限界の第 1 項の 1 文に入れた。一次は枝 `exp/gse-per-person-weight-eye`（worktree `~/GSE-prototype-weight-eye`）の v2 の `conditions.md` 追記 1（凍結 b0f5821a）と notes の「D7 実データ」・判断 53。
- 投稿先は TMLR で、年内は投稿できない（判断 4）。前の attack-me は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/`（round 7 まで。UMUAI に出した版）。

## 手順

1. `.claude/skills/attack-me/SKILL.md` と `paper-write` の Step 7 を読む。stage は `revision`（UMUAI の不採録の後の改訂）。置き場は `20261125-paper3-next-venue/attack-me/revision-integrated/round-1/`。
2. 編集者の役 E は TMLR の一次で接地する（`paper-write/venue-fit.md` の TMLR の逐語）。UMUAI の不採録の理由（"lack sufficient depth"）を E に渡し、S14 と書き直し v2 がそれに応えたかを判定させる。
3. Codex を加える（memory: attack-me と /cross-review は毎回 Codex）。Codex には既知の未決を渡す（memory: Codex には既知の未決を渡す）。既知の未決は次のとおり。
   - TMLR の形式への移しと匿名化は未着手。
   - 公開 repo に v2 を入れるかは未決。
   - S14 は探索で、読みの文は凍結済み。数と文は変えられない（変えるなら新しい版として凍結する）。
4. 特に見てほしい点を査読者に渡す（結論は渡さない）。
   - 頻度だけの基準線が CoAuthor で E1 と同じくらい強い（T = 0.94〜0.99）。追記 1 で差の文を書かないと決めてある。この扱いが読者に十分か。
   - 本文の 1 文（限界の第 1 項）が、確認の主張に読まれないか。
   - S14 が「深さが足りない」への答えとして働くか。それとも別の論点を増やしただけか。
5. 指摘は一次で裏取りし、直しは paper-write の Step 4 の最後の規則に従う（足すより移す）。S14 の数と文は凍結の範囲なので直さない。限界の文と配置だけを直す。
6. minor が 2 回続いたら閉じる（memory: attack-me は判定の推移を見てから回す）。寄与・一般化の major が 2 回続いたら、書き方で閉じず、研究の形を変えるかを研究者に聞く（memory: 論文 1・2 の不採録）。
7. attack-me を閉じた後に、`paper-write/venue-fit.md` を当て直す（判断 4 の約束）。前の 11 誌はやり直さず、S14 で開いた新しい方向の候補を 5 誌前後に絞って、同じ門（無料・AI の方針・範囲の一句・最近の近い論文）に当てる。新しい方向は 2 つある。評価の方法論（比べの相手しだいで得が消える・見分けと予測の得は別の問い。例: DMLR）と、打鍵の識別との接点（T-BIOM は論文 B で範囲の外と返されたので門 1 を厳しく見る）。範囲の一句は、E の判定を受けた後の一言で当てる。結果は TMLR と並べて研究者に AskUserQuestion で聞く（研究者が 2026-11-27 に「TMLR 以外も一応探す」と希望）。
8. 記録は判断 6（attack-me）と判断 7（venue-fit の当て直し）として `decisions.md` に書き、push だけする（PR は作らない）。

## してはいけないこと

- 実データの書き手ごとの値と打鍵の中身を外部の LLM（Codex を含む）に送らない。送るのは原稿の tex と補足だけ。
- 追記 1 の読みの文を、attack-me の指摘で書き換えない。
