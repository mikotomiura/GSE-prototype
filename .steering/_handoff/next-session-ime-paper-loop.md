# 次セッション — IME 論文: 評価一式の issue をループで実行する（W1 から）

> 作成: 2026-09-28（`next-session-ime-paper-issues.md` を実施し、27 本に分解した直後）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/_issue-plan.md` と `issues/NNN.md`。状態は着手時に測り直す。
> ⚠️★★★ **分解セッションの前提を持ち込まない**（CLAUDE.md「セッション境界」）。*issue ファイルだけを読んで実行が成立しないなら、分解が失敗している* —— そのときは実行せずに研究者へ返す。

## §0 打ち込む用（G-GEAR で・`/clear` の直後に）

```
.steering/_handoff/next-session-ime-paper-loop.md を読んで、IME 論文の評価一式の W1（issue 001）をモード C で実行してください。
一次資料: .steering/20260927-ime-observation-paper-eval-design/_issue-plan.md（§2 波・§4 機械の割り当て・§7 config の注意）と issues/001.md。
⚠️ 実行の前に docs/loop-engineering.md を Read する。base ブランチ feature/ime-eval-kit を origin/main から作って push してから回す。
⚠️ W1 は 1 本だけ（--issues 001）。緑なら merge ゲート（watchdog の再検証・clean な checkout で 001-acceptance.sh・レビュー）を通して base へ merge → push。
Skill: subagent-delegation・verify-before-claiming・git-workflow。応答は日本語。/model sonnet（実行制御）。
コミットは git add パス指定（-A 禁止）。main への merge は W6 まで終わってから（研究者の判断）。
```

## §1 状態（2026-09-28）

- ★ issue **27 本**（`issues/001.md`〜`027.md`）。任意 3 本（025 / 026 / 027）は `Status: blocked`。
- ★ acceptance は全 27 本に `NNN-acceptance.sh`（共通の関数は `issues/_acceptance-lib.sh`）。実装前は**すべて赤**・違う OS では **exit 2**（2026-09-28 に G-GEAR で確認）。
- ★ `_loop-config.json`: モード C・`parallel: 1`・`base_branch: feature/ime-eval-kit`・`events_path` は **G-GEAR のパス**。verify = `kit/check.sh` / `kit/check.sh --compile` / `scripts/check-shell-portability.sh`（⚠️ W1 の前は `kit/check.sh` が無いので赤 —— 001 が作る）。
- 研究者が確定した判断（`decisions.md`）: 17 = E1 は単体ロガーを評価 ／ 18 = Windows 専用の issue は G-GEAR でループ ／ 19 = 読みは SudachiPy を前処理だけ ／ 20 = GSE で開発・公開時に新 repo へ書き出す ／ 21 = 作成物はすべて `papers/ime-observation/`。slicer の裁定は 22（言語・逐語コピーの範囲・`t` の意味）。

## §2 手順

1. `git fetch` → `git switch -c feature/ime-eval-kit origin/main` → `git push -u origin feature/ime-eval-kit`（★ 分解の PR が main に入っていること）。
2. W1: `bash scripts/loop-run.sh .steering/20260927-ime-observation-paper-eval-design --issues 001`
3. 緑なら merge ゲート → base へ merge → push。⚠️ **依存先の成果物は後続の worktree に入らない**（`docs/loop-engineering.md` 2026-09-27）ので、**波ごとに**これを行う。
4. W2 以降は `_issue-plan.md` §4 のコマンド（★ 機械ごとに `--issues` を分ける。Mac では `events_path` を書き換えてから・その変更はコミットしない）。
5. ★ W1 が緑で基盤に問題が無ければ、W2 から `parallel` を 2〜3 に上げてよい（⚠️ `_loop-config.json` の変更はコミットして base に入れる）。

## §3 気をつけること

- ⚠️ **worker に合成キーを送らせない**。実行器は既定で送らず、acceptance も送らない。★ 実際に送るのは M1 / M5 以降（人とメイン）。
- ⚠️ **プロトコル凍結（M3 / M6）の前に、ImeShadow と正解を突き合わせない**。パイロットは `seal_obs.py` で封印する（issue 015）。
- ⚠️ `papers/` の文書に `.steering/` のパス・被験者 ID・`gse-dataset`・絶対パスを書かない（issue 024 の秘匿の検査に当たる）。
- ⚠️ GSE 本体（`src-tauri/` ほか）を変えない。各 acceptance が `forbid_gse_changes` で検査する。
- ★ マイルストーン M0（コーパス）は W2 の 002 の後。作品の選定・青空文庫からの取得・`pip install` は**研究者の承認**を取ってから。

## §4 やらないこと

- 人の打鍵データを使う（著者本人も含む）／Phase1 / G1 / O1 のデータを混ぜる
- プロトコル凍結前に ImeShadow と正解を突き合わせる
- バッテリーを測る（判断 12）
- 新しい公開 repo を研究者の承認なしに作る・push する（M12）
