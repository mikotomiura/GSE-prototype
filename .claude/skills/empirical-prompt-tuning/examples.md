# Empirical Prompt Tuning — 具体的な評価イテレーション記録例

## 例 1: `rust-standards` Skill の Lite 評価（2 iter で収束）

### シナリオ
新しい Rust ファイル `src-tauri/src/analysis/probe_scheduler.rs` を追加し、
`anyhow::Result` でエラーを伝播、`tracing` でログ、`windows` crate 禁止確認を行う。

### 要件チェックリスト
1. [critical] `tracing::info!` / `warn!` / `error!` のみ使用（`println!` 禁止）→ 理由: GSE ではログ集約のため
2. [critical] `anyhow::Result<T>` を返り値に使用 → 理由: エラーチェーンの統一
3. `unsafe` ブロックがあれば `/// # Safety` コメント付き
4. `cargo clippy` 警告 0 件（チェックリスト確認のみ）
5. 命名が `snake_case` に統一されている

### Iteration 0 — Structural check（dispatch なし）
- description「`hook.rs` / `logger.rs` を編集するとき」に `probe_scheduler.rs` の記載なし
- **修正**: description に `probe_scheduler.rs` を追加

### Iteration 1
変更点: description の対象ファイルリストに `probe_scheduler.rs` を追加

| シナリオ | 成功/失敗 | 精度 | steps | retries |
|---|---|---|---|---|
| median (probe_scheduler) | ○ | 100% | 6 | 0 |

不明瞭点（新出）:
- 「`windows` crate を使わない場合の依存チェックは省略して良いか?」と subagent が裁量補完

**収束**: 不明瞭点 1 件残り。次 iter へ。

### Iteration 2
変更点: `windows` crate ルールに「使わない場合も Cargo.toml に winapi がないか確認」を追記

| シナリオ | 成功/失敗 | 精度 | steps | retries |
|---|---|---|---|---|
| median (probe_scheduler) | ○ | 100% | 5 | 0 |

不明瞭点（新出）: なし
**収束**: Lite tier — 1 シナリオ × 2 iter クリア。停止。

---

## 例 2: `implementation-workflow` Skill の Full 評価（3 iter）

### シナリオ A（median）: 新機能 `probe_scheduler.rs` の追加
### シナリオ B（edge-low）: 既存テスト 0 件のモジュールのバグ修正
### シナリオ C（adversarial）: `implementation-workflow` を参照せず独力で進もうとする

### Iteration 0 — Structural check
- Step B の「サブエージェントを起動」が「File-finder と impact-analyzer の両方」なのか「どちらか」なのか不明
- **修正**: 「両方を並列で起動」と明文化

### Iteration 1 — 3 シナリオ並列
| シナリオ | 成功/失敗 | 精度 | steps |
|---|---|---|---|
| A (median) | ○ | 90% | 8 |
| B (edge-low) | × | 60% | 14 |
| C (adversarial) | ○ | 80% | 6 |

不明瞭点:
- **B**: [critical] 「Step F でテスト 0 件のモジュールのテスト戦略が不明瞭」→ cargo test の scope 未定義
- **B**: Step D の「30 分粒度」が既存テスト 0 件のケースでは過剰に見える

### Iteration 2
変更点: Step F に「既存テスト 0 件の場合は最小スモークテストを 1 本追加してから実行」を追記

| シナリオ | 成功/失敗 | 精度 | steps |
|---|---|---|---|
| A (median) | ○ | 95% | 7 |
| B (edge-low) | ○ | 90% | 11 |
| C (adversarial) | ○ | 85% | 6 |

不明瞭点: なし（全シナリオ新出ゼロ）

Hold-out シナリオ（2 本追加）:
| シナリオ | 精度 |
|---|---|
| H1: refactor + テスト変更なし | 85% |
| H2: 複数ファイル横断の feature | 80% |

→ 直近平均 90% から最大 10% 落ち。過適合なし。**停止。**

---

## Deferred evaluation の記録例

`.steering/deferred-evaluations.md` に追記するフォーマット:

```markdown
## hook-constraints — deferred 2026-06-16
- 理由: dispatch unavailable (subagent 内動作)
- 想定シナリオ:
  1. フックコールバック内で channel send を使う新規実装
  2. Atomic フラグ操作の正しい Ordering を選ぶ
- チェックリスト草案:
  - [critical] コールバック内に Mutex ロックがない → 理由: デッドロック防止
  - [critical] `try_send` でブロッキングしない → 理由: フックのタイムアウト
  - `Ordering::Relaxed` か `SeqCst` かを明示的に選択
- 想定 tier: Lite
```
