# 引き継ぎ — 肖像と招待の設計制約の台帳と決定 ＋ 小さなサーヴェイ（S-PI）

> 作成: 2026-10-05（前のセッションのコンテキストが長くなったため、研究者の指示で区切った）。
> ⚠️ **このメモを一次資料にしない。** 決定は `.steering/20261005-portrait-invitation-constraints/decisions.md`、要件は同 `requirement.md`、手順は同 `design.md` を開き直す。数値と逐語は、文献カードと原本で確かめ直す。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-invitation-constraints.md を読んで、
タスク .steering/20261005-portrait-invitation-constraints/ を続けてください。
作業は worktree C:/wt/portrait-invitation-constraints（ブランチ docs/portrait-invitation-constraints）で行います。
grill は済んでいます。次は「1. 台帳」と「2. 小さなサーヴェイ」を並行で始めてください。
```

## §1 どこまで済んだか

- **前のタスク S-MR**（`.steering/20261005-motivation-reentry-survey/`・ブランチ `docs/motivation-reentry-survey`・最終 `ed261ab6`・push 済み・**PR は計測の run の後**）: サーヴェイ 1 ラウンド・`/cross-review` 2 巡（40 件すべて採用）・研究者の方針「核を今後の GSE 研究で検証する」（判断 6）。カードは `docs/literature/20261005-motivation-fatigue-reentry-surface.md`、新規登録は [P437]–[P453]。
- **本タスク**: grill だけ済んだ（requirement.md・design.md・tasklist.md・decisions.md 判断 1〜3）。ブランチ `docs/portrait-invitation-constraints` は `docs/motivation-reentry-survey` から切った。**サーヴェイの subagent はまだ 1 本も投げていない。**

## §2 研究者が決めたこと（decisions.md 判断 1〜3 の要旨）

| 論点 | 決定 |
|---|---|
| 招待と肖像 | **役割で分ける**: 肖像 ＝ ワクワク（評価されない驚き・**状態を表さない**・壁紙＋小面）／ 招待 ＝ 身体回帰への誘い（別の小さな要素・ADR-026 / 035） |
| タンジブル | **まず PC だけで作る**。机上の物体は第 2 候補。画面の質感は本物の触覚ではないと明記 |
| 範囲 | **台帳 ＋ 決定 ＋ 小さなサーヴェイ**（実装・ADR・RP・expression-channel.md は範囲外） |
| サーヴェイの問い | **情報回避**・**無視の罪悪感**・**促しへの反発**（3 angle・10〜15 ソース） |
| 置き場所 | `.steering/` と `.idea/`。ADR に上げるのは EH1 の後 |
| /reimagine | 使わない |
| 追加 | **物体の必要性**も決定項目に入れる（研究者の逐語「物体自体の必要性も併せて議論しよう」）。議論は既存の材料から |

## §3 これからやること（tasklist.md の順）

1. **台帳**（`constraints-ledger.md`）: 肖像・招待・物体の 3 区分。各行に出典（ADR の D 番号・`[Pn]`・ファイル:行）と格（Accepted ／ Proposed ／ 設計案 ／ 証拠）。⚠️ ADR は決定の節を**全部**読む（025 / 026 / 027 / 033 / 035・021 D4）。入力の一覧は design.md。
2. **小さなサーヴェイ S-PI**（`/literature-review`）: 3 angle を Sonnet で並列に投げる。angle の中身は design.md。名前空間は現象 = `P`・尺度 = `V`。
3. **決定**: ラベルの方針・無視の扱い・物体の必要性を、推奨と理由を添えて研究者に聞く（AskUserQuestion）。→ EH1 の設計の制約と EH3 で測るもの（回避・罪悪感・反発）を導く。→ `.idea/` に還元。用語が固まったら glossary に追記。
4. **閉じる**: コミット・push（**PR は出さない**）・`/cross-review` 2 巡。

## §4 前のセッションで分かった事実（決定の材料・一次で確かめ直すこと）

- **[P362]（AI Fatigue Scale・AF001）の 15 項目に、作業・勉強への動機の低下を問う項目は無い**。4 因子は cognitive overload ／ emotional strain ／ behavioural avoidance and disengagement ／ physical and sensory exhaustion。「離脱」は **AI からの**離脱。項目は `C:\Users\johnd\Downloads\ai-fatigue-fulltext\AF001\ffbe473e_af001_p6.png`（Table 1）。
- **用語の訂正**: 介入を「非随伴」と呼ぶのは不正確（形は打鍵に随伴する）。**「予期しない驚き」（上位の語）／「予期しない・評価を含まない驚き」（介入案の条件）**と呼ぶ。慣れると「予期された・取り組みに随伴する帰結」になるリスク（[P99] の engagement-contingent は自由選択で d = −0.40・自己報告で −0.15・係争中 [P107]）。
- **物体の材料**: [P98]（ノート PC の横の e-ink の端末・36 週・N = 1・減少への負の情動・他者の「それ引用数？」・著者「評価の圧力を距離を置ける場所へ運ぶ」）／ [P101]（UbiFit・表示ありで活動を「維持」）／ [P102]（同じ表現の反復は 3 週で 43.5% 減・「減る」こと自体が否定的に読まれる）。いずれも `docs/literature/20260815-portable-ambient-object-and-activity-coupling.md`。再査定 §3・§4 案 C・§7（物体は第 2 候補・「物理だから良い」は失格）。
- **罪悪感の既存の証拠**: [V75] 記録をやめた後に罪悪感（活動 16.2%・お金 8.9%）。反発の尺度 [V115] [V116] は登録済み。**情報回避（ostrich）は references に 0 本。**
- **既決**: ADR-025（自分の量を返さない）・ADR-026 D3 の PC-1〜PC-12 と D4（招待面に量を置かない）・ADR-033（非再捕捉）・ADR-035（Proposed・招待の有無と時期を本人が統制）・選択の対称性（glossary）。
- **TTTF の LT**（`C:\Users\johnd\Downloads\LT_symbiotic-intelligence.pptx.txt`・研究者が話すスライド）の 15 枚目「AI の引き算」（待つ・黙る・退く／内面を断定しない／役目を終えたら消える／確かめる負担を残さない）は、肖像と招待の設計の原則として使える。⚠️ 連絡先が書いてあるので、ファイルの中身を外部に出さない。

## §5 守ること（CLAUDE.md・memory から・本タスクに効くものだけ）

- **応答は日本語**。AskUserQuestion は推奨と理由を必ず添える。
- **サブエージェント**: 渡す前に `subagent-delegation` Skill を読む。サーヴェイは `general-purpose` に `model: sonnet` を明示・**入れ子禁止**・締切 20 分・有料の本文と DB を使わない・学術 API にメールアドレスを送らない・repo を書かない（scratchpad だけ）。⚠️ **前回、WebFetch の要約を逐語として返した subagent があった** → 「逐語として書くのは原本（PDF を pypdf・Europe PMC の XML）から自分で抜いた文だけ。WebFetch の要約は『要約』と明記」と brief に書く。断定に使う一次は**メインが開いて**照合する（改行・合字・負号の落ちに注意。正規化してから探す）。
- **references.md**: append はメインが直列で。**重複は DOI で grep する**（前回、題の語で探して [P362] の重複を見落とした）。登録の直前に全ブランチ・全 worktree の末尾番号を測り直す（前回の末尾は [P453]）。`PYTHONUTF8=1 python scripts/check_citations.py` を違反なしまで繰り返す。**1 ラウンド = 1 コミット**。
- **git**: `git add -A` / ディレクトリ単位の add を使わない（ファイルを名指し）。main checkout（`C:\GSE-prototype`）は別ブランチ（`docs/ime-manuscript-outline`）の未コミット作業があるので触らない。**計測の run 中なので PR を出さず push だけ**。
- **スクリプトの書き方**: bash の heredoc に引用符やバックスラッシュを含む Python を書かない（前回 bash が止まった）→ Write でファイルにしてから実行する。python の書き戻しは `newline=''` で LF を保つ。
- **`/cross-review`**: メインが `code-reviewer`（Claude）と `bash scripts/run-codex-review.sh <base>..<head> -- <paths>`（Codex）を別々に並列起動する。範囲はコミット済み・パス限定・出力は scratchpad。2 巡（1 巡目 = 自文書・他文書の矛盾 ／ 2 巡目 = 足した規則の境界条件）。指摘は一次で裏取りしてから当てる。
- **Codex の台帳**: worktree の `.codex/budget.json` に記帳される。`git checkout --` で戻さず、修正と一緒にコミットする。2026-10-05 は S-MR のブランチで 94,209 トークン使用（日次 300,000）。⚠️ 予算ガードの hook は `C:\GSE-prototype` の台帳を読むので、worktree の記帳が映らない。
- **「0 件」「研究はゼロ」と書かない**: 「S-PI の範囲（日付・ツール・検索語）で見つからなかった」と書き、探索の範囲をカードに残す。温度の区分（確定 ／ PLAUSIBLE BUT UNPROVEN ／ 判定不能 ／ 未決）を守る。
- **AI 疲労 DB の側と混ぜない**: GSE の設計の話を、研究者（DB を作った相手）に渡す 3 点に入れない。
- **主張の格は EH0**: 「GSE が示した」と書かない。RP §1・ADR・収集の変更は研究者が別に決める。
