# 設計

## 実装アプローチ

**docs のみの是正。コード変更ゼロ。** ★ **docs をコードに合わせる。逆はしない。**

⚠️★★★ **順序が重要**: 先に**コードの ground truth を 1 回だけ確定**し、それを全エージェント・全編集で共有する。
★ 各ファイルごとに独立に「コードはどうなっているか」を調べ直すと、**調べ方の差で結論がぶれる**。

1. **ground truth の確定**（★ メインが実測・完了）
2. **監査の並列化**（サブエージェント 3 本・★ 編集はさせない。`file:line` の根拠つきで報告のみ）
3. **是正は直列**（★ メインが行う。並列編集は同一ファイルの競合と方針のぶれを生む）
4. **検証 → レビュー → `/cross-review`**

## 是正の 3 分類（★ これを全ファイルで統一する）

| 型 | 何をするか | 例 |
|---|---|---|
| **(1) 現行仕様の記述** | ⚠️★★★ **是正必須。** 実体に合わせるか、削除する | `functional-design.md`「Wall Need: `p_stuck >= 0.70` が累積 30 秒」 |
| **(2) 実行可能な指示** | ⚠️★★★ **是正必須。** ★ 特に**被験者・研究者向けは契約**である | runbook「Wall が出たら案内文に従う」（★ 前タスクで是正済み） |
| **(3) 過去形・ADR 参照つきの記述 / 訂正注記** | ★ **触らない。** 履歴であり、消すと「なぜ変わったか」が失われる | `architecture.md:223`「⚠️ `wall_server.rs` は存在しない」 |

★ **設計提案（「v2 ではこうする」）は (1) と区別する** —— ⚠️ ただし **ADR-015 が削除した機能を将来案として
挙げ続けるなら、「復活には新規 ADR が要る」旨の注記を足す**（★ 読者が「実装にある」と誤読するため）。

## 変更対象

### 修正するファイル（★ 監査結果で確定させる）
- `docs/functional-design.md` — Wall 仕様 19 箇所 ＋ Wall 以外の陳腐化
- `docs/architecture/intervention-decision-engine.md` — `InterventionAction` の型定義 ほか 8 箇所
- `docs/architecture/gse-v2-overview.md` — 同上 ＋ Monk Mode（4 箇所）
- `docs/architecture/personalization-and-online-learning.md` — 3 箇所
- `docs/development-guidelines.md` — Wall Server の性能・セキュリティ要件（3 箇所）＋ 規約の陳腐化
- `docs/repository-structure.md` — `Overlay.tsx` の説明 ほか ＋ **ファイル配置の全件照合**
- `docs/wbs-verification-halfyear.md` — 4 箇所（⚠️ 過去の計画部分は是正不要）

### 触らないファイル
- ⚠️ `docs/design-history.{md,ja.md}`（履歴文書）/ `docs/adr/*`（確定済み判断）/
  `docs/preregistration-v0.3.md`（凍結）/ `src-tauri/` `src/`（コード）

## メインが独立に実施した横断チェック（★ サブエージェントの結果に依存しない検算）

| # | 検査 | 結果 |
|---|---|---|
| 1 | `docs/architecture.md` が本当に是正済みか | ★ **是正済み**。残る 2 箇所は L57 / L223 の「存在しない」という明示的訂正 |
| 2 | docs が参照する `src-tauri/src/**.rs` `src/**.tsx` `scripts/*` は実在するか | ★ **存在しない参照は 1 件のみ** = `architecture.md:223` の `wall_server.rs`（★ 「存在しない」と書いている行なので正しい） |
| 3 | docs の `invoke("...")` が実在コマンドか | ★ **存在しない参照 0 件**（実在 38 コマンドと照合） |

→ ★ **陳腐化は「ファイル名・コマンド名」ではなく「仕様の記述」に集中している**という見立てが立つ。

## テスト戦略

★ 文書のみなので、**機械検査 + 実測 grep** で行う（`verify-before-claiming` ルール 5: 予測せず走らせる）。

| # | 検査 | 合格条件 |
|---|---|---|
| 1 | `PYTHONUTF8=1 python scripts/check_citations.py` | 違反なし |
| 2 | `git status --porcelain src-tauri src` | **空**（コード変更ゼロ） |
| 3 | 対象 7 ファイルの `Wall` / `Monk Mode` / `Zen Timer` / `wall_server` | ★ **残るものが全て過去形・ADR 参照つき・訂正注記**であること（目視 + grep） |
| 4 | docs → コードのファイル参照 | 存在しない参照ゼロ（上表 #2 のスクリプトを再実行） |
| 5 | docs → Tauri コマンド参照 | 存在しない参照ゼロ（上表 #3 を再実行） |

## ロールバック計画

★ ブランチ `docs/stale-sweep`。**ファイル単位で 1 コミット**に近い粒度で積み、
問題があれば該当コミットのみ revert する。⚠️ コード変更が無いので実行時リスクはゼロ。
