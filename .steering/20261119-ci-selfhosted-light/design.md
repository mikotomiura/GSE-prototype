# 設計

## 優先度を下げる

- `check` の頭（checkout の前）に、self-hosted のときだけ走る段を置く。
  - Windows（powershell）: この段の親を順にたどって `Runner.Worker.exe` を見つけ、`PriorityClass = BelowNormal` にする。
    CreateProcess は優先度の指定が無いとき、親が BelowNormal か Idle ならその優先度を子に継ぐ。Runner.Worker が後の段を起こすときは指定しないので、cargo・rustc・テストの実行は BelowNormal で走る。
  - macOS（bash）: 同じく `Runner.Worker` を見つけて `renice -n 10`。子は nice を継ぐ。
- 次の段で、その段自身の優先度を出す（Windows: bash の優先度を powershell から読む。macOS: `ps -o nice=`）。違っていたら警告を出す。CI は止めない。
- GPU は CI で使わない。並列は既に `CARGO_BUILD_JOBS: 2`。

## push の枝

- `on.push.branches` を `[main]` にする（`feature/*` を外す）。PR 側の run が門なので、push 側は二重だった。

## 変数

- PR を出す前に `gh variable delete GSE_WIN_FORCE_HOSTED`（研究者の決定・2026-11-19）。11-05 の仕組み（変数が "1" なら hosted）はそのまま残す。

## テスト

- 手元: `check_workflow_invariants.py`（--self-test・本検査・unittest）、YAML の読み込み、Windows の確かめの段の文を git-bash で空打ち（`Normal` が返る）。
- 実際の run: G-GEAR と Mac の check のログで、下げた行と確かめの行を見る。
