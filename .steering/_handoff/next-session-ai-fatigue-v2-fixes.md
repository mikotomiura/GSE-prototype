# 次セッション — AI 疲労 文献 DB v2: 完了レビューの直し → 作り直し → Codex 2 巡目 → 出荷

> 作成: 2026-10-03（`ai-fatigue-v2` の 3 つ目のセッションの終わり・コンテキストが約半分になったので直しの波の前で区切った）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20261002-ai-fatigue-v2/`（decisions **判断 6〜9**・tasklist）。
> ★ ユーザーは **判定者 1**。DB を作ったのは「相手の研究者」。研究者が決めることはユーザーに聞かない。★ 3 つのファイルは**まだ研究者に渡していない**（全部仕上げてから渡す・記憶 `project_ai_fatigue_handover_when_complete`）。
> ★ 前のメモ `next-session-ai-fatigue-v2-finish.md` の §2 の 1〜5 は終わった。残りは 6（完了）だけで、その途中の「直し」から。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-v2-fixes.md を読んで、AI 疲労 DB v2 の残り（decisions 判断 9 の指摘 1〜17 の直し → 表と提案の作り直し → selftest・メタ変異・--final → コミット → Codex 2 巡目 → 出荷）を進めてください。worktree は C:\wt\ai-fatigue-v2（ブランチ docs/ai-fatigue-v2）。C:\GSE-prototype は別のトラックの作業ツリーなので触らない。

⚠️ 私（判定者 1）に文献の判定を求めない。判定・数・研究者に渡す値を変える直しは無いはず（変わったら止まって報告）。
⚠️ git add -A / git add <dir> は使わない。抄録・本文・記入表・問いの逐語はコミットしない。外部に出る操作（研究者への送信・著者への照会）はしない。push と PR は完了時の出荷フローで。
★ 応答は日本語。サブエージェントの前に subagent-delegation Skill、.docx を作り直す前に anthropic-skills:docx Skill。
```

## §1 このセッションで終わったこと（2026-10-03）

| 何 | 状態 | どこ |
|---|---|---|
| 判定者 1 の「除外 E4 背景」6 件の読み方 | ✅ 意図は「範囲の外・背景として残す」・値は変えず注記して残す | 判断 6 |
| ログ 214 行（ta1 71・ta1e 1・ai_ta 142） | ✅ `check_log.py` 違反 0・`--session` 一致・selftest・メタ変異 12 規則 PASS | `screening-log.jsonl`・`build_log.py`・`check_log.py` |
| 追加候補の表 v2（`0d830c1f…`） | ✅ `check_candidates.py --final` 違反 0・メタ変異 20 規則 PASS。R〜W 列・『一致の表』『群ごとの一覧』 | 判断 8 |
| 提案のドキュメント v2（`99678b75…`・35 頁） | ✅ `check_proposal.py` 違反 0・メタ変異 14 規則 PASS・LibreOffice で画像にして目で見た | `proposal/proposal-v2.md`・判断 8 |
| Downloads の退避ファイルなど 38 個を削除 | ✅ 判定者 1 の確認（4 問とも推奨どおり）・名前と SHA を記録 | 判断 7 |
| コミット | ✅ `6f2fe81f`（未 push）。このメモと判断 9 は次のコミット | — |
| 完了レビュー | ✅ code-reviewer（CRITICAL/HIGH 0）・security-checker（CRITICAL/HIGH/MEDIUM 0）・Codex 1 巡目（2 回・112,456 tokens） | 判断 9（指摘 18 件・すべて一次で確かめた） |

数（変わらないはず）: 判定者 1 = 全文段 8（除外 4・保留 4）＋ 題名・抄録段 71（含める 49・保留 15・除外 7〈E2 1・E4 背景 6〉）／AI の予備判定だけ 142（含める 83・除外 59）／一致 48/71／医療者 93 件はすべて AI。

## §2 次にやること（この順）

1. **判断 9 の 1〜17 を直す**（道具 6 本と原稿）。直す方針は判断 9 に書いた。要点:
   - 書き方（1・9・10）: 「AI の判定を見ない／見ず」→「問いに AI の判定を載せていない（判定者 1 は判定の前に評価版を読んでいる）」／「S02-08 など追加候補の 7 件と X01」／判定者 2 用の版の作り方から『品質評価』を外す（`INTRO_MUST` も）。
   - 対応表（2・3・6・7）: 題名・抄録段の除外の用途を E コードで分ける（E2・E4 背景 → 背景保持、E1・E3 → 除外）。全文段の含めるの自由記入の用途は result の use。9.3 の E コードは除外のときだけ。9.1 の判定者1 の期待は 34 件のログから。★ それぞれ緑の対照（E1 の理由のログ・含めるの件を入れた前のログの写し）と変異を selftest に足す。
   - 検査の穴（4・5・14・15・17）: 空行の下の余分な行・例外を検出と数えない（3 本）・逐語の照らし方・原本が無ければ違反・群の行の順と「43 件」の文。
   - xlsx の内部の語（8）: 『探索の一覧』K 列の「・判断 6」を落とす（検査器も独立に同じ変換）＋ xlsx の禁止の語の規則。
   - .docx（11）: thumbnail の部品・関係・型の宣言を消し、app.xml を中立に。検査器で部品の一覧を許可した名前に限る。
   - 置き換え（12・13）: 提案の前に表の SHA を照らす・dry-run の出力を消す・退避を finally で消す・SHA の記録を一時ファイルから置き換える・止まる表示に「前の実行が記録を書く前に止まった可能性」。
   - 16: 判断 6 に訂正の行を足す（本文は書き換えない）。
2. **作り直す**: `build_candidates.py` → `build_proposal.py`（★ どちらも Downloads と archive が記録の SHA と一致していることを先に確かめる。今は表 `0d830c1f…`・提案 `99678b75…`）。数・判定の値が変わったら止まって報告。
3. **検査**: 3 本の `--selftest`（★ `check_candidates.py --selftest` は数分・裏で）→ `meta_mutate.py` 3 本（★ 10 分以上・裏で）→ `check_log.py --session`・`check_candidates.py --final`・`check_proposal.py` 違反 0 → LibreOffice で PDF → 画像にして目で見る（`"/c/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf`、画像は `uv run --with pymupdf`）。
4. **漏れの検査**: コミットするファイル（xlsx・docx の XML の部品すべて・原稿・ログ・記録）に抄録と問いの逐語の 40 字の窓が無いこと。このセッションの道具は scratchpad の `leak_scan.py`（`C:\Users\johnd\AppData\Local\Temp\claude\C--GSE-prototype\114858cc-76a4-4d2f-92d3-4da26a97e57a\scratchpad\leak_scan.py`）。★ 題名の断片は除く（問いの 2 行目が題名なので）。陽性対照（抄録を 1 つ混ぜると NG）も回した。`scripts/` に写して残してもよい。
5. **コミット** → **Codex 2 巡目**（直しの差分だけ・パス限定・xlsx/docx/ログは渡さない・出力は scratchpad。記憶 `project_cross_review_two_rounds`）→ 指摘を一次で確かめて対応 → `tasklist.md` の完了の項目（元の資料 4 つの SHA・前の 2 タスクに差分なし・ステージに抄録なし）を確かめて埋める → **出荷**（git-workflow ルール 6）。
6. **完了の報告**で判定者 1 に伝えること: 渡す直前に Excel で開いて保存すると最終更新者にアカウント名が入る → 渡す直前に `check_candidates.py`・`check_proposal.py` を回す（SHA が違えば止まる）（判断 9 の 18）。
- コンテキストが半分ほどになったら、区切りで引き継ぎを書く。

## §3 落とし穴

- **Codex の台帳**（`.codex/budget.json`・作業ツリーで M・CRLF の警告が出るが git が LF にする）: 本ブランチの today は 2026-10-03 / 112,456 / 2 回、history の 2026-10-02 は 402,115 / 9 回。origin/main の 2026-10-02 は 422,989 / 10 回（本ブランチの分岐の後に他の PR が +20,874 / +1）。★ merge で衝突したら `_comment_merge_2026_09_11` の規則どおり和を採る（10-02 は origin/main の 422,989 が本ブランチの 402,115 を含む）。`git checkout --` で戻さない（記憶 `feedback_codex_budget_is_a_ledger`）。
- Codex の /cross-review は 1 回 2000 行を超えると人の承認が要る（コマンドの手順）。分けて回す。ラッパーは `C:\GSE-prototype\scripts\run-codex-review.sh <base>..<head> -- <paths>` を worktree の中から呼ぶ（台帳は worktree の `.codex/budget.json` に記帳される）。
- 前のタスクの `check_candidates.py --final` と `check_proposal.py`（v1）は、Downloads の表が v2 に変わり v1 の .docx を消したので赤になる（v1 の時点の記録として残す・判断 1・判断 7）。
- 記入表 1 の原本（`Downloads\ai-fatigue-fulltext\_abstracts\ta_sheet1_original.xlsx`）は残した。`check_log.py` が行の順を確かめるのに使う（直し 15 で、無ければ違反にする）。
- git-bash: `uv run python` にパスを渡すときは Windows の形・`PYTHONIOENCODING=utf-8`・json を読むときは `encoding='utf-8'`（cp932 で落ちる）・`git show origin/main:<path>` は `MSYS_NO_PATHCONV=1`・heredoc にバックスラッシュを書かない・`… | tail` は終了コードを隠す。
- 前のメモ（`next-session-ai-fatigue-v2-finish.md` §4）の落とし穴もそのまま有効。
