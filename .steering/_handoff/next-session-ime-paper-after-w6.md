# 次セッション — IME 論文: W6（024）の後 —— Mac の確認と、main への merge の判断

> 作成: 2026-09-30（G-GEAR で W6 の 024 を merge したセッションの最後に）。前の handoff（`next-session-ime-paper-ggear-w6.md`・`next-session-ime-paper-mac.md`）の後継。前のものは読まなくてよい。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（判断 67〜71）・`issues/024.md`・`tasklist.md`・`_issue-plan.md` §5。状態は着手時に測り直す。
> ★ 両方の機械が同じ base に push するので、push の前に `git fetch` で相手の push を読み、`git pull --no-rebase` で取り込む（force しない）。

## §0 打ち込む用

### Mac で（`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-after-w6.md を読んで、§1 のとおり G-GEAR で merge した W6（issue 024 の export.py）を Mac で確かめてください。
手順: base（feature/ime-eval-kit）を origin から取り込み（main checkout を別セッションが使っていれば B10 のとおり base 用の worktree で扱う・ブランチを切り替えない）、clean な worktree（短いパス）で 024-acceptance.sh を回す。★ 最後に出る「書き出しの一覧の SHA-256」が G-GEAR の値（§1）と一致するかを見る（判断 68）。あわせて Mac で回せる全 acceptance も回す。
緑で一致なら tasklist.md の「⚠️ Mac: 024-acceptance.sh を回す」の行に結果を書いてコミットし、git pull --no-rebase の後に push する。赤・不一致なら直さずに原因を読み、研究者に報告する。
一次資料: .steering/20260927-ime-observation-paper-eval-design/ の decisions.md（判断 67〜71）・issues/024.md・blockers.md（B10・B11）。Skill: verify-before-claiming・git-workflow。応答は日本語。
コミットは git add パス指定（-A 禁止）。main への merge はしない（研究者の判断）。新しい公開 repo を作らない・DOI を取らない（M12 は研究者）。
```

### ★ G-GEAR で（Mac の確認の後・2026-09-30 追記）

> ✅ Mac の確認は済んだ（tasklist・blockers B13）。書き出しの中身は一致していたが、比べる値の測定器が Windows で CRLF を混ぜていたので直した。残りは G-GEAR での 1 回の確認だけ。

```
.steering/_handoff/next-session-ime-paper-after-w6.md の §0「G-GEAR で」を実施してください。
base（feature/ime-eval-kit）を git fetch → git pull --no-rebase で取り込み、clean な checkout（短いパス）で .steering/20260927-ime-observation-paper-eval-design/issues/024-acceptance.sh を回す。
★ 失敗 0 件で、最後の「書き出しの一覧の SHA-256」が Mac の値 577caafffe2c0aa743f34ae1491cdaa8297d119296e72f03a42d29200936f34a（91 ファイル）と一致するかを見る（blockers.md B13）。
一致なら tasklist.md の「⚠️ G-GEAR: 直した 024-acceptance.sh を回し…」の行に結果を書いてコミットし、git pull --no-rebase の後に push する。不一致なら直さずに原因を読み、研究者に報告する。
コミットは git add パス指定（-A 禁止）。main への merge はしない（研究者の判断）。応答は日本語。
```

### どちらの機械でも（Mac と G-GEAR の確認の後）

```
.steering/_handoff/next-session-ime-paper-after-w6.md の §2 を読んで、IME 論文の評価一式（feature/ime-eval-kit）を main へ merge するかを研究者に AskUserQuestion で確かめてください（勝手に merge しない）。merge するなら git-workflow のルール 6（push → PR → CI 緑なら merge）と /finish-task の手順で、タスク完了時の /cross-review（Codex）も回す。
```

## §1 状態（2026-09-30 の終わり・G-GEAR）

- base `feature/ime-eval-kit`: W1〜W6 の 25 本（任意の 025 / 026 / 027 は `## Status: blocked`）がすべて merge 済み。W6 の 024 は `c6305340`（`a193c751` ＋ merge ゲートの直し `24264d40`・`d8e3f1d9`・`9cf4eac9`）。
- ✅ merge 後の base（`c6305340`）の clean な checkout で全 acceptance 25 本: G-GEAR で回る 22 本がすべて失敗 0 件、macOS 専用の 004 / 007 / 012 は exit 2（対象外）。`_style_check.py papers/ime-observation` 違反 0 件。
- ★ **024 の書き出しの一覧の SHA-256（G-GEAR・Windows・`c6305340`）**: `9e586e5254063ec6a27ef50971ab83557da17d0c1343bc046faa8682b8b0b3b5`（91 ファイル）。★ 判断 68 により、同じ commit なら Mac でも同じ値になるはず。⚠️ 024 以外の `papers/` を変える commit の後では値が変わるので、比べるのは同じ commit どうし。
  - ★ **2026-09-30 追記（Mac）: この値は測定器の改行（Windows の CRLF）を含んでいた（B13）。** 中身はバイト一致で、直した測定器での値は `577caafffe2c0aa743f34ae1491cdaa8297d119296e72f03a42d29200936f34a`（Mac で確認済み・G-GEAR で確認待ち）。
- このセッションの裁定（判断 67〜71・詳細は decisions.md）:
  - 67 秘匿の検査の絶対パス: 書き出す機械の実在の値＋ユーザー名を伴うホームの形を拒み、明示した架空の名前の一覧（alice / alice2 / bob / carol / dave / erin / gina / harry / YAMADA~1 / name）だけ通す。
  - 68 ★ **パイロットと本計測（M1 / M4 / M5 / M7 / M10）のロガーは `export.py` の書き出しからビルドする**（ログの `manifest_sha256` が公開の manifest と一致する）。同じ commit の書き出しは機械によらず同じバイト列（LF）。`_issue-plan.md` §5 の M1 / M5 / M10 の前提に 024 を足した。
  - 69 逐語コピーの日本語の文字列リテラル（73 個）は内部の対訳表 `kit/export/translations.internal.json`（72 項目・書き出さない）で英訳する。
  - 70 元が git の作業ツリーの中なら、書き出すファイルはすべて追跡済みで HEAD と一致していること（違えば exit 2）。秘密の名前の型は exit 2。★ **公開の書き出しは、リリースする commit の新しい clone から行う**（README）。
  - 71 判断 67 (b) を「絶対パスの字句の中の Users / home の成分の次の成分」で判定する形に書き直した。
- `_style_check.py` を直した: 明示したファイルでも `*.internal.*` を対象外にする（`style_ok` が対訳表で止まらないように）。
- ⚠️ 未決として残したもの（前から）: 照合器の `clock_offsets_ms` の出どころ（M1 / M3）／`dwell_ms == 0` の扱い（判断 45・M3）。LOW の記録: JSON の中でさらにエスケープした綴り（バックスラッシュ 4 つ）は 024 の検査が見逃しうる。

## §2 研究者に確かめること

1. ★ **`feature/ime-eval-kit` を main へ merge するか**（W6 の後・研究者の判断と決めてあった）。main との分岐点からの差は `papers/` と `.steering/` のほかに 4 ファイルだけ（2026-09-30 に `git diff --stat <merge-base>..feature/ime-eval-kit -- . ':!papers' ':!.steering'` で確認）: `.gitattributes`（論文キットの eol の 9 行）・`docs/experiment-tracking.md`（1 行）・`docs/repository-structure.md`（9 行）・★ `.codex/budget.json`（Codex の予算の台帳 —— ⚠️ memory「Codex ledger split by branch」: merge では両方の記帳を**合算**する。`git checkout --` で片方に戻さない）。GSE 本体（`src-tauri/`・`src/`・`scripts/`・`.github/`）は変えていない（各 acceptance の `forbid_gse_changes`）。⚠️ main との乖離は大きい（2026-09-30 の spawn の表示で「origin/main より 93 コミット後ろ / 161 コミット先」）→ merge の前に main を取り込むか、PR で衝突を見る。
2. 次のマイルストーン（`_issue-plan.md` §5）: M0（コーパスの確定: 作品を選ぶ・青空文庫から取得の承認・SudachiPy の pin）→ M1（macOS の較正パイロット。★ ロガーは書き出しからビルド・判断 68）。

## §3 片付けの状態（2026-09-30）

- `loop/024-issue` の worktree と枝・検証用の `C:/wt/clean-024`・`C:/wt/clean-base` を片付けた（着手時に `git worktree list` と `git branch --list 'loop/*'` で確かめ直す）。
- ローカルの枝 `archive/ime-013-attempt1-stop`・`archive/ime-023-attempt1-stop`（push していない）は残っている。

## §4 気をつけること

- ⚠️ `024-acceptance.sh` は書き出した側で `cargo test --locked`（ロガー）と `rustfmt` を使う（Mac にも入っているはず）。★ 書き出した側の macOS の専用ファイル（`src/driver_macos/`）がコンパイルされるのは Mac だけ（G-GEAR では構文解析だけ）→ Mac の `cargo test` が初めての確認になる。
- ⚠️ 024 の `export.py` は、元が git の作業ツリーの中だと**未追跡・未コミットのファイルがあれば止まる**（判断 70）。clean な worktree で回す。acceptance は一時的な写し（git の外）と一時的な git repo も作る。
- ⚠️ heredoc の中のバックスラッシュは化ける（このセッションでも `\\?\` の 1 つが落ちた）→ 文書の直しは Edit か、ファイルに書いた Python で。
- ⚠️ ループの `loop-run.sh` の終わりの `spawn_err: unbound variable` は既知の雑音（B2）。
- ⚠️ worker に合成キーを送らせない。GSE 本体を変えない。人の打鍵データを使わない。凍結（M3 / M6）の前に ImeShadow と正解を突き合わせない。新しい公開 repo を作らない（M12・研究者）。
