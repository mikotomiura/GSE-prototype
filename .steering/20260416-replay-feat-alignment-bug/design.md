# 設計 v2: semantic clock の分離と metrics 入力の再定義

## 問題の再定義: clock semantic の不整合

要件から導ける第一原理: **metrics は「ユーザーがラベル押下した瞬間の HMM 出力」を測る**。

- `user_label.t` は production 実行中に `SystemTime::now()` から取られた **wall-clock ms**
- `feat.t` (NDJSON 記載) も同じ `SystemTime::now()` 由来の **wall-clock ms**
- ⇒ 両者は**同じ時間軸**で比較されるべき値

一方、`gse-replay` が `--metrics` で使っている feat は `step()` を再実行した **virtual clock** 生成物:
- virtual tick は `session_start_ms + k * ENGINE_TICK_MS` で grid 化される
- engine pause 状態の再構成で production と乖離する (IME active の扱い差、auto-reset の未再現)

**metrics が regen feat を使う構造は、そもそも clock semantic が label と揃っていない**。これが本件バグの「構造的な」原因。たまたまセッションによってラベルが grid 近傍に落ちれば動き、外れれば全滅する。Mac baseline は偶然揃っていたに過ぎない。

→ **fix: metrics は NDJSON に記録された logged feat (production が wall-clock で書いた値) を source of truth とする**。

## 責務の再分離

| 用途 | データ source | 役割 |
|---|---|---|
| `--metrics` | **logged feat (NDJSON 内 `feat` エントリ)** | production 実行時の HMM 出力とラベルを突き合わせる |
| `--snapshot` / デフォルト JSON 出力 | **regen feat (step() 再実行)** | HMM engine の決定論的再現性 verify |

`gse-replay` は両方のモードを単一バイナリで提供するが、**入力データが別系統**であることを明示的に分岐させる。

## 実装アプローチ

### 変更点1: NDJSON から logged feat を抽出するコレクタを追加

`bin/replay.rs` に `collect_logged_feats(path: &PathBuf) -> Result<Vec<FeatSnapshot>, String>` を追加。構造は `collect_user_labels` と完全並列:

- ファイルサイズガード (MAX_SESSION_BYTES 共通)
- 行ごとに serde でパース
- `type == "feat"` のみ抽出し、NDJSON の `t` フィールドを `timestamp` にマップ (`#[serde(rename = "t")]`)
- timestamp 昇順でソート

具体的な型:
```rust
#[derive(serde::Deserialize)]
struct LoggedFeatDto {
    #[serde(rename = "t")]
    timestamp: u64,
    f1: f64, f3: f64, f4: f64, f5: f64, f6: f64,
    p_flow: f64, p_inc: f64, p_stuck: f64,
    raw_x: f64, raw_y: f64, ewma_x: f64, ewma_y: f64,
    obs: usize, alpha: f64,
}
impl From<LoggedFeatDto> for FeatSnapshot { /* field-by-field */ }
```

### 変更点2: `main()` の分岐を責務に合わせて再構築

```rust
if args.metrics {
    // semantic: production の wall-clock 出力と label を突き合わせる
    let labels = collect_user_labels(&args.session_path)?;
    let feats = collect_logged_feats(&args.session_path)?;   // ← NEW source
    let metrics = compute_session_metrics(&labels, &feats);
    // ... 従来の pretty-print / json 分岐
    return ExitCode::SUCCESS;
}
// snapshot / stdout-json は従来通り run_replay (regen) を使う
let snapshots = run_replay(&args.session_path)?;
```

`run_replay` 呼び出しは metrics path から外す (`run_replay` は metrics に不要になる)。

### 変更点3: `run_replay` コメントを設計意図どおり修正

現状コメント (`bin/replay.rs:79-81`) は「feat variant は読み飛ばし専用」と主張していたが、metrics が実際には再生成を使っていた矛盾がある。fix 後にコメントを「snapshot 検証専用」に明確化。

## テスト戦略: 3 層

### 層1 — unit: `LoggedFeatDto` のシリアライズ互換性
- `tests` モジュールで実 NDJSON の 1 行分の文字列 (`{"type":"feat","t":...,...}`) を serde でパース
- FeatSnapshot に変換後のフィールド一致を assert
- **目的**: スキーマ変更 (`schema_dto.rs` との整合) を検知する

### 層2 — integration: `collect_logged_feats` の単体動作
- `tests/` ディレクトリに新規 `replay_metrics_logged_feats.rs` 追加
- tempfile に手書き最小 NDJSON (meta + 3 feat + 1 user_label) を書き、`gse-replay --metrics` を走らせて stdout JSON を parse
- warnings 空 + support = 1 を assert

### 層3 — 実データ回帰: 本件セッションを fixture 化
- `gse_20260415_144120.ndjson` のうち **key 行を除去したスリム版** (prose は機密なので keystroke は落とす) を `tests/fixtures/phase1_ime_heavy.ndjson` としてコミット
  - meta / feat / user_label / ime_state のみ残す
  - feat と label は元のまま ⇒ alignment 再現
- この fixture に対し warnings < 2 + support >= 4 (6件中 4件以上マッチ) を期待する回帰テスト追加
- **目的**: 将来同種の regression を CI で捕捉する

## バックフィル計画 (実装と同等の重要事項)

### 事前計測 (fix 実装前)
1. Mac baseline `gse_20260415_080921.ndjson` を dataset repo の raw/ から取得
2. `collect_logged_feats` 相当のスクリプト (Python) で logged feat 件数・label alignment を先に確認
3. 期待する fix 後の数値を事前メモ (実測との乖離があれば設計前提が崩れている)

### 実装後の再計算
1. `gse-dataset/metrics/P000/macos/gse_20260415_080921.metrics.json` を fix 後の値で上書き
2. `gse-dataset/metrics/P000/windows/gse_20260415_144120.metrics.json` を fix 後の値で上書き
3. 旧 metrics JSON は `decisions.md` に snapshot として保存 (ロールバック証跡)
4. dataset repo に「`data(revised): rebuild metrics after replay-feat-alignment fix`」コミット

### baseline_metrics.md の更新
1. fix 前の n=2 値と fix 後の値を両方記載 (before/after)
2. Phase 2a Go/No-Go 判定は fix 後の値で再評価

## 変更対象ファイル

| ファイル | 変更 |
|---|---|
| `src-tauri/src/bin/replay.rs` | `LoggedFeatDto` 型 + `collect_logged_feats` 関数 + `main()` 経路切替 + L79-81 コメント修正 |
| `src-tauri/src/bin/replay.rs` (tests モジュール) | 層1 unit test |
| `src-tauri/tests/replay_metrics_logged_feats.rs` | 層2 integration test (新規) |
| `src-tauri/tests/fixtures/phase1_ime_heavy.ndjson` | 層3 実データ fixture (新規、機密部分除去) |
| `src-tauri/src/analysis/metrics.rs` | 変更なし (public interface 不変) |
| `.steering/20260415-phase1-ground-truth/baseline_metrics.md` | fix 後数値で更新 |
| `gse-dataset/metrics/P000/macos/*.metrics.json` | fix 後再生成 |
| `gse-dataset/metrics/P000/windows/*.metrics.json` | fix 後再生成 |

## 既存パターンとの整合性

- `collect_user_labels` と対称構造 → レビュアが理解しやすい
- `analysis/metrics.rs` の public API (`compute_session_metrics(labels, feats)`) は不変 → 他コードが壊れない
- `tests/snapshots/minimal.json` (snapshot regression) は触らない → step() 決定論 verify は生存
- architecture-rules: NDJSON I/O は `bin/` (CLI 層) に閉じ、`analysis/` は純粋計算のまま

## 影響範囲と受け入れ条件

| 影響先 | レベル | 対処 |
|---|---|---|
| Phase 1 metrics 全般 | **HIGH** | fix 後全既存セッションで再計算 (バックフィル計画参照) |
| `baseline_metrics.md` | HIGH | before/after 両方記載して更新 |
| `gse-dataset/metrics/**` | MEDIUM | 再生成して commit、履歴に証跡残す |
| `tests/snapshots/minimal.json` | NONE | regen path 不変で互換 |
| HMM engine (`loop_step.rs`) | NONE | 触らない |
| Tauri frontend / IPC | NONE | 触らない |

## リスクと緩和

| リスク | 緩和策 |
|---|---|
| 層3 fixture が機密 prose を漏らす | key 行を除去し feat/label/ime_state のみ保持。コード規約でレビュー時に再確認 |
| fix 後 Mac baseline 数値が悪化して Phase 2a No-Go | 事前計測で事前把握、期待値との乖離があれば設計見直し |
| 旧 metrics JSON を dataset repo で上書きして履歴を失う | commit メッセージに before-sha を残し、必要なら `git revert` で復帰可能 |
| logged feat が無い古いセッション (Phase 1 以前) | `compute_session_metrics` が既に「no feat snapshots found」警告を返す。問題なし |

## テスト戦略 (TDD 実行順)

1. **fail** 層1 unit test: `LoggedFeatDto` の serde デシリアライズを assert → 未実装で fail
2. **fail** 層2 integration test: tempfile NDJSON で warnings 空を期待 → 現実装 (regen) で fail
3. 実装: `LoggedFeatDto` / `collect_logged_feats` / `main()` 分岐切替
4. **pass** 層1 / 層2 が通る
5. 層3 fixture を生成 (`gse_20260415_144120.ndjson` からスリム化)
6. **fail → pass** 層3 実データ回帰: warnings < 2 + support >= 4
7. **既存 51 tests 全 PASS 維持確認** (test-runner サブエージェント)
8. code-reviewer + security-checker 並列起動でレビュー

## ロールバック計画

- コード変更: `git revert <commit-sha>` で元に戻る。public API 不変のため依存先影響なし
- dataset repo metrics JSON: 新 commit で上書きしているため、`git revert` で前値に戻せる。新旧 hash を完了ログに記載
- baseline_metrics.md: before/after 併記しているため、fix ロールバック時は after 節を削除するだけ

## Open 点 (v2 で明示化)

- **Mac baseline が偶然動いた理由**: logged feat vs regen の差分を事前計測で確認する (本件が解消されたら同セッションの metrics 数値は微変動するはず)
- **層3 fixture の key 行除去**: logger.rs が key 内容を記録しない設計 (vk_code のみ) を再確認、機密性の境界を document 化
- **Phase 2a Go/No-Go の期待値**: fix 後 Mac n=2 + Windows n=1 で再計算し、retrospective の閾値 (Stuck precision ≥ 0.6) を満たすか

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v2
- 根拠: 実データ回帰 (層3 fixture) による再発防止 + バックフィル計画の主要化で Phase 2a Go/No-Go 判定ゴールへの橋渡しが明確、clock semantic 原則が将来の類似バグにも汎用に使える
