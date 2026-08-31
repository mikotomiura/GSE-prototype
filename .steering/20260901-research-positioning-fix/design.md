# 設計

## 実装アプローチ

**文書のみの是正。コード変更ゼロ。** 一次証拠は `survey-notes.md` に揃っているので再サーヴェイはせず、
**未取得の一次（de Jong 本文 / Bell 本文 / DOI 未確定分）だけ**をサブエージェント 3 本で並列に取りに行き、
`docs/references.md` への append は**メインが直列で**行う（★ 並列 append は採番が壊れる）。

順序は **references.md（採番の確定）→ 本文の是正 → カード → _index → 機械検算**。
★ 逆順にすると本文が未登録 `[Pn]` を参照して `check_citations.py` が赤になる。

## 変更対象

### 修正するファイル

- `docs/references.md`
  - **append**: `[P192]` 以降に約 24 件（★ 末尾の次番号・renumber 禁止）
  - **既存行の訂正 2 件**（★ 番号・key・状態は変えない。**接地列のみ**）:
    - `[P8]` Oppezzo — 「Physical Anchor（歩行→創造性）の理論根拠」→
      「歩行→**拡散的思考**。⚠️ **認知回復の根拠ではない**（[P162] は歩行特化推定値が存在しないと明記）」
    - `[P10]` Kaplan ART — 「Physical Anchor（注意回復理論 ART）」→
      「⚠️★★★ **限定資源モデルそのもの**（[P192] が ego depletion へ明示接続）／事前登録検定は全 null →
      **理論基盤として引かない**」

- `docs/research-positioning.md` — 5 件の是正（下記「是正の内訳」）

- `docs/literature/_index.md` — de Jong カードの行を追記（★ 件数の手書きがあれば実測値に合わせる）

### 新規作成するファイル

- `docs/literature/20260901-typing-dynamics-mental-fatigue.md` — de Jong et al. (2020) の落合フォーマットカード

### 削除するファイル
- なし（★ append-only / tombstone 規約により行の削除はしない）

## 是正の内訳（research-positioning.md）

| # | 行 | 現状 | 是正後 |
|---|---|---|---|
| (1) | L209 | 「身体性・自然と回復 [P2][P8][P10][P14] … Physical Anchor の**理論基盤**」 | ART を理論基盤から外す。★ 語彙を「回復」→「**関与の再開**」へ（Lin 2020 / Hopstaken 2015）。⚠️ 「回復」「消耗」「リソースの補充」は**限定資源モデルの語彙**なので使わない |
| (2) | L111 / L211 / L657 / L667 / L749 | [P8] を「歩けば認知が回復する」の根拠として引く | 誤読の是正を **L211 の 1 箇所に集約**し、他 4 箇所から [P8] を外す（判断 1） |
| (3) | L228 / L597 / L602 / L667 | Lv2 Wall を**現行機能**として記述 | 現行レパートリーから Wall を外し、**実体名（Nudge / Physical Anchor）**へ。⚠️ **Wall が「あった」という設計空間上の記述は ADR-015 への参照つきで過去形にする**（履歴を消さない） |
| (4) | L455-457 | [P166] を「実環境 > 仮想環境 ＝ GSE に有利」と読む | ⚠️ 同著者の事前登録 RCT (2021) が null であることを併記し、**有利という読みを取り下げる**。★ 併せて L457 の「[P162] との未解決の矛盾」を**用量**で説明する（Bell の一次取得が前提） |
| (5) | L752 / L1119 | 完了条件「時間 ＋ 復帰」を現行の決定として記述 | **ADR-018 D1・D2 に追随**（系は完了を判定しない・閾値を置かない）。⚠️ `glossary.md:240` の禁止用語に一致させる |

## 影響範囲

- ★ **`docs/` 内の他文書からの参照**: `research-positioning.md` を参照している docs が
  同じ古い主張を持っていないかを grep で確認する（★ `verify-before-claiming` ルール 2「消費者を探す」）。
- ⚠️ **凍結文書 `docs/preregistration-v0.3.md`** にずれがあっても**直さない**。発見したら `blockers.md` に記録。
- ⚠️ **過去 ADR 本文**は触らない。

## 既存パターンとの整合性

- `citation-ssot`: append-only / 恒久 ID / renumber 禁止 / 重複防止キー = DOI・arXiv・正規化 URL /
  ★ **書誌未確定は `provisional`（捏造した DOI・URL を書かない）**
- `literature-card`: 落合フォーマット 6 項目 + 「やり残し」1 行 + §4 差分との関係 1 行
- ★ 既存本文の書式（⚠️ / ★ / ★★★ による危険度マーク、逐語は英語原文のまま `*"..."*`）を踏襲する

## テスト戦略

★ 本タスクは文書のみなので、検証は**機械検算 + 実測 grep** で行う（`verify-before-claiming` ルール 5:
「赤になる / 緑になる」は走らせてから言う）。

| # | 検査 | 合格条件 |
|---|---|---|
| 1 | `PYTHONUTF8=1 python scripts/check_citations.py` | **違反なし**（未登録参照 / 欠番 / 相互リンク無しの同一 key / tombstone 誤用がゼロ） |
| 2 | `git status --porcelain src-tauri src` | **空**（コード変更ゼロ） |
| 3 | `grep -nE 'Lv2 *Wall' docs/research-positioning.md` | ★ **現行機能としての記述がゼロ**（過去形・ADR-015 参照つきの記述のみ残る） |
| 4 | `grep -n '完了条件' docs/research-positioning.md` | ★ ADR-018 に追随した記述のみ（`glossary.md:240` の禁止用語に一致） |
| 5 | 追加した `[Pn]` の連番 | ★ `[P192]` から**欠番なし**で連続（check_citations.py が検出） |

⚠️ **単体テスト / 統合テスト / E2E は不要**（`src-tauri/` `src/` に触らないため）。

## ロールバック計画

★ 作業ブランチ `docs/research-positioning-fix` を切り、1 コミット 1 論理単位で積む
（references append → 本文是正 → カード + index）。問題があれば該当コミットを revert すれば
`docs/references.md` の採番だけが残る。⚠️ **番号は再利用しないので、revert しても [P192..] は欠番にしない**
（再是正時は続きの番号を使う）。
