# 実測ログ — Loop 基盤の穴（起票 3 / 10 ＋ Status 無視）

> ★ 実施日: **2026-09-20**。⚠️ **すべて実 repo の使い捨て worktree `loop/zzz-issue`
> （`C:/wt/GSE-prototype-zzz-issue`）で実行した**（研究者の grill 裁定）。
> ★ 撤去済み（`bash scripts/loop-spawn.sh --cleanup zzz`）。
>
> ⚠️★★★ **なぜ機械検査で代替しないか**: 権限判定は Claude Code のランタイム内にあり、
> **設定ファイルを読むだけでは「拒否されるか」を確かめられない**。
> ★ 「`deny` 配列に 2 件入った」は**「拒否される」の証拠にならない**。

共通条件:

```
--max-turns 3 --permission-mode acceptEdits --model haiku --output-format json
--allowedTools "$(jq -r .headless.allowed_tools \
    .steering/20260914-mhd-feature-offline-tiers/_loop-config.json)"
```

★ `allowed_tools` は **issue 004 が走ったときと同じ文字列**を使った（⚠️ `git checkout` は含まれていない）。

---

## M1 — 対照: deny **7 件**（現状）で `git checkout main` を依頼

| | 値 |
|---|---|
| deny | `["Bash(git push:*)","Bash(gh pr merge:*)","Bash(git reset --hard:*)","Bash(git rebase:*)","Bash(sudo:*)","Bash(rm -rf:*)","Bash(chmod -R:*)"]` |
| branch(before) | `loop/zzz-issue` |
| **branch(after)** | ⚠️★★★ **`main`** |
| `permission_denials` | `[]`（**0 件**） |
| `result` | 「完了しました。`main` ブランチへ切り替えました。」 |

→ ★ **起票 10（2026-09-15・issue 004）の再現に成功した。**
⚠️ `allowed_tools` に `git checkout` が無いにもかかわらず通る。
★ 原因は追跡済み `.claude/settings.json:113-116` の `allow: ["Bash(git *)", "Bash(gh *)"]`。

---

## M1b — `permission_denials` の**実スキーマ**（起票 3）

★ `git push --dry-run` を依頼して 1 件の拒否を作った:

```json
{
  "tool_name": "Bash",
  "tool_use_id": "toolu_01XjCvcHbEgXvmayXVmQEEMa",
  "tool_input": {
    "command": "git push --dry-run 2>&1",
    "description": "Test git push without making changes"
  }
}
```

⚠️★★★ **`.tool_name` だけを集計しても起票 3 は閉じない。**
★ Bash の拒否はすべて `tool_name == "Bash"` になるので、
**「何が拒否されたか」は `.tool_input.command` にしかない**。
→ ★ 実装では `Bash(<command の先頭 2 語>)` を集計キーにし、生配列も保存する（判断 3）。

---

## M2 — 対策後: deny **9 件**で同じ依頼

| | 値 |
|---|---|
| deny | 上記 ＋ `"Bash(git checkout:*)"`, `"Bash(git switch:*)"` |
| branch(before) | `loop/zzz-issue` |
| **branch(after)** | ★ **`loop/zzz-issue`（不変）** |
| `permission_denials` | **1 件**: `{"tool_name":"Bash","tool_input":{"command":"git checkout main", ...}}` |
| `result` | 「Bash の実行許可がブロックされました。」 |

→ ★ **worktree 限定の `deny` が、追跡済み `settings.json` の `allow: Bash(git *)` に優先した**
（★ 判断 1 の前提「`deny` は allow に優先する」を実測で確認）。
★ 対話セッションの権限は 1 バイトも変えていない。

---

## M3 — ⚠️★★★ 迂回の実測: `git -C . checkout main`

| | 値 |
|---|---|
| deny | **9 件**（M2 と同じ） |
| branch(before) | `loop/zzz-issue` |
| **branch(after)** | ⚠️★★★ **`main`** |
| `permission_denials` | **`[]`（0 件）** |
| `result` | 「コマンド実行完了。main ブランチに切り替わりました。」 |

⚠️★★★ **これが本タスクで最も重要な実測である。**

★ `docs/loop-engineering.md` が **2026-09-14 時点で「未検証」と断っていた**逐語 ——

> - **綴りを網羅できない**。`Bash(git push:*)` は前置一致なので `git -C <dir> push …` は当たらず、
>   追跡済み `.claude/settings.json` の `allow: ["Bash(git *)","Bash(gh *)"]` に拾われる。

→ ★ **2026-09-20 に検証された。** ⚠️ **`deny` を 9 件にしても `git -C . checkout` は通る。**

★ したがって:

- ⚠️ **`deny` は境界ではない**（★ 件数を増やしても閉じない。★ M3 がその証明）。
- ★ **境界は `loop-run.sh` のブランチ検査**（`ensure_branch`）である ——
  ⚠️ **どの綴りで到達したかに関係なく、HEAD が `loop/<id>-*` から外れたことを見る**。

### reflog（★ M1 / M3 の痕跡）

```text
b7a1cae HEAD@{2026-09-20 17:17:34 +0900}: checkout: moving from loop/zzz-issue to main   ← M3 (deny 9 件・迂回)
1bdbb24 HEAD@{2026-09-20 17:15:53 +0900}: checkout: moving from main to loop/zzz-issue   ← 手で復帰
b7a1cae HEAD@{2026-09-20 17:15:34 +0900}: checkout: moving from loop/zzz-issue to main   ← M1 (deny 7 件)
```

---

## M4 — ⚠️★★★ 派生的な発見: **逸脱した worktree は `--cleanup` で撤去できない**

★ M3 の後片付けで `bash scripts/loop-spawn.sh --cleanup zzz` を実行したときの**実測**:

```text
loop-spawn: worktree 見つからず (既に撤去?)
Deleted branch loop/zzz-issue (was 1bdbb24).
loop-spawn: cleanup 完了 issue zzz
```

⚠️ ところが直後の `git worktree list` は:

```text
C:/wt/GSE-prototype-zzz-issue    b7a1cae [main]      ← ★ 残っている
```

**原因**（★ `scripts/loop-spawn.sh:57` 逐語）:

```bash
wt="$(git worktree list --porcelain | awk -v id="$id" '/^worktree /{p=substr($0,10)} /^branch /&&$0 ~ ("loop/" id){print p}')"
```

→ ⚠️★★★ **worktree を「ブランチ名」で引いている**ので、
★ **逸脱して `main` に乗った worktree は 1 件もヒットしない**。
⚠️ しかも **branch だけは消え**（`git branch --list 'loop/*'` が空）、
★ **worktree は `main` を掴んだまま登録に残る**。

★ これが残す実害:

1. ⚠️ **同じ id の再実行が恒久的に死ぬ** —— `loop-spawn.sh:90` の
   「同名 worktree が既に存在」に当たり続ける。
2. ⚠️ **main checkout が `main` をチェックアウトできなくなる**
   （★ git は同一ブランチの二重チェックアウトを拒む）。
3. ⚠️ `--cleanup` が **「完了」と報告する**ので、★ **失敗が誰にも見えない**。

→ ★ 手で `git worktree remove --force <path>` ＋ `git worktree prune` して回復した。

⚠️★★★ **これは起票 10 の二次被害であり、本タスクの範囲外である**
（★ 直すのは `loop-spawn.sh --cleanup` の引き方）。
→ ★ **新しい起票として `blockers.md` に上げる**（起票 18）。
★ ただし **ブランチ検査（`ensure_branch`）が入れば、そもそも逸脱した attempt が
`blocked` で止まる**ので、この形に到達する確率は大きく下がる。

---

## ⚠️ この実測が見ていないもの（★ 明示する）

- ★ **他の綴り**: `git -c alias.x=checkout x` / `git worktree add` /
  `git switch` の別形 / `GIT_DIR` を使う形。⚠️ **1 つも試していない。**
  → ★ ただし **ブランチ検査は綴りに依存しないので、これらも同じく拾う**（★ B1〜B3 が検査する）。
- ★ **`permission_mode` を昇格させた場合**（`auto` / `bypassPermissions`）。
  ⚠️ `docs/loop-engineering.md` が「未検証」と書いている 2 点目は**依然として未検証**。
  ★ 本タスクは既定の `acceptEdits` でしか測っていない。
- ★ **watchdog セッション**（`run_watchdog`）は `WD_TOOLS` が別の allowlist だが、
  ⚠️ 同じ `settings.json` の `allow` を受けるので**同じ迂回が成立するはず**。★ 測っていない。

---

## S 系 — Status フィルタの 3 状態（★ 2026-09-20 実施）

★ `scripts/loop-run-guard-test.sh` が一時 git repo ＋ `claude` stub で**実際に `loop-run.sh` を回して**判定する。

| # | 状態 | 期待 | 結果 |
|---|---|---|---|
| S1 (a) | 既定実行・`Status: blocked（注釈つき）` の 002 | 実行計画に**出ない** | ★ OK |
| S1 (a) | 既定実行・通常の 001 | 実行計画に**出る**（外しすぎない） | ★ OK |
| S1 (a) | 除外の可視化 | ログ / report に「Status=blocked で除外」 | ★ OK |
| S2 (b) | `--issues 002`（明示） | 実行計画に**出る** ＋ 警告 1 行 | ★ OK |
| S3 (c) | `## Status` 節が**無い** 003 | 実行計画に**出る** | ★ OK |
| S4 | blocked な 002 に依存する 004 | `preflight_dag` が **die しない** | ★ OK |

⚠️★★★ **S4 は本変更が招いた回帰の予防である**。
★ `preflight_dag` の依存存在確認を `$ALL`（フィルタ後）で引いていると、
**`blocked` を外したせいで「issues/ に存在しません」と誤診して die する**。
→ ★ 存在確認だけ `ALL_FILES`（フィルタ前）に対して行うようにした。

---

## ★ 突然変異テスト —— ⚠️「検査が空振りしていないこと」の確認

⚠️ memory「Acceptance self-test」の型（★ **4 回再発している**）を避けるため、
★ **実装を一時的に壊して検査が赤くなるか**を確かめた（★ 確認後に `md5sum` で復元を検証）。

| 変異 | 内容 | 結果 |
|---|---|---|
| M-a | `ensure_branch` を常に `return 0` にする | ★ **B1（3 件）と B3 が赤**（18 → 14 合格） |
| M-b | Status フィルタを `ALL="$ALL_FILES"` に戻す | ★ **S1 の 1 件目が赤**（18 → 17 合格） |
| M-c | `detail` から `by_tool` を落とす | ★ **D1 の 2 件が赤**（18 → 16 合格） |
| M-d | `issue_done` 直前の `ensure_branch` を殺す | ★ **B4 の 2 件が赤**（30 → 28 合格） |
| M-e | `merge-base --is-ancestor` の検査を殺す | ★ **B5 が赤**（30 → 29 合格） |
| M-f | 生配列への `redact` を外す | ★ **D2 の「生配列に秘密が残った」が赤**（30 → 29 合格） |

→ ★ **どの変異も検出された。** ⚠️ 復元後の `md5sum` は毎回元と一致。

---

## ★ レビュー後の追試（2026-09-20・`code-reviewer` ∥ `security-checker` の反映後）

| 検査 | 結果 |
|---|---|
| `bash scripts/loop-run-guard-test.sh` | ★ **30 / 30**（B1〜B5・S1〜S8・D1〜D2） |
| `bash scripts/loop-worktree-deny-test.sh` | ★ **34 / 34** |
| `bash scripts/check-shell-portability.sh` | ★ **12 / 12** |
| `bash scripts/check-tests-are-wired.sh` | ★ **16 / 16**（★ `loop-run-guard-test.sh` を CI に配線済み） |
| CRLF（`tr -cd '\r' \| wc -c`） | ★ 変更した 5 ファイルすべて **0** |

⚠️★★★ **`check-shell-portability.sh` は一度赤になった**（★ 記録に残す）:
`ensure_branch` の `detail` に書いた `$wt」` が **`$name` に多バイト文字を直付けした形**で、
★ bash 3.2 は変数名を誤って長く読む。→ `${wt}」` に直して緑になった。
⚠️ **この規約は macOS 既定の bash 3.2 のために在り、手元の bash 5.2 では再現しない。**

---

## ⚠️ 追試で分かった、検査の *前提* が壊れていた 2 例（★ 記録に値する）

★ どちらも「検査が見逃した」ではなく **「そもそも壊すことに失敗していた」**形である。
⚠️ 気づかなければ **「検出できた」という偽の緑**になっていた。

1. **B1 の逸脱先を `main` にしていた** → ⚠️ git が二重チェックアウトを拒んで**逸脱が起きなかった**。
   ★ 起票 10 の逐語「main checkout が `main` に居たら checkout は失敗していた」そのもの。
   → ★ どこにもチェックアウトされていない `escape-target` を逸脱先にした。
2. **`escape-target` が `main` と同一コミットだった** → ⚠️ B5（履歴の入れ替え）で
   **HEAD が 1 mm も動かず**、ancestry 検査が正しく「子孫である」と判定した。
   → ★ `escape-target` に独自コミットを積み、`main` にも別コミットを積んで**本物の分岐**を作った。

---

## ★ 突然変異 M-g（★ `/cross-review` 反映後・2026-09-20）

| 変異 | 内容 | 結果 |
|---|---|---|
| M-g | 履歴検査のアンカーを **attempt ごとの HEAD** に戻す（＝ Codex が指摘したバグを再導入） | ★ **B6 の 2 件が赤**（32 → 30 合格） |

⚠️★★★ **B6 は一度「空振りする陰性対照」だった**（★ 記録に値する）:

- ★ 最初の B6 は stub が **1 attempt で commit ＋ amend** する形だった。
  → ⚠️ **M-g を入れても緑のまま**だった。
- ★ 理由: 誤検知は **attempt 2 の worker が *attempt 1 の* コミットを amend する**ときにしか起きない。
  1 attempt で終わると、アンカーがどちらの定義でも **worktree 生成時点と同じ**になる。
- → ★ `verify.test` を `test -f done.marker` にして **attempt 1 を必ず落とし**、
  attempt 2 で amend ＋ marker 作成をさせる形に直したら、M-g で**赤になった**。

★ これで突然変異は **計 7 種**（M-a〜M-g）すべてが該当検査を赤にすることを確認済み。

---

## ⚠️★★★ `/cross-review` が 2 回 fail-closed でブロックされた（★ 手順の記録）

| 回 | 当たった綴り | どこ | 対応 |
|---|---|---|---|
| 1 | 実在サービス風の環境変数名 | ★ D2 のテストフィクスチャ | ★ フィクスチャ側を `CI_TOKEN` へ寄せた |
| 2 | ⚠️ **同じ綴り** | ★ **「なぜ直したか」を書いたコメント** | ★ コメントの綴りも寄せた |

⚠️ 2 回目は `secrets-filter.sh` 自身が逐語で警告している型である ——
「**『漏洩について書く』と『漏洩を再導入する』は同じ動作である**」。

★ **`--ack-filtered` は使っていない**（⚠️ 「人が目で見て確認したときだけ」と明記されている）。
★ `git diff … | bash scripts/secrets-filter.sh; echo $?` が **0** になるまでフィクスチャ側を直した。

⚠️★ **注意**: `git diff <range>` は**コミット済み**を見るので、
★ 作業ツリーを直しただけでは rc は変わらない（★ 2026-09-20 に 1 度取り違えた）。

---

## ★ 突然変異 M-h（★ `/cross-review` 2 巡目の反映後・2026-09-20）

| 変異 | 内容 | 結果 |
|---|---|---|
| M-h | ファイル名由来の id 検証を `bad_ids=""` で殺す | ★ **S9 が赤**（35 → 34 合格） |

⚠️★★★ **S9 でも「検査が空振りする」型を踏んだ**（★ 本タスクで 3 回目）:

- ★ 最初の実装は `for id in $ALL_FILES; do case "$id" in …` だった。
  → ⚠️ **その時点で既に単語分割されている**ので、`0 06.md` は
  `0` と `06` という**見かけ上は正当な 2 つの id** になり、**検証を素通りした**。
- → ★ `issue_ids | grep -vE '^[A-Za-z0-9._-]+$'` と、**分割される前に行単位で**見る形に直した。

★ これで突然変異は **計 8 種**（M-a〜M-h）。
⚠️ **B7 だけは変異対象が無い**（★ 「検出しないこと」を固定する検査であるため）。

---

## ★ `reset --soft` の実測（★ 判断 9 の根拠・2026-09-20）

```text
$ git reset -q --soft "$BASE"
HEAD=a524430… BASE=a524430…
→ git merge-base --is-ancestor "$BASE" HEAD : TRUE   ← ★ 検出されない
--- 作業ツリー ---
a
b
A  b                                                  ← ★ 成果物は残っている
```

→ ★ **`--is-ancestor` は TRUE**（HEAD == BASE なので当然）。⚠️ 検査は通る。
→ ★ ただし **作業ツリーに成果物 `b` がステージされたまま残る**。
⇒ ⚠️ 害は「**コミットが捨てられる**」であって「**別の内容を測る**」ではない。
★ 判断 9 でこれを**許容と裁定**し、検査 **B7** で「**検出しないこと**」を固定した。

---

## ★ 最終の検査結果（2026-09-20）

| 検査 | 結果 |
|---|---|
| `bash scripts/loop-run-guard-test.sh` | ★ **35 / 35**（B1〜B7・S1〜S9・D1〜D2） |
| `bash scripts/loop-worktree-deny-test.sh` | ★ **34 / 34** |
| `bash scripts/check-shell-portability.sh` | ★ **12 / 12** |
| `bash scripts/check-tests-are-wired.sh` | ★ **16 / 16** |
| 突然変異 | ★ **8 種すべてが該当検査を赤にした**（M-a〜M-h） |

---

## ⚠️★★★ CI で赤になった（★ 手元では 35/35 緑・2026-09-20）

★ **PR #212 の Windows `check` が `Loop run guard gate` だけで落ちた**（合格 34 / 不合格 1）。

```text
NG   B6 陰性対照: amend しただけで done にならなかった
{"...","event":"blocked","attempt":1,"detail":"セッション異常終了 subtype=unknown "}
```

**原因**（★ 一次のログから）:

- ★ `loop-run.sh` は `res="$( (cd "$wt" && … claude …) 2>&1 )"` で
  **stdout と stderr を混ぜて**受け取り、それを `jq` で読む。
- ⚠️ B6 の stub は `git commit` を打つ。★ **CI の git は `core.autocrlf` が有効**で、
  「in the working copy of 'w.txt', LF will be replaced by CRLF」を **stderr に出す**。
- → ⚠️ **JSON が壊れて `subtype=unknown`** ＝「セッション異常終了」で attempt が blocked になった。

⚠️★★★ **手元では 1 度も再現しない**（★ このマシンの git は autocrlf が無効）。
★ `docs/agent-shared.md` 逐語「**⚠️★★ 手元の検証は CI の代替にならない**」の実例である。
⚠️ **同じ自己ホスト機（gse-win = G-GEAR）で走っているのに落ちた** —— ★ runner は
NetworkService で **HOME と git config が違う**（★ memory「Win runner tool PATH」と同じ根）。

**対策（★ 二重にした）**:

1. ★ stub 本体を `{ … } >/dev/null 2>&1` で包み、**stdout に JSON だけ**を出させる
   （★ 本物の `claude` の振る舞いに合わせる）。
2. ★ 一時 repo に `core.autocrlf false` / `core.safecrlf false` を設定して環境非依存にする。

**★ 再発防止（⚠️ 「直した」で終わらせない）**:

★ **B2 の stub が stdout と stderr の両方にわざとノイズを出す**ようにした。
→ ⚠️ **B2 が緑であること自体が「ノイズは漏れていない」の証明**になる。

| 変異 | 内容 | 結果 |
|---|---|---|
| M-i | stub の出力を捨てる包みを外す（＝ CI で起きたバグを再導入） | ★ **B2 が赤**（35 → 34 合格） |

★ これで突然変異は **計 9 種**（M-a〜M-i）。
