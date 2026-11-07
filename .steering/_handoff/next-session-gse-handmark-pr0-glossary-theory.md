# 引き継ぎ —— 手跡 PR 0 の残り: glossary「手跡」・理論 §1.4・文献 [P485]〜[P554] を main へ

> 作成: 2026-11-08（`.steering/20261108-handmark-to-main-plan/`）。ADR-050・ADR-051・README・地図 R10 は、計画のタスクの PR（枝 `docs/handmark-to-main-plan`）で入る。この引き継ぎは、その残りの文書だけを扱う（ADR-048 Migration 2・ADR-051 Migration 1）。コードは変えない。

## 入口の文

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-handmark-pr0-glossary-theory.md を読んで、手跡の文書（glossary・理論 §1.4・文献）を main に入れる作業を /start-task から始めて。
```

## 何をするか

1. 枝 `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）の `docs/glossary.md` の「手跡」の項を、main の `docs/glossary.md` に持ち込む。
   - ADR-048 D2 を反映する。許すのは行為の性質だけで、系の判断は許した以上に読めないこと。
   - ADR-050・ADR-051 を参照する。
2. 枝の `docs/theory/measurement-terminating-practice-portraiture.md` の §1.4 と、関わる節（測り方・反証・限界）を main の同じ文書に持ち込む。
   - main の版との差分を先に見る。枝は main より古い。
   - ADR-048 D2 を反映する。
3. 文献: 枝が足した [P485]〜[P554] のうち、持ち込む本文が引くものを main の `docs/references.md` に同じ番号で足す（`citation-ssot`）。
   - 2026-11-08 の時点で、main の P は [P484] で止まっている。V は、枝と main で同じ行だった（V290・V295・V298 で照合した）。
   - 足す前に、main で P485 以降が使われていないかを grep で確かめ直す。DOI の重なりも確かめる（名前空間を横断する重複の節）。
   - 使わない番号を飛ばすか、全部を足すかは研究者に聞く。番号は恒久 ID なので、飛ばしても後で足せる。
4. 枝の `docs/adr/ADR-040-handmark-input-not-recorded.md` の冒頭に「main で ADR-050 に振り直した」という注を足すかを、研究者に聞く。枝へのコミットになる。

## 守ること

- `citation-ssot`・`verify-before-claiming`（長い一次を 1 節だけ読んで代表させない）。
- `docs/glossary.md` の禁止用語（「不便益 HCI である」「段階的介入」など）に当たらないかを見る。
- 完了時は code-reviewer と /cross-review（Codex を加える）。push・PR は研究者に確かめてから。docs だけの PR は `[skip ci]` にできる（memory: feedback-push-only-no-pr-during-runs）。
