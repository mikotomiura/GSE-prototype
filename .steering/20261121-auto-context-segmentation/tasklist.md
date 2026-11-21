## tasklist

### 準備
- [x] main から worktree を切る（`feature/auto-context-segmentation`）。今のチェックアウト（`docs/ai-fatigue-motivation-claims`・未コミットあり）では作業しない
- [x] 作業記録（この .steering/ と glossary の 2 語）を worktree の側へ移す

### 層 1（Rust・`--features` の `context`）
- [x] IME オンの秒を既存の入力（キー行・IME の行）から作れるかを確かめ、decisions に書く
- [x] `PoleInputs` のリテラル 5 か所を確かめる（`Default` で書かれているか）
- [x] `feat_offline/context.rs`: tick 内の数（focus・pointer・keys・cat_counts・ime_on）と単体テスト
- [x] `replay.rs`: `collect_focus_timestamps`・`collect_pointer_bins`、欠測の 3 状態（極 B と同じ規則）
- [x] `mod.rs`: `FeatureRow.context` と構築箇所
- [x] 統合テスト `tests/context_features.rs`（fixture は置かずテストの中で作る）と（切り替えの前後・旧ログで null）
- [x] `cargo test --manifest-path src-tauri/Cargo.toml --workspace` が緑
- [x] `gse-replay --snapshot` が minimal と byte-equal
- [x] `scripts/check_no_feature_output.sh --self-test` が緑
- [x] `p1_features_io.py` が未知のキー（context）で落ちないこと（合成の封筒 8100 行で load_envelope が通る。`build_p1_episode_db.py` は duckdb が無く回せないが、読むのは T0_BLOCKS の 5 つだけ・79 行目）

### 層 2（experiments/）
- [x] `experiments/20261121-auto-context-segmentation/` を `_template` から作る（run.sh の Step 0 を残す）
- [x] `gen_synth.py`（seed を固定）: 陽性・陰性・壊した入力の 3 種
- [x] `acs_core.py`（窓・（混合ガウス・BIC・k=1 を許す）・平滑化（強制の境界は吸収しない）と単体テスト
- [x] `evaluate.py`: 合成・再現性・宣言との照合（巡回の帰無分布）・循環（状態・量の軸）
- [x] `criteria.json` の数値を研究者と確定し、実データより前にコミットする
- [x] 合成で陽性は終了コード 0、壊した入力は非 0 を確かめる

### 実データ
- [ ] `data.md` に入力（本人の段 1・O1）の SHA-256 と capabilities_gate の結果を書く
- [ ] 実行して、人ごとの判定（使える／使えない／判定できない）と落ちた段を notes.md に書く
- [ ] 本人の区間の一覧を研究者に振り返ってもらい、decisions に残す
- [ ] 識別子の要否の見積もりを decisions に残す

### 文書・レビュー・完了
- [x] `docs/glossary.md`（特徴行の項に context）・`docs/functional-design.md`
- [ ] code-reviewer と security-checker を並列で回し、指摘に対応する
- [ ] /finish-task で /cross-review（Claude と Codex）。Codex にはコードの diff だけを渡す
- [ ] コミット（git-workflow に従う）。push と PR は研究者に確かめてから
