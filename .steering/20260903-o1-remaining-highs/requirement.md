# O1 の残り HIGH を塞ぐ（#1 / #3 / #4 / #5）

## 背景

`.steering/_handoff/next-session-prompt-o1-remaining-highs.md` が O1 配布前の残 HIGH を 5 件
挙げていた。本セッションで **#1 / #3 / #4 / #5** に着手する（#2 = G1 側のロスター形検査の
移植は研究者判断でスコープ外）。

### ⚠️ 引き継ぎメモの記述を一次資料で検算した結果（★ メモを一次資料にしない）

| # | メモの記述 | 実コードでの確認 | 判定 |
|---|---|---|---|
| 1 | `O1_MGMT_SHEET_ID` はコメント 2 件のみ・`GSE_O1_Submit.gs` に 0 件 | `grep -rn O1_MGMT_SHEET_ID Form_O1/ Form_G1/` → `GSE_O1_Form_Builder.gs:119,131` の 2 件だけ。両方コメント | ✅ 一致 |
| 2 | `ROSTER_HEAD` は O1 に 14 件 / G1 に 0 件 | `grep -c` → O1 Builder 14 / G1 Builder 0 / 両 Submit 0 | ✅ 一致（★ 今回スコープ外） |
| 3 | 「conflict 行が無制限に積み上がる」「`o1FindRosterByEmail_`」「`applyRunValidation_` の 100 行を超えうる」 | ⚠️ **3 点とも実体と違う**（下記） | ❌ **要訂正** |
| 4 | メール重複は先頭行を黙って採用（P-ID 重複は止まる） | `GSE_O1_Form_Builder.gs:998-1013` が最初の一致で `return`。`:1609-1626` は P-ID 重複で中止 | ✅ 一致 |
| 5 | `LockService.getScriptLock()` はプロジェクト単位・対策は窓を狭めるだけ | `:1058` / `:1589` / `:1595` / `:1620` を逐語確認 | ✅ 一致 |

#### ⚠️ #3 の訂正（★ このメモを鵜呑みにすると存在しないバグを直しに行く）

1. ★ **`o1FindRosterByEmail_` という関数は存在しない**。実名は `o1FindInPhase1Roster_`
   (`GSE_O1_Form_Builder.gs:989`)。
2. ★ **`applyRunValidation_` は O1 に無い**。`grep -rn applyRunValidation_ Form_O1/ Form_G1/` の
   ヒットは **全件 `Form_G1/GSE_G1_Form_Builder.gs`**（`:1615` 定義）。100 行の上限
   (`:1619-1620` 逐語「100 行で足りる（G1 の被験者は 2 桁）」) は **G1 の「G1 実施トラッキング」
   タブのドロップダウン**の話で、O1 の conflict とは無関係。
3. ⚠️★★★ **現在の conflict 経路は 1 行も書いていない**。`GSE_O1_Form_Builder.gs` の
   書き込みは `:1272` / `:1550` / `:1556` / `:1561` / `:1570` の 5 か所だけで、
   conflict 分岐 (`:1531-1540`) は **`Logger.log` して `return null` するだけ**である。
   → ★ **「積み上がる行」は今は存在しない。**

→ ★ したがって #3 は **既存バグではなく、#1（追記ログ）を作るときに満たすべき設計制約**
  として扱う（★ ログ行は本質的に無制限に伸びるので、上限と fail-open を最初から設計に入れる）。

## ゴール

1. ⚠️ O1 専用の運用管理シート（**提出イベントの追記ログ**）が実装され、配備される。
2. ⚠️ ログ行が無制限に伸びない（上限と、上限に当たったときの挙動が決まっている）。
3. ⚠️ ロスターに同じメールが 2 行あるとき、**P-ID 重複と同じく止まる**（黙って先頭を採らない）。
4. ⚠️ プロジェクト跨ぎの二重採番が、**G1 を 1 行も触らずに**自己修復される。
5. ★ PR #148 がマージされ、`GSE_O1_Form_Builder` が実物へ **SHA-256 照合つきで**配備される。

## スコープ

### 含むもの
- `Form_O1/GSE_O1_Form_Builder.gs` の改修（#1 / #3 / #4 / #5）
- `Form_O1/o1_form_builder_test.cjs` へのテスト追加（★ 正常 / 不在 / 壊れ の 3 状態 + 陰性対照）
- PR #148 のマージ
- GAS 実物への配備（`GSE_O1_Form_Builder`）と管理シートの初期化

### 含まないもの
- ⚠️ #2（G1 側へのロスター形検査の移植 / T-23 の機械的検査）— 研究者判断でスコープ外
- ⚠️ `Form_G1/` の変更（★ #5 は **G1 を触らない**解で解く）
- ⚠️ `GSE_O1_Submit.gs` の変更（★ 今回の 4 件はいずれも Builder 側）
- ⚠️ §5 の持ち越し（連絡先空欄 / gse-dataset push / 死リンク / validate_blocks 17 件 / 所要時間 3 通り）
- ⚠️ 送信 timeout の実測（`check-o1-release-readiness.sh` の残 1 件・研究者の実機操作）

## 受け入れ条件

- [ ] `node Form_O1/o1_form_builder_test.cjs` が緑（★ 追加分を含め、陽性対照つき）
- [ ] `bash Form_O1/o1_form_builder_mutation_test.sh` が緑（★ 変異が**当たっている**ことを先に確認）
- [ ] ⚠️ 管理シートが未設定でも **被験者の登録は止まらない**（fail-open）ことをテストで固定
- [ ] ⚠️ 管理シート ID にロスター ID を入れたら **構築系が止まる**（fail-closed）ことをテストで固定
- [ ] ⚠️ メール重複で **発番も送信もしない**ことをテストで固定
- [ ] ⚠️ 二重採番が起きたとき O1 が **自分を採番し直して送る**ことをテストで固定
- [ ] PR #148 が MERGED
- [ ] ⚠️ 実物 `GSE_O1_Form_Builder` の SHA-256 が repo 側と一致

## 関連ドキュメント

- `docs/o1-deletion-ledger.md` §5b（P-ID↔個人の対応表は 1 か所）
- `.claude/skills/data-privacy/SKILL.md`
- `.claude/skills/verify-before-claiming/SKILL.md`
- `.claude/skills/browser-verification/SKILL.md`

## 運用メモ

- /reimagine 適用: **Yes**（★ #5 のみ。設計判断であり、案が複数ある）
- 理由: 研究者の選択。#1/#3/#4 は自明な実装なので /reimagine は不要。
