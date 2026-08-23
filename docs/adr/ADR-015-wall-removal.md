# ADR-015: Lv2 Wall と Monk Mode を全削除する

- **ステータス**: ★★★ **Accepted**（2026-08-23・研究者判断）
- **日付**: 2026-08-23
- **関連**: **ADR-004**（Decision Engine 境界）/ **ADR-003**（Core 外の opt-in extension）/
  `.steering/20260612-retro-labeling-and-corner-intervention/decisions.md` **D-5** /
  `.steering/20260814-expression-place-and-modality/decisions.md` **PM-D4 / PM-D11** /
  `.claude/skills/intervention-design/SKILL.md` / `.claude/skills/physical-anchor/SKILL.md`
- **作業記録**: `.steering/20260823-wall-removal/`

---

## Context

### 1. ★ 「Wall」は 3 つの別物で、既決の状態がそれぞれ違った

| 層 | 削除前の既決 |
|---|---|
| **ハード全画面ブロック UI** | ★ **D-5（2026-06-12・ユーザー承認）が「残さない」と決定済み**。⚠️★★★ **しかし未履行だった** |
| **`wall_server.rs`**（QR + `/unlock` の 1 ビット経路） | ⚠️ D-5 が「能動的に QR をスキャンして散歩する」を**強制力の中心として維持**と明記／⚠️★★★ **PM-D11 が Physical Anchor の運搬路として再利用する前提** |
| **Lv2 の判定・ログ・評価** | `intervention_eval.rs` が **HIR** を計算／`schema_dto.rs` が NDJSON schema を持つ／⚠️ **凍結中の G1 事前登録が「介入（Nudge / Wall）」を名指し** |

### 2. ⚠️★★★ 未履行だった D-5 の逐語

> **確定（2026-06-12 ユーザー承認）**: Lv2 は**ソフトのみ**。**ハード全画面ブロックは残さない**。
> 強制力は「能動的に QR をスキャンして散歩する」コミット + 画面端ビネット + 打鍵警告に限定。
> **クリック遮断なし**。walk-hard モードは実装しない。

⚠️ 実装は逆だった —— `Overlay.tsx` 逐語:
> `- Wall: **全画面 + クリックブロック**（QR スキャンまで操作不可・**現状維持**）`

### 3. ★ Monk Mode は **Wall 専用**だった

`intervention-design` SKILL **ルール 5** 逐語:
> **Monk Mode は Wall を無効化するだけ**。Monk Mode = true のとき、Wall 起動をスキップする。
> **Nudge は引き続き表示される（Monk Mode は Nudge を無効化しない）**。

★ 実装も同じで、`monk_mode` の作用は `apply_wall_suppressions` と累積リセットだけだった。
→ ⚠️★★★ **Wall を消すと Monk Mode は何もしないトグルになる。**

---

## Decision

### D1. ★★★ **Wall を全削除する**（UI / サーバ / 判定 / ログ / schema）

| 削除したもの |
|---|
| `src-tauri/src/wall_server.rs`（QR 生成・`/shake`・`/unlock`・ファイアウォールルール管理） |
| `InterventionAction::Wall`／Wall 閾値 6 種／`wall_accum_ms`／daily cap／cooldown／`force_wall` |
| `DismissReason` の Wall 応答（`early_unlock` / `completed` / `idle_timeout`） |
| Frontend の Wall UI（全画面ブロック・QR 表示・打鍵警告バナー・スマホ接続バッジ） |
| 依存 `tiny_http` / `qrcode` |

### D2. ★★★ **Monk Mode も一緒に削除する**（研究者判断）

★ 理由: **Wall 削除で定義上デッドになる**（Context-3）。⚠️ **UI に「何もしないトグル」を残さない。**
★ `session_meta` の `monk_mode` フィールドも外した。

### D3. ★ **HIR（有害介入率）は残す**

⚠️ **指標そのものは `research-positioning §5` H-X2 の最重要安全指標**である。
★ 変わったのは**対象から Wall が消えた**ことだけ（ACT = `{nudge}` になった）。

### D4. ⚠️★★★ **本 ADR は PM-D11 を覆す**

★ PM-D11（2026-08-15）逐語:
> ★ **二値なら既存の Wall Server の経路がそのまま使える** —— Wall は既にスマホ ↔ PC を
> QR ＋ `/shake` の **1 ビット**で行い、オンデマンド起動・停止時にファイアウォールルールを削除する。
> ★ **「歩いた」の 1 ビットは同じ形**なので、**新しい境界クラスを作らない**。

→ ⚠️★★★ **Physical Anchor は運搬路を失った。**
★ 実装時に **境界クラスの再設計が要る**（`data-privacy` / `physical-anchor` / PM-D4 の「一段大きい」判定）。
⚠️ **本 ADR では再設計しない。**

### D5. ⚠️ **凍結文書と履歴記録は書き換えない**

| 種別 | 扱い |
|---|---|
| **G1 事前登録**（第 17 版・凍結中） | ⚠️ **書き換えない。** ★ 起動モード表の「介入（Nudge / Wall）」は**実装とずれる**が、**ずれを記録として残す**（凍結の意味を守る） |
| `design-history.md` / `design-history.ja.md` / `references.md` | ⚠️ **書き換えない**（★ **何があったかの記録**である） |
| `research-positioning §5` | ⚠️ **書き換えない**（研究者確認が要る節） |

---

## Consequences

- ★ **既存データは壊れない** —— ⚠️ 削除前に実測で確認した:
  **フィクスチャ全数 / gse-dataset の `metrics/` のどちらにも `wall` は 1 件も無い**。
- ★ **確証標本 0/3 名 ＝ 収集開始前**なので、`preregistration.md §3.6` の回復不能問題は起きない。
- ⚠️ **NDJSON schema の破壊的変更**（`wall_accum_ms` / Wall action / Wall 応答 reason / `monk_mode`）。
  ★ **gse-dataset と parity 同期済み**。
- ⚠️★★★ **`elapsed_ms`（`intervention_response`）を書く経路が無くなった** ——
  ★ 書式は additive に残すが **現状 production では常に `null`**。⚠️ 復活しないなら次の整理で落とす候補。
- ⚠️ **`intervention-design` SKILL のルール 5（Monk Mode）と Lv2 の記述が無効**になった。
- ⚠️ **`physical-anchor` SKILL の「Wall Server から拡張する」パターンが無効**になった（D4）。
- ★ **削除したテスト 4 本を `.steering/20260823-wall-removal/decisions.md` D-5 に列挙**した
  （CLAUDE.md「既存のテストを無断で削除しない」）。

---

## Alternatives

- **全画面ブロック UI だけ消す**（D-5 の履行のみ）: ★ schema 不変・PM-D11 の経路維持・HIR 維持。
  ⚠️ **研究者は「wall_server も含めて全削除」を選択した**ため却下。
- **Monk Mode を Nudge 抑制へ転用する**: ⚠️ **振る舞いの新規追加**（Nudge はこれまで抑制されなかった）。却下。
- **Monk Mode を記録項目としてだけ残す**: ⚠️ **UI に何もしないトグルが残る**。却下。

---

## Migration

1. ✅ Rust（判定 / 評価 / ログ / schema / lib / `wall_server.rs` 削除 / 依存）— **完了**
2. ✅ Frontend（`App.tsx` / `Overlay.tsx` / `Dashboard.tsx` / `App.css`）— **完了**
3. ✅ `schema/current.json` 再生成 ＋ **gse-dataset 同期** — **完了**
4. ⚠️ **`intervention-design` / `physical-anchor` SKILL の改訂** — ★ 本 ADR と同時
5. ⚠️★★★ **Physical Anchor の運搬路の再設計** — ★ **別タスク**（D4）
6. ⚠️ **運用文書（`verification-runbook` / `pilot-runbook` / `wbs-verification-halfyear`）の Wall 記述** — ★ 別タスク
