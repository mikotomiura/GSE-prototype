# 引き継ぎ —— 手跡を main に入れる（地図 R10）

> **使用済み（2026-11-08）**: このメモから `.steering/20261108-handmark-to-main-plan/` を始め、計画は ADR-051 にまとめた。次の入口は `next-session-gse-handmark-pr1-late-slice.md`（PR 1）・`next-session-gse-handmark-pr0-glossary-theory.md`（PR 0 の残り）・`next-session-gse-handmark-pr2-7-list.md`・`next-session-gse-handmark-windows.md`。

> 作成: 2026-11-08（Mac のセッション）。研究者が「新しいセッションで始める」を選んだ。このメモは入口で、一次ではない。

## 入口の文

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-handmark-to-main.md を読んで、手跡を main に入れる計画を /start-task から始めて。
```

## 何をするか

段 1 の後期（手跡を日ごとに無作為で表示・ADR-043 D4・ADR-048）のために、手跡を main に入れる。後期の始まりまでに要る（地図 `docs/architecture/gse-design-map.md` §3.1 の R10）。研究者本人の段 1（R5）は 2026-11-08 0:56 に前期（手跡なし）で始まった（`next-session-gse-after-m5-part3.md` §14）。

研究者の決定（2026-11-08）:
- 段 1 にメディア表現を混ぜるのは今の計画どおり（前期は手跡なし、後期に日ごとの無作為で手跡）。
- 確認の段は本人を除く 3 名ほど（ADR-043 D3 の 2〜4 名の中）。手跡を合わせた段 1 で行う。始める時期は R4・R6′・R7・R8（倫理審査）しだい。

## 材料の在り処（どれも main に無い）

- 試作の実装: 枝 `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`・最後は 351f94e5・2026-10-30）。main より 308 コミット遅れ、main に無い差分は 111 ファイル・約 1.2 万行（`git diff --stat origin/main...origin/spike/handmark-stage`）。記録は `.steering/20261016-handmark-stage-spike/`・`20261021-handmark-stage-pointer/`・`20261030-handmark-edge-strip-impl/`、引き継ぎは `.steering/_handoff/next-session-handmark-stage-followups.md` ほか。
- 設計の記録: 枝 `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）の `.steering/20261015-tangibility-design/`（判断 9・20・28）・`20261016-handmark-expression-design/`（判断 2・3）・`20261017-handmark-why-interesting/`・`20261020-handmark-multi-input/`・`20261021-handmark-input-adr/`・`20261023-handmark-window-boundary/`・`20261029-handmark-edge-strip-design/`。
- 波紋の小面の試作は閉じた（枝 `spike/handmark-a-surface`・判断 7・試視で見えにくかった）。
- 決定: main の ADR-043 D4・ADR-048 D1〜D3（決めずに残すもの 1〜5）・ADR-025 D1。

## 計画で決めること（研究者に 1 問ずつ聞く）

1. 試作のうち本番に入れる部分と捨てる部分（背景の層・下の縁の帯・ポインタの入力・トレイの試作の項目）。
2. ADR-048 D2 の漏れの確かめ方（系の判断を、速さ・リズム・止まりの量だけから当てる場合と手跡の見た目から当てる場合を比べる。許す上回りの幅・区間推定・データの分け方を先に決める）。
3. 後期の日ごとの無作為の割り付けと記録（割付の上の開始日・初めて表示した日・累積の表示の量を分けて記録・ADR-043 D4）。前期の長さを人ごとにずらす仕組み。
4. tangibility 枝の ADR-040（手跡の入力を記録しない・Proposed）を main の次の番号（ADR-050 以降）に振り直すか、新しい ADR にまとめ直すか。
5. 日の終わりの問いの動機づけ・同期・共存の項目（ADR-048 D3・尺度の文は文献のラウンドの後・決めずに残すもの 1）と、段 1 の既存の日の終わりの問い（`day_question`）との関係。
6. PR の割り方（試作の rebase より、main の上に本番の形で書き直すほうが安全かもしれない。`/reimagine` の対象）。

## 守ること

- 返答・問い・記録は日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。
- 実装は `/start-task` から。設計判断は Opus。完了時は code-reviewer と /cross-review（Codex を加える）。
- UI を変えたら画面を見るまで完了にしない。研究者の本人の試しの gse-next（`/Users/johnd/GSE-S1-self/S1_実施用_macOS/gse-next.app`・ログイン時に自動で立ち上がる）が動いている間は、同じ名前のプロセスに AX で押さない（memory: jxa-same-name-process-ax-crosstalk）。
- Codex に O1・段 1 の記録の本文を送らない。台帳は 2026-11-08 に 24,321 / 1 回。
- この Mac の空きは約 8.1 GiB で、self-hosted の macOS の検査が止まる 8 GiB に近い。CI を起こす PR の前に空きを作る。
- push・PR は研究者に確かめてから。
