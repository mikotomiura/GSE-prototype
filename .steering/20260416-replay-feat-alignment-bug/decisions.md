# 設計判断: replay feat アライメントバグ

## D1. 根本原因

**gse-replay --metrics が label に feat を対応付けられない根本理由は、replay の `ImeActivate` 処理が production の 8 秒 auto-reset を再現していないため。**

### 再現観察 (Windows セッション `gse_20260415_144120.ndjson`)

| 指標 | 元 NDJSON (production live) | replay 再生成 |
|---|---|---|
| feat 件数 | 96 | **6** |
| 時刻範囲 | session_start+5727ms..+100722ms (95s) | session_start+2000ms..+8691ms (**7s のみ**) |
| user_label との ±1000ms 近接 | 全 6 件マッチ (delta 12..517ms) | 全 6 件 miss (最近傍でも −8792ms) |

### メカニズム (コードベースで追跡)

1. 元セッションの `ime_state` 遷移:
   - `t=+34ms`: off/inactive
   - `t=+326ms`: off/inactive
   - `t=+8903ms`: **on/active** (pause 開始)
   - `t=+23266ms`: off/inactive (再開、14363ms 後)
   - `t=+24536ms`: **on/active** (再度 pause)
   - `t=+100707ms`: off/inactive (76171ms 後)

2. replay 動作 (`bin/replay.rs:473-483`):
   ```rust
   ReplayEvent::ImeState { t, on, active } => {
       ime_open = on;
       let out = step(&mut state, &engine, Some(LoopInput::ImeActivate { active }), t, ime_open);
   }
   ```
   → `step()` 内 `engine.set_paused(active)` (`loop_step.rs:248`) を忠実に呼ぶ。

3. gate tick ループ (`loop_step.rs:265-268`):
   ```rust
   if engine.get_paused() {
       state.was_paused = true;
       return out;  // feat 発行なし
   }
   ```
   → pause 中は feat 発行ゼロ。

4. production 動作 (`lib.rs:649-677` の IME Monitor スレッド) は同じ `engine.set_paused(active)` (L703) を呼ぶが、追加で **8 秒 auto-reset** を持つ:
   ```rust
   if ime_active_since.elapsed() > 8s {
       tracing::warn!("IME_ACTIVE stale for >8s — auto-resetting");
       IME_ACTIVE.store(false);
       engine_for_monitor.set_paused(false);
       emit ImeState { active: false };  // ← 新規 log エントリ
   }
   ```

5. auto-reset の副作用として、IME active 状態が 8s を超えると `IME_ACTIVE=false` + `engine.set_paused(false)` + ログ追記が行われるため production では feat 発行が継続する。**一方でログには auto-reset の書き戻し以降のイベントしか残らず、初回 active→reset→再active のサイクルの区切りがログから完全には復元できない**。

6. 今回のセッションでは auto-reset が期待した時刻 (+8903+8000=+16903ms 付近) で `active=false` ログが出ていない。考えられる理由:
   - 実装上 `is_candidate_window_open()` の次回 polling が active=true を返し、直ちに IME_ACTIVE を再セット → ログとしての off エントリが残らず次の off (23266ms) まで沈黙した
   - または auto-reset 直後のチェックで真の IME が依然 active とみなされ、`last_active=Some(false)` から `true` への遷移として再び ImeState{active:true} ログが書かれるべきだが、`emit_ime_state` の呼び出しパスを観測すると 1 秒あたり最大 10 回の polling の中で状態遷移のみログする (last_active との差分)。auto-reset 直後に polling で再度 active=true が返ると `last_active=Some(false)` → `Some(true)` の遷移としてログ行が追加されるはず — 今回の NDJSON で見えていない理由は未完解明 (polling 間隔の境界 or auto-reset と polling のレース)
   - 実態としては production engine は 8s 毎に pause 解除されるが**ログには残らない**ため、NDJSON からの replay は必然的にずれる

### 結論

**`gse-replay` で再生成される feat 列は production が実際に emit した feat 列と等価ではない**。特に IME active が 8s 超継続するセッション (日本語入力で頻出) で大幅乖離する。metrics はこの乖離を承知で再生成 feat を使っているため、ユーザーラベルとのマッチングが全滅する。

## D2. Fix 方針: **Option A — metrics は NDJSON の logged feats を直接使う**

### 採用理由
1. **セマンティクス**: metrics は「ユーザーがラベル押下した瞬間に HMM がどう予測していたか」を測る。その予測は live 実行時にログされた `feat` エントリそのもの。再生成で再計算する必然性はない
2. **アライメント保証**: logged feats は production wall-clock の tick に連動しており、ユーザー操作と自然に整合する
3. **工数 cheap**: `collect_logged_feats()` を `collect_user_labels()` と並列に追加するだけ
4. **snapshot 用途の分離**: `--snapshot` による step() 決定論検証は従来通り re-run を使う (既存 15 snapshots テストを破壊しない)

### 不採用理由
- **Option B (8s auto-reset を replay で再現)**: production の IME Monitor は polling + atomic + auto-reset の複合状態。replay で忠実再現しても log に残らないタイミングが再現不能
- **Option C (pause_state 新イベント)**: schema 破壊変更 + 旧セッション互換なし
- **Option D (replay で pause しない)**: HMM 内部状態が drift し snapshot test が全件破綻

## D3. 影響範囲と後続処理

### 既存 metrics JSON の再生成
- `gse-dataset/metrics/P000/macos/gse_20260415_080921.metrics.json` は Mac 側で偶然マッチしていたが、本 fix 後に再生成すべき (数値が変わる可能性)
- `gse-dataset/metrics/P000/windows/gse_20260415_144120.metrics.json` は fix 後に必ず再生成 (現在全 0 → 意味のある値へ)

### baseline_metrics.md
- 既存記載は fix 後に再計測した値で更新する必要あり。retrospective の「M1 類似の観察誤り学習」に追記
- Mac と Windows で同じ計算パスが使われることを fix 後に再確認

### Phase 2a Go/No-Go
- Fix 前: baseline_metrics.md の数値が信頼できない → Go 判定不能
- Fix 後: 再計算値で Go/No-Go を改めて評価

## D4. 副次的発見: logged feats にも `timestamp() -> None` で replay 排除されるコメントの精度

`bin/replay.rs:79-81`:
```
replay は FeatSnapshot 列を step() 再実行で自前生成するため、本 variant は入力からの読み飛ばし専用
```

この設計コメントは **step() の決定論検証 (snapshot path) には正しい**。しかし metrics path で同じ再生成列を使う実装は、コメントが主張する「専用」の意図を破っている。metrics パスで logged feat を使うよう fix すれば、コメントの設計意図とも整合する。

## D5. TDD 順序

1. 失敗する回帰テスト: `compute_session_metrics_on_logged_feats_matches_production()` — 合成 NDJSON (meta + key + ime_state{active:true が 10s 持続} + feat 15 件 + user_label 3 件) を入力として、warnings 空 + support>0 が成立することを期待
2. 失敗確認 (現実装では warnings 生成)
3. `collect_logged_feats()` 実装
4. `--metrics` 経路をそれで置き換え
5. テスト PASS 確認
6. 既存 51 tests PASS 維持
7. 実データ (`gse_20260415_144120.ndjson`) での warnings=0 を実証

## D6. 実装後の fix 検証結果 (2026-04-16)

### 実データ再計算 (`gse_20260415_144120.ndjson`)

| 指標 | fix 前 (regen feat) | fix 後 (logged feat) |
|---|---|---|
| warnings | 6 件 (全ラベルが ±1000ms 窓外) | **0 件** |
| per_class support | Flow 0 / Inc 0 / Stuck 0 | Flow 4 / Inc 1 / Stuck 1 |
| Macro F1 | 0.000 | **0.722** |
| Micro F1 | 0.000 | **0.667** |
| Detection lead median | +26315 ms | **-93 ms** (実質同期) |
| Stuck precision / recall / F1 | 0 / 0 / 0 | **1.0 / 1.0 / 1.0** |
| Flow precision / recall / F1 | 0 / 0 / 0 | 1.0 / 0.5 / 0.667 |
| Incubation precision / recall / F1 | 0 / 0 / 0 | 0.333 / 1.0 / 0.5 |

### ロールバック用 fix 前 JSON スナップショット

```json
{
  "total_labels": 6,
  "confusion": {"matrix": [[0,0,0],[0,0,0],[0,0,0]]},
  "per_class": [
    {"class":"flow","precision":0.0,"recall":0.0,"f1":0.0,"support":0},
    {"class":"incubation","precision":0.0,"recall":0.0,"f1":0.0,"support":0},
    {"class":"stuck","precision":0.0,"recall":0.0,"f1":0.0,"support":0}
  ],
  "macro_f1": 0.0,
  "micro_f1": 0.0,
  "detection_lead_ms_median": 26315,
  "stuck_recovery_ms_median": null,
  "warnings": [
    "label at t=1776264098036 has no FeatSnapshot within ±1000ms",
    "label at t=1776264100076 has no FeatSnapshot within ±1000ms",
    "label at t=1776264131043 has no FeatSnapshot within ±1000ms",
    "label at t=1776264133111 has no FeatSnapshot within ±1000ms",
    "label at t=1776264169265 has no FeatSnapshot within ±1000ms",
    "label at t=1776264177709 has no FeatSnapshot within ±1000ms"
  ]
}
```

### Mac baseline (`gse_20260415_080921`) の再計算

Mac NDJSON は `gse-dataset/raw/` に存在しない (`.gitignore` 対象)。ローカルの Mac 端末でのみ raw 保持が原則。Phase 2a 着手時までに Mac 側で `gse-replay --metrics --json` を fix 後 CLI で再実行し、dataset metrics JSON を上書きすることで補完する (completion-log.md の次アクション)。

## D7. Phase 2a Go/No-Go 判定への影響

- **fix 前**: Stuck precision は Mac 2/2 (P=1.0) だけだったが、Windows 分は warnings で脱落 → 実データ n=2
- **fix 後**: Windows 1 件が合流可能。Stuck precision 平均 = (Mac 1.0 + Windows 1.0) / 3 = **1.0** (n=3)、Go 条件 ≥ 0.6 を**満たす**

Phase 2a 着手は本 fix + Mac 分再計算 (後続) + サンプル n=5 到達待ちで継続判定。

## D8. レビューで指摘を受けた MEDIUM 5 件の処理方針

code-reviewer + security-checker の並列レビューで HIGH なし、MEDIUM 5 件。本タスクで対応したもの 3 件 + 別タスクに分離したもの 2 件:

### 本 fix 内で対応済み
- **M1 (silent skip 可視化)**: `collect_logged_feats` / `collect_user_labels` にスキップ件数カウント + `tracing::warn!` (件数のみ、行内容は出さない)。`feat` 0 件時は別途 warn で attention
- **M2 (schema_dto drift 検知)**: `logged_feat_dto_round_trips_schema_dto_feat_shape` テスト追加。`schema_dto::LogEntryDto::Feat` から serialize → `LoggedFeatDto` で parse → `FeatSnapshot` 変換の round-trip を assert。片方のフィールド定義が drift すれば CI で落ちる
- **M5 (層3 テスト閾値厳格化)**: `warnings.len() < 2` → `warnings.is_empty()` (第一 assert)、`matched >= 4` → `matched == 6` (全件マッチ要件)。Phase D-2 実測値どおり

### 後続タスクに分離
- **M3 (NaN/Inf/範囲外 float バリデーション)**: `From<LoggedFeatDto> for FeatSnapshot` を `TryFrom` 化し、`is_finite()` + 確率範囲 + `alpha ∈ [0,1]` 検査。**本 fix のスコープ (feat source 切替) を超える入力検証の拡張**のため別タスク起票 — `.steering/20260416-replay-input-validation/` (仮) 候補
- **M4 (2 パススキャン統合)**: `collect_logged_feats` + `collect_user_labels` を 1 パス化する `collect_session_artifacts(path) -> Result<(Vec<UserLabelEvent>, Vec<FeatSnapshot>), String>`。**性能最適化で、500MB ガード下では許容**。別タスク起票候補 — `.steering/20260416-replay-single-pass-collector/` (仮)

### LOW 3 件 (code-reviewer) — 任意改善、別 PR
- &Path vs &PathBuf (clippy ptr_arg)
- ReplayEvent::Feat を unit variant 化して metrics 経路が直接 from_str
- エラーメッセージのフルパス短縮 (security-checker LOW とも関連)
