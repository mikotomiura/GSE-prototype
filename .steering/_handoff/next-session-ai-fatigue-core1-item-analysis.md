# 引き継ぎ: 核 1 を磨く —— AI 疲労の尺度の項目の内容分析（動機の低下を直接問う項目の有無と対象）

作成 2026-10-14（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。AskUserQuestion には推奨と理由を添える。

## 0. 始め方

worktree `/Users/johnd/GSE-prototype-af-core1`（ブランチ `docs/ai-fatigue-core1-item-analysis`・`docs/ai-fatigue-motivation-claims` から切った）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-core1-item-analysis.md を読んで、/start-task でタスクを立て、§3 の問いを grill で確定してから §4 の分析を始めて。C の中での扱いと DB の研究者に渡すかは研究者が決める。
```

- `.idea/` は版管理の外なので worktree には無い。読むときは `/Users/johnd/GSE-prototype/.idea/20261005-motivation-fatigue-reentry-surface.md` を開く。
- 前のセッションで取得した PDF・テキスト（job の scratchpad）は消える。必要なら §6 の URL から取り直す。
- 核 2 の引き継ぎ（`next-session-ai-fatigue-core2-discriminant.md`）とは別のタスク。並行してよいが、`docs/references.md` の採番が衝突するので、両方で出典を足すときは片方を先に main へ入れてから、もう片方を取り込んで採番する。

## 1. 前のタスクで分かったこと（一次は各ファイル）

- タスク: `.steering/20261014-ai-fatigue-motivation-claims/`（summary.md・decisions.md 判断 1〜6）。カード: `docs/literature/20261014-ai-fatigue-motivation-discriminant.md`（S-AF2・[P485]–[P497]）。
- 核 1 の元の形「AI 疲労と呼ばれているものの中身の少なからぬ部分は、動機（投資を続ける意思）の低下である」は、今の手がかりでは支えられない。
  - 代表的な尺度 Lau et al. 2026 [P362]（前刷り [P485]・最終の 15 項目は前刷りの Table 1・p.18）には、作業・勉強への動機の低下を直接問う項目が無い。行動の因子（Behavioural avoidance and disengagement）は AI を避ける項目。
  - ただし得点の成分は未検証。直接問わなくても得点が動機の低下を映す可能性は残る。同じ論文の研究 3（N = 290）は MFI の reduced motivation を同じ人で測ったが、AI 疲労との相関は MFI の合成値（r = .59）でしか報告していない（p.21・p.37）。公開データ [P486] は合計点だけ。
  - 1 標本では AI 疲労（4 項目・Kim et al. 2023 の改変とされる）と学習動機の HTMT = 0.10 [P488]。
  - 質的研究 [P487] の「動機の離脱」は AI への依存と自信の低下。
  - 一般の疲労では「疲労の自己報告に動機（apathy）が混ざる」は既知 [P489] [P490]。
- 研究者の決定（判断 3）: 核 1 は単独の研究にしない。主張を「AI 疲労の尺度ごとに、動機の低下を直接問う項目の有無と対象（作業 / AI / 真偽の判断）が違う。代表的な尺度には作業への動機の低下を直接問う項目が無い（得点の成分は未検証）」に直し、項目の内容分析を C の構想の材料として DB の研究者に示す（提案）。C の中での扱いは DB の研究者とユーザーが決める。
- C とは: AI 疲労 DB の作業の記号で、測定論の論文（提案書 v2 §6.3・Q10 で DB の研究者が「共同で進める」と答えた）。提案書 §6.1 の M4（回避・苛立ち・無力感・関与の低下が同じ「疲労」の得点に入る）を「何への動機・関与か」に分けて広げる位置づけになる（判断 6）。

## 2. このタスクのゴール（案・grill で確定する）

公開の文献だけから、AI 疲労（と隣の構成概念）の尺度の項目を集め、各項目が動機・関与の低下を直接問うか、問うならその対象は何かをコード化した表を作る。結果は C の材料の案として、ユーザーが DB の研究者に示すかを決める。

## 3. grill で確かめたい問い（Claude の案）

1. 対象の尺度の範囲: AI 疲労だけか、生成 AI のテクノストレス・AI 燃え尽き・AI exhaustion まで入れるか。比べる側（ZEF [P437]・MFI・SNS 疲労・画面疲労）を参照として入れるか。
2. 尺度の集め方: S-AF2 で見つかったものから始めるか、系統的に探すか（OpenAlex の題名検索 "AI fatigue" 2025 年以降 248 件ほか・S-AF2 カードの検証状態）。DB の研究者の DB の一次研究と重なる。DB の判定・34 件の写し・追加候補の表は使わない（公開の論文の本文から項目を取る）。この線引きでよいか。
3. コードブック: 「動機・関与の低下を直接問う」の判定基準と、対象の区分（作業・勉強／AI の利用／AI の情報・真偽の判断／その他）。MFI reduced motivation・ZEF motivational を基準の例に使うか。
4. コード化する人: ユーザーが判定者になるか。Claude の予備のコード化を、DB の作業と同じく「AI の予備判定」として分けて載せるか。一致を測るなら 2 人目は誰か（研究者の判断）。
5. 置き場所と形: `.steering/` のタスクに置くか、`experiments/` に置くか（`reproducibility-discipline`）。表の形式（CSV / xlsx）。
6. 項目の文言の引用と尺度の著作権: 論文・C で項目を逐語で載せてよいか（尺度ごとに一次で確かめる）。
7. 付随: Lau et al. の著者に、研究 3 の MFI 下位尺度との相関を求めるか（外部への連絡・送るのはユーザー・前のタスクで「後で決める」）。

## 4. 分析の骨格（案）

1. 尺度の一覧を作る（書誌・項目の出典の頁・項目数・下位尺度・項目の入手の可否）。項目が本文・付録・補足資料に無い尺度は「項目未入手」として分ける。
2. コードブックを先に書いて固定する（判定の例と境界の例を含める）。
3. 項目ごとにコード化する（逐語・判定・対象・根拠）。Claude の予備判定とユーザーの判定を列で分ける。
4. 集計: 尺度ごとに「動機・関与の低下を直接問う項目の数と対象」。
5. 限界: 項目の内容は得点の成分を示さない（得点の成分は相関・因子のデータが要る）。

## 5. 守ること

- AI 疲労を GSE が検出・診断する、とは書かない。AI 疲労を HMM の状態や打鍵からの推定の対象に足さない。
- 尺度を無検証で短縮・改変しない。尺度の使用許諾は使う前に一次で確かめる。
- DB の研究者の判断に属すること（C の中での扱い・著者・データの扱い・判定者 2）を、ユーザーに決めさせない・Claude が決めない。「研究者の決定待ち」と書く。
- GSE の設計の話を、DB の研究者に渡すものに混ぜない。
- 出典は `citation-ssot`（append-only）。断定に使う一次はメインが開く。サブエージェントは Sonnet・入れ子禁止・締切を書く。
- `git add -A`・`git add <dir>` を使わない。PR は研究者が確かめてから（push だけで止める）。

## 6. 一次資料

- `.steering/20261014-ai-fatigue-motivation-claims/`（summary.md・decisions.md）
- `docs/literature/20261014-ai-fatigue-motivation-discriminant.md`・`docs/literature/20261005-motivation-fatigue-reentry-surface.md`
- `.steering/20261002-ai-fatigue-v2/proposal/proposal-v2.md` §6（M1〜M7・論文の構想）
- `.steering/20261001-ai-fatigue-34-screening/measurement-issues.md`（M4 の元の記述）
- Lau et al. 前刷り: OSF API `https://api.osf.io/v2/preprints/kp7zs_v1/` → primary_file（`https://osf.io/download/695f334390930483cfdbc7b8/`）・Table 1 は p.18
- Alwahaishi & Ahmed 2026（AI 疲労 4 項目の出典 Kim et al. 2023 を本文で確かめる）: Europe PMC `PMC13290586`
- Miranda et al. 2026: arXiv:2605.23123
