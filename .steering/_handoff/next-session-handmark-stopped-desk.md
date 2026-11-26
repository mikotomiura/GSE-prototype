# 引き継ぎ: 手跡の止まりの層（ADR-056）の試作 —— PR-b（机上の確かめ）

作成 2026-11-21（G-GEAR・Windows）。前のセッションは設計と PR-a（状態・層・駆動役・窓・切り替え）まで終えた。研究者の指示により、PR-b は新しいセッションで行う（判断 12）。
応答と記録は日本語で書く。★・⚠️ などの記号を多用しない（研究者の指摘）。

## 0. 始める前に確かめること

- worktree は `C:\GSE-wt\stopped-state`、枝は `feature/handmark-stopped-state-prototype`。origin/main `bd557a6b` から切った。並行のセッションがあるので、この worktree で作業する。`git fetch` してから、枝が origin と揃っているかを見る。
- タスクの記録は `.steering/20261121-handmark-stopped-state-prototype/`。requirement.md・design.md（採用はハイブリッド）・decisions.md（判断 1〜12）・tasklist.md を先に読む。`/start-task` はもう済んでいる。続きなので `/add-feature` の Step E から入る。
- PR-a のコミット:
  - `1bfe092e`: 止まりの層の試作
  - `f30b822c`: 点検の指摘の直し
  - 検査の結果: cargo test --workspace 1394 passed・clippy `-D warnings`・fmt・tsc・`npm run test:handmark` 54 passed。どれも緑。
  - PR はまだ出していない。タスクの完了の時に、PR-b とまとめて /cross-review にかけてから出す。PR-a と PR-b を別の PR に分けるかは、そのときに研究者に確かめる（判断 9 の分け方）。

## 1. 先に読むもの

- `docs/adr/ADR-056-handmark-stopped-state.md`。D2 の確かめ方 (i)〜(iii) と、D4 の漏れの検査。
- `.steering/20261120-handmark-coexistence-design/design-proposal.md` の §4.4。「確かめ方」の 2・3。
- PR-a のコード:
  - `src-tauri/src/analysis/handmark/stopped.rs`: `replay_stopped`・`replay_stopped_live`・`ambient`・`StopGate`
  - `src-tauri/src/analysis/handmark/state.rs`: `Stage::idle_since`
  - `src/components/handmarkStoppedDraw.ts`: `drawStopped`
- 机上の道具の今の流れ（前のセッションの影響調査の結果。行番号は `bd557a6b` 時点）:
  - `desk.rs` の入口は `build()`（:1008）。窓ごとに A と B を作る（:1108-1109）。
  - A は `a_features`（:607）で作る。入力は打鍵の時刻とポインタのビンだけ。
  - B_state は `b_state_features`（:796）で作り、列は `B_STATE_NAMES`（:60）の 13 列。入力は speed・irreg・phase の差・場・波紋の数で、drift と layout_seed は入っていない。
  - 見た目は Rust 側で描き直す。`stream_samples`（:724）が `Stage::new` から `press`・`advance_to` を `LIVE_LAG_MS` 遅れで流し、`replay_live` とビット一致する。
  - B_pixel は、`bin/replay.rs` の `write_frame`（:2195-2215）がコマをバイナリに書き、`experiments/20261115-handmark-leak-desk/scripts/pixels.mjs` が `handmarkStageDraw.ts` で描く。`pixels.mjs` はオフセットを直書きしている（:36-59）。
  - 検定は `stats.py`・`report.py`。版は `DESK_VERSION`（:37）。
  - 一時停止の区間は、`DeskFile.pauses`（:157・`recording_pause` の行）として既に読んでいる。今は窓を除くことにだけ使う。
- `.steering/20261115-handmark-desk-tool/`（机上の道具の設計）と、`experiments/20261115-handmark-leak-desk/` の README。
- `.claude/skills/reproducibility-discipline/SKILL.md`（`experiments/` を触るので必須）・`docs/experiment-tracking.md`。

## 2. やること（design.md §7・tasklist の PR-b）

1. **机上の出力の口**: `desk.rs`・`bin/replay.rs` に `--stopped <cfg>`（`parse_stopped_cfg` と同じ書式）を足す。
   - このときだけ、止まりの層のコマの列と、止まりの列を足した B′ を出す。
   - 切っているときの出力・`write_frame`・`DESK_VERSION` は今と同じにする（回 2 を揺らさない・判断 10）。
   - 再生には `DeskFile.pauses` を `(時刻, 一時停止か)` の列にして渡す。区間の起点 t0 は、今の `segments()` と同じ値を使う。
   - 種は区間の日の種（`seg.seed`）を使う。
   - `replay_stopped_live` とのビット一致のテストを足す。
2. **重ね描き**: `experiments/20261121-handmark-stopped-desk/` を作る（reproducibility-discipline に従う）。
   - 今のコマの画に、画面と同じ順（`drawFrame` → `drawStopped`）で重ねる。`pixels.mjs` は書き換えずに、新しいスクリプトで行う。
3. **経過が読めない (i)〜(iii)**（ADR-056 D2）:
   - 本人の段 1 の記録を、形 3 つ × W（10・20・30 秒）の研究者用の設定で描き直す。
   - 立ち上がりと W より長い止まりについて、移り変わりが終わった後のコマを使う。
   - (i) 1 枚の見た目から、止まりの始まりからの経過を推す。
   - (ii) 数十秒ぶんの時系列から、W より前の経過を推す。
   - (iii) 時系列から、`grid_start` からの経過を推す。
   - 合否は判断 9 による。止まりの単位でまとめた交差検証で当て、ラベルを止まりの単位で入れ替えた帰無の分布の 95 パーセント点を超えたら「偶然を上回った」とする（片側 5%）。
   - 結果には、止まりの数と帰無の分布の幅を必ず添える。
   - 見た目は、今ある基層（`drift` の霧と粒）・ポインタの跡・止まりの層を合わせた最終の画から取る。
4. **漏れの検査**（ADR-051 D3）: 今の手順で、A と B′（今の B に v と ambient の列を足したもの）を比べる。
5. **今ある基層の扱い**: (iii) で今の基層（`drift`）が偶然を上回ったら、研究者に確かめる。置き換えるか（有限の窓の平滑）、残すか（設計案 §4.4）。黙って消したり残したりしない。
6. 結果は decisions.md に新しい判断として書く。推測で書かない。results/ の一次を読んでから書く。
7. 完了処理:
   - /cross-review を 2 巡回す（1 巡目は矛盾、2 巡目は足した規則の境界条件）。範囲は PR-a と PR-b の差分 `bd557a6b..HEAD`。
   - その後 /finish-task を回し、出荷のフローに進む。
   - 次のタスク（研究者自身の試し・手動の確かめ・値の確定・ADR-056 の「決めずに残すもの」1）の引き継ぎを書く。

## 3. 決まっていること（このタスクの判断）

- 判断 2: 一時停止が明けた後も、最初の打鍵までは返さない。
- 判断 3: 段 1 の後期の配布物には入れない。
- 判断 4: 形は 3 つを切り替える。
- 判断 5: 完了の線は、研究者自身の試しの前に置く。
- 判断 7: 窓だけに出す（端の帯は変えない）。
- 判断 8: 打鍵の後なら、マウスだけを使う間も出す。
- 判断 9: 合否は片側 5%。
- 判断 10: ハイブリッドで、切っているときは何も変わらない。
- 判断 11: 点検の指摘を直した。
- 判断 12: 手動の確かめは試しのタスクへ回した。PR-b は新しいセッションで行う。

## 4. してはいけないこと（CLAUDE.md と引き継ぎの制約）

- 止まりの長さ・経過時間・残り時間・累計を、見た目でも数字でも返さない（ADR-025 D1・ADR-048 D2・ADR-056）。推定の出力（`p_stuck` など）を手跡に入れない（ADR-047 D2）。
- 研究者自身に止まりの層を画面で見せない。段 1 の期間の外で行う（判断 5・判断 12）。机上の描き直しは晒しにならない。
- 本人の段 1 の記録・NDJSON の生ログ・打鍵の内容を、外部の LLM（Codex を含む）に送らない。/cross-review の Codex 側には、コードの差分だけを渡す。記録や results の数値の生データを含めない（`docs/external-skills.md`・data-privacy）。
- 回 2（12-09 以降）で使う机上の道具の、切っているときの出力を変えない。
- 再生の決定性（`to_bits` の一致・ADR-051 D5）を壊さない。
- `git add -A`・`git add <dir>` を使わない（明示のパスだけ）。権限や allowed-tools を自分で広げない。`.codex/budget.json` を `git checkout --` で戻さない。
- `cargo` は `src-tauri/` から叩くか、`--manifest-path src-tauri/Cargo.toml` を付ける。`println!`・`eprintln!`・`winapi`・TS の `any` を使わない。ログは `tracing`。
- 事実を断定する前は `verify-before-claiming`、サブエージェントへ渡す前は `subagent-delegation` の Skill を読む。サブエージェントには model・範囲・禁止・締切を書く。入れ子にしない。
- 検査のスクリプトは、実際の記録と実装で通して回すまでは「確かめていない」として扱う。変異で赤になることも確かめる（memory の方針）。
- 窓の列の検査（`handmark_guard.rs` の `the_window_lists_only_named_slots`）は、`Array(` を含む書き方（`Array.isArray` も含む）を拾う。窓や描画の TS を書くときは、この検査に注意する。

## 5. 次のタスク（PR-b の後）に渡すもの

- 研究者自身の数日ずつの試しと、手動の確かめ（3 つの形が出るか）。どちらも段 1 の期間の外で行う。起動は `GSE_DEBUG=1` と `GSE_HANDMARK_STOPPED=form=band;rise_ms=2000;window_s=20;strength=0.5` の形。
- 値（移り変わりの長さ・記憶の窓・強さ・形）は研究者が決める。決めたら、ADR-056 の「決めずに残すもの」1 を閉じる新しい判断を書く（ADR の本文は書き換えない）。
- 机上の道具（ADR-051 D7 の PR 4）への受け渡し: 境界の状態（判断 2・判断 8）と、確かめ方 (i)〜(iii)（ADR-056 Migration 3）。
