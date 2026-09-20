# 重要な設計判断

> ★ 判断 1〜5 は **2026-09-20 の grill（`grilling` skill・Opus）で研究者が裁定した**。
> ⚠️ セッションの推測ではない（AskUserQuestion の回答）。

## 判断 1: 起票 10 の「境界」は**ブランチ検査**に置き、deny は多層防御に留める

- **判断日時**: 2026-09-20（★ 研究者が grill で回答）
- **背景**: ⚠️ 起票 10 は「worker が `git checkout main` で worktree 隔離を自分で外せた」実測。
  ★ `docs/loop-engineering.md` は逐語で「**この 7 件は「多層防御」であって境界ではない**」
  「**deny の件数を増やす方向で解こうとしないこと**」と書いており、
  ⚠️ deny を足すだけの対処はこの逐語と衝突する。
- **選択肢**:
  - A: ブランチ検査を**境界**にし、deny 2 件は worktree 限定の**多層防御**として足す。追跡済み `settings.json` は触らない
  - B: A ＋ 追跡済み `.claude/settings.json` の `allow` から `Bash(git *)` を外しサブコマンドを列挙する
  - C: ブランチ検査のみ（deny は増やさない）
- **採用**: **A**
- **理由**:
  - ★ 「綴りを網羅する」方向では**原理的に閉じない**（README 逐語）。★ **検知できる側**に境界を置く。
  - ⚠️ **B は worktree だけに効かせられない** —— ★ `settings.local.json` の `allow` は
    追跡済み `settings.json` と **union** であり、`allow` を worktree 内で*狭める*手段は存在しない
    （★ 2026-09-20 に一次で確認）。→ B を採ると**対話セッションの権限も同時に変わる**。
  - ★ 逆に **`deny` は worktree 限定で効かせられる**（`deny` は allow と frontmatter の**両方に優先**）。
    → ⚠️ 「allow を絞る」という起票 10 の「本筋」の意図は、**worktree 限定の deny で実質的に達成できる**。
  - ★ C は「deny の件数を増やさない」逐語には忠実だが、⚠️ **worker が checkout を実行できるまま**であり、
    未コミット変更の消失リスクが残る（★ 001 / 002 / 003 はいずれも未コミットで終わっている）。
- **トレードオフ**: ⚠️ deny は 7 → 9 件に増える。★ README の「件数を増やす方向で解こうとしない」に
  **部分的に反する**が、★ **件数で解こうとしていない**（境界はブランチ検査）ことを
  `docs/loop-engineering.md` に明記して整合させる。
- **影響範囲**: `scripts/loop-worktree-deny.sh` / `.steering/_template/loop-config.README.md`
  / `scripts/loop-worktree-deny-test.sh` / `scripts/loop-run.sh` / `docs/loop-engineering.md`
- **見直しタイミング**: ⚠️ `git -C <dir> checkout` / `git -c alias.x=checkout x` のような
  **綴り違いの迂回が実測された**とき（★ そのときも deny を増やさず、ブランチ検査が拾ったかを見る）

---

## 判断 2: ブランチ逸脱は events に記録して **`blocked`**（fail-closed・自動復帰しない）

- **判断日時**: 2026-09-20（★ 研究者が grill で回答）
- **背景**: ★ `ensure_deny` は「**検知（記録）と回復（再注入）を分ける**」という先例を持つ。
  ⚠️ ブランチも同じく「記録して `git checkout loop/<id>-issue` で戻す」型が採れる。
- **選択肢**:
  - A: events に記録して `blocked`。worktree はそのまま人に渡す
  - B: 記録して自動復帰（`git checkout`）し attempt を続行
  - C: 記録だけして `run_verify` に進む（非致命扱い）
- **採用**: **A**
- **理由**:
  - ⚠️ **B は未コミット変更を壊しうる** —— ★ checkout が失敗するか、変更を別ブランチへ持ち越す。
    ★ 起票 10 の実害が「偶然無かった」のは worker が commit **後**に checkout したからであり、
    ⚠️ 自動復帰はその偶然に依存する設計になる。
  - ⚠️ **C は別ブランチの内容を verify して緑/赤を出す**事故を残す（起票 10 の対策 2 の逐語）。
  - ★ `deny` と違い、**ブランチ逸脱は「起きてはならないこと」であって回復すべき状態ではない**。
- **トレードオフ**: ⚠️ 1 回の逸脱で issue が落ちる。★ ただし `permission_denials` と違い
  **逸脱は正常動作では起きない**（★ `_loop-config.json` の `allowed_tools` にも
  `/loop-issue` の frontmatter にも `git checkout` は入っていない）。
- **影響範囲**: `scripts/loop-run.sh` の `run_issue`
- **見直しタイミング**: ⚠️ 正常な運用で逸脱が頻発したら（★ そのときは原因が別にある）

---

## 判断 3: `permission_denials` は **events に集計 ＋ 生配列をファイル保存**

- **判断日時**: 2026-09-20（★ 研究者が grill で回答）
- **背景**: 起票 3。★ 件数だけでは「10 件」の内訳が説明できない。
- ⚠️★★★ **起票 3 の「`WORK_TMP` に保存する」は成立しない**（★ 2026-09-20 に一次で確認）:
  `scripts/loop-run.sh:298-300` が `WORK_TMP="$(mktemp -d)"` ＋ `trap cleanup_tmp EXIT` で
  **run 終了時に `rm -rf` する**。→ ★ 後から内訳を読むには**別の置き場**が要る。
- **選択肢**:
  - A: events の `detail` に tool 名の集計 ＋ 生の `permission_denials` 配列をファイル保存
  - B: events の `detail` に集計だけ（ファイルを残さない）
  - C: `claude -p` の JSON 全体を保存
- **採用**: **A**
- **理由**:
  - ★ board（`loop-status`）から**読める**のは events なので、集計はそこに要る。
  - ★ 実際の調査には **tool 入力（コマンド文字列）**が要るので、生配列も要る。
  - ⚠️ C は worker の**応答全文**を含み、6 attempt × 8 issue で数 MB 規模になりうる。
    ★ 必要なのは `permission_denials` だけである。
- **置き場**: `$TASK_DIR/_loop-artifacts/<id>-attempt<N>-denials.json`
  ⚠️ `.gitignore` に `.steering/**/_loop-artifacts/` を追加する
  （★ 既存の `.steering/**/_loop-events.jsonl` と同じ作法）。
- **トレードオフ**: ⚠️ ディスクに残る。★ ただし `permission_denials` 配列だけなので小さい。
- **影響範囲**: `scripts/loop-run.sh` / `.gitignore`
- **見直しタイミング**: ⚠️ 内訳を 1 度説明できたら、保存を続けるか判断し直す

---

## 判断 4: Status フィルタは **`blocked` だけ**外す（`## Status` 無しは回す・`done` は外さない）

- **判断日時**: 2026-09-20（★ 研究者が grill で回答）
- **背景**: 判断 26 の申し送り。★ `issue_ids()` が `## Status` を読まない。
- **選択肢**:
  - A: `blocked` のみ除外 ／ Status 無しは回す ／ `done` は除外しない
  - B: `blocked` ＋ `abandoned` を除外 ／ Status 無しは回す
  - C: B ＋ Status 無しも除外（fail-closed）
- **採用**: **A**
- **理由**:
  - ⚠️★★★ **`done` を除外してはならない** —— ★ `ALL` から外すと `deps_met()` が
    **永久に false** になり、その issue に依存する後続が「依存 issue が未完のため未実行」で
    落ちる（`loop-run.sh:440` / `:494`）。★ 完了の復元は `events` からの seed が担っている。
  - ★ Status 無しを除外すると、**新規に切った issue が黙って走らなくなる**
    （⚠️ `.steering/_template/loop-issue.md` の `## Status` 節は**見出しだけで値が空**）。
  - ★ `abandoned` は現に使われた実績が無く、⚠️ 今は増やさない（★ 必要になったら足す）。
- **`--issues` との関係**: ★ **明示指定はフィルタを適用しない**（⚠️ 警告は出す）。
  → ★ `blocked` の 004 / 006 も `--issues 004` なら回せる。
- **除外の可視化**: ★ 除外した id を **stdout のログと `_loop-run-report.md`** に出す
  （⚠️ events には出さない —— ★ events 語彙は 10 種で固定であり、
  「**実行しなかった**」は状態遷移ではない）。
- **トレードオフ**: ⚠️ `## Status` を書き忘れた `blocked` 相当の issue は走ってしまう。
- **影響範囲**: `scripts/loop-run.sh` の `issue_ids()` / `ALL` の決定 / レポート
- **見直しタイミング**: ⚠️ `abandoned` を実際に使い始めたら

---

## 判断 5: 「worker は commit してから終わる」は**文章の契約**に留める（機械強制しない）

- **判断日時**: 2026-09-20（★ 研究者が grill で回答）
- **背景**: 起票 10 の対策 3。⚠️ 001 / 002 / 003 の worker は**いずれも未コミットで終わった**。
- **選択肢**:
  - A: `.claude/commands/loop-issue.md` に明記する（文章のみ）
  - B: A ＋ attempt 終了時に `git status --porcelain` が空でなければ events に 1 行残す
  - C: 含めない（別タスク）
- **採用**: **A**
- **理由**:
  - ★ **LLM の守らなさはブランチ検査が拾う**（★ 未コミットのまま checkout すれば
    HEAD が外れるので判断 2 の検査に掛かる）。
  - ⚠️ **B は過去の成功例を全部赤にする** —— ★ 001 / 002 / 003 / 005 / 007 / 008 は
    未コミットで終わって**なお merge された**。⚠️ 「未コミット = 異常」は現に成り立っていない。
- **トレードオフ**: ⚠️ 契約は書くが強制はしないので、破られても記録に残らない。
- **影響範囲**: `.claude/commands/loop-issue.md`
- **見直しタイミング**: ⚠️ 未コミット由来の作業消失が実際に起きたら B へ上げる

---

## 判断 6: 用語の追記先は `docs/glossary.md` ではなく `docs/loop-engineering.md`

- **判断日時**: 2026-09-20（★ 本セッションの判断。⚠️ 研究者の裁定ではない）
- **背景**: ★ `grilling` skill は逐語「確定した内容は **その場で** `docs/glossary.md` に inline 追記する」
  と指示している。
- **一次で確認したこと**: ⚠️ `docs/glossary.md` は **GSE の研究/製品ドメインの用語集**であり、
  Loop 工学の用語（worktree / attempt / issue / events）は **1 件も入っていない**
  （★ 2026-09-20 に grep。`attempt` の 1 件は「提出物 `.age` の試行の連番」で別概念）。
  ★ Loop 工学の用語の SSOT は `docs/loop-engineering.md` 「基本単位」節である
  （★ `CLAUDE.md` 逐語「用語 / Done・Stop / budget / events 契約 / モデル割当の単一 SSOT」）。
- **採用**: ★ 新語（**ブランチ検査** / **worktree 逸脱**）は `docs/loop-engineering.md` に書く。
- **理由**: ⚠️ ドメイン用語集に道具の用語を混ぜると、★ **禁止用語の検査（`glossary.md` の役割）**が
  Loop 工学の語まで抱えることになる。
- **トレードオフ**: ⚠️ `grilling` skill の逐語から外れる。★ 本判断に理由を残して整合させる。
