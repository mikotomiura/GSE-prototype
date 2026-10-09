# 設計

## アプローチ

3 つの段を順に進める。決定は台帳とサーヴェイの結果を材料に、研究者に推奨と理由を添えて聞いてから記録する。

1. **台帳**（`constraints-ledger.md`）: 肖像・招待・物体の 3 区分で、既存の制約を 1 行ずつ出典つきで並べる。各行に「決まっている（ADR Accepted）／原則だけ（Proposed）／設計案（`.idea`・再査定）／証拠（文献カード）」の格を付ける。読むものは下の「入力」。⚠️ 長い一次資料を 1 節だけで代表させない（verify-before-claiming ルール 7）。ADR は決定の節を全部読む。
2. **小さなサーヴェイ**（`/literature-review`・S-PI）: 3 angle を Sonnet で並列に投げ、断定に使う一次はメインが開く。名前空間は、現象（情報回避・罪悪感・反発）は `P`、測る道具（尺度）は `V`。予算は 3 angle・10〜15 ソース。
   - **A1 情報回避**: 自分の状態・健康・成績のデータの表示を、見たくなくて避ける（ostrich effect・information avoidance・self-tracking の回避）。どんな表示の形（数値・ラベル・比較）が回避を強めるか。反証側（見せても避けない・見せた方がよい）。
   - **A2 無視の罪悪感**: 通知・促し・リマインダ・招待を無視したり断ったりしたときの罪悪感。規則で対称にしても残るか。どんな出し方が罪悪感を強める・弱めるか。反証側（罪悪感は小さい・行動を変えない）。
   - **A3 促しへの反発**: 促しへのリアクタンス。出し方（頻度・言い方・選べるか・理由を言うか）との関係。尺度は [V115] [V116] が登録済みなので、出し方との関係の一次を足す。
3. **決定**（decisions.md）: ラベルの方針・無視の扱い・物体の必要性。物体は既存の材料（[P98] [P101] [P102]・再査定 §3 / §4 案 C / §7・`.idea/20260909-physical-foreground-flip-cover-media.md`）から論点を立てる。最後に EH1 の設計の制約と EH3 で測るものを導く。

## 入力

- ADR: 025 / 026 / 027 / 033 / 035（決定の節は全部）・021 D4（招待の二値）
- 文献カード: `20260815-portable-ambient-object-and-activity-coupling.md`・`20260906-legibility-demotion-and-ambient-behavioral-evidence.md`・`20260807-self-state-externalization-and-ambient-media.md`・`20260907-pc-invitation-surface-and-peripheral-cost.md`・`20261005-motivation-fatigue-reentry-surface.md`
- 用語: `docs/glossary.md`（招待・選択の対称性・非再捕捉・返権の負荷逆説・権限・負担の二重台帳）
- 理論: `docs/theory/generative-relinquishment-theory.md`（GR-H5・GR-H9）
- 設計案: `.idea/20261005-motivation-fatigue-reentry-surface.md`・`.idea/20260909-physical-foreground-flip-cover-media.md`・再査定（main checkout の `.steering/20260921-media-expression-theory-audit/`・未追跡）

## 変更対象（worktree `C:/wt/portrait-invitation-constraints`・ブランチ `docs/portrait-invitation-constraints`・`docs/motivation-reentry-survey` から切った）

- 新規: `.steering/20261005-portrait-invitation-constraints/`（requirement / design / tasklist / decisions / constraints-ledger）
- 新規: `docs/literature/20261005-<slug>.md`（サーヴェイのカード）
- 追記: `docs/references.md`（末尾の次番号から・**DOI で重複を確かめてから**）・`docs/literature/_index.md`
- 追記（用語が固まったら）: `docs/glossary.md`
- 版管理外: `C:/GSE-prototype/.idea/20261005-motivation-fatigue-reentry-surface.md`

## 影響範囲

- `references.md` の採番は並行セッションと衝突しうる → 登録の直前に全ブランチの末尾番号を測り直す。
- 本ブランチは `docs/motivation-reentry-survey` の上にある → PR は S-MR の PR の後（計測の run の後）。

## 検証戦略

- `check_citations.py` を違反なしまで繰り返す。
- 台帳は、全行に出典があるかを目で確かめ、ADR の D 番号はファイルの見出しで照合する。
- `/cross-review` 2 巡（1 巡目 = 台帳と ADR の矛盾・自文書の矛盾 ／ 2 巡目 = 決定で足した規則の境界条件）。パス限定・出力先は scratchpad。
