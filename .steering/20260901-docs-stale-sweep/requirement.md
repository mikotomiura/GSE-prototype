# docs の陳腐化一掃 — 削除済み機能・実装と食い違う記述の是正

- **開始**: 2026-09-01
- **前タスク**: `.steering/20260901-research-positioning-fix/`（blockers.md 持ち越し 1 / 2 / 3）
- **入口**: 研究者の指示「具体的な docs などの修正なども行いましょう。情報などはかなり古いと思うので」

## 背景

ADR-015（2026-08-23）で **Wall / Zen Timer / Monk Mode / `wall_server.rs` を全削除**したが、
⚠️ **ADR-015 Consequences 6 が挙げた「運用文書の Wall 記述」の積み残しが、docs 全体に残っている。**

★ 前タスクで `research-positioning.md` / `glossary.md` / runbook 3 本は是正済み。
**本タスクは残りを一掃する。**

### 実測（2026-09-01・`grep -c 'Wall\|Monk Mode\|Zen Timer\|wall_server'`）

| ファイル | 件数 | 状態 |
|---|---|---|
| `docs/functional-design.md` | **19** | ⚠️★★★ **未是正・最大**。Wall Need 閾値 / cooldown / daily cap / Wall Server / Monk Mode を**現行仕様として記述** |
| `docs/architecture/intervention-decision-engine.md` | **8** | ⚠️★★★ **未是正**。`InterventionAction{None,Nudge,Wall,Defer}` を現行型として記述 |
| `docs/architecture/gse-v2-overview.md` | **4** | ⚠️ **未是正**。同上 ＋ Monk Mode |
| `docs/wbs-verification-halfyear.md` | **4** | ⚠️ **未是正**。強 Wall / Wall 閾値を WBS の前提に置く |
| `docs/architecture/personalization-and-online-learning.md` | **3** | ⚠️ **未是正** |
| `docs/development-guidelines.md` | **3** | ⚠️ **未是正**。Wall Server の性能・セキュリティ要件 |
| `docs/repository-structure.md` | **2** | ⚠️ **未是正**。`Overlay.tsx` を「Nudge/Wall 介入オーバーレイ」と説明 |
| `docs/architecture.md` / `agent-shared.md` / `glossary.md` / `research-positioning.md` / runbook 3 本 | — | ★ **是正済み**（ADR 参照つきの過去形・訂正注記） |
| `docs/design-history.{md,ja.md}` / `docs/adr/*` | — | ⚠️ **触らない**（履歴文書・確定済み判断） |

### ★ コードの ground truth（2026-09-01 実測）

```
src-tauri/src/analysis/intervention.rs:16-20
pub enum InterventionAction { None, Nudge, Defer }
```
★ `src-tauri/src/lib.rs` の `#[tauri::command]` 一覧に **`start_wall_server` / `monk_mode` 系は存在しない**。
★ `src/components/Dashboard.tsx:564-587` のデバッグボタンは **`debug_force_probe` と Nudge の 2 つのみ**。

## ゴール

⚠️★★★ **docs を読んだ人（人間・エージェント）が「実装にあるはずのもの」を探して見つからない、という状態をゼロにする。**
★ 判定は **「実行可能な指示 / 現行仕様の記述として、削除済み機能が登場しないこと」**。

## スコープ

### 含むもの
- 上表の**未是正 7 ファイル**の是正
- ⚠️ **Wall 以外の陳腐化も拾う**（研究者の指示「情報などはかなり古い」）——
  ★ **docs の記述とコードの実体が食い違う箇所全般**（型・コマンド名・フィールド名・閾値・ファイル名）

### 含まないもの
- ⚠️ **`docs/design-history.{md,ja.md}`** —— **履歴文書。過去の実装を記述するのが役目**（触らない）
- ⚠️ **`docs/adr/*`** —— 確定済み判断。改訂は新規 ADR の追補で行う（ADR-012 / ADR-018 の先例）
- ⚠️ **`docs/preregistration-v0.3.md`** —— **凍結文書**
- ⚠️ **`src-tauri/` / `src/`** —— **コード変更ゼロ**（docs をコードに合わせる。逆はしない）
- ⚠️ **段階呼称 Lv1〜Lv4 の docs 全体一括改名** —— ADR-018 D7 が「別タスク」と明記。
  ★ ただし**削除済み機能に触れる箇所は実体名へ寄せる**（Wall 是正と不可分なため）

## 受け入れ条件

- [ ] 未是正 7 ファイルから、**現行仕様・実行可能な指示としての Wall / Monk Mode / Zen Timer / `wall_server` が消えている**
- [ ] 残る言及は**すべて ADR-015 参照つきの過去形か訂正注記**である
- [ ] `InterventionAction` の記述が**コードの実体（`None/Nudge/Defer`）と一致**する
- [ ] Wall 以外に発見した実装との食い違いも是正されている（★ 発見できなかったら「探した範囲」を明記）
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が違反なし
- [ ] `git status --porcelain src-tauri src` が空
- [ ] `code-reviewer` + `security-checker` 並列 → `/cross-review`

## 運用メモ
- **/reimagine 適用: No** — 設計判断を伴わない事実整合。取るべき形はコードが既に決めている。

---

## ⚠️★★★ スコープ追加（2026-09-01・研究者の指摘）—— 軸が 1 本足りなかった

研究者の指摘: **「表現層の内容など、最新の全体設計なども全体にちゃんといきわたってる？」**

★ **当初のスコープは「古い記述が残っているか」の軸しか見ていなかった。**
⚠️ **逆向きの軸 —— 「新しい決定が、それを反映すべき文書に届いているか」—— が抜けていた。**

### 実測（2026-09-01）

**ADR-018（2026-08-30・最新の ADR）を参照している docs は、Physical Anchor を語る 6 本のうち 0 本。**

| ファイル | Physical Anchor 言及 | ADR-018 参照 |
|---|---|---|
| `docs/agent-shared.md` | 2 | ❌ |
| `docs/architecture.md` | 4 | ❌ |
| `docs/architecture/expression-channel.md` | 3 | ❌ |
| `docs/architecture/gse-v2-overview.md` | 2 | ❌ |
| `docs/functional-design.md` | 1 | ❌ |
| `docs/wbs-verification-halfyear.md` | 4 | ❌ |

★ ADR 別の浸透（言及ファイル数・`adr/` 自身を除く）: ADR-014=**4** / ADR-015=8 / ADR-016=**2** /
ADR-017=5 / ADR-018=5（⚠️ **うち 4 本は本日メインが編集した結果**であり、元は `glossary.md` の 1 本のみ）。

### ★ 特に重い 2 箇所

1. **`docs/architecture/expression-channel.md`** —— ★ **表現チャネルの SSOT**。
   ADR-017 の D3 / D7 / D10 を全面的に引いているのに、**それらを改訂した ADR-018 を 1 度も参照していない**。
   ⚠️ **§6「出口との構造的関係（ADR-017 D7）」（L267-285）が旧のまま** ——
   ADR-018 **D5 が出口の評価量を「実行率 / 完了率」から「招待の受容 ＋ 機会保存の行動指標」へ差し替えた**のに
   反映されていない。加えて L269「**Lv2 Wall**」/ L285「**Lv3/Lv4**」が残る。
2. ⚠️★★★ **`docs/agent-shared.md:12-14`** —— ★ **Claude Code と Codex CLI が毎セッション読む**
   プロジェクト一行説明。逐語「段階的介入 (**Lv1 Nudge → Lv3/Lv4 Physical Anchor**)」。
   ★ ADR-018 **D7（Lv 呼称廃止）＋ D1（完了条件撤廃）で「強度が単調に上がる段」という構造自体が現存しない**。
   → ⚠️★★★ **全エージェントが毎セッション、既に無い構造を前提に起動している。**
   ★ **本タスクで最も実害が大きい 1 行である。**

### 逆向きの穴（O1）

⚠️ **O1（継続的自然作業収集）は現在進行中の収集**（`Form_O1/` / `docs/o1-deletion-ledger.md` /
`src-tauri/src/o1.rs`）だが、**ADR-014 は 4 ファイル・ADR-016 は 2 ファイル**にしか言及が無い。
★ **`functional-design.md`（機能仕様の SSOT）に O1 の記述があるかは監査中。**

### 追加した受け入れ条件

- [ ] **ADR-018 の 7 決定**が、反映されるべき docs に届いている（★ 特に expression-channel.md §6 と agent-shared.md）
- [ ] **ADR-017（表現チャネル）** の決定が `functional-design.md` に届いている（★ 無いなら「無い」ことを記録）
- [ ] **O1（ADR-014 / ADR-016）** が機能仕様・アーキテクチャ・リポジトリ構成の各 SSOT に届いている
- [ ] `docs/agent-shared.md` のリンクハブ表に、実在するのに載っていない docs が無い
