# research-positioning.md の SSOT 是正と de Jong (2020) カード化

- **開始**: 2026-09-01
- **入口**: `.steering/_handoff/next-session-research-positioning-fix.md`
- **前タスク**: `.steering/20260830-mitou-2027-proposal-slimming/`（サーヴェイ 4 本の一次証拠は
  同ディレクトリの `survey-notes.md`（331 行）に全部ある。★ 再サーヴェイは不要）

## 背景

2026-08-30〜31 の未踏 2027 提案書の書き直しでサーヴェイ 4 本を回した結果、
**`docs/research-positioning.md`（研究の問い・差分の SSOT）に不整合が見つかった**が、
当該タスクのスコープ外として残されていた。

⚠️ 本タスクの着手時に **5 件目（ADR-018 との齟齬）を新たに実測で発見**した（下記 (5)）。

| # | 不整合 | 現状 |
|---|---|---|
| (1) | **ART（注意回復理論）を Physical Anchor の「理論基盤」として引いている**（L209） | ⚠️★★★ ART は **限定資源モデルそのもの**であり、事前登録された検定は 5 本すべて null |
| (2) | **[P8] Oppezzo & Schwartz が「歩けば認知が回復する」の理論根拠として引かれている**（L211 ほか計 6 箇所） | ⚠️ [P162] は逐語で「**歩行に特化した推定値は存在しない**」 |
| (3) | **Lv2 Wall が「現行機能」として書かれている**（L228 / L597 / L602 / L667） | ⚠️★★★ **ADR-015（2026-08-23）で削除済み**。SSOT が古い |
| (4) | **[P166] Stevenson 2018 を「実環境 > 仮想環境 ＝ GSE に有利」と読んでいる**（L456） | ⚠️ **同じ著者の事前登録 RCT（2021）は null**。そのまま出すと自傷 |
| (5) | ★ **完了条件「時間 ＋ 復帰」を現行の決定として書いている**（L752 / L1119） | ⚠️★★★ **ADR-018 D1 が既決 D11 条件 2 を取り下げ済み**。かつ `docs/glossary.md:240` は「完了 / クリア / 時間達成」を**既に禁止用語**にしている |

併せて、サーヴェイの予定外の収穫として **de Jong et al. (2020)**（実オフィス 6 週間・打鍵動態から
精神的疲労を検出）が見つかった。★★★ **GSE のセンシング方式そのものの先行研究**であり、
⚠️ **著者自身が GSE の偽陽性リスクを名指ししている**ため、カード化して §3/§4 に還元する。

## ゴール

`docs/research-positioning.md` が **2026-09-01 時点の確定済み ADR（ADR-015 / ADR-017 / ADR-018）と
一次文献の状態に一致**し、査読者の第一撃（「ART に依拠している時点で限定資源モデルを再輸入している」）に
無防備な記述が残っていない状態。

## スコープ

### 含むもの
- `docs/research-positioning.md` の 5 件の是正
- `docs/references.md` への一次資料 append（append-only・採番は `[P192]` / `[V89]` から）
- `docs/literature/<日付>-typing-dynamics-mental-fatigue.md`（de Jong カード）+ `_index.md` 追記
- `[P8]` / `[P10]` の**接地列の訂正**（★ tombstone ではない → `decisions.md` 判断 1）

### 含まないもの
- ⚠️ **`docs/preregistration-v0.3.md`** —— **凍結文書**。ずれは記録として残すのみ
- ⚠️ **過去 ADR の本文**（ADR-001〜018）—— 改訂は新規 ADR の追補で行う（ADR-012 / ADR-018 の先例）
- ⚠️ **`docs/mitou_docs/`** —— 2026-08-31 に確定済み
- ⚠️ **`src-tauri/` / `src/`** —— **コード変更ゼロ**
- ⚠️ **`docs/` 全体の Lv1〜Lv4 一括改名** —— ADR-018 D7 が明示的に「本 ADR の範囲外（別タスク）」と
  している。★ 本タスクは **research-positioning.md 内のみ**実体名へ寄せる
- 再サーヴェイ（`survey-notes.md` の一次証拠を使う。★ 未取得の一次のみ取りに行く）

## 受け入れ条件

- [x] `research-positioning.md` の 5 件が是正され、**ART が「理論基盤」から外れている**
- [x] `[P8]` / `[P10]` の接地列が訂正され、本文の誤用（「歩けば認知が回復する」）が消えている
- [x] **Wall が現行機能として登場しない**
- [x] `docs/literature/` に de Jong カードがあり、`_index.md` に載っている
- [x] `docs/references.md` に未登録の一次資料が append されている（★ append-only・番号再利用なし）
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` が **違反なし**
- [x] `git status --porcelain src-tauri src` が **空**
- [ ] `/cross-review` をパス限定で実行済み
  - ⚠️ 2026-09-01: sandbox 内ではネットワーク制限で `codex exec` が失敗。
    `require_escalated` 再実行は「外部 Codex/OpenAI service へ diff を送る明示承認が不足」として
    auto review に拒否されたため、**ユーザーの明示承認待ち**。

## 関連ドキュメント

- `.steering/20260830-mitou-2027-proposal-slimming/survey-notes.md` — ★ **一次証拠と逐語の全部**
- `docs/adr/ADR-015-wall-removal.md` — Wall 削除
- `docs/adr/ADR-017-expression-channel-boundary.md` — 境界クラス・D10 センシング恒久除外
- `docs/adr/ADR-018-physical-anchor-without-completion.md` — ★ 完了条件を課さない / D7 段階呼称
- `docs/glossary.md` §禁止用語 — ★ 既に ADR-018 D6 で更新済み（本文がこれに追随していない）
- Skill: `citation-ssot` / `literature-card` / `verify-before-claiming`

## 運用メモ
- **/reimagine 適用: No**
- 理由: アーキテクチャ判断も API 設計も伴わない **SSOT 文書の事実整合**であり、
  取るべき形は一次文献（`survey-notes.md`）が既に決めている。複数案が競合する余地が無い。
