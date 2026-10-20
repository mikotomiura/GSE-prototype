# 引き継ぎ: C（TRACE）—— 登録の日

作成 2026-10-20（Mac）。`next-session-ai-fatigue-c-attack-me-round7.md` を置き換える（あちらの §2.1 は判断 72〜75 で済んだ）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。未決を完了報告に並べない。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない。登録版の本文で確かめる。

## 始め方

研究の物は `~/TRACE`（非公開・main は判断 75 の後のコミット。`git -C ~/TRACE log --oneline -12` で確かめる）。検討の記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は `decisions.md` の 75 まで）。

```
.steering/_handoff/next-session-ai-fatigue-c-registration-day.md を読んで、§2 から進めて。
```

## 1. いまの状態

- attack-me は round 7（全文・major）と round 8（差分・minor・再査読なし）を終えた。記録は `attack-me/prereg-c-registration/round-7/`・`round-8/`。研究者の決定は判断 72・74。
- 登録版は 0.21（`~/TRACE/registration-en.md`・約 20,800 語）、外枠は 11 版、草稿の状態の注記は 0.21・11 版。
- 主な変更（0.19 → 0.21）: 段 1 の 80% の門を群ごと／網の記録を同じ数の無作為の記録と混ぜ、群の比で配る／含めることに合意し中心だけ合意できない記録は本体に入れ中心は unresolved／E5 の連結は時間の窓の中だけ、確かめの標本の E5 は本体の RQ4 に入れない／C5 の新しい値「stated by the report, not linked」／C2b の target_from_stem／監査の 30 件を群の比で配分し群ごとに推定／締切を遅らせる上限 2027-01-31／AI の下書きは著者 2 との話し合いの後／感度分析 5（著者 2 の値）／2 人の一致が 80% 未満の符号に印（n < 5 は印なし）／別の模型は `--another-model` のときだけ有効な出力の無い束。
- 道具と検査: check_screening・make_dummy・check_validation_cases・check_coding_book（と `--mutate`）・check_synthesis_mutants（68 本）・様式の作り直し・草稿の組版。結果は判断 75 の追記（このセッションの最後の通し）。/cross-review は 4 巡（判断 73・74・75）。

## 2. 次にやること（この順）

### 2.1 前の日まで（`registration-day.md` の「前の日まで」）

- 6: 判定者 1 の DB を Excel で閉じてから `update_trace_db.py` で作り直し、段 2・3 の『最終』と『最終の中心』に「合意できない」が出ることを確かめる。
- 7: 研究者が、反例集 V03 に足した 2 項目と、key-items.csv の target_from_stem の値（新しい 2 項目と既存の 3 項目）を確かめる（AI が下書きした）。
- Drive の共著者の物（草稿の docx と PDF・案内）は 0.19 の時の版のまま。選別の形の細部（群ごとの門・混ぜる記録・中心だけの unresolved）が変わったので、置き換えるかを研究者に聞く（推奨: 置き換える。上書きの前に研究者の手直しが入っていないか比べる・判断 71）。共著者には、混ぜる記録の仕組みを知っていても構わないが、冊のどれが網の記録かは示さない。

### 2.2 当日

`registration-day.md` の「当日（メイン）」と「当日（研究者）」のとおり。版 1.0 と **[at registration]** を 0 件に（今は登録版に 9 か所）。`hash_attachments.py` は columns.md と key-items.csv・cases.md・findings.md が変わったので必ず取り直す。締切を遅らせたときの手順は `registration-day.md` の「締切を遅らせたとき」。

## 3. 守ること

- 登録の前に判定を始めない（第一著者・AI・共著者のどれも）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo（GSE-prototype も TRACE も）や査読者に渡すファイルに写さない。確かめの検索をやり直さない。
- 査読の結果は研究の証拠ではない（attack-me）。採否は研究者。
- `git add -A` を使わない。PR は研究者が確かめてから（push で止める）。TRACE の main はまだ push していない（研究者に聞いてから）。
- Drive の共有の設定と GitHub の公開設定は、研究者の確認なしに変えない。
- 研究者のメールアドレスを外のサービスに渡さない（このセッションで Unpaywall の API に付けてしまった・判断 72）。
- attack-me を閉じたら `round-1/tmp/`〜`round-8/tmp/` を消してよいかを研究者に聞く（Skill の決まり。panel.md の URL と SHA-256 から取り直せる）。
