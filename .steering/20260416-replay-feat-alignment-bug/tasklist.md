# タスクリスト — replay feat アライメント fix (v2 採用後)

## 調査 (完了済み、/reimagine で v2 採用)
- [x] I-1〜I-4: コード読解 (replay.rs / loop_step.rs / metrics.rs / ENGINE_TICK_MS)
- [x] M-1〜M-4: 実データ計測 (再生成 feat 6件 / 元 96件、IME pause が主原因)
- [x] D-1: 原因 decisions.md D1 に記録 (clock semantic mismatch + IME auto-reset 未再現)

## Fix 実装 (TDD 順序厳守)

### Phase A: 回帰テスト先行 (赤)
- [x] A-1: 層1 unit test: `bin/replay.rs` tests モジュールに `logged_feat_dto_deserialize_matches_ndjson()` 追加
  - 実 NDJSON 1 行文字列を serde で `LoggedFeatDto` に parse → FeatSnapshot 変換後のフィールド一致 assert
  - **現実装では LoggedFeatDto 未定義のため fail**
- [x] A-2: 層2 integration test: `tests/replay_metrics_logged_feats.rs` 新規作成
  - tempfile に手書き最小 NDJSON (meta + 3 feat + 1 user_label) を書く
  - `Command::cargo_bin("gse-replay").args([path, "--metrics", "--json"])` を呼び stdout の JSON を parse
  - `warnings` 空 + `total_labels=1` + `per_class.flow.support=1` を assert
  - **現実装 (regen) では warnings に「no FeatSnapshot within ±1000ms」が出るので fail**
- [x] A-3: 層3 実データ回帰: `tests/fixtures/phase1_ime_heavy.ndjson` 作成
  - 元 `gse_20260415_144120.ndjson` から **key 行を除去**、meta + ime_state + feat + user_label のみ残す (機密な文字内容ゼロ化)
  - 対応 test: `tests/replay_metrics_logged_feats.rs` 内に `real_session_ime_heavy_matches_labels()` 追加
  - `warnings.len() < 2` + `confusion_matrix_total >= 4` を assert
  - **現実装で fail**

### Phase B: Fix 実装 (緑)
- [x] B-1: `bin/replay.rs` に `LoggedFeatDto` struct + `From<LoggedFeatDto> for FeatSnapshot` impl 追加
  - `#[serde(rename = "t")]` で timestamp マッピング
  - schema_dto.rs `LogEntryDto::Feat` の 15 フィールドと同期 (DTO 冒頭に同期コメント記載)
  - `#[serde(deny_unknown_fields)]` は **付けない** (forward-compat)
- [x] B-2: `bin/replay.rs` に `collect_logged_feats(path: &PathBuf) -> Result<Vec<FeatSnapshot>, String>` 関数追加
  - 構造は `collect_user_labels` と完全並列
  - ファイルサイズガード (MAX_SESSION_BYTES)
  - `type == "feat"` のみ抽出、timestamp 昇順ソート
  - parse error は silent skip (collect_user_labels 同様)
- [x] B-3: `main()` の `--metrics` 分岐を書き換え
  - `run_replay()` 呼び出しを metrics path から外す
  - `collect_logged_feats()` → `compute_session_metrics(&labels, &feats)` の順
  - `--snapshot` / stdout JSON 出力は従来通り `run_replay()` 維持
- [x] B-4: `bin/replay.rs:79-81` の「feat variant 読み飛ばし専用」コメントを「snapshot 検証専用、metrics は logged feat を使用」に修正
- [x] B-5: Phase A の A-1/A-2/A-3 テストが **全て PASS** することを確認

### Phase C: 既存テスト保全
- [x] C-1: test-runner サブエージェントで `cargo test --workspace` 実行
  - 期待: 51 + 3 (A-1/A-2/A-3) = 54 tests PASS
  - 既存 snapshot 回帰 (minimal.json 15件) を含む

### Phase D: バックフィル (v2 設計の主要要素)
- [x] D-1: 事前計測: Mac baseline `gse_20260415_080921.ndjson` を dataset raw/ から取得 (可能なら) → 新 `--metrics` で再計算、既存 JSON との差分確認
  - dataset repo の raw/ には logged NDJSON が無ければ skip、旧値と新値の比較は諦める
- [x] D-2: Windows `gse_20260415_144120.ndjson` で新 `--metrics --json` 実行、意味のある数値 (support > 0、warnings 空) を確認
- [x] D-3: `gse-dataset/metrics/P000/windows/gse_20260415_144120.metrics.json` を fix 後の値で上書き
  - 旧値を decisions.md にスナップショット保存
- [ ] D-4: Mac baseline metrics JSON の再計算は D-1 のデータ入手状況次第。入手不能なら defer
- [x] D-5: `baseline_metrics.md` を before/after 併記で更新

### Phase E: ドキュメント同期
- [x] E-1: `docs/architecture.md` line 301 修正 — 「metrics は logged feat 使用」
- [x] E-2: `docs/functional-design.md` line 228 修正 — 同上
- [x] E-3: `.steering/20260415-docs-phase1-backfill/design.md` line 45 の該当箇所修正 (任意)

## Phase F: レビュー
- [x] F-1: `code-reviewer` + `security-checker` を **並列起動**
  - security-checker は外部入力パース (NDJSON) に関わるため必須
  - HIGH 指摘は全対応、MEDIUM はユーザー確認

## Phase G: 完了
- [x] G-1: blockers.md BL-2 の「恒久対応」を本タスクへのリンクに更新
- [x] G-2: `20260415-windows-onboarding/completion-log.md` の次アクションを更新
- [ ] G-3: gse-prototype 側 commit (`fix(metrics): use logged feat instead of regen`)
- [ ] G-4: gse-dataset 側 commit (`data(revised): rebuild metrics after alignment fix`)
- [ ] G-5: 両 repo push
- [ ] G-6: `/finish-task`
