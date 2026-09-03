# タスクリスト — O1 配布前の残り 5 件 (preflight-4)

## 検算（★ メモを一次資料にしない）
- [x] ⑤ を実コードで検算 → ⚠️ **メモの誤り**（`tray.rs:94` が既に `o1::recording_active` を通している）
- [x] `session_active` の素通し消費者を全部 grep → ★ **他に無い**（分析 `lib.rs:3365` / liveness `lib.rs:4067` とも経由済み）
- [x] ④ を実コードで検算 → ★ 実在。⚠️ **OS 終了シグナルのハンドラも 0 件**でメモより悪い
- [x] ①②③ を検算 → ★ 主張どおり
- [x] 研究者判断を取る（① = C / ④ = A' / ②③ = 手順書のみ）

## 必須 Skill
- [x] `verify-before-claiming`（★ 検算の作法）
- [x] `data-privacy`（★ ルール 6 = 削除保証）
- [x] `reproducibility-discipline`（★ ③ の experiments/ 規約）
- [x] `git-workflow`（★ コミット前）

## ④ 実装（A'）
- [x] `o1.rs`: `O1SessionShape` ＋ 純関数 `is_closable_orphan`
- [x] `o1.rs`: `scan_session_shape` (meta 行の形だけ読む)
- [x] `o1.rs`: `close_orphaned_sessions(dir, current, now_ms)` ＋ 改行なし終端の扱い
- [x] `lib.rs`: 起動時 (O1 のみ・ロガー起動直後) に 1 回呼ぶ
- [x] テスト: 正常 / 不在 / 壊れ の 3 状態
- [x] ⚠️ **陰性対照**: Phase1 / G1 / 既に閉じた O1 / 現在開いているファイル が **1 バイトも変わらない**
- [x] ⚠️ 削除保証: 猶予の起点が**必ず今以降**になることをテストで固定

## ②③ 手順書
- [x] ③ `experiments/20260903-o1-runtime-cost/` を規約どおり作る
- [x] ③ 両 OS の計測スクリプト
- [x] ② 記録票 ＋ 手順（★ `$MEASURE` のパスを readiness ゲートから読む）

## ① 文書化
- [x] 運用ルールを書く（⚠️ **機械的に強制されない**ことも書く）

## ⑤ 訂正
- [x] 引き継ぎメモに訂正を追記（⚠️ 消さない）

## ★ 追加でやったこと（★ 計画に無かったが必要だった）
- [x] ⚠️ **時計故障の fail-closed ガード** `MIN_PLAUSIBLE_EPOCH_MS`（★ `now_epoch_ms()` が失敗時に `1` を返し、猶予が最初から経過済みになる穴を自分で見つけた）
- [x] ⚠️ **変異注入 8 件** → 全部赤。★ **どの検査が赤にしたか**も記録（§0-1 #2 の教訓）
- [x] ⚠️ ③ の `summarize.py` を **3 状態で検算** → ★ **自分の測定器の偽陽性を 1 件発見して修正**（サンプル不足でも個別欄が PASS と出た）
- [x] `cargo fmt` / `cargo clippy`

## ★ レビュー対応（★ 2 人 ＋ Codex の指摘で **根本原因**が出た）
- [x] ⚠️★★★ **`src-tauri/src/ndjson_scan.rs` を新設** — 判定規則が `packaging` / `reconcile` / `o1` の **3 か所にコピーされて食い違っていた**根本を解消
- [x] ⚠️ `has_data_row` を `packaging` と一致させた（★ `hook_health` / `ime_state` を数えない）
- [x] ⚠️★★★ `has_session_end` を **数値パース**に変更（★ 途中で切れた `session_end` を「閉じている」と読まない）
- [x] `logger::write_meta_end` を `pub(crate)` にして**形の二重記述を撤去**
- [x] ⚠️★★★ 時計ガードを **3 段**に（床 ＋ **高水位マーク** ＋ 上限）
- [x] `lib.rs` を `catch_unwind` で包み、**嘘のコメントを訂正**
- [x] `.gitignore` に生サンプル 2 種（⚠️ **既存 44 ファイルを巻き込まないよう絞った**・陽性/陰性対照つき）
- [x] `run.sh` の引数検証（★ `x[$(echo PWNED)]` で実際に弾かれることを実測）
- [x] 下流実験 `20260819-silence-presence-decomposition/README.md` に**申し送り**
- [x] ⚠️ **結合テスト**（孤児回収 → 収束器: 猶予前は候補にならない / 48h ちょうどで候補になる）
- [x] ⚠️ **変異注入 6 件＋陰性対照** → 全部赤・対照は緑（★ 途中でハーネスの誤報告を 1 件発見して修正）
- [x] `cargo test --features package --workspace` 575 緑 / リプレイ byte-equal / **schema drift 無し**

## レビュー / 完了
- [x] `cargo test --workspace`（★ `src-tauri/` から）
- [x] リプレイ回帰（★ byte-equal）
- [x] code-reviewer + security-checker
- [x] ⚠️ `/cross-review` 必須
- [ ] commit / PR

## ⚠️ 今回やらないこと（★ 完了報告に明記）
- ②③ の**実測そのもの**（★ 研究者の実機操作）
- ① のコード変更（★ 研究者判断 C）
- §2 の触らないもの（`Form_G1/` / 事前登録 §3）
- §3 の持ち越し 6 件
