# Loop 基盤の是正（起票 P1-I / J / K / B / D ＋ 起票 A）

## 背景

P1 前タスク（`.steering/20260921-p1-prereg-cli-poles/`）の Loop 実行で、Loop 基盤そのものの欠陥を 6 件踏んだ
（一次: 同 `decisions.md` の起票 P1-B / D / H / I / J / K・判断 18 / 21 / 22、`_loop-retrospective.md` §2）。
加えて `.steering/20260921-loop-spawn-resolve-base/blockers.md` の**起票 A**（spawn 経路の `id` / `short` が無検査）が未解決。
いずれも「無人モードで黙って誤る」型であり、次に Loop を回す前（B → D）に塞ぐ。

## ゴール

次の 6 件を是正し、各是正に**変異で赤になることを確かめた**検査を付ける。

| 起票 | 是正後の振る舞い |
|---|---|
| **P1-I** | verify 緑でも、worktree が dirty ／ worktree 生成時点からのコミットが 0 件なら `issue_done` を出さない。**失敗 attempt（種別 `uncommitted`）**として次の attempt へ進む |
| **P1-J** | 切り元のローカルブランチと `origin/<base>` を**祖先関係で分ける**: 一致 → origin ／ ローカル先行 → ローカル ／ ローカル遅れ → origin ／ 分岐 → fail-closed。選んだ理由を stderr（→ run ログ）に出す |
| **P1-K** | `loop-spawn.sh` の worktree 生成を**ロックで直列化**（mkdir ロック・git-bash に flock が無い前提）。`git worktree add` 失敗で**ブランチだけ残った**ら片づける |
| **P1-B** | パス限定の allow（例 `Bash(bash .steering/*/issues/*-acceptance.sh:*)`）が `claude -p` で効くかを**実測**。効けばテンプレートと loop-engineering.md に入れる。効かなければ**広げずに記録**する |
| **P1-D** | `issue_deps_raw` が太字などの装飾を剥がしてから拾う。拾えない 3 桁数字が Dependencies 節に残れば **WARN を出して続行** |
| **起票 A** | spawn 経路の `id` / `short` に `--cleanup` 経路と同じ検証を入れる |

## スコープ

### 含むもの
- `scripts/loop-spawn.sh` / `scripts/loop-run.sh` の是正
- 検査: `scripts/loop-run-guard-test.sh` / `scripts/loop-spawn-cleanup-test.sh` の拡張（または新規の同型テスト）
- `docs/loop-engineering.md`（events 語彙 `uncommitted` の追加・各是正の運用記述）、`.steering/_template/loop-config.json`（P1-B が効いた場合）、`/loop-status` の board が新語彙を解釈できること

### 含まないもの
- ⚠️ **P1-H**（verify に回帰 acceptance を足す）—— 起票のまま残す。当面は判断 22 の運用（メインが全 acceptance を回す）で補う
- P1-A / C / E / F / G（P1 本体側の起票）
- Loop をこのタスク自身に使うこと（直す対象で自分を回す循環を避ける）
- P1-B が効かなかった場合に `Bash(bash:*)` 等へ許可を広げること

## 受け入れ条件

- [ ] P1-I: stub `claude` で「verify 緑・dirty」「verify 緑・コミット 0」の各 attempt が `issue_done` にならず `uncommitted` で次 attempt に進む検査が緑。判定を潰す変異で赤
- [ ] P1-J: ローカル先行／遅れ／一致／分岐の 4 状態の検査が緑（分岐は非 0 終了）。変異で赤
- [ ] P1-K: 2 本同時 spawn がどちらも worktree を得る検査が緑。`worktree add` 失敗時に残骸ブランチが残らない検査が緑。変異で赤
- [ ] P1-B: 実測結果（効いた／効かない・`permission_denials` の値）が decisions.md に記録されている
- [ ] P1-D: 太字依存が拾えること・拾えない数字で WARN が出ることの検査が緑。変異で赤
- [ ] 起票 A: spawn 経路で `-` 始まり等の `id` / `short` が拒否される検査が緑。変異で赤
- [ ] 既存検査（`loop-run-guard-test.sh` / `loop-spawn-cleanup-test.sh` / `loop-worktree-deny-test.sh` / `check-shell-portability.sh`）がすべて緑
- [ ] code-reviewer ＋ security-checker ＋ `/cross-review` 済み

## 関連ドキュメント

- `docs/loop-engineering.md`（Loop の SSOT）
- `.steering/20260921-p1-prereg-cli-poles/decisions.md`・`_loop-retrospective.md`
- `.steering/20260921-loop-spawn-resolve-base/blockers.md`（起票 A）
- `.steering/_handoff/next-session-loop-foundation-p1-fixes.md`（⚠️ 一次ではない）

## 運用メモ
- /reimagine 適用: No
- 理由: 各起票の是正方針は grill で研究者が選択済み（decisions.md 判断 1〜6）。複数案の比較はそこで済んでいる
- 実行方式: 単発タスク（/fix-bug）。設計はメイン（Opus）、実装は Sonnet subagent、レビューはメイン

## 再現・期待と実際・ログ（/fix-bug Step 2 —— ★ 一次の実測記録から写す。研究者への再聴取はしていない）

| 起票 | 再現（実測） | 期待 | 実際 | ログ・根拠 |
|---|---|---|---|---|
| P1-I | issue 005 / 008 で worker が `max_turns` に達し未コミットのまま終了 → verify 緑 | done にしない | `issue_done` が出た（空の merge になりうる） | 前タスク decisions.md 起票 P1-I・救済コミット `49d867b` |
| P1-J | PR のため push 後、ローカルで 005 を merge（未 push）→ 006 を spawn | ローカル（005 を含む）から切る | `origin`（005 を含まない）から切られた | 同 起票 P1-J・provenance「1 コミット後ろ」 |
| P1-K | `loop-run.sh --parallel 2` で 007 ‖ 008 を同時 spawn | 両方 worktree を得る | `error: could not lock config file .git/config: File exists`・008 はブランチだけ | 同 起票 P1-K |
| P1-B | worker が `bash <acceptance>` を実行 | 実行できる | 承認待ちで拒否（`permission_denials=16`） | 同 起票 P1-B・001 attempt 1 |
| P1-D | Dependencies に `- **001**（…）` と書く | 依存 001 を拾う | 全 issue `deps=[]`・警告なし | 同 判断 18 付随 |
| 起票 A | spawn 経路に `-x` 等の id / short | 拒否 | 無検査 | `.steering/20260921-loop-spawn-resolve-base/blockers.md` 起票 A |
