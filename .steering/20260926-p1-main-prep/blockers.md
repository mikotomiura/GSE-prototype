# blockers — D. P1 本体の準備

## B-1: `verify_level: recheck` の watchdog が verdict を出せない（2026-09-26・実行セッション）

- **症状**: W1（001 ‖ 007）で、両方とも worker の verify（test / typecheck / lint / acceptance）は通ったのに、
  watchdog（Haiku）が空応答を 2 回返して `blocked`（`watchdog の verdict を解釈できず fail-closed`）になった。
  ★ 009（`parse`）は watchdog を通らないので影響を受けなかった。
- **実測**（007 の worktree で watchdog の呼び出しをそのまま再現）: `subtype: error_max_turns` / `num_turns: 21` / `result: ""` /
  `permission_denials: 4`。拒否の中身は 4 件とも `bash …/007-acceptance.sh`（`cd … && bash …`・絶対パス・`./` 付きの綴り違い）。
- **原因**: `scripts/loop-run.sh:348` の `WD_TOOLS` に acceptance スクリプトの実行が許可されておらず、
  watchdog は「acceptance を独立に再実行する」という本務ができないまま 20 ターンを使い切る。
  （★ 同じ `loop-run.sh` の注記「`recheck` の watchdog は完全に信頼できる gate ではない・acceptance スクリプトのほうが確実」と整合する。）
- **なぜ直さないか**: 直すなら `WD_TOOLS`（許可の綴りは絶対パス・`cd &&` 複合で当たらない）と watchdog のプロンプト（実行すべき正確なコマンドを渡す）の両方を変える必要があり、
  共有基盤（`scripts/loop-run.sh`）の変更になる。本 task の Allowed Files の外で、レビューとテストが要る。→ **起票候補 P1-L**（下記）。
- **対処（判断 23）**: `verify_level: recheck` の 7 本（001〜005・007・008）を `parse` に落とす。
  ★ 落としても **acceptance は 2 段で残る**: (1) `loop-run.sh` の `run_verify` が `issues/00X-acceptance.sh` を worktree の中で回す（AC の機械検査）／
  (2) merge 前にメインが **clean な検証用 worktree**（`/c/wt/GSE-prototype-verify`）で 10 本 ＋ 過去 3 本を正しい終了コードで回す（handoff の指示）。
  watchdog が担っていたのは「LLM の意見つきの再実行」で、acceptance の再実行自体は (2) が同じ強さで担う。
- **切り戻し**: 上の 2 段で足りないと判断される場合は、issue の `verify_level` を戻して P1-L を先に直す。

### 起票候補 P1-L（`scripts/loop-run.sh` の watchdog）
- `WD_TOOLS` に acceptance の実行を許可し、プロンプトに `bash <TASK_DIR>/issues/<id>-acceptance.sh` を**そのまま**書く（許可の綴りと一致させる）。
- 空応答（`error_max_turns`）を「AC 未充足」ではなく「watchdog の故障」として区別して events に残す。
- ⚠️ 直したら `recheck` の issue で 1 本試してから戻す（`--dry-run` では観測できない）。

### 証拠
- W1 で `blocked` になった枝の先端（クリーンアップで撤去した）: `loop/001-issue` = `aa4892c1` / `loop/007-issue` = `4ef99cae`（reflog に残る）。
- 再現の生出力: 007 の watchdog 呼び出し → `error_max_turns`・21 ターン・`result` 空（本セッションの scratchpad `wd-007.json`）。

## B-2: `004-acceptance.sh` の「Rust 不変」が `main` との差分で、007/008 を merge した base では常に赤（2026-09-26・実行セッション・★ 分解の欠陥）

- **症状**: 004 の worker は実装とテストを終えてコミットしたが、`004-acceptance.sh` の 12 行目（`git diff --quiet main -- src-tauri/src/`）が rc=1 になり、
  worker は「gate であり Allowed Files の外」として書き換えずに Status を `blocked` にして止まった（`blocked`・events）。
- **原因**: base（`feat/p1-main-prep`）は W1/W2 で merge した 007/008 の Rust の変更（`dispersion.rs` / `mod.rs` / `replay.rs`）を既に含み、`main` にはまだ無い。
  → `main` との差分で「004 が Rust を変えていない」を見ると、**004 が何を書いても赤**になる。分解時に「Rust の issue は別の chain だから交差しない」と考え、acceptance の**基準ブランチ**を見落とした。
  （★ worker の診断は正しい。ただし変更の出所は「issue 001」ではなく 007/008。）
- **他の acceptance への波及**: 全 acceptance の `git diff … main` を grep して確かめた。他は凍結 JSON・schema・fixture・`Cargo.toml`・007/008 が触らない Rust ファイル（009 の `restart.rs` / `stall_onset.rs`）・`scripts/build_analysis_db.py` の比較で、影響しない。006 / 010 は最初から base（`feat/p1-main-prep`）を基準にしている。
- **対処（判断 25）**: 004 の 12 行目の基準を `feat/p1-main-prep`（無ければ `main`）へ変える。★ 強さは変えていない（004 の変更が Rust に及べば赤）。
  修正版を **clean な検証用 worktree で worker のコミットに対して**回し、rc=0（13 テスト OK・AC5 の実 CLI・AC7 の白リスト・配線検査を含む）を確認した。
- ⚠️ **教訓（issue-slicing への還元）**: acceptance の「変えていない」検査は、**base が他の issue の merge で進むこと**を前提に、`main` ではなく base を基準にする。
