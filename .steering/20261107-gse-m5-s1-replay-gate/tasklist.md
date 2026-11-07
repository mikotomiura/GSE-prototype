# タスクリスト —— M5 の 3 本目（再生・段 1 の配布の門・文書と同期）

## 場面ごとの道具（完了前に照合する）

| 場面 | 道具 |
|---|---|
| Rust を書く | `rust-standards`・新しい `.rs` は `architecture-rules`・`logger.rs` は `data-privacy` |
| 実装の区切りの点検 | `code-reviewer` ＋ `security-checker`（並列） |
| 完了時 | `/cross-review`（code-reviewer と Codex のラッパーをメインから直接並列に・引き継ぎ §4） |
| テストの実行 | `test-runner` |
| Codex に送らないもの | O1・段 1 の実の記録（fixture は合成） |

## 0 着手前

- [x] ディスクの空き（12GiB）・取り消しの経路の画面の確かめ（判断 0）
- [x] grill・requirement・decisions 判断 1〜5・design（/reimagine ハイブリッド）

## PR 1: 再生

### P 確かめ用の印（判断 3）
- [x] P1 `s1_driver.rs`: `ProbeCard.debug`・`Effect::Assigned` の印・`DayRowData.debug`・`debug_show_probe` が `apply` の後で立てる・`day_row_for_close` が写す
- [x] P2 `logger.rs`: 4 行の構造体と書式関数（真のときだけ `,"debug":true`）・byte 固定の検査が変わらないこと・真の行の検査
- [x] P3 `lib.rs`: 割り当て・ラベル・差し替え・日の問いの行に写す（`activity_label_*` の引数は増やさない）
- [x] P4 `schema_dto.rs`・`emit_schema` で `schema/current.json`

### R 再生の本体 `s1_replay.rs`
- [x] R1 行の読み取り（段 1 の行種・`key`・`focus_transition`・`recording_pause`・`meta`）・`probe_frame` から `ArbiterConfig`（`lambda_per_ms` の往復の検査）・複数のファイルの並べ
- [x] R2 開いているカードの区間を記録から作る（プローブ・日の問い・ローテートまたぎ・一時停止で下ろした・終了）
- [x] R3 tick を回す（位相・一時停止・スリープの復帰の推定・枠の動き出し・`on_quit`・`on_closed`）
- [x] R4 照合と分類（鍵・`boundary_*`・`unverified.*`・`match/differ/missing/extra`・`near_pause_outside_window`・`first_divergence_ms`）
- [x] R5 位相 4 通りの割れを `boundary_tick` に
- [x] R6 カードの集計（回答率・`superseded`・`dropped_by_pause` ほか）・`lag_check`
- [x] R7 `--day-questions` の押下の数
- [x] R8 `lib.rs` の Effect → LogEntry の写しを純関数に切り出す（挙動は変えない）

### B bin
- [x] B1 `replay.rs`: `--probes`・`--day-questions`・排他・`--utc-offset-secs`・`--day-state`・複数の位置引数・使い方の文・exit 1

### T 検査
- [x] T1 往復（駆動役 → 本物の書式 → 再生で全件一致）・2 秒の遅れの陽性対照（0〜1900 ms 一致・2100 ms 以上で割れる）
- [x] T2 壊すと赤（1 行消す・1 行足す・seed・境目の 1 秒前と 4 秒前・`debug`）
- [x] T3 個別（ローテートまたぎ・一時停止で下ろした・`superseded`・取り消しの `tail`・スリープ・`--day-questions` の JST と UTC）・引数
- [x] T4 `cargo test --workspace`・6 本のゴールデンの `--snapshot`・`emit_schema` の byte-equal・clippy
- [x] T5 手で: 判断 0 の隔離した HOME の記録（手元だけ）を `--probes` に通し、確かめ用のカードが `debug_check` に入る

### S gse-dataset（判断 5）
- [x] S1 `~/gse-dataset` に枝を切り `schema/current.json` を写す・parity check が緑（push・PR は研究者に確かめてから）

### V 点検と完了
- [x] V1 code-reviewer ＋ security-checker（並列）・指摘への対応
- [x] V2 docs（`functional-design.md`・`glossary.md`・`development-guidelines.md` §3 の再生のモード）
- [x] V3 `/finish-task`（PR 1 は #392 で merge 済み・PR 2 は G4）

## T5 の記録（2026-11-07）

- 判断 0 の記録（main の版・印なし）を `--probes` に通すと、確かめ用のボタンのカード 3 枚が `extra`（調停器が出していない発火）に見えた。判断 3 の印が要ることの実例。
- 新しい版で隔離した HOME を作り直し、同意 → 確かめ用のプローブに「思い出せない」→ 確かめ用の日の問いを「今日は答えない」。4 行（割り当て・2 つのラベル・日の問い）に `"debug":true`。`--probes` で `debug_check` 2・`extra` 0。走らせた 3 分の間に無作為の候補は落ちず、`match` は 0。
- 取り消しで下ろしたカード（行なし）は `cards.open_at_input_end` に入る（取り消しは行が無いので見分けられない・既知の限界に足す）。

## PR 2: 門・launcher・文書（PR 1 の後・design.md の末尾に設計を足す）

- [x] G0 設計（design.md の PR 2 の節・decisions 判断 9・10・研究者の承認 2026-11-07）
- [x] G1 `scripts/check-s1-release-readiness.sh` と selftest
- [x] G2 段 1 の launcher `launch-s1-windows.bat`（BOM・chcp・CRLF・`GSE_DISABLE_PROBES` を付けない・`eh3.mode` で中断）
- [x] G2b `make-common-app-zip.sh --mode s1`（印 2 つ・タグと実体の検査・展開後の検査・selftest）
- [x] G2c O1 の門の `s1.mode` の判定を段 1 の分岐に合わせる・selftest
- [x] G2d 検査: 3 本の selftest・O1 の門の本体の前後の差分・`check-shell-portability.sh`
- [x] G2e code-reviewer ＋ security-checker（並列）
- [x] G3 `docs/architecture.md`・`docs/architecture/gse-design-map.md`
- [x] G4 `/finish-task`（/cross-review 2 巡・判断 12・13。push と PR は研究者に確かめてから）

## PR 2 の記録（2026-11-07）

- /cross-review 2 巡目の後（判断 13）: 段 1 の門の selftest 85/0・O1 の門の selftest 78/0・組み立て 23/0・移植性 12/0。実物の O1 の zip（macOS・Windows）に門を当て、O1 の配布物として正しく赤（s1.mode・launcher・実体・タグ）で、それ以外は緑。
- 点検の後: 段 1 の門の selftest 55/0・O1 の門の selftest 78/0（PR 1 の 72 に 6 件）・組み立て 23/0・移植性 12/0（判断 11）。
- 点検の前: 段 1 の門の selftest 39/0。組み立ての selftest 23/0（足した検査は複製を壊して赤を確かめた）。移植性の検査 12/0。
- 段 1 の門の本体（`--audience self --dist <無い>`）は exit 1: 段 1 を含むタグが無い・配布物が無い（正しい赤）。
- O1 の門の本体は変更の前後で `s1.mode` の行の文言だけが変わる（前後とも exit 1・他の未達は変わらない）。
- 門が本物の launcher を赤にした: O1 の launcher から写した 2 行目の日本語のコメントが `chcp 65001` より前にあった。段 1 の launcher は chcp を 2 行目へ上げた。O1 の launcher（`launch-o1-windows.bat`）も同じ並びだが、配布中のものなので触らない（研究者に知らせる）。
