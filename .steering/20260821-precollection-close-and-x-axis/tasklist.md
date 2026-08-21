# タスクリスト

## 準備
- [x] 引き継ぎ (`_handoff/next-session-prompt-precollection-close-and-x-axis.md`) を読む
- [x] `.steering/20260821-precollection-close-and-x-axis/` を作成
- [x] `liveness.rs` / `lib.rs` / `g1.rs` / `capabilities.rs` / `logger.rs` の該当箇所を読む
- [x] 前タスクの `blockers.md` (D-1) と `code-review.md` (所見 C) を読む

## T-0 — `starve_window` の陽性対照 (⚠️ 期限あり・★ 最優先)
- [x] 発火条件を**実装から**導く (推測しない)
- [x] ランブック `t0-runbook.md` を書く
- [x] 値だけを取り出すスクリプトを用意する (⚠️ 生 NDJSON は repo に置かない)
- [x] ★ **研究者が実機で実施** (Windows 11 / `g1_mode = "marker"` / `app_version 0.1.27`)
- [x] ⚠️★★★ **発火した** —— `starve_window` **1 行** / `win_ms = 60000` / `n_lt30 = 3` / `sum_lt30_ms = 21000`
- [x] ★ 対照: `hook_health` **0 行** (30 秒未満なので期待どおり ＝ 2 トラックが閾値で分割されている)
- [x] `t0-result.md` に**値だけ**を転記

## T-1 — 自動終了 × 押下の競合 ＋ 所見 C (⚠️ 期限あり)
- [x] `design-v1.md` (案 A: CAS のみ) を書く
- [x] ★ `/reimagine` で v2 (排他 ＋ エポック照合) を再生成し `design-comparison.md` で比較
- [x] ★ 研究者が **v2** を採用
- [x] `g1::BlockEndAction` / `g1::decide_block_end` を**純関数**として追加
- [x] `lib.rs` に `BLOCK_TRANSITION`（★ 最外側の直列化点）を導入
- [x] `start_session` の臨界区間化 (★ `Rotate` 送信 〜 `SESSION_START_MS.store(now)` を一続きに)
- [x] 自動終了スレッドの臨界区間化 (★ `emit` / 自動提出は**外**に出す)
- [x] 所見 C: `liveness::starved_ms_carried_into_new_window` (★ 1 行の純関数)
- [x] ⚠️ **交錯 2 方向**をテストで固定 (押下が先 = `Superseded` / 押下が後 = 排他の順序)
- [x] ⚠️ 対照テスト (通常の tick は数える / 通常のブロック境界は不変)
- [x] ★ ソース走査でロック順序を固定 (⚠️ バイト数スライスしない)

## T-2 — ADR-013 Migration 3 / 4
- [x] `scripts/capabilities_gate.py` (★ 3 群 ＋ 旧ログ ＋ `MIXED`・`--self-test` つき)
- [x] `scripts/tests/test_capabilities_gate.py` (20 テスト)
- [x] `experiments/_template/` (`run.sh` の **Step 0** がゲート ＋ `README.md`)
- [x] `docs/development-guidelines.md` **§10.5** (新設・判定表と使い方の SSOT)
- [x] `docs/architecture/personalization-and-online-learning.md §5.2` 冒頭に警告
- [x] `docs/experiment-tracking.md` (ディレクトリ規約 ＋ 再現性チェックリスト)
- [x] ⚠️★★ **CI に載せる** (`--self-test` ＋ 単体テスト)
- [x] ★ **実ログで検算** (新ログ exit 3 / 旧ログ exit 4 / 混在 exit 6 ＝ 空振りしていない)
- [x] ADR-013 Migration 2b / 2c / 3 / 4 を**実施済み**に更新

## T-3 — X 軸の再定義 (⚠️ 議論のみ・実装しない)
- [x] ⚠️★★★ 冒頭で「現行 G1 は変えない」を固定
- [x] 論点 1: D2 の operational definition と**打ち切りの扱い** → ★ **主張範囲を明文化**
- [x] 論点 2: D4 の採用ゲート → ★ **退化検出は数値化 / 勝ち幅は「決め方」を凍結**
- [x] 論点 3: D5 の H-X1d → ★ 研究者判断「**今は載せない・P2 開始時に採択**」
- [x] 論点 4: D7 の帰結 → ★ **G1 は免除されない**を明文確認 ＋ メモ §4 との緊張を裁定
- [x] `.idea` メモを材料として使う (★ G2 失敗分岐の**入口**として ADR に記録)
- [x] ⚠️ メモ §6 の数値は**運ばない** (出典未登録・`citation-ssot`)
- [x] ★ 出口: **Proposed のまま ＋ Accepted 条件を明文化** (研究者判断)
- [x] ⚠️ 副産物: `glossary.md` の「打ち切り」が**旧 G2 のまま**だったのを直す
- [x] ⚠️ **実装しない** (`raw_x` / 合成式 / `feat` 行に 1 バイトも触っていない)

## テスト / 検証
- [x] `cargo test --workspace` **緑** (438 + 29 + 1 = **468** / 0 failed)
- [x] ★ **新テスト 11 本が実際に走ったことを確認** (⚠️ OS ゲート付きモジュールに入れていない)
- [x] ゴールデン **6 本 byte-equal** (`replay_snapshot_goldens_byte_equal`)
- [x] `HMM_VERSION` **0.4.0 据え置き**
- [x] `emit_schema` の出力が `schema/current.json` と **byte-equal** (★ 記録仕様を変えていない)
- [x] `cargo clippy` — 新規警告ゼロ / `cargo fmt --check` 緑
- [x] Python: **83 テスト**緑 / `capabilities_gate --self-test` 緑 / `check_vignettes --self-test` 緑
- [x] schema parity (`gse-dataset` 突合) **exit 0** (⚠️ `| tail` にパイプせずリダイレクトで確認)
- [x] `check_citations.py` 緑

## レビュー
- [x] code-reviewer + security-checker を**並列**起動
- [x] `/cross-review` (⚠️ パス限定で・exit 0)
- [x] ⚠️★★★ **HIGH 3 件に対応** —— code-reviewer H-1 (所見 C の修正が効いていなかった) /
      H-2 (`SESSION_META_RECORDED` の巻き戻し漏れ) / security-checker H-1 (JSON にファイル名)
- [x] MEDIUM 11 件 / LOW 7 件を採否つきで処理 (`code-review.md`)

## ドキュメント
- [x] ADR-013 Migration の更新
- [x] ADR-009 の更新 (D2 / D4 / D5 / D7 ＋ Accepted 条件)
- [x] `glossary.md` に「競合イベント」「上下界 (recovery)」を追加、「打ち切り」を現行定義へ
- [x] `docs/development-guidelines.md §10.5` 新設

## 完了処理
- [x] `design.md` の最終化
- [x] `decisions.md` の作成
- [x] `blockers.md` (⚠️ **直さないと決めた**ものの記録)
- [x] `code-review.md` (Codex / security-checker / code-reviewer の 3 系統)
- [ ] git commit
