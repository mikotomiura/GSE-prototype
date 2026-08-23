# O1 の非打鍵タスクの穴と事前登録

- **日付**: 2026-08-23
- **種別**: ★ **設計と議論のみ**（⚠️ **実装しない**。`src-tauri/` も `src/` も触らない）
- **入口**: `.steering/_handoff/next-session-prompt-o1-nonkeystroke-and-preregistration.md`
- **前段**: `.steering/20260823-r3-accept-and-role-category/`（ADR-014 Accepted / O1 命名 / 判断 6 実装）

## 背景

`docs/architecture/workspace-behavior-observation.md §9`（2026-08-23 追記）が
**非打鍵タスク（CAD / 動画編集 / スライド / SD デザイン）の穴**を 3 件記録して未解決のまま残した。

- **7-a**: 非打鍵区間を「在席×非打鍵」と分類したあと **そこから先が無い**
- **7-b**: **O1（GSE 本体・常時）と ADR-012（別計測器・宣言ブロック）が同じ作業を別の計器で見る**が、
  突き合わせ方が未設計
- **7-c**: **非打鍵タスク向けの「段 2 の判定量」が空欄**（★ `vibe_coding` には V-1〜V-3 を書いた）

★ 併せて **O1 の事前登録**は「G1 を待たずに今日から進められる」唯一の項目である
（⚠️ 計器の実装 R3-a は **G1 の収集完了待ち**）。

## ゴール

★ 引き継ぎ §4 の **論点 1〜4** について、**閉じたもの / 閉じなかったもの**を分けて記録する。
⚠️ 「閉じなかった」は失敗ではない。**何が埋まれば閉じるか**を書けば足りる。

## スコープ

### 含むもの
- ★ `workspace-behavior-observation.md §9` への追記（判定量候補・7-b の訂正・閉じる条件）
- ★ **ADR 新設**（非打鍵区間の受け方）—— ⚠️ **段 1 を 1 文字も変えずに書ける場合のみ**
- ★ **O1 の事前登録の起草**（⚠️ **凍結しない・`experiments/` にはまだ置かない**）

### 含まないもの
- ⚠️ **実装**（`src-tauri/` / `src/` / schema / `HMM_VERSION`）
- ⚠️ **スマホ表現チャネル / Physical Anchor**（別タスク）
- ⚠️ **6 段階 ablation の事前宣言**（★ n と検出力の算術が未了）
- ⚠️ **計器の実装 R3-a**（★ G1 の収集完了待ち）

## 受け入れ条件

- [ ] 論点 1〜4 の**閉/未閉**を分けて記録した
- [ ] ⚠️ **凍結物を 1 文字も変えていない**
      （`workspace-behavior-observation.md §2.1` 段 1 / ADR-009 D2 の順序 /
       G1 事前登録 第 17 版 / `research-positioning.md §5` / ADR-012 D7 制約 4）
- [ ] ⚠️ **段 1 に候補チャネルを 1 本も足していない**
- [ ] ⚠️ **役割カテゴリで穴を埋めていない**
- [ ] ⚠️ **禁止語 grep** の結果を報告した
      （★ 式は `.steering/20260819-nonkeystroke-observation-space/requirement.md` の受け入れ条件にある。
       ⚠️ **ここに列挙すると自らの検査に引っかかる**ので書かない —— ADR-012 §Consequences と同じ作法）
- [ ] ⚠️ **実装していない**ことを明示した
- [ ] ★ 採番（ADR 番号・判定量の接頭辞）を **repo 全域**で数えてから使った
      （⚠️ `docs/` だけ見て「空いている」と言わない —— 2026-08-23 の `N1` 誤報告の再発防止）

## 関連ドキュメント

- `docs/architecture/workspace-behavior-observation.md`（全文・特に §7 / §9）
- `docs/adr/ADR-014-continuous-natural-work-collection.md`（D4 / D4b / D4c / D4d / D9 / 判断 1・4）
- `docs/adr/ADR-012-nonkeystroke-observation-formative-track.md`（D1 / D4 / D5 / D6 / D7 / D8 / D9）
- `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md`（D2 / D3 / D4）
- `docs/adr/ADR-010-task-scope-gating.md`（D1 / D3 / D5）
- `docs/adr/ADR-013-collection-self-description.md`（D1 の 3 群）
- `docs/architecture/personalization-and-online-learning.md`（§3.1 / §3.2 / §3.3 / §3.4 / §11-7 / §11-8）
- `docs/research-positioning.md`（§8 段別表 T0–T3 / §9 A-Q3）
- `docs/architecture/domain-adapter-boundary.md`（§Adapter C）
- `.steering/20260821-workspace-behavior-triage/survey-input-channels.md`（§3.6 / §4 表 8）
- `.steering/20260823-r3-accept-and-role-category/`（decisions.md D-11 / D-20 / role-category-feasibility.md）
