# まとめの引き継ぎ: 段 1 の事前登録の凍結の前に、申告・Mh-D の入力・残りの値を一つの流れにし、構想を直してからスライドを作り直す

作成: 2026-11-26（`.steering/20261126-gse-concept-field-companion/` の後・研究者の依頼）。このメモは順番と門を決める入口で、各作業の中身は下の個別の引き継ぎにある。

## なぜ一つにするか

進行中の事前登録の作業（枝 `docs/stage1-prereg-values-and-stop-rule`・worktree `/Users/johnd/GSE-prototype-prereg-values`・PR 未作成）は、申告の扱いと推定器の入力を値として決めている。A3（詰まりの定義は Q3 の stuck だけ）、A4（遅れの上限・無回答）、B1〜B6（申告と停滞の対応・回答の操作の除外など）、E8（表の特徴の基本の一覧・リズムの特徴の検討は凍結の前に残す）がそれにあたる。
同じ日に決めた 2 本の見直しは、どちらもこの値に直接かかる。

- 申告の聞き方（割り込み）とラベルとしての質（判断 14）。聞き方を変えると A〜B の前提が変わる。
- Mh-D の入力（判断 13）。S1-E8 そのものである。

事前登録は凍結の後に変えられない。だから、この 2 本は凍結の前に結論を出し、事前登録の作業と同じ流れに入れる。

## 順番と門

### 段 A: 凍結の前（3 本を並べ、凍結を最後に置く）

| 筋 | 入口の引き継ぎ | 置き場 | 機械 |
|---|---|---|---|
| A-1 事前登録の残りの値と凍結の前提 | `.steering/_handoff/next-session-gse-stage1-prereg-freeze-prereqs.md` | worktree `/Users/johnd/GSE-prototype-prereg-values`（既存） | Mac |
| A-2 申告の聞き方とラベルの質 | `.steering/_handoff/next-session-gse-probe-asking-and-label-quality.md` | 新しい worktree（A-1 と同じチェックアウトを使わない・memory の parallel-sessions-share-checkout） | Mac |
| A-3 Mh-D の入力の候補と記録の確かめ | `.steering/_handoff/next-session-gse-mhd-input-candidates.md` | 新しい worktree | Mac。Windows の端末での記録の確かめは G-GEAR に任せる |

門（凍結してよい条件）:
1. A-2 の結論（3 名の版に入れる／段 1 の後にする）を研究者が決めている。入れるなら、A-1 の A〜B の値をその形に合わせ直している。3 名の同意文書（11-14 承認）の改訂の要否を確かめている。
2. A-3 の候補のうち S1-E8 に入れるものを研究者が決め、A-1 の E8 に入っている。リズムの特徴の検討（A-1 の判断 34）もこの中で終えている。3 名の端末で打鍵以外の行が記録されることを確かめている。
3. A-1 の tasklist の凍結の前提が全部済み、attack-me（Codex を加える）を通している。

A-2 と A-3 は A-1 と並行で進めてよい。凍結は A-1 のセッションが最後に行う。A-2・A-3 の結論は、A-1 の decisions.md に判断として写す。

### 段 B: 経年変化の先行の調べ（段 A と並行でよい）

- 使われた跡を見せる表現（edit wear / read wear の系譜など）、暦で姿が変わる同居者に近い先行、溜まる表現の漏れを測った先行。
- `/literature-review` で 1 ラウンド。references.md にある文献は番号だけ挙げさせる（memory の feedback-literature-skip-known-refs）。
- 結果は `.steering/20261126-gse-concept-field-companion/design.md` §4・§6 に返す。

### 段 C: 全体の構想を直す（段 A の凍結の後）

- `design.md`（場は描かない約束の総体・手と同居者・二つの時計・裏は 3 つの検査）に、段 A と段 B の結論を入れる。
- 判断 7 の別タスクを片付ける。Nudge の面の削除、EH3 の割り当ての削除（段 1 の後）、使っていない Proposed の ADR への印、Dashboard を裏方に縮める設計、ADR-046 の 3 状態の名前の除去、`docs/agent-shared.md` のリンクハブの直し。
- この形を ADR にするかを研究者に聞く（`design.md` §6 の 9）。
- 一次の文書（`docs/research-positioning.md`・`docs/architecture/gse-design-map.md`）を、新しい形に合わせる。

### 段 D: スライドを作り直してから整理する（段 C の後）

- 対象は `docs/slides/project-overview/` の 5 本（`GSE_project_overview`・`_detail`・`_findings`・`_tech`・`GSE_handmark_design`）。作り方は `build_*.py`・`figs*.py`・`tpl.pptx`・`README.md`。
- 先に、5 本の役割を新しい構想で決め直す。統合・削除も含める（整理）。そのうえで作り直す。
- 図を主にする（memory の feedback-slides-figure-first）。足すスライドにも毎回図を伴わせる。図の文字は本文より小さくしない。組んだ画像を自分で見て確かめてから報告する。
- 場は描かない（判断 9）。スライドでも、場を一枚の絵として描かず、約束と、場の中に現れるもの（手・同居者・仕組みの面）で示す。

## 守ること

- 本人の記録の中身・個々の申告・日ごとの割付を出力しない。記録の集計を Codex に送らない。
- 段 1 の途中で HMM を手で動かさない（ADR-044 D1）。本人の段 1 は今の形で終える（ADR-043 D9）。
- gse-next（`~/Desktop/S1_実施用_macOS/`）を止めない。
- push と PR は研究者に確かめてから。決めることは AskUserQuestion で、日本語で、推奨と理由を添えて聞く。

## 入口の文

段 A（どれか 1 本ずつ別セッションで）:

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-integrated-before-freeze-then-slides.md を読んで、段 A の A-2（申告の聞き方とラベルの質）から始めて。
```

（A-1・A-3 も同じ文の「A-2」を差し替えて使う。）
