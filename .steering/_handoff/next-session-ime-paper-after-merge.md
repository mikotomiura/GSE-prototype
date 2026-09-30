# 次セッション — IME 論文: main への merge の後 —— Mac の確認と M0（コーパスの確定）

> 作成: 2026-09-30（G-GEAR で `feature/ime-eval-kit` を main へ merge したセッションの最後に）。前の handoff（`next-session-ime-paper-after-w6.md`）の後継。前のものは読まなくてよい。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（判断 72〜78）・`blockers.md`（B14）・`issues/024.md`（追補 2・3）・`tasklist.md`・`_issue-plan.md` §5。状態は着手時に測り直す。
> ★ 評価一式は **main に入った**（PR #276）。以後の作業は main から枝を切る（`feature/ime-*` など）。両方の機械が同じ枝に push するときは、push の前に `git fetch` → `git pull --no-rebase`（force しない）。

## §0 打ち込む用

### Mac（先に・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-after-merge.md を読んで、§2 の Mac の確認をしてください。
main を pull し、main の clean な worktree で .steering/20260927-ime-observation-paper-eval-design/issues/024-acceptance.sh を回し、
（1）失敗 0 件か（2）書き出しの一覧の SHA-256 が G-GEAR の値と一致するか（3）POSIX だけの検査（読めない dir・実行権限）が緑かを確かめる。
あわせて Mac で回せる全 acceptance（001〜004 006 007 010〜012 015〜024 028）を回す。
結果を tasklist.md に記録し、一致しなければ blockers.md に起票して原因を測る（B13 の教訓: 先に測定器を対照で検算する）。
Skill: verify-before-claiming・git-workflow。応答は日本語。コミットは git add パス指定（-A 禁止）。
```

### どちらでも（Mac の確認の後）

```
.steering/_handoff/next-session-ime-paper-after-merge.md を読んで、§3 の M0（コーパスの確定）を始めてください。
作品の選定と青空文庫からの取得は研究者の承認が要ります（AskUserQuestion で推奨と理由を添えて確かめる）。
一次資料: _issue-plan.md §5 の M0・design.md §2・kit/corpus/README.md。Skill: reproducibility-discipline・citation-ssot。応答は日本語。
```

## §1 状態（2026-09-30 の終わり）

- `feature/ime-eval-kit` を main へ merge した（PR #276）。GSE 本体（`src-tauri/`・`src/`・`scripts/`・`.github/`）は変えていない。
- この日の流れ（判断 72〜78）:
  - 判断 72: 今日 merge・Codex の上限を一時的に 750,000 に引き上げて /cross-review を 2 巡（範囲は GSE 本体に入る 3 ファイル＋公開の境界）。終わって 300,000 に戻した。当日の合算は 800,363 / 14 回（main との 2 度の merge で合算）。
  - 判断 73: 事前登録の凍結（M3 / M6）は **OSF Registries** に登録して公開の日時を示す（研究者が行う）。M3 / M6 の Done に「登録の URL・日時を `experiment/notes.md` に・最初の本計測の run より前」を足した。未決: エンバーゴを使うか・M6 の追補を別の登録にするか（M6 の前に一次で確かめる）。
  - 判断 74〜76（1 巡目）: 書き出し器は `kit/export/*.internal.*` に改名して**公開しない**・書き出しの最後に `_style_check.py` を出力に回す・角括弧の `[P017]` も止める。＋仕様の範囲の直し (a)〜(m)。
  - 判断 77 → 78（2 巡目）: 連続する区切りは混ざっていても飛ばす。`kit/analysis/pipeline.py:1481` の selftest の架空の名前 `x` を **`harry`** に（`alice` はその selftest のログイン名と重なる）。＋仕様の範囲の直し (a)〜(n)（変換後の出力の署名・壊れた `.git`・検査の道具を commit に固定・道具が読まない種類を書き出さない・web の URL を誤って止めない・出力を検査の後に改名 ほか）。
  - B14: Codex の前の機密フィルタが 024 の acceptance の架空の値（`.env` の陰性対照）に当たり、研究者の確認で `--ack-filtered`。
- ★ **書き出しの呼び方が変わった**: `python3 papers/ime-observation/kit/export/export.internal.py --out DIR [--allow-missing-license] [--style-check PATH] ...`。git の作業ツリーの中では、検査の道具（既定は `.steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py`）も commit 済みでなければ止まる。書き出し器は公開されない。
- ★ 024 の書き出しの一覧の SHA-256（G-GEAR・Windows・`papers/` = merge の時点）: `298a470b94f0fe6a5b0d953ff0b37c0420e38afaedca757b0f227e309d5ca4a0`（89 ファイル）。⚠️ `papers/` を変える commit の後では値が変わるので、比べるのは同じ内容どうし。
- 全 acceptance（G-GEAR・clean な checkout）: G-GEAR（Windows 11・`5eda5dca` の clean な checkout）で Windows で回る 22 本（001〜003 005 006 008〜011 013〜024 028）がすべて失敗 0 件・macOS 専用の 004 / 007 / 012 は exit 2（対象外）・`_style_check.py papers/ime-observation` 違反 0 件。

## §2 Mac の確認（次にやること）

- 024 の acceptance を Mac で回す（判断 68: 同じ commit の書き出しは機械によらず同じバイト列）。POSIX だけの検査（`chmod 000` の読めない dir・`*.rs` に実行権限が無く `*.sh` にはある）はこのとき初めて走る。
- ⚠️ 書き出しの (g) は書き出す機械のホスト名も探す。Mac のホスト名が公開物の中に現れれば止まる（止まったら規則を緩めず、当たった行を直す）。
- ⚠️ 書き出し器は git の作業ツリーの中では「追跡済みで HEAD と一致」を求める。acceptance は clean な worktree で回す。

## §3 次のマイルストーン（`_issue-plan.md` §5）

1. **M0**: コーパスの確定（作品を選ぶ・青空文庫から取得〔研究者の承認〕・`sudachipy` / `sudachidict_core` を `kit/corpus/requirements.txt` に pin・`build_corpus.py --validate`）。★ `kit/corpus/data/` には直下の `*.jsonl` だけを置く（それ以外は書き出しが止まる・判断 78 (d)）。
2. **M1**: macOS の較正パイロット。★ ロガーは書き出しからビルドする（判断 68）。
3. **M3**: 事前登録の凍結（macOS 版）→ ★ OSF Registries に登録（判断 73・研究者）。登録の日時は M4 の最初の run より前。
4. 公開 repo の作成・DOI は M12（研究者）。

## §4 気をつけること

- ⚠️ Codex の台帳（`.codex/budget.json`）は枝ごとに記帳される。merge では両側の増分を合算する（`git checkout --` で戻さない）。回す前に origin/main の台帳も見る。
- ⚠️ heredoc の中のバックスラッシュは潰れる（今回も 2 回踏んだ）→ 文書は Write / Edit で書き、`od -c` で確かめる。
- ⚠️ 書き出しの検査は `README.internal.md` に誤検知の例（`tokenizer_notes.txt`・`secret-sharing.md`・`*.asc`）と直さない形（空白を含むパス）を書いてある。止まったら規則を緩めず、名前か中身を直す。
- ⚠️ 人の打鍵データを使わない。凍結（M3 / M6）の前に ImeShadow と正解を突き合わせない。新しい公開 repo を作らない（M12・研究者）。
