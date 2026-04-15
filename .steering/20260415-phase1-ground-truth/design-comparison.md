# 設計案比較 — v1 vs v2

## v1 の要旨

requirement.md の文面に沿って「Dashboard の GT 3 択ボタン + 5 秒ホールド機構 + Tauri コマンド経由の `set_engine_paused` + 分析スレッドローカル `Arc<AtomicU64>` で `recovered_at` オンライン補完 + Rust 内蔵 `gse-replay --metrics`」を採用。既存パターン（手書き LogEntry シリアライザ、`#[tauri::command]` 登録）を忠実に踏襲。HIGH リスク #2 対策として「Analysis Thread recv 段で drain + `step()` 冒頭で `prev_paused` edge 検出」の 3 段ガードを追加。

## v2 の要旨

**汚染源を最初から作らない設計**に再構成。GT 付与は **OS グローバルホットキー**（`Cmd+Shift+Option+F/I/S`、2 秒デバウンス）で 1 秒以内に発火。**pause 機構を一切導入しない**。Dashboard は読み取り専用の counter widget のみ。`recovered_at` は `gse-replay --metrics` 実行時にオフライン純粋関数で後付け計算（ログには常に `None`）。メトリクスは Rust 内蔵 + JSON 出力 + オプショナル Python ヘルパーの 2 層。HIGH リスク #2 は設計レベルで発生源が消える。

## 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| **GT 付与 UX** | Dashboard 3 ボタン、5 秒ホールド、マウス必須 | OS グローバルホットキー ⌘⇧⌥F/I/S、2 秒デバウンス、マウス不要 |
| **認知負荷** | 5 秒の押下 + ボタンに視線移動 | キー 1 ストロークで完結（タイピング習慣の延長） |
| **Flow を壊すリスク** | 高（マウス移動 + 5 秒の意識的動作） | 低（打鍵の一部として発火できる） |
| **Engine pause** | `set_engine_paused` Tauri コマンド追加、Atomic 経由、`was_paused` 同期強化が必要 | **追加しない** |
| **HIGH リスク #2 (pause 中バッファ滞留)** | 対策 3 段ガード（B+C 併用）で軽減 | **設計レベルで発生源なし** |
| **recovered_at 計算** | 分析スレッド内、`Arc<AtomicU64>` + `out.feat.p_flow > 0.5` で逐次補完、再書き込み | gse-replay 内、純粋関数、常にログは `None`、閾値変更で再計算可 |
| **IPC コマンド数** | 2 (`record_user_label` + `set_engine_paused`) | 1 (`record_user_label`) |
| **タイムスタンプ** | クライアント側 (`Date.now()`) | サーバー側 (`now_ms()`、clock drift 排除) |
| **メトリクス surface** | Rust 内蔵 `--metrics` pretty-print のみ | Rust `--metrics` + `--metrics --json` + `ml/analyze.py` Python ヘルパー |
| **追加依存** | なし | `tauri-plugin-global-shortcut` |
| **変更規模** | logger.rs / lib.rs / loop_step.rs / replay.rs / Dashboard.tsx + analysis/metrics.rs | logger.rs / lib.rs / replay.rs / Dashboard.tsx + analysis/metrics.rs（+ Cargo.toml + capabilities） |
| **loop_step.rs 変更** | 必要（`was_paused` 同期強化、edge 検出） | **不要** |
| **engine.rs 変更** | 不要（`set_paused` 既存） | 不要 |
| **Dashboard.tsx 変更** | ボタン 3 + 5 秒ホールド state machine + mouseLeave ガード + toast | counter widget（読み取り専用） |
| **テスト戦略** | T1-6 で Tauri pause → extractor.reset 連動を検証（複雑） | T1-2 で純粋関数 `compute_recovered_at` を網羅（単純） |
| **ロールバック容易性** | 中（loop_step.rs 改修を元に戻すと誤検知リスクが復活） | 高（全変更が追加のみ、削除で元の状態に戻る） |
| **受け入れ条件との整合** | requirement L39「5 秒ホールド中の HMM pause が実機で目視確認済み」に完全一致 | **L39 と不整合**（採用時は受け入れ条件の書き換えが必要） |
| **将来拡張（Monk Mode 等の真の pause 機能）** | 本タスクで入れた pause 機構を流用 | 別タスクで正面から設計（責務分離） |

## 推奨案

**v2（再生成案）を採用**

### 根拠

1. **Flow を壊さないラベリング**: 本タスクのゴールは HMM の "Flow" 認識性能を測ることであり、ラベル付与自体が Flow を壊すと計測バイアスが入る。5 秒ホールドは Flow を壊すため、測定器が対象を変質させる問題が発生する。ホットキーは認知状態を最も侵さない。

2. **HIGH リスク #2 の解消方法の質**: v1 は「3 段ガードで軽減」、v2 は「発生源を断つ」。レビューやテストで見逃すリスクが圧倒的に低い（テストで検知できるのは作った機構の不具合であり、作らなかった機構は検知する必要がない）。

3. **production path を変更しない**: v2 は `loop_step.rs` / `engine.rs` を一切触らない。Phase 0 で安定させた分析パイプラインに手を入れずに Phase 1 の計測基盤を積み上げられる。

4. **閾値変更への柔軟性**: `recovered_at` をオフライン計算することで、Phase 2a 以降で `p_flow > 0.5` の閾値や回復窓サイズを変更した際に過去セッションを再評価できる。v1 はログ記録時の閾値でロックインされる。

5. **受け入れ条件の不整合は軽微**: requirement.md L39 の「5 秒ホールド中の HMM pause」は v1 の実装前提に引きずられた書き方であり、Phase 1 の本質的なゴール「GT 付きセッション ≥ 10 件 + メトリクス算出」から演繹されたものではない。受け入れ条件を「ラベル記録時に HMM 入力が汚染されないこと」へ書き換えることで意味は維持される。

### v2 採用時の追加タスク

- `requirement.md` L18 の「Dashboard への GT 3 択ボタン UI + 5 秒ホールド機構（誤タッチ防止）」を「グローバルホットキー + Dashboard counter widget」に修正
- `requirement.md` L39 の受け入れ条件を「ラベル記録時に HMM 入力が汚染されないこと（T1-6 で差分確認）」に修正
- 運用メモの Open 質問 1/2/4 が解決済みとして記録（3 は v2 でオフライン計算に確定）

### v1 を選ぶべきケース（参考）

- グローバルホットキーの OS 衝突・プラットフォーム差異でトラブった時の切り戻し案
- 将来 Monk Mode 等で真の pause 機能が必要になった時、v1 で作った pause 機構を再利用できる
- 「ラベル付与そのものが GT 収集の儀式であり、あえて 5 秒間 Flow を中断して意識的に内省する」UX が有効と判断される場合（研究視点としてあり得る）
