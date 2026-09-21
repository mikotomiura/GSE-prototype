# 次セッション — ⑤'' **起票 23（`resolve_base` が config を `tail -1` で選ぶ）の是正**

> 作成: 2026-09-21。⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/blockers.md`（**起票 23**・`:838`〜）／
> `scripts/loop-spawn.sh`（**`:37` が当該行**）／ `scripts/loop-spawn-cleanup-test.sh`（回帰群）／
> `docs/loop-engineering.md`（Loop の SSOT）／ `.github/workflows/ci.yml`（★ 配線は 2 か所）。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-issue23-resolve-base.md を読んで、⑤'' を実施してください。

【0】★ 最初に、S5（PR #219 で merge 済み）の /cross-review を実施する。
     ⚠️ 2026-09-21 は Codex の予算切れで回せなかったぶんである（研究者裁定で冒頭実施）。
     対象は S5 の 2 コミット（90e34de / 5a429d0）をパス限定で。

【1】起票 23（scripts/loop-spawn.sh の resolve_base が .steering/*/_loop-config.json を
     `tail -1` で黙って 1 つ選ぶ）を是正する。
【2】回帰テストを scripts/loop-spawn-cleanup-test.sh に足す（★ CI 配線済み・変異対照つき）。
【3】完了時に code-reviewer + security-checker を並列、そのうえで /cross-review（Codex）を 2 巡。

⚠️ 実装タスクなので **/start-task が先**（.steering/ に requirement / design / tasklist を作る）。
★ 設計判断は Opus、実装は Sonnet。サブエージェントは model を毎回明示・入れ子禁止。
⚠️ git add -A / git add <dir> は使わない（作業ツリーに別ブランチの未コミット作業がありうる）。
⚠️ .codex/budget.json を git checkout -- で戻さない（台帳。記帳が消えて復元不能になる）。
応答は日本語。

状態は一次（blockers.md の起票 23・loop-spawn.sh:37・ci.yml）で確かめ直すこと。
```

---

## §1 ★ 直前のセッション（2026-09-21）で何が終わったか

| | 中身 | 状態 |
|---|---|---|
| **PR #218** | ⑤' サーヴェイ **S3 / S4** ＋ **名称ゲート `J-2` の裁定** ＋ 起票 6 件を理論本文へ | ✅ **merge 済み**（`3da3154`） |
| **PR #219** | **S5**（S3/S4 のやり残しを一次で取りに行く）＋ `[P430]`–`[P432]` | ⚠️ **本セッション終了時点で open**（★ CI 待ち） |

★ **採番の末尾は `[P432]`**（`docs/references.md`）。次は `[P433]` から。

⚠️★★★ **PR #219 が未 merge なら、最初にそれを片づける**（★ 起票 23 は `loop-spawn.sh` の **base の pin** を触るので、
**未 merge の枝が残っていると混ざる** —— ⚠️ まさに起票 23 が問題にしている事故と同型である）。

## §2 ★ なぜ起票 23 が次なのか（⚠️ 一次で確かめた）

★ **研究者裁定（2026-09-21）** —— `blockers.md` の起票 23 逐語:

> 「⚠️ **⑤'（理論の回）の *後* に実施する。★★★ ⑥（P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極）の実施前には *必ず* 解決させる。**」
> 「⚠️ **理由**: ⑥ は **Loop で回す**ので、★ `resolve_base` が古い枝を選ぶと **worktree が 38 コミット前から切られ、全 issue が誤った base の上で走る**。」

★ 再開順は **⑤ ✅ → ⑤' ✅ → 本起票 → ⑥**。

### ⚠️ 今まさに踏める状態である（★ 実測）

- ★ 現存する `_loop-config.json` は **1 つだけ** = `.steering/20260914-mhd-feature-offline-tiers/_loop-config.json`
- ⚠️ その `base_branch` は **完了済みタスクの作業ブランチ**のまま残っている
- ★ `scripts/loop-spawn.sh:37` 逐語:

  ```bash
  cfg="$(ls -1 .steering/*/_loop-config.json 2>/dev/null | tail -1 || true)"
  ```

- ★ 起票に**実測の再現手順**が残っている（`LOOP_FORCE=1 bash scripts/loop-spawn.sh --no-exec zzz` → **38 コミット前の枝**から worktree）

## §3 ★ 何を作るか（⚠️ 起票が「次に何をするか」として書いている 2 点）

1. ★ config を **タスクで選ぶ**（引数か env でタスクを指定する / `--task` を足す）か、
   ⚠️ **複数ヒット・不一致なら止める（fail-closed）**。★ **`tail -1` で黙って選ばない。**
2. ★ 併せて「**解決した base がいま何であるか**」を**人が承認できる形**にする
   （⚠️ 現在も `base=… (start=…)` は出ているが、★ **無人モードC では誰も読まない**）。

### ★ 受け皿はもう在る（⚠️ 新しく作らない）

- **回帰テスト**: `scripts/loop-spawn-cleanup-test.sh`（★ 起票 18 が足した **9 群 29 件・変異対照つき**）
- **CI 配線**: `.github/workflows/ci.yml` の **`:658` と `:760` の 2 か所**で実行されている
- ⚠️ **`jq` を要らない作り**になっている（★ `ci.yml:651` の注記逐語「本テストは **jq を要らない**」）→ ★ **その性質を壊さない**

## §4 ⚠️ 実施の作法（★ `CLAUDE.md` から。省略しない）

- ★ **実装タスクなので `/start-task` が先**。`.steering/[YYYYMMDD]-[task-name]/` に
  `requirement.md` / `design.md` / `tasklist.md` を作る。
- ★ **モデル**: 設計判断・Plan は **Opus**、実装・テストは **Sonnet**。
- ⚠️ **サブエージェント**: `model` を**毎回明示**（★ `general-purpose` など定義ファイルを持たない相手）・**入れ子禁止**・**締切**・**範囲と禁止事項**。
  ★ 契約は `subagent-delegation` Skill。⚠️ **一次で確かめる仕事は代行させない**（★ 戻り値はメインが原典で裏取りする）。
- ★ **完了時のレビュー**: `code-reviewer` ＋ `security-checker` を**並列** → そのうえで **`/cross-review`（Codex）は必須**。
  ⚠️ **2 巡**（1 巡目 = 自文書・他文書の矛盾 ／ 2 巡目 = **自分が足した規則の境界条件**）。
- ⚠️ **git**: `git add -A` / `git add <dir>` を**使わない**（★ ファイル名を明示）。ブランチは `fix/[task-name]`。
- ⚠️★★★ **`.codex/budget.json` を `git checkout --` で戻さない**（★ 台帳。記帳が消えて復元不能）。
- ★ **テストを叩く場所**: ⚠️ `Cargo.toml` は repo 直下に**無い**（`src-tauri/` にある）。
  ★ 本タスクは bash なので `bash scripts/loop-spawn-cleanup-test.sh` で足りるはずだが、
  Rust を触るなら `cd src-tauri` か `--manifest-path src-tauri/Cargo.toml`。
- ★ **応答は日本語**。

### ⚠️ Codex の予算について（★ 2026-09-21 の実測）

★ 2026-09-21 は **`314093/300000`** まで使い切った（invocations 8）。⚠️ **日付が変われば `today` がリセットされる**はずだが、
★ **回す前に `.codex/budget.json` の `today` を確認**すること。
⚠️ **上限（`daily_token_budget` = 300000）を勝手に引き上げない** —— ★ 過去の引き上げはいずれも**研究者の明示指示**があった。
（★ 2026-09-21 も研究者が「予算一時的に引き上げてもいいよ. 重要なレビューであれば」と明示したので 350000 へ上げ、**実施後に 300000 へ戻した**。）

## §5 ⚠️ 本セッションで持ち越した未回収

| # | 何 | ★ どこに効く |
|---|---|---|
| **1** | ⚠️★★★ **S5（PR #219）の `/cross-review` が未実施**（★ 2026-09-21 の Codex 予算を使い切ったため） | ★★★ **研究者裁定（2026-09-21）: CI 緑なら merge し、`/cross-review` は *次セッションの冒頭* に実施する。** → ⚠️ **本セッションの最初の仕事がこれである**（★ 起票 23 に入る *前*）。★ 対象は **merge 済みの `main`** なので、範囲は `git diff <merge 前の main>..main` か、**S5 の 2 コミット（`90e34de` / `5a429d0`）**をパス限定で指定する。⚠️ 予算ガード（`daily_token_budget` = 300000）を勝手に引き上げないこと |
| **2** | ⚠️★★★ **書籍 *Autographic Design* の pp.33 / 62 / 80 / 186–187 が未読** | ★★★ **`SUB-PGP` の (ii)（肖像の文脈）が残るか消えるかは、ここだけで決まる**。★ 経路候補: **図書館（ILL / 所蔵館）／[P431] の書評本文（403）／mL Talks の録画** |
| **3** | **Galanter (2016)** `doi:10.1002/9781118475249.ch5` ／ **Boden & Edmonds (2009)** `doi:10.1080/14626260902867915` | ★ S3 カード 1 の**外的妥当性の留保**が開いたまま |
| **4** | ⚠️ **Google Books の本文内検索をメインが再現できていない**（★ レート制限） | ★ 書籍全体の語の在否（`portrait` 0 件等）は**サブエージェント報告のまま** |
| **5** | ⚠️ **`docs/glossary.md` が Codex 未検査** | ★ 文脈行に未踏提案書の逐語があるため除外した。→ 次は **`-U0` 相当で文脈行を落とした diff** を渡す |
| **6** | **起票 24（ライブ変換の層を識別できない）** `20260914-instrument-change-arbitration/blockers.md` | ⚠️ 研究者判断は「**起票だけ**」。★ 今やるならその判断を覆すことになる |
| **7** | `citation-ssot` の **LOW 13**（追記区切りの規約化）／ `glossary.md:49-51` の**列数ずれ**（★ 既存） | ★ どちらも**別タスク**として起票済み |

⚠️★★★ **起票 24 は 2 つのファイルに在り、片方（`mhd-feature-offline-tiers` 側・`check` job の `permissions:`）は *取り下げ済み* である。**
★ **必ずファイルとセットで呼ぶ。**

## §6 ★ 本セッションで環境に入れたもの

- ★ **`yt-dlp` 2026.08.19**（`python -m pip install yt-dlp`）。⚠️ **動作確認済み** —— YouTube の自動生成字幕を取得できた。
  ★ 使い方: `python -m yt_dlp --skip-download --write-auto-subs --sub-langs "en.*" --sub-format vtt -o "yt-%(id)s.%(ext)s" <URL>`
  ⚠️ **警告が出るが動く**（"No supported JavaScript runtime" / "no impersonate target"）。
  ⚠️★★★ **自動字幕は逐語の格が低い**（★ 人名が崩れる）→ **`provisional` で登録し、論文で引くなら原典に当たり直す**。

## §7 ⚠️ 直前のセッションで踏んだ落とし穴（★ 繰り返さない）

1. ⚠️★★★ **`gh pr checks --watch` は全チェック完了前に `exit 0` で抜けることがある。**
   → ★ **`gh run view <id> --json status,conclusion` を見る**（⚠️ 終了コードを信じない）。
2. ⚠️★★★ **「入手できない」も *断定* である。** ★ 1 経路の失敗を「不可能」と読み替えない
   （★ 研究者の指摘で探索し直したら、**書籍の序章全文と McCormack の掲載版**が取れた）。
3. ⚠️ **採番を詰めたら `docs/references.md` の *本文中の参照* も remap する。**
   ★ 検算は**付け替えた直後**に（⚠️ 番号帯は次ラウンドが再利用するので、後回しにすると grep で区別が付かない）。
   → ★ 規則は `citation-ssot` の**ルール 2** に書いた。
4. ⚠️ **サブエージェントの要約は三次資料**。★ 2026-09-21 は **2 件を一次で読み直して訂正**した
   （`individualization` = 人ではなく**物体** ／ `cede` の 1 件は **"concede" の偽陽性**）。
5. ⚠️ **`.codex/budget.json` は JSON。** ★ コメント行を足すときは**末尾カンマと引用符の位置**に注意
   （⚠️ 2026-09-21 に **2 回壊した**。★ どちらもその場で修復し、`tokens_used` / `invocations` / `history` は無傷だった）。
