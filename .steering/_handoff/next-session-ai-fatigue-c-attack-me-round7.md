# 引き継ぎ: C（TRACE）—— 登録の前の attack-me round 7 → 登録の日

作成 2026-10-20（Mac）。`next-session-ai-fatigue-c-after-coauthor-reply.md` を置き換える（あちらの §2.1〜2.3 は判断 69〜71 で済んだ）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。未決を完了報告に並べない。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない（判断 61・round 6 の verdict のメインの誤り）。査読者に渡す前に、渡す文を登録版の本文で確かめる。

## 始め方

研究の物は `~/TRACE`（https://github.com/mikotomiura/TRACE・非公開・main は `059664b`）。検討の記録は worktree
`/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`・`0d5e9b33`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は `decisions.md` の 71 まで）。

```
.steering/_handoff/next-session-ai-fatigue-c-attack-me-round7.md を読んで、§2 から進めて。
```

## 1. いまの状態（判断 69〜71 の後）

- 共著者（Yuusuke Harada・Hiroshima University・ORCID 0009-0006-7252-5115）が全部を引き受けた（選別の 2 人目・本体の集合の符号化の全部・草稿を読む）。登録版は 0.19（`~/TRACE/registration-en.md`）、外枠は 10 版、草稿の状態の注記は 0.19・10 版にそろえてある。
- 道具の宿題（合意できない記録・監査の推定・共著者の符号化の順）は済み。検査はすべて緑（`check_screening`・`make_dummy`・`check_validation_cases`・`check_coding_book`〔`--mutate` 21/21〕・`check_synthesis_mutants` 8/8・符号化の様式の作り直しは差分なし・草稿の組版はエラー 0）。/cross-review は 2 巡済み（判断 70）。
- Drive の草稿 3 つは今日の版に置き換え済み。案内は研究者の手直し（「0. 概要」・2 文の削除）を残し、古い 1 文だけ直した（判断 71）。
- 研究者の決定（2026-10-20）: 登録の前に attack-me の round 7 を回し、その後に登録する。

## 2. 次にやること（この順）

### 2.1 attack-me round 7（登録の凍結の前）

`.claude/skills/attack-me/SKILL.md` を Read してから始める（査読者 3 人＋意図の監査役・4 本とも Opus の `paper-reviewer`・指摘はメインが一次で裏取り）。`subagent-delegation` の契約（model の明示・範囲と禁止事項・締切）も守る。記録は `attack-me/prereg-c-registration/round-7/`。前の round の形（`round-6/` の `panel.md`・`brief-R*.md`・`carryover-*.md`・`context-A.md`・`context-B.md`・`verdict.md`）にならう。

- 起点: round 6 の指摘を直した版は GSE の `e8cd4efe`（判断 31・登録版 0.11）の `.steering/20261017-ai-fatigue-c-outline/registration-en.md`。対象: TRACE `059664b` の `registration-en.md`（0.19）。その後 TRACE へ移った（判断 53）ので、差分はリポジトリをまたいで作る（`git -C /Users/johnd/GSE-prototype-af-c show e8cd4efe:<path>` と TRACE の版を diff）。
- ⚠️ 差分は小さくない。語数は 12,751 → 18,082 で、diff の行は 227。0.11 の後に入ったもの: 確かめの検索と確かめの標本 300 件（判断 38〜42）、選別の形の作り替え（人 2 人・AI は段 1 の網・段 1 の 2 割と 80%・監査・合意できない記録・判断 54〜59・67〜70）、符号化の 2 人目が全部（判断 45・9〔manuscript 側〕）、コードブック第 2 版の改訂と反例集（判断 58・64・65）、C6c・C7 (ii) をデザインで分けて問題の型を 3 区分に（判断 50）。差分だけで回すか、全文を読ませて差分を重く見るかを研究者に聞く（推奨: 全文＋差分を重く見る。差分が全体の 4 割を超え、round 6 の監査役も「登録版は差分と grep の行だけ」読んだことを限界に挙げている）。
- 査読者の立場は round 6 と同じ 3 人（R1・R2・R3）でよいかを研究者に聞く。round 1〜6 の接地の本文は `round-1/tmp/sources/` にある。新しく入った選別の形（人 2 人と AI の網・監査）には、その立場で接地できる論文が手元にあるか確かめる（無ければ足すかを聞く。実在の個人を名乗らせない）。
- 添付で変わったもの（査読者の読んでよい一覧に入れるか決める）: `registration-attachments/ai-screening/instructions.md`（AI の網の本文・題は「AI screener」のまま・判断 67 で変えていない）、`registration-attachments/validation-cases/`（反例集・キー・所見）、`codebook-c2b-en.md`（第 2 版・10-19 の改訂）、`registration-attachments/coverage/`、`manuscript/outline.md`（10 版）、`manuscript/draft/main.tex`。
- carryover: round 6 の残った穴 4 つ（E5 と Q7 の衝突・2 度目の改訂を逸脱と書く・取り直しと束の隙間・感度分析 5 の時点）が、その後の版でどうなったかを各査読者に渡す。感度分析 5 は判断 67 で外した。carryover には指摘の見出しだけでなく本文と扱いを渡す（round 6 で R1・R3 が注記した）。
- 判定（accept / minor / major / reject）と直す順を出し、採否は研究者が決める。直したら検査を全部走らせ、/cross-review（判断 56 のやり方）をかける。

### 2.2 登録の日

`registration-day.md` のとおり。前の日までに残っているのは 6（判定者 1 の DB を Excel で閉じてから `update_trace_db.py` で作り直し、段 2・3 の『最終』に「合意できない」が出ることを確かめる）だけ。当日（メイン）は 2〜10（選別の順の照合・Python の版・検査の全部・添付 3 と GSRR-25・`hash_attachments.py` と SHA-256・版 1.0 と **[at registration]** を 0 件に〔今は登録版に 9 か所・外枠に 1 か所〕・体裁の検査と組版・`mode --set two-human`・コミットと push）。当日（研究者）は OSF への写しと添付を上げる。識別子と日付が来たら登録版・外枠・草稿に書く。登録が済んだら、共著者に段 1 を始めてよいと知らせるのは研究者。

## 3. 守ること

- 登録の前に判定を始めない（第一著者・AI・共著者のどれも）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo（GSE-prototype も TRACE も）や査読者に渡すファイルに写さない。確かめの検索をやり直さない。
- 査読の結果は研究の証拠ではない（attack-me）。採否は研究者。
- `git add -A` を使わない。PR は研究者が確かめてから（push で止める）。
- Drive の共有の設定と GitHub の公開設定は、研究者の確認なしに変えない。Drive の文書を上書きする前に、研究者の手直しが入っていないか比べる（判断 71 で実際に入っていた）。
