# gse-m5-s1-replay-gate（M5 の 3 本目: 再生・段 1 の配布の門・文書と同期）

## 背景

M5 の 1 本目（調停器 `analysis/probe_arbiter`）と 2 本目（駆動役 `s1_driver.rs` と画面・PR #391・main 3a792fb9）で、段 1 の問い（無作為・層化のプローブと日の終わりの問い）は O1 の記録の上で出て、行が NDJSON に残るようになった。残っているのは計画（`.steering/20261105-gse-m5-probe-wiring-plan/`）の B6・B7 である。

- 記録の行が調停器の判定どおりに出ているかを、記録だけから確かめる道がまだ無い（Replay-as-Truth の背骨に段 1 が乗っていない）。
- 段 1 の配布物を作るときに、印・同意の承認・EH3 との同居を検査する門が無い（O1 の門だけがある）。
- 文書（`docs/architecture.md`・`docs/architecture/gse-design-map.md`）と gse-dataset の schema が、EH3・R1・段 1 の行種に追いついていない。

## ゴール

1. `gse-replay --probes` が、記録の `key`・フォーカス・`recording_pause` の行から同じ調停器を回し、`probe_assignment`・`probe_suppressed`・`day_question` の行と比べた一致・欠け・余り・境目・確かめを JSON で出す。`gse-replay --day-questions` が回答の後の押下の数を出す。
2. 段 1 の配布物の門 `scripts/check-s1-release-readiness.sh` が、陽性対照つきの selftest で、壊すと赤になる。
3. 文書と gse-dataset の schema が段 1 の行種まで揃い、`/finish-task` の schema parity check が通る。

## スコープ

### 含むもの

- (a) 再生（PR 1）
  - `gse-replay --probes`（R1 の `--invitation` と相互に排他）・`--day-questions`。
  - 回答率の集計で `superseded` を本人の未回答と分ける。
  - ローテートをまたぐカードを `probe_id` でファイルをまたいで結ぶ。
  - 一時停止で下ろしたカード（`probe_assignment` あり・ラベル行なし・直後に `recording_pause`）の分類。
  - 一時停止の境目（`recording_pause` の行の時刻の前 2 秒）にかかる不一致は「境目」として別に数え、一致・欠け・余りに混ぜない（判断 2）。
  - 確かめ用のボタンで出したカードの行に `debug: true` を付け（偽のときは書かない）、再生は「確かめ」として分けて数える（判断 3）。
  - 既存のゴールデンの `--snapshot` の byte-equal を保つ。
  - gse-dataset の schema の同期（EH3・R1・段 1 の行種と `debug`・判断 5）。
  - `S1_TICK_LAG_MS = 2000` で押下が届き切るかを、再生との一致の数で確かめられる範囲で測る。
- (b)(c) 門と文書（PR 2）
  - `scripts/check-s1-release-readiness.sh`: `s1.mode` がある・`GSE_DISABLE_PROBES` を付けない・本人用の印（計画の判断 5）・他の参加者向けは同意文書の承認の印・EH3 の印と同居しない（計画の判断 7）。O1 の門の selftest の型（陽性対照・壊すと赤・対照の文字列は実行時に連結）にならう。
  - 段 1 の launcher（作る場所を既存の launcher から確かめる）。
  - `docs/architecture.md`、`docs/architecture/gse-design-map.md`（§1 のラベルの行・§4）。

### 含まないもの

- 調停器・駆動役の判定の変更（再生で不一致が見つかったら、直すかどうかは研究者に聞いてから別に扱う）。
- Windows の画面の確かめ（研究者に頼む・CI は緑）。
- 段 1 の配布そのもの（タグを打つ・配る）。
- 実の O1・段 1 の記録を再生の fixture に使うこと（合成で作る）・Codex に記録の本文を送ること。

## 受け入れ条件

- [ ] `cargo test --manifest-path src-tauri/Cargo.toml --workspace` が緑（`--probes` の一致・欠け・余り・境目・確かめ・ローテートまたぎ・一時停止で下ろしたカード・`superseded` の検査を含む）
- [ ] 合成の記録で、駆動役が書いた行と `--probes` の再生が全件一致する検査がある（壊すと欠け・余りが出ることも検査する）
- [ ] 既存のゴールデンの `--snapshot` が byte-equal
- [ ] `--probes` と `--invitation` を同時に渡すと拒む
- [ ] `debug: true` は確かめ用のカードの行だけに出る（本物の行の直列化が変わらない検査）
- [ ] `bash scripts/check-s1-release-readiness.sh --selftest` が緑で、各検査に陽性と陰性の対照がある
- [ ] `emit_schema` の出力が `src-tauri/schema/current.json` と一致し、gse-dataset 側と schema parity check が通る
- [ ] 文書の 2 本が段 1 の行種と門を書いている

## 関連ドキュメント

- `.steering/20261105-gse-m5-probe-wiring-plan/`（design.md・decisions 判断 0〜10・tasklist の B6・B7）
- `.steering/20261106-gse-m5-s1-core/`（§2-10 の `superseded`）
- `.steering/20261107-gse-m5-s1-driver-ui/`（design.md の「実装中に変わった点と既知の限界」・decisions 判断 1〜10）
- `.steering/_handoff/next-session-gse-m5-part3-replay-gate.md`
- `docs/architecture.md`・`docs/architecture/gse-design-map.md`・`docs/development-guidelines.md` §3・§10

## 運用メモ

- /reimagine 適用: Yes（(a) 再生の設計だけ。(b)(c) は O1 の門の型にならうので不要）
- 理由: 調停器を直接回すか駆動役ごと回すか、照合の単位を何にするかなど複数の案があり、最良が自明でない（研究者が推奨どおり選んだ・2026-11-07）。
- 作業場所: worktree `/Users/johnd/GSE-prototype-m5-replay`・枝 `feature/gse-m5-s1-replay-gate`（origin/main 3a792fb9 から）。
