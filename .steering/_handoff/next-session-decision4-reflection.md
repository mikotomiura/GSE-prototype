# 次セッション — 研究者判断バッチ 6（判断 4）の帰結を SSOT へ反映する

> 作成: 2026-09-20。前段: `.steering/_handoff/next-session-theory-stage3-followups.md` §2 の 10 件を研究者に聞き、
> ★ 回答を `.steering/20260919-theory-ssot-promotion/decisions.md` **判断 4** に記録した（★ 10 件とも回答済み・**反映は未着手**）。
> ★ 本タスクは**反映だけ**を行う。新しい裁定はしない（★ 反映の途中で規定の無い点が出たら止まって研究者に聞く）。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-decision4-reflection.md を読んで、判断 4 の帰結を反映してください。
まず /start-task で作業単位を作り（task 名の例: decision4-reflection）、§2 の作業を順に行い、§4 の受け入れ条件を満たしたら /finish-task（/cross-review を含む）まで進めてください。
設計判断は Opus、機械的な置換は Sonnet。サブエージェントは実装・操作は sonnet、レビュー・企画は opus で起動する（model を毎回明示・操作系は入れ子にしない）。
応答は日本語。ブランチ docs/adr-030-stall-onset-definition のまま、main へ switch しない。git add -A / git add <dir> は使わない。
```

## §1 決まったこと（★ 一次は判断 4 の表。ここは索引）

| # | 回答 | 反映の要否 |
|---|---|---|
| 1 | ADR-034 を **Accepted** | ★ 要（§2-1） |
| 2 | ADR-033 は **ADR-008 と一緒に** Accepted（ADR 本文どおり） | 不要 |
| 3 | ADR-035 D1 は**このまま**（例外なし） | 不要 |
| 4 | ADR-035 の未決 3 つは **Physical Anchor の実装設計で決める** | ★ 要（§2-5・引き継ぎへ移すだけ） |
| 5 | Nudge の時期の統制は **見直し候補に載せる** | ★ 要（§2-4） |
| 6 | G1 の途中離脱者の数え方は **収集開始の前提条件にする** | ★ 要（§2-2） |
| 7 | 「誤受容」などを **「誤採用」「採用率」へ改名** | ★ 要（§2-3） |
| 8 | ADR-033 D6 の検査を **EH1 の支持に数える** | ★ 要（§2-4） |
| 9 | 理論名は **S3 を回してから決める** | 本タスクでは不要（§5） |
| 10 | 補足の検索は **差分を外部の文書に書く前に行う** | 本タスクでは不要（§5） |

## §2 作業（★ 上から順に。各項は反映先を一次で開いてから直す）

### 2-1. ★ ADR-034 を Accepted にする（判断 4 #1）

- `docs/adr/ADR-034-g1-o1-parallel-conduct.md` の**ステータス行**を Accepted にする（★ 先例 ADR-029: `- **ステータス**: ★★★ **Accepted**（2026-09-13・研究者判断）`）。★ 判断の一次（`decisions.md` 判断 4 #1）を括弧に入れる。
  - ⚠️ 本文（D1 の律速 3「本 ADR の Accepted」・Consequences 5・Migration 1）は**書き換えない**。★ 状態の欄（Consequences 5 の「状態」）に日付つきで「✅ 2026-09-20 に Accepted」を足すのは先例あり（Consequences 6 を 2026-09-19 に閉じた書き方）。
- `docs/adr/README.md`（Migration 1）:
  - ADR-034 の行: ステータスを Accepted へ。
  - ADR-014 の行: 「⚠️★★★ 判断 1 の『時間軸で解く』・… は ADR-034（Proposed）が上書きする予定」→ **上書きした**（2026-09-20）へ。右端の時期の欄「G1 の収集完了後」も合わせる。
  - ★ ADR-014 の本文には注記を入れない（★ 先例: ADR-029 が ADR-016 D4 を上書きしたとき、ADR-016 の本文には触れず README の行で示した —— 2026-09-20 に grep で確認）。⚠️ 迷ったら先例を一次で確かめる。
- `docs/o1-roster-operations.md` §5 の冒頭（`:83` 付近）「⚠️★★★ ADR-034 が Accepted になってから効く。それまでは…」→ 効いている状態へ（日付つき）。
- ★ **古い記述を探す**: `grep -rn "収集完了" docs/ .claude/skills/` で「O1 の開始 = G1 の収集完了後」「G1 の収集完了まで配布しない」を拾う。2026-09-20 時点で見つけたもの:
  - `docs/glossary.md:88`（O1 の実験名の行「日付は作る日＝ G1 の収集完了後」）
  - `docs/architecture/workspace-behavior-observation.md:393` / `:456`（「G1 の収集完了まで配布しない」）
  - ⚠️ ADR-034 D3 が置き換えたのは「**`--mode g1` の配布物を G1 の最初の配布と別のタグで作らない**」であって、「G1 の被験者へ新ビルドを配らない」は**維持**である（★ 旧文を消さずに、何が変わったかを書く）。
  - ⚠️ 被験者向け文書（`participant-setup-guide.md`・同意文書）は**変えない**（ADR-034「影響を受ける文書」）。`wbs-verification-halfyear.md` は次の WBS 改訂に回す（同）。
- ★ memory `project_g1_build_distribution_boundary.md`（「ADR-014 判断 4 は未修正」）を更新する。

### 2-2. ★ G1 の事前登録 第 19 版（判断 4 #6）

- `experiments/20260801-controlled-friction-task/preregistration.md` の先頭に **第 19 版の改訂履歴**を足す（★ 第 18 版の書き方に揃える）。
  - ★ 中身: 「収集開始の前提条件」（第 18 版で 1〜6）に **7 を足す** ——「**G1 を途中でやめた人の途中までの記録を確証解析でどう数えるか**（§3.6 の同意撤回に当たるか・n に数えるか・補充するか）を**収集開始の前に**決めて記録する」。
  - ⚠️ **中身（数え方そのもの）は本タスクで決めない**（★ 研究者判断が要る。★ 前提条件として立てるだけ）。
  - ⚠️★★★ **§3 は凍結**。`§3.1`〜`§3.6` に 1 文字も触らない。★ `experiments/20260801-controlled-friction-task/check_frozen_sections.py` を回して緑を確かめる（★ 第 18 版から機械検査つき）。★ 「変えていないもの」の節を第 18 版と同じ形で書く。
  - ★ 一次の事実（2026-09-20 確認）: §3.6 逐語「❌ **被験者を事後に除外しない**（除外規則: 事前に宣言した同意撤回のみ）」・§2.4-7 の「補充しない」は**適格性ゲート（§2.9）で外れた被験者**の規則・`consent.md` §5 は「途中でやめられます」と「削除を求められます」を別の項に分ける。
- `docs/adr/ADR-034` の Consequences「代償・残る障害」7 の状態の欄を「G1 の収集開始の前提条件 7（事前登録 第 19 版）で決める」へ（日付つき）。

### 2-3. ★ 「誤受容」ほかの改名（判断 4 #7）—— ★ 機械的な置換は Sonnet

- 置換: 「誤受容」→「**誤採用**」／「受容率（AI の提案を採った割合）」→「**採用率**」／「正しい提案の受容」→「**正しい提案の採用**」。
- ★ 対象（契約・理論の本文）:
  - `.steering/20260916-gse-theory-operationalization-review/` の **measurement-dictionary.md**・**eval-ncc-analysis-contract.md**・**eval-ncc-dag.md**・**gr-h4-h9-h11-h12-falsification-table.md**・**core-proposition-coverage-matrix.md**
  - `docs/theory/generative-relinquishment-theory.md`（6 か所）・`docs/theory/theory-architecture-and-roadmap.md`（3 か所）
- ⚠️ 変えないもの: 変数名 `accepted_wrong`・**過去の判断記録**（各 `decisions.md` / `requirement.md` / `design.md` / `tasklist.md` / `next-task.md` / `theory-propagation-audit.md` / `_handoff/*`）・`.idea/`（追跡外）。
  - ⚠️ `theory-propagation-audit.md` と `design.md` を記録と見るか契約と見るかは、開いて確かめる（★ 定義を持つ行があれば契約として扱う）。
- ★ 注記を更新: 測定辞書 `:20`・分析契約 `:13` の「★ 改名するかは研究者判断・未決」→「2026-09-20 に改名した（判断 4 #7）」。
- ⚠️ 置換の前後で `grep -c` を取り、件数を `.steering/` に記録する。★ 「受容」だけの行（SSOT の「受容」＝ ADR-018 D5・ADR-033 D3 (b) の「受容率」）を**巻き込まない**（★ 語の境界を目で確かめる）。
- ★ `docs/glossary.md` に「誤採用」を載せるかは判断する（★ 載せるなら「SSOT の『受容』とは別の構成概念」を定義に入れる）。

### 2-4. ★ 評価契約と見直し候補（判断 4 #5 / #8）

- **#8**: `.steering/20260916-gse-theory-operationalization-review/core-cs-evaluation-contract.md` §5.0 の `:98`「⚠️ それを EH1 の支持に数えるか … は未決」を閉じる → 「2026-09-20 研究者判断: 数える（証拠の種類は『実装の検査』と明記する。⚠️ 検査は `OnlineUpdater` の実装まで存在しない）」。★ 理由の 2 点（テスト内の陽性対照は配布物にも被験者にも届かない ／ §3 の EH1 の定義が「replay / log / test による監査」）を添える。
- **#5**: Nudge の時期（と有無）を本人が統制する経路を**見直し候補（未決）**として登録する。
  - ⚠️ `intervention-design` Skill に「見直し候補」の節は**まだ無い**（2026-09-20 grep）。★ 置き場所を決める。候補: `docs/architecture/intervention-decision-engine.md` に未決の節を足し、`intervention-design` Skill から 1 行で参照する。
  - ★ 書く中身: [P386] §2 の警告は現行の Nudge に当たる（RP §3 `:252`）／ ADR-035 は招待だけが対象 ／ **Nudge を被験者に出す研究（Phase 2 の AB/BA・Phase 3 の MRT）を設計する前に決める** ／ 現在の G1（起動モード第 1 週で介入を止める・`protocol.md`）と O1（判断 O1-5・`lib.rs`）では Nudge を出さない。

### 2-5. ★ 引き継ぎの整理（判断 4 #4 ほか）

- `.steering/_handoff/next-session-theory-stage3-followups.md` の §2 冒頭の注記を「反映済み」へ更新し、§3（実装フェーズへ渡すもの）に **ADR-035 の未決 3 つ**（① 事後の透明性 ② 止めた瞬間の表示中の招待 `PS-Q10` ②③ ③ opt-in 率での数え方）を足す。

## §3 ⚠️ 守ること（★ CLAUDE.md・memory から）

- ★ **`/start-task` から始める**。`.steering/[YYYYMMDD]-[task]/` に requirement / design / tasklist を置き、判断は decisions.md。
- ★ `verify-before-claiming` を起動する（★ ステータスの変更・古い記述の書き換えは「事実を断定する」操作）。**反映先は一次を開いてから直す**。
- ⚠️ **ADR の本文は書き換えない**（ステータス行・状態の欄・日付つきの注記だけ）。**事前登録は凍結**（改訂履歴の側で扱う）。
- ⚠️ 「先行研究が存在しない」と書かない。禁止用語（`docs/glossary.md`）。引用に触れたら `check_citations.py` を「違反なし」まで回す（★ 1 回で全件出ない）。
- ★ **完了時に `/cross-review` は必須**（★ 2 巡: 1 巡目 = 自文書と他文書の矛盾 ／ 2 巡目 = 自分が足した規則の境界条件）。★ `scripts/run-codex-review.sh -- <paths>` で**パスを限定**する（★ 無関係な未コミット変更で BLOCKED になる）。⚠️ Codex は repo を読めない（資料をプロンプトに貼り「シェル禁止」）。⚠️ 予算で skip したら**理由を完了報告に書く**。⚠️ `.codex/budget.json` を `git checkout --` で戻さない。
- ⚠️ `git add -A` / `git add <dir>` 禁止（★ 作業ツリーに `.worktrees/`・`tmp/` がある）。ファイルを明示して add する。
- ★ コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs: .steering/<task>/` ＋ `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`。1 コミット 1 論理単位（★ 2-1〜2-5 を分けてよい）。
- ⚠️ NDJSON 生ログ・キーストローク内容を外部 LLM に送らない。

## §4 受け入れ条件

1. ADR-034 のステータスが Accepted で、README の ADR-014 行と ADR-034 行が整合している。`o1-roster-operations.md` §5 が効いている状態になっている。
2. `grep -rn "収集完了" docs/ .claude/skills/` の各ヒットについて、直したか・直さない理由を `.steering/` に記録した。
3. 事前登録に第 19 版があり、`check_frozen_sections.py` が緑。
4. §2-3 の対象ファイルで「誤受容」が 0 件（★ 注記の中の旧名の言及を除く —— 除いた行は記録する）。変えない記録ファイルの件数は元のまま。
5. CORE-CS §5.0 の未決が閉じ、Nudge の見直し候補が登録され、`intervention-design` Skill から辿れる。
6. `/cross-review` の 2 巡を通した（または skip の理由を書いた）。

## §5 本タスクの後（★ 2026-09-20 の相談で合意した順序の案 —— 研究者が変えてよい）

1. ★ **次: 本タスク**（判断 4 の反映・段 3 を閉じる）
2. ★ **その次: G1 / O1 の残タスクの棚卸し**（★ `/start-task` の grill で範囲を確定してから）
   - ⚠️ まず既存の引き継ぎの**状態を一次で確かめ直す**（★ どれも段 3 より古い）: `g1-o1-precollection-findings.md`（2026-09-01）・`next-session-post-adr032-approvals-and-parallel-tracks.md`（2026-09-14）・`next-session-o1-consent-secondary-use.md`（2026-09-13）。
   - 既知の論点（★ 状態は未確認）: G1 の収集開始の前提条件 1〜7（★ 7 は本タスクで足す・中身は研究者判断）／ ADR-034 Migration 3（G1 の最初の配布のタグの記録先）／ O1: ADR-031 / ADR-032 の Accepted（同意文書 §3 の改訂 = 研究者承認）・`check-o1-release-readiness.sh` の緑・ADR-034 Migration 6（O1 の事前登録に「G1 のログを入力に取ったら止まる」検査）。
   - ⚠️★ **ブランチ `docs/adr-030-stall-onset-definition` は main より 132 コミット先行している**（2026-09-20 実測）。★ 配布物はリリースタグ（`v*` の push）から作るので、G1 / O1 の配布の前に main へのマージの計画が要る。
3. ★ **文献ラウンド（1 本にまとめる）** —— ★ G1 / O1 を塞がないので、その後でよい。⚠️ **外部の文書（論文・未踏の提出物）で差分を主張する締切が先に来るなら前に出す**（判断 4 #10 の発火条件）。
   - (a) SR で Semantic Scholar の取得に失敗した **7 本**の再実行（C1-b / C3-b / C5-a / C5-b / **C6-a / C6-b** / C7-c・429・`search-log.md`）。★ 特に C6-a / b は差分の候補 (i)（ADR-033 D2 と D3 の組）の網に直結する。★ API キーの有無を確かめる（無ければ間隔を空ける）。
   - (b) 差分の候補（未検証）4 つと組み合わせの**補足の検索**（判断 4 #10）。★ 先に検索式を SR の `deviations.md` に protocol の改訂として記録する。★ 入力の候補: C7-0608（STOIC）。(i) は D2（応答を控える根拠に使う）を述べた先行を探す式が要る。
   - (c) **S3**（生成芸術論の過程・終端・撤退）→ 理論名を決める（判断 4 #9）。
   - ★ `/literature-review` で回し、サーヴェイはサブエージェント並列・`references.md` への append だけメインが直列・**毎ラウンド即コミット**。
4. 任意: Codex の予算が戻ったら、SSOT の本体（ADR-033 / 034 / 035・RP §4）を Codex で 1 巡（段 3 でほぼ全単位 skip したため）。
