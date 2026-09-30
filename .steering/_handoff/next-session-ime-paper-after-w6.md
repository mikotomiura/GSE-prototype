# 次セッション — IME 論文: W6（024）の後 —— main への merge の判断と、次のマイルストーン

> 作成: 2026-09-30（G-GEAR で W6 の 024 を merge したセッションの最後に）。前の handoff（`next-session-ime-paper-ggear-w6.md`・`next-session-ime-paper-mac.md`）の後継。前のものは読まなくてよい。
> ✅ **2026-09-30 更新（G-GEAR）**: Mac の確認（`b2e284e2`・B13）と G-GEAR の確認がどちらも済んだ。★ 024 の書き出しは両 OS で同じバイト列（一覧の SHA-256 `577caaff…`・91 ファイルが一致・判断 68）。**残りの機械ごとの作業は無い**。次は §2（研究者の判断）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（判断 67〜71）・`blockers.md`（B13）・`issues/024.md`・`tasklist.md`・`_issue-plan.md` §5。状態は着手時に測り直す。
> ★ 両方の機械が同じ base に push するので、push の前に `git fetch` で相手の push を読み、`git pull --no-rebase` で取り込む（force しない）。

## §0 打ち込む用（どちらの機械でも・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-after-w6.md を読んで、§2 の 1 と 2 を研究者に AskUserQuestion で確かめてください（推奨と理由を添える・勝手に決めない）。
1 は IME 論文の評価一式（feature/ime-eval-kit）を main へ merge するか。merge するなら git-workflow のルール 6（push → PR → CI 緑なら merge）と /finish-task の手順で、タスク完了時の /cross-review（Codex）も回す（勝手に merge しない）。
2 は事前登録の凍結（M3 / M6）を公開で示す方法。決まったら decisions.md に判断 72 以降として記録し、_issue-plan.md §5 の M3 / M6 の Done を直す。
まず base（feature/ime-eval-kit）を git fetch → git pull --no-rebase で取り込み、git status と git log で §1 の状態を測り直す。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の decisions.md（判断 67〜71）・blockers.md（B13）・_issue-plan.md §5・design.md §4 / §6。Skill: verify-before-claiming・git-workflow。応答は日本語。
コミットは git add パス指定（-A 禁止）。新しい公開 repo を作らない・DOI を取らない（M12 は研究者）。
```

## §1 状態（2026-09-30 の終わり）

- base `feature/ime-eval-kit`（origin と一致・先頭は G-GEAR の記録のコミット）: W1〜W6 の 25 本（任意の 025 / 026 / 027 は `## Status: blocked`）がすべて merge 済み。W6 の 024 は `c6305340`（`a193c751` ＋ merge ゲートの直し `24264d40`・`d8e3f1d9`・`9cf4eac9`）。その後は `.steering/` の記録と acceptance の測定器の直し（Mac の `b2e284e2`）だけで、`papers/` は `c6305340` から変わっていない。
- ✅ 全 acceptance（2026-09-30）:
  - G-GEAR（`c6305340` の clean な checkout）: Windows で回る 22 本がすべて失敗 0 件（macOS 専用の 004 / 007 / 012 は exit 2 ＝対象外）。
  - Mac（`8bcf2a81`〜`b2e284e2`）: Mac で回せる 22 本がすべて失敗 0 件（Windows 専用の 005 / 008 / 009 / 013 / 014 は対象外）。書き出した側の macOS のドライバの `cargo test` も緑。
  - `_style_check.py papers/ime-observation` 違反 0 件（両 OS）。
- ★ **024 の書き出しの一覧の SHA-256（直した測定器・`papers/` = `c6305340`）**: `577caafffe2c0aa743f34ae1491cdaa8297d119296e72f03a42d29200936f34a`（91 ファイル）—— **Mac と G-GEAR で一致**（判断 68 を両 OS で確かめた）。⚠️ 以前 G-GEAR で記録した `9e586e52…` は、一覧を Python のテキストの stdout に書いていたため Windows で CRLF が混ざった値（B13）。比べる値として使わない。⚠️ `papers/` を変える commit の後では値が変わるので、比べるのは同じ内容どうし。
- このタスクの W6 の裁定（判断 67〜71・詳細は decisions.md）:
  - 67 秘匿の検査の絶対パス: 書き出す機械の実在の値＋ユーザー名を伴うホームの形を拒み、明示した架空の名前の一覧（alice / alice2 / bob / carol / dave / erin / gina / harry / YAMADA~1 / name）だけ通す。
  - 68 ★ **パイロットと本計測（M1 / M4 / M5 / M7 / M10）のロガーは `export.py` の書き出しからビルドする**（ログの `manifest_sha256` が公開の manifest と一致する）。`_issue-plan.md` §5 の M1 / M5 / M10 の前提に 024 を足した。
  - 69 逐語コピーの日本語の文字列リテラル（73 個）は内部の対訳表 `kit/export/translations.internal.json`（72 項目・書き出さない）で英訳する。
  - 70 元が git の作業ツリーの中なら、書き出すファイルはすべて追跡済みで HEAD と一致していること（違えば exit 2）。秘密の名前の型は exit 2。★ **公開の書き出しは、リリースする commit の新しい clone から行う**（README）。
  - 71 判断 67 (b) を「絶対パスの字句の中の Users / home の成分の次の成分」で判定する形に書き直した。
- ⚠️ 未決として残したもの（前から）: 照合器の `clock_offsets_ms` の出どころ（M1 / M3）／`dwell_ms == 0` の扱い（判断 45・M3）。LOW の記録: JSON の中でさらにエスケープした綴り（バックスラッシュ 4 つ）は 024 の検査が見逃しうる。

## §2 研究者に確かめること

1. ★ **`feature/ime-eval-kit` を main へ merge するか**（W6 の後・研究者の判断と決めてあった）。
   - main との分岐点からの差は `papers/` と `.steering/` のほかに 4 ファイルだけ（2026-09-30 に `git diff --stat <merge-base>..feature/ime-eval-kit -- . ':!papers' ':!.steering'` で確認）: `.gitattributes`（論文キットの eol の 9 行）・`docs/experiment-tracking.md`（1 行）・`docs/repository-structure.md`（9 行）・★ `.codex/budget.json`（Codex の予算の台帳 —— ⚠️ memory「Codex ledger split by branch」: merge では両方の記帳を**合算**する。`git checkout --` で片方に戻さない）。GSE 本体（`src-tauri/`・`src/`・`scripts/`・`.github/`）は変えていない（各 acceptance の `forbid_gse_changes`）。
   - ⚠️ main との乖離は大きい（2026-09-30 の spawn の表示で「origin/main より 93 コミット後ろ / 161 コミット先」）→ merge の前に main を取り込むか、PR で衝突を見る。
2. ★ **事前登録の凍結（M3 = macOS 版・10 月中旬／M6 = Windows 版の追補）を公開で示す方法**（2026-09-30 に G-GEAR のセッションで研究者に指摘した・未決）。
   - 事実（一次）: 今の設計では凍結の印（`experiment/preregistration.md` の `frozen_at:` と `sha256:` の行）と凍結の commit のタグは **private の GSE にしか残らない**（`_issue-plan.md` §5 の M3 の Done・判断 63）。公開 repo の履歴は M12（12 月・M8 と M10 の後）から始まる（判断 20）。`design.md` と `decisions.md` に凍結を公開で示す方法の記述は無い（grep で確認）。→ このままだと、読者・査読者は「凍結が本計測より前だった」ことを第三者として確かめられない。
   - 案: (a) 凍結した事前登録を OSF に登録する（日付つき）／(b) 凍結した事前登録を Zenodo に先に寄託する（日付と DOI）／(c) 事前登録だけを先に公開 repo に置く。⚠️ どれも外部への操作（研究者が行う・または承認を得て行う）。⚠️ BRM が事前登録の公開を求めるかは一次で確かめていない。
   - ★ M3 の前に決める。決まったら M3 / M6 の Done に「公開の日付の記録」を足す。
3. 次のマイルストーン（`_issue-plan.md` §5）: M0（コーパスの確定: 作品を選ぶ・青空文庫から取得の承認・SudachiPy の pin）→ M1（macOS の較正パイロット。★ ロガーは書き出しからビルド・判断 68）。
4. （参考）公開 repo を作るのは M12（IME 論文のマイルストーン・12 月・M8 と M10 の後、M13 の BRM 投稿の前）。GSE 本体の公開とは別（判断 5・GSE 本体の OSS 公開は未踏採択後）。

## §3 片付けの状態（2026-09-30）

- `loop/024-issue` の worktree と枝・検証用の `C:/wt/clean-024`・`C:/wt/clean-base`・`C:/wt/clean-024m` を片付けた（着手時に `git worktree list` と `git branch --list 'loop/*'` で確かめ直す）。
- ローカルの枝 `archive/ime-013-attempt1-stop`・`archive/ime-023-attempt1-stop`（G-GEAR・push していない）は残っている。

## §4 気をつけること

- ⚠️ 024 の `export.py` は、元が git の作業ツリーの中だと**未追跡・未コミットのファイルがあれば止まる**（判断 70）。書き出しと `024-acceptance.sh` は clean な checkout で回す。
- ⚠️ 「機械によらず同じ」を確かめる値は、値を作る道具そのものが機械によらないことを先に確かめる（B13: 一覧を Python のテキストの stdout に書くと Windows で CRLF が混ざる）。
- ⚠️ Windows の git-bash は `/` で始まる引数や `rev:path` を native のプログラムへ渡すときに書き換える（`git show origin/…:path` は `MSYS_NO_PATHCONV=1` が要る）。
- ⚠️ heredoc の中のバックスラッシュは化ける → 文書の直しは Edit か、ファイルに書いた Python で。
- ⚠️ ループの `loop-run.sh` の終わりの `spawn_err: unbound variable` は既知の雑音（B2）。
- ⚠️ worker に合成キーを送らせない。GSE 本体を変えない。人の打鍵データを使わない。凍結（M3 / M6）の前に ImeShadow と正解を突き合わせない。新しい公開 repo を作らない（M12・研究者）。
