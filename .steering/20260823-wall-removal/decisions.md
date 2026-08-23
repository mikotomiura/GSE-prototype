# 決定記録 — Wall (Lv2 介入) の全削除

> 2026-08-23 / `.steering/20260823-wall-removal/`

---

## D-1: ★★★ 着手前に「Wall」を 3 つに切り分けた（★ 既決の状態が違う）

| 層 | ★ 既決の状態 |
|---|---|
| **ハード全画面ブロック UI** | ★ **D-5（2026-06-12・ユーザー承認）が「残さない」と決定済み。**⚠️★★★ **しかし未履行だった** —— `Overlay.tsx:221` 逐語「Wall: **全画面 + クリックブロック**（QR スキャンまで操作不可・**現状維持**）」 |
| **`wall_server.rs`（QR + `/unlock` の 1 ビット経路）** | ⚠️ **D-5 が「能動的に QR をスキャンして散歩する」を強制力の中心として *維持* と明記。**⚠️★★★ **`PM-D11`（2026-08-15）が Physical Anchor の運搬路として再利用する前提** |
| **Lv2 介入の判定・ログ・評価** | ⚠️ `intervention_eval.rs` が **HIR（最重要安全指標）** を計算／`schema_dto.rs` が NDJSON schema を持つ／**凍結中の G1 事前登録が「介入（Nudge / Wall）」を名指し** |

★ **研究者は上記を提示したうえで「wall_server も含めて全削除」を選択した**（2026-08-23）。

## ⚠️★★★ D-2: 本タスクは **PM-D11 を覆す**

- ★ PM-D11 逐語: 「★ **二値なら既存の Wall Server の経路がそのまま使える** …
  ★ **『歩いた』の 1 ビットは同じ形**なので、**新しい境界クラスを作らない**」
- → ⚠️★★★ **Physical Anchor は運搬路を失った。** ★ 実装時に **境界クラスの再設計が要る**。
- ⚠️ **本タスクでは再設計しない**（★ 「空いた」ことを記録するまで）。

## ★ D-3: 削除前に確認した事実（★ リスクを下げたもの）

| # | 確認 | ★ 結果 |
|---|---|---|
| 1 | 既存フィクスチャの `wall` / `wall_accum_ms` | ✅ **1 件も無い**（`tests/fixtures/*.ndjson` 全数） |
| 2 | gse-dataset `metrics/` の `wall` | ✅ **1 件も無い** |
| 3 | 確証標本 | ✅ **0/3 名 ＝ 収集開始前** |

→ ★ **既存データは壊れない。** ⚠️ 壊れたのは**将来の計画**（PM-D11）である。

## ⚠️★★★ D-4: **Monk Mode が定義上デッドになった**（★ 研究者判断が要る）

- ★ `intervention-design` SKILL **ルール 5** 逐語:
  > **Monk Mode は Wall を無効化するだけ**。Monk Mode = true のとき、Wall 起動をスキップする。
  > **Nudge は引き続き表示される（Monk Mode は Nudge を無効化しない）**。
- ⚠️★★★ **実装もそのとおりだった** —— `monk_mode` の唯一の作用は `apply_wall_suppressions` と
  `update_wall_accumulation` のリセットだけ。→ ★ **Wall を消すと Monk Mode は何もしないトグルになる。**
- ⚠️ **`monk_mode` は `session_meta` の記録項目でもある**（NDJSON schema）。
- ★ 選択肢: **(a) Nudge も抑制する**（「邪魔しない」という名前の意図に合わせる）/
  **(b) 一緒に削除する** / **(c) 記録項目としてだけ残す**。→ ⚠️ **未決。研究者へ返す。**

## ★ D-5: テストを 4 本削除した（⚠️ 無断削除ではない）

★ CLAUDE.md 禁止事項「既存のテストを無断で削除しない」に従い、**削除したものを列挙する**:

| テスト | 何を検査していたか |
|---|---|
| `wall_after_sustained_stuck_and_opportunity` | Wall 発火判定（累積 30s × need/opportunity） |
| `monk_mode_suppresses_wall` | ⚠️★ **Monk Mode の唯一の作用**（→ D-4） |
| `wall_active_advances_last_tick_no_accum_blowup_on_dismiss` | 解除直後の即時再発火の回帰（cross-review HIGH-A 由来） |
| `force_wall_decision_returns_wall_and_starts_cooldown` | デバッグ強制 Wall |

★ さらに `intervention_response_line_wall_with_elapsed` を
**`intervention_response_line_can_still_carry_elapsed_ms` へ置換**した
（⚠️ `elapsed_ms` を書く経路は Wall だけだったので、**現状 production では常に `null`**）。

## ★ D-6: 進捗（2026-08-23 時点）

| 範囲 | 状態 |
|---|---|
| `intervention.rs`（判定・閾値・cooldown・cap・累積） | ✅ 完了 |
| `intervention_eval.rs`（HIR の対象から Wall を外す） | ✅ 完了（★ **HIR 指標自体は残す**） |
| `logger.rs`（`wall_accum_ms` / Wall 応答 reason） | ✅ 完了 |
| `schema_dto.rs` ＋ `schema/current.json` ＋ gse-dataset parity | ✅ 完了（**26,790 bytes・in sync**） |
| `lib.rs`（module / commands / state / shutdown） | ✅ 完了 |
| `wall_server.rs` の削除 | ✅ 完了（`git rm`） |
| `Cargo.toml`（`tiny_http` / `qrcode`） | ✅ 完了 |
| ⚠️ **Frontend**（`App.tsx` / `Overlay.tsx` / `Dashboard.tsx` / `App.css`） | ⚠️ **未着手** |
| ⚠️ **docs / SKILL / ADR** | ⚠️ **未着手** |

⚠️★★★ **現状はコミットできない** —— Rust は緑だが、**Frontend が削除済みの Tauri コマンド
（`force_wall` / `start_wall_server` / `stop_wall_server`）を呼び続けている**ため、
このままコミットするとアプリが実行時に壊れる。

### ★ Rust 側の検証（すべて緑）

`cargo test --workspace` **461 passed / 0 failed**（★ 465 − 削除した Wall テスト 4 本）／
ゴールデン replay **15 snapshots 一致**／`cargo fmt --check` OK／
schema parity **in sync (26,790 bytes canonical)**。
